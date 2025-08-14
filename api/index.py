"""
Vercel entry point for the Ad-Creative Insight Pipeline Web Interface
"""
import os
import sys

# Add the project root to Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Import the Flask app from the web_frontend directory
from web_frontend.app import app

# Vercel expects the app to be available as 'app'
if __name__ == "__main__":
    app.run()