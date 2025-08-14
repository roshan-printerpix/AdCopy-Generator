#!/usr/bin/env python3
"""
Simple startup script for Railway deployment
"""
import os
import sys

# Add current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import and run the Flask app
from web_frontend.app import app, socketio

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5003))
    debug = os.environ.get('FLASK_ENV') != 'production'
    
    print("🚀 Starting Ad-Creative Insight Pipeline Web Interface...")
    print(f"📱 Running on port: {port}")
    
    socketio.run(app, debug=debug, host='0.0.0.0', port=port)