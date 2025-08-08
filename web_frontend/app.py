"""
Simple Flask web frontend for the Ad-Creative Insight Pipeline.
Shows real-time progress of pipeline execution.
"""

from flask import Flask, render_template, jsonify, request
from flask_socketio import SocketIO, emit
import threading
import time
import sys
import os

# Add the project root to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main import run_pipeline
from utils.config import Config

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'
socketio = SocketIO(app, cors_allowed_origins="*")

# Global variables to track pipeline state
pipeline_status = {
    'running': False,
    'current_step': None,
    'steps': {
        'data_collection': {'status': 'pending', 'count': 0, 'message': ''},
        'cleaning': {'status': 'pending', 'count': 0, 'message': ''},
        'structuring': {'status': 'pending', 'count': 0, 'message': ''},
        'deduplication': {'status': 'pending', 'count': 0, 'message': ''},
        'storage': {'status': 'pending', 'count': 0, 'message': ''}
    },
    'total_insights': 0,
    'start_time': None,
    'end_time': None,
    'errors': [],
    'scraped_data': []  # Store scraped data for viewing
}

def emit_progress_update():
    """Emit progress update to all connected clients."""
    socketio.emit('progress_update', pipeline_status)

def run_real_pipeline(sources_config):
    """
    Run the actual pipeline with real Reddit data and progress updates.
    """
    global pipeline_status
    
    try:
        pipeline_status['running'] = True
        pipeline_status['start_time'] = time.time()
        pipeline_status['errors'] = []
        
        # Step 1: Data Collection
        pipeline_status['current_step'] = 'data_collection'
        pipeline_status['steps']['data_collection']['status'] = 'running'
        pipeline_status['steps']['data_collection']['message'] = 'Scraping r/ppc subreddit...'
        emit_progress_update()
        
        # Import here to avoid circular imports
        from data_collection.pipeline_entry import collect_and_process_data
        
        raw_content = collect_and_process_data(sources_config)
        raw_count = len(raw_content) if raw_content else 0
        
        # Store scraped data for viewing
        pipeline_status['scraped_data'] = raw_content[:10] if raw_content else []  # Store first 10 for display
        
        pipeline_status['steps']['data_collection']['status'] = 'completed'
        pipeline_status['steps']['data_collection']['count'] = raw_count
        pipeline_status['steps']['data_collection']['message'] = f'Collected {raw_count} posts from subreddits'
        emit_progress_update()
        
        if not raw_content:
            raise Exception("No raw content collected from Reddit")
        
        # Step 2: Cleaning
        pipeline_status['current_step'] = 'cleaning'
        pipeline_status['steps']['cleaning']['status'] = 'running'
        pipeline_status['steps']['cleaning']['message'] = 'Cleaning and normalizing text...'
        emit_progress_update()
        
        from cleaning.cleaning_controller import process_raw_content
        
        cleaned_content = process_raw_content(raw_content)
        cleaned_count = len(cleaned_content)
        
        pipeline_status['steps']['cleaning']['status'] = 'completed'
        pipeline_status['steps']['cleaning']['count'] = cleaned_count
        pipeline_status['steps']['cleaning']['message'] = f'Cleaned {cleaned_count} pieces of content'
        emit_progress_update()
        
        if not cleaned_content:
            raise Exception("No content survived cleaning process")
        
        # Step 3: Structuring
        pipeline_status['current_step'] = 'structuring'
        pipeline_status['steps']['structuring']['status'] = 'running'
        pipeline_status['steps']['structuring']['message'] = 'Converting to structured insights with LLM...'
        emit_progress_update()
        
        from structuring.structuring_controller import process_cleaned_content
        
        structured_insights = process_cleaned_content(cleaned_content)
        structured_count = len(structured_insights)
        
        pipeline_status['steps']['structuring']['status'] = 'completed'
        pipeline_status['steps']['structuring']['count'] = structured_count
        pipeline_status['steps']['structuring']['message'] = f'Created {structured_count} structured insights'
        emit_progress_update()
        
        if not structured_insights:
            raise Exception("No structured insights created")
        
        # Step 4: Deduplication
        pipeline_status['current_step'] = 'deduplication'
        pipeline_status['steps']['deduplication']['status'] = 'running'
        pipeline_status['steps']['deduplication']['message'] = 'Checking for duplicates...'
        emit_progress_update()
        
        from deduplication.deduplication_controller import batch_check_duplicates
        
        unique_insights = batch_check_duplicates(structured_insights)
        unique_count = len(unique_insights)
        
        pipeline_status['steps']['deduplication']['status'] = 'completed'
        pipeline_status['steps']['deduplication']['count'] = unique_count
        pipeline_status['steps']['deduplication']['message'] = f'Found {unique_count} unique insights'
        emit_progress_update()
        
        if not unique_insights:
            raise Exception("No unique insights found after deduplication")
        
        # Step 5: Storage
        pipeline_status['current_step'] = 'storage'
        pipeline_status['steps']['storage']['status'] = 'running'
        pipeline_status['steps']['storage']['message'] = 'Storing insights in Supabase...'
        emit_progress_update()
        
        from supabase_storage.supabase_client import get_supabase_admin_client
        from supabase_storage.insight_inserter import batch_insert_insights
        
        supabase_admin_client = get_supabase_admin_client()
        successful_inserts, failed_inserts = batch_insert_insights(supabase_admin_client, unique_insights)
        stored_count = len(successful_inserts)
        
        pipeline_status['steps']['storage']['status'] = 'completed'
        pipeline_status['steps']['storage']['count'] = stored_count
        pipeline_status['steps']['storage']['message'] = f'Successfully stored {stored_count} insights'
        emit_progress_update()
        
        if failed_inserts:
            pipeline_status['errors'].append(f"Failed to store {len(failed_inserts)} insights")
        
        # Complete
        pipeline_status['running'] = False
        pipeline_status['current_step'] = None
        pipeline_status['total_insights'] = stored_count
        pipeline_status['end_time'] = time.time()
        emit_progress_update()
        
    except Exception as e:
        pipeline_status['running'] = False
        pipeline_status['errors'].append(str(e))
        pipeline_status['end_time'] = time.time()
        
        # Mark current step as error
        if pipeline_status['current_step']:
            pipeline_status['steps'][pipeline_status['current_step']]['status'] = 'error'
            pipeline_status['steps'][pipeline_status['current_step']]['message'] = f'Error: {str(e)}'
        
        pipeline_status['current_step'] = None
        emit_progress_update()

