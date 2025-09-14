
import os
import sys
import threading
import webbrowser
import time
from pathlib import Path
import uvicorn
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Simple HTML UI
SIMPLE_UI = """<!DOCTYPE html>
<html>
<head>
    <title>ElevateCRM - TECHGURU</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }
        .container { max-width: 600px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        h1 { color: #333; text-align: center; }
        .button { display: inline-block; padding: 12px 24px; background: #007bff; color: white; text-decoration: none; border-radius: 5px; margin: 10px; }
        .button:hover { background: #0056b3; }
        .info { background: #e7f3ff; padding: 15px; border-radius: 5px; margin: 20px 0; }
    </style>
</head>
<body>
    <div class="container">
        <h1>ElevateCRM</h1>
        <p style="text-align: center; color: #666;">by TECHGURU</p>
        
        <div class="info">
            <strong>Server Status:</strong> Running on localhost:8000<br>
            <strong>Mode:</strong> Standalone Windows Application
        </div>
        
        <div style="text-align: center;">
            <a href="/docs" class="button">API Documentation</a>
            <a href="/api/v1/health" class="button">Health Check</a>
        </div>
        
        <h3>Quick Start</h3>
        <ul>
            <li>Visit <strong>/docs</strong> for interactive API documentation</li>
            <li>Visit <strong>/api/v1/health</strong> to check system status</li>
            <li>Use the API endpoints to manage your CRM data</li>
        </ul>
    </div>
</body>
</html>"""

class ElevateCRMLauncher:
    def __init__(self):
        self.app_dir = Path(sys.executable).parent if getattr(sys, 'frozen', False) else Path(__file__).parent
        self.backend_port = 8000
        self.frontend_url = f"http://localhost:{self.backend_port}"
        
    def setup_directories(self):
        dirs = ["data", "logs", "uploads"]
        for dir_name in dirs:
            (self.app_dir / dir_name).mkdir(exist_ok=True)
    
    def create_fastapi_app(self):
        from app.main import app as backend_app
        
        @backend_app.get("/", response_class=HTMLResponse)
        async def root():
            return SIMPLE_UI
        
        return backend_app
    
    def start_backend(self):
        try:
            app = self.create_fastapi_app()
            uvicorn.run(app, host="127.0.0.1", port=self.backend_port, log_level="info", access_log=False)
        except Exception as e:
            logger.error(f"Failed to start: {e}")
    
    def open_browser(self):
        time.sleep(2)
        try:
            webbrowser.open(self.frontend_url)
        except:
            pass
    
    def run(self):
        print("Starting ElevateCRM...")
        self.setup_directories()
        
        browser_thread = threading.Thread(target=self.open_browser, daemon=True)
        browser_thread.start()
        
        self.start_backend()

if __name__ == "__main__":
    launcher = ElevateCRMLauncher()
    launcher.run()
