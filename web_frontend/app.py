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
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

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

@app.route('/insights')
def insights():
    """Insights management page."""
    return render_template('insights.html')

@app.route('/config')
def config():
    """Pipeline configuration page."""
    return render_template('config.html')

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

# Insights Management API Endpoints

@app.route('/api/insights')
def get_insights():
    """Get insights with pagination."""
    try:
        from supabase_storage.supabase_client import get_supabase_admin_client
        from deduplication.supabase_lookup import get_insight_status_summary
        
        # Get pagination parameters
        page = int(request.args.get('page', 1))
        limit = int(request.args.get('limit', 10))
        offset = (page - 1) * limit
        
        client = get_supabase_admin_client()
        
        # Get total count
        count_result = client.table('insights').select('id', count='exact').execute()
        total_count = count_result.count if count_result.count else 0
        
        # Get insights with pagination
        result = client.table('insights').select('*').range(offset, offset + limit - 1).order('id', desc=True).execute()
        
        insights = []
        if result.data:
            for insight in result.data:
                # Check if insight has any status records (used vs not used)
                status_summary = get_insight_status_summary(insight['id'])
                has_status = status_summary['total_combinations'] > 0
                
                insights.append({
                    'id': insight['id'],
                    'insight': insight['insight'],
                    'results': insight['results'],
                    'limitations_context': insight['limitations_context'],
                    'difference_score': insight['difference_score'],
                    'status': 'Tested' if has_status else 'Not Tested',
                    'status_details': status_summary
                })
        
        return jsonify({
            'insights': insights,
            'total_count': total_count,
            'page': page,
            'limit': limit,
            'total_pages': (total_count + limit - 1) // limit
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/products')
def get_products():
    """Get all available products."""
    try:
        from supabase_storage.schema_manager import get_all_products
        
        products = get_all_products()
        return jsonify({'products': [p['name'] for p in products]})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/regions')
def get_regions():
    """Get all available regions."""
    try:
        from supabase_storage.schema_manager import get_all_regions
        
        regions = get_all_regions()
        return jsonify({'regions': [r['code'] for r in regions]})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/insights/<insight_id>/status', methods=['POST'])
def update_insight_status(insight_id):
    """Move insight to testing status."""
    try:
        from supabase_storage.supabase_client import get_supabase_admin_client
        from supabase_storage.insight_inserter import move_insight_to_testing
        
        data = request.get_json()
        product_name = data.get('product_name')
        region_code = data.get('region_code')
        status = data.get('status')  # 'whitelist' or 'blacklist'
        
        if not all([product_name, region_code, status]):
            return jsonify({'error': 'Missing required fields'}), 400
        
        if status not in ['whitelist', 'blacklist']:
            return jsonify({'error': 'Status must be whitelist or blacklist'}), 400
        
        client = get_supabase_admin_client()
        
        # Check for existing status record to prevent conflicts when adding new
        existing_status = client.table('status').select('*').eq('insight_id', insight_id).eq('product_name', product_name).eq('region_code', region_code).execute()
        
        # If this is a new status (not editing), check for conflicts
        if not existing_status.data:
            # This is a new status record - check if it would create a conflict
            # For now, we allow multiple statuses per product/region combination
            pass
        
        # Map frontend status to backend status (use the actual enum values)
        backend_status = 'whitelist' if status == 'whitelist' else 'blacklist'
        
        success = move_insight_to_testing(client, insight_id, product_name, region_code, backend_status)
        
        if success:
            return jsonify({'message': 'Status updated successfully'})
        else:
            return jsonify({'error': 'Failed to update status'}), 500
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/insights/<insight_id>/status-details')
def get_insight_status_details(insight_id):
    """Get detailed status information for an insight."""
    try:
        from deduplication.supabase_lookup import get_insight_status_summary
        
        status_summary = get_insight_status_summary(insight_id)
        
        # Transform the data for frontend display
        details = []
        for record in status_summary.get('records', []):
            # Map backend status to frontend display (using actual enum values)
            display_status = 'Whitelist' if record['status'] == 'whitelist' else 'Blacklist'
            details.append({
                'product_name': record['product_name'],
                'region_code': record['region_code'],
                'status': display_status,
                'updated_at': record['updated_at']
            })
        
        return jsonify({
            'details': details,
            'summary': status_summary['status_breakdown']
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

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
    port = int(os.environ.get('PORT', 5003))
    debug = os.environ.get('FLASK_ENV') != 'production'
    
    print("🚀 Starting Ad-Creative Insight Pipeline Web Interface...")
    print(f"📱 Running on port: {port}")
    
    socketio.run(app, debug=debug, host='0.0.0.0', port=port)