@app.route('/')
def index():
    """Main dashboard page."""
    return render_template('index.html')

@app.route('/api/status')
def get_status():
    """Get current pipeline status."""
    return jsonify(pipeline_status)

@app.route('/api/start', methods=['POST'])
def start_pipeline():
    """Start the pipeline execution."""
    global pipeline_status
    
    if pipeline_status['running']:
        return jsonify({'error': 'Pipeline is already running'}), 400
    
    # Reset status
    pipeline_status = {
        'running': False,
        'current_step': None,
        'steps': {
            'data_collection': {'status': 'pending', 'count': 0, 'message': ''},
            'cleaning': {'status': 'pending', 'count': 0, 'message': ''},
            'structuring': {'status': 'pending', 'count': 0, 'message': ''},
            'deduplication': {'status': 'pending', 'count': 0, 'message': ''},
            'storage': {'status': 'pending', 'count': 0, 'message': ''}
        },
        'total_insights': 0,
        'start_time': None,
        'end_time': None,
        'errors': [],
        'scraped_data': []
    }
    
    # Get configuration from request - default to r/ppc
    config = request.get_json() or {}
    sources_config = config.get('sources', {
        'reddit': {
            'enabled': True,
            'subreddits': ['ppc'],
            'limit': 20,
            'time_filter': 'week',
            'sort': 'hot'
        },
        'web': {'enabled': False},
        'apis': {'enabled': False}
    })
    
    # Start pipeline in background thread
    thread = threading.Thread(target=run_real_pipeline, args=(sources_config,))
    thread.daemon = True
    thread.start()
    
    return jsonify({'message': 'Pipeline started successfully'})

@app.route('/api/reset', methods=['POST'])
def reset_pipeline():
    """Reset pipeline status."""
    global pipeline_status
    pipeline_status = {
        'running': False,
        'current_step': None,
        'steps': {
            'data_collection': {'status': 'pending', 'count': 0, 'message': ''},
            'cleaning': {'status': 'pending', 'count': 0, 'message': ''},
            'structuring': {'status': 'pending', 'count': 0, 'message': ''},
            'deduplication': {'status': 'pending', 'count': 0, 'message': ''},
            'storage': {'status': 'pending', 'count': 0, 'message': ''}
        },
        'total_insights': 0,
        'start_time': None,
        'end_time': None,
        'errors': [],
        'scraped_data': []
    }
    emit_progress_update()
    return jsonify({'message': 'Pipeline status reset'})

@socketio.on('connect')
def handle_connect():
    """Handle client connection."""
    print('Client connected')
    emit('progress_update', pipeline_status)

@socketio.on('disconnect')
def handle_disconnect():
    """Handle client disconnection."""
    print('Client disconnected')

if __name__ == '__main__':
    print("🚀 Starting Ad-Creative Insight Pipeline Web Interface...")
    print("📱 Open your browser to: http://localhost:5002")
    socketio.run(app, debug=True, host='0.0.0.0', port=5002)