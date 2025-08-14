"""
Simple Flask web frontend for the Ad-Creative Insight Pipeline.
Shows real-time progress of pipeline execution.
"""

from flask import Flask, render_template, jsonify, request
import sys
import os

# Add the project root to Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Try to import main pipeline, but handle gracefully if dependencies are missing
try:
    from main import run_pipeline
    PIPELINE_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Pipeline dependencies not available: {e}")
    PIPELINE_AVAILABLE = False
    
    def run_pipeline(config):
        return {"error": "Pipeline dependencies not available"}

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'your-secret-key-here')

# Configure Flask for Vercel serverless environment
app.config['ENV'] = 'production'
app.config['DEBUG'] = False

# For Vercel serverless environment, we'll disable SocketIO and use polling instead
SOCKETIO_AVAILABLE = False

# Global variables to track pipeline state (simplified for Vercel)
pipeline_status = {
    'running': False,
    'current_step': None,
    'total_insights': 0,
    'errors': ['Pipeline execution not available in serverless environment'],
    'message': 'Use the insights management page to view existing data'
}

def emit_progress_update():
    """Emit progress update to all connected clients."""
    # SocketIO disabled for Vercel serverless environment
    pass

# Pipeline execution is not available in Vercel serverless environment
# This function is kept for compatibility but will not be used

@app.route('/health')
def health_check():
    """Health check endpoint for Railway."""
    return jsonify({
        'status': 'healthy',
        'pipeline_available': PIPELINE_AVAILABLE,
        'message': 'Ad-Creative Insight Pipeline Web Interface is running'
    })

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
    # For Vercel serverless environment, we can't run long-running processes
    # Return a message indicating this limitation
    return jsonify({
        'error': 'Pipeline execution not available in serverless environment',
        'message': 'Use the insights management page to view existing data'
    }), 501

@app.route('/api/reset', methods=['POST'])
def reset_pipeline():
    """Reset pipeline status."""
    global pipeline_status
    pipeline_status = {
        'running': False,
        'current_step': None,
        'total_insights': 0,
        'errors': ['Pipeline execution not available in serverless environment'],
        'message': 'Use the insights management page to view existing data'
    }
    return jsonify({'message': 'Pipeline status reset'})

# Insights Management API Endpoints

@app.route('/api/insights')
def get_insights():
    """Get insights with pagination."""
    # Get pagination parameters
    page = int(request.args.get('page', 1))
    limit = int(request.args.get('limit', 10))
    offset = (page - 1) * limit
    
    # Try to get real data from Supabase
    try:
        from supabase import create_client
        from utils.config import Config
        
        # Create client directly to avoid the proxy issue
        client = create_client(Config.SUPABASE_URL, Config.SUPABASE_SERVICE_ROLE_KEY)
        
        # Get total count
        count_result = client.table('insights').select('id', count='exact').execute()
        total_count = count_result.count if count_result.count else 0
        
        # Get insights with pagination
        result = client.table('insights').select('*').range(offset, offset + limit - 1).order('id', desc=True).execute()
        
        insights = []
        if result.data:
            for insight in result.data:
                insights.append({
                    'id': insight['id'],
                    'insight': insight['insight'],
                    'results': insight.get('results', ''),
                    'limitations_context': insight.get('limitations_context', ''),
                    'difference_score': insight.get('difference_score', 0),
                    'status': 'Not Tested',  # Simplified for now
                    'status_details': {'total_combinations': 0}
                })
        
        return jsonify({
            'insights': insights,
            'total_count': total_count,
            'page': page,
            'limit': limit,
            'total_pages': (total_count + limit - 1) // limit
        })
        
    except ImportError as e:
        # Return mock data if dependencies aren't available
        mock_insights = [
            {
                'id': f'mock-{i}',
                'insight': f'Sample insight {i}: This is a mock insight for testing the interface.',
                'results': f'Mock results for insight {i}',
                'limitations_context': f'Mock limitations for insight {i}',
                'difference_score': 0.8,
                'status': 'Not Tested',
                'status_details': {'total_combinations': 0}
            }
            for i in range(1, min(limit + 1, 6))  # Show up to 5 mock insights
        ]
        
        return jsonify({
            'insights': mock_insights,
            'total_count': 5,
            'page': page,
            'limit': limit,
            'total_pages': 1,
            'note': 'Showing mock data - pipeline dependencies not available'
        })
        
    except Exception as e:
        print(f"Error in get_insights: {str(e)}")
        
        # Return mock data on any error
        mock_insights = [
            {
                'id': 'error-mock',
                'insight': 'Unable to connect to database. This is mock data for testing.',
                'results': 'Database connection error',
                'limitations_context': 'Cannot access real data',
                'difference_score': 0,
                'status': 'Error',
                'status_details': {'total_combinations': 0}
            }
        ]
        
        return jsonify({
            'insights': mock_insights,
            'total_count': 1,
            'page': page,
            'limit': limit,
            'total_pages': 1,
            'error': f'Database error: {str(e)}'
        })

@app.route('/api/products')
def get_products():
    """Get all available products."""
    try:
        from supabase import create_client
        from utils.config import Config
        
        # Create client directly
        client = create_client(Config.SUPABASE_URL, Config.SUPABASE_SERVICE_ROLE_KEY)
        result = client.table('products').select('*').execute()
        
        products = [p['name'] for p in result.data] if result.data else []
        return jsonify({'products': products})
        
    except ImportError as e:
        # Return default products if dependencies aren't available
        default_products = ['Facebook Ads', 'Google Ads', 'TikTok Ads', 'LinkedIn Ads']
        return jsonify({'products': default_products, 'note': 'Using default products'})
    except Exception as e:
        # Return default products on error
        default_products = ['Facebook Ads', 'Google Ads', 'TikTok Ads', 'LinkedIn Ads']
        return jsonify({'products': default_products, 'error': f'Database error: {str(e)}'})

@app.route('/api/regions')
def get_regions():
    """Get all available regions."""
    try:
        from supabase import create_client
        from utils.config import Config
        
        # Create client directly
        client = create_client(Config.SUPABASE_URL, Config.SUPABASE_SERVICE_ROLE_KEY)
        result = client.table('regions').select('*').execute()
        
        regions = [r['code'] for r in result.data] if result.data else []
        return jsonify({'regions': regions})
        
    except ImportError as e:
        # Return default regions if dependencies aren't available
        default_regions = ['US', 'EU', 'APAC', 'LATAM', 'MENA', 'CA', 'UK', 'AU']
        return jsonify({'regions': default_regions, 'note': 'Using default regions'})
    except Exception as e:
        # Return default regions on error
        default_regions = ['US', 'EU', 'APAC', 'LATAM', 'MENA', 'CA', 'UK', 'AU']
        return jsonify({'regions': default_regions, 'error': f'Database error: {str(e)}'})

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

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5003))
    debug = os.environ.get('FLASK_ENV') != 'production'
    
    print("🚀 Starting Ad-Creative Insight Pipeline Web Interface...")
    print(f"📱 Running on port: {port}")
    
    app.run(debug=debug, host='0.0.0.0', port=port)