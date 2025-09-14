#!/usr/bin/env python3
"""
ElevateCRM Fixed Launcher
Handles missing static files and ensures robust startup
"""

import os
import sys
import threading
import webbrowser
import time
from pathlib import Path
import uvicorn
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Simple HTML UI
SIMPLE_UI = """<!DOCTYPE html>
<html>
<head>
    <title>ElevateCRM - TECHGURU</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); min-height: 100vh; }
        .container { max-width: 600px; margin: 0 auto; background: rgba(255,255,255,0.95); padding: 30px; border-radius: 15px; box-shadow: 0 8px 25px rgba(0,0,0,0.15); backdrop-filter: blur(10px); }
        h1 { color: #333; text-align: center; margin-bottom: 10px; }
        .subtitle { text-align: center; color: #666; margin-bottom: 30px; font-style: italic; }
        .button { display: inline-block; padding: 12px 24px; background: linear-gradient(45deg, #007bff, #0056b3); color: white; text-decoration: none; border-radius: 8px; margin: 10px; transition: all 0.3s; box-shadow: 0 2px 10px rgba(0,123,255,0.3); }
        .button:hover { transform: translateY(-2px); box-shadow: 0 4px 15px rgba(0,123,255,0.4); }
        .info { background: linear-gradient(45deg, #e7f3ff, #f0f8ff); padding: 20px; border-radius: 10px; margin: 20px 0; border-left: 4px solid #007bff; }
        .status { color: #28a745; font-weight: bold; }
        ul { padding-left: 20px; }
        li { margin-bottom: 8px; }
        .logo { text-align: center; margin-bottom: 20px; font-size: 48px; }
    </style>
</head>
<body>
    <div class="container">
        <div class="logo">🚀</div>
        <h1>ElevateCRM</h1>
        <p class="subtitle">by TECHGURU</p>
        
        <div class="info">
            <div class="status">✅ Server Status: Running on localhost:8000</div>
            <div>📱 Mode: Standalone Windows Application</div>
            <div>💾 Database: SQLite (Local)</div>
        </div>
        
        <div style="text-align: center; margin: 30px 0;">
            <a href="/docs" class="button">📚 API Documentation</a>
            <a href="/api/v1/health" class="button">❤️ Health Check</a>
        </div>
        
        <h3>🎯 Quick Start Guide</h3>
        <ul>
            <li><strong>/docs</strong> - Interactive API documentation with Swagger UI</li>
            <li><strong>/api/v1/health</strong> - System health and status check</li>
            <li><strong>/api/v1/auth/</strong> - User authentication endpoints</li>
            <li><strong>/api/v1/customers/</strong> - Customer management</li>
            <li><strong>/api/v1/products/</strong> - Product and inventory</li>
        </ul>
        
        <div style="margin-top: 30px; padding: 15px; background: #f8f9fa; border-radius: 8px; text-align: center; font-size: 14px; color: #666;">
            <strong>💡 Tip:</strong> Keep this console window open while using ElevateCRM
        </div>
    </div>
</body>
</html>"""

class ElevateCRMLauncher:
    def __init__(self):
        self.app_dir = Path(sys.executable).parent if getattr(sys, 'frozen', False) else Path(__file__).parent
        self.backend_port = 8000
        self.frontend_url = f"http://localhost:{self.backend_port}"
        
    def setup_directories(self):
        """Create necessary directories"""
        dirs = ["data", "logs", "uploads", "app", "app/static"]
        for dir_name in dirs:
            dir_path = self.app_dir / dir_name
            dir_path.mkdir(parents=True, exist_ok=True)
        
        # Create a minimal static file if missing
        static_dir = self.app_dir / "app" / "static"
        readme_file = static_dir / "README.md"
        if not readme_file.exists():
            readme_file.write_text("# ElevateCRM Static Files\nStandalone executable static content.")
    
    def create_fastapi_app(self):
        """Create FastAPI app with safe static file handling"""
        # Import the backend app
        try:
            # Add the current directory to Python path for imports
            if str(self.app_dir) not in sys.path:
                sys.path.insert(0, str(self.app_dir))
            
            # Import the app directly (not create_app function)
            from app.main import app as backend_app
            
        except ImportError as e:
            logger.error(f"Could not import backend app: {e}")
            # Fallback: create minimal FastAPI app if import fails
            from fastapi import FastAPI
            backend_app = FastAPI(title="ElevateCRM", version="1.0.0")
            
            @backend_app.get("/api/v1/health")
            async def health():
                return {"status": "healthy", "mode": "standalone", "error": "backend_import_failed"}
        
        # Override the root route with our UI
        @backend_app.get("/", response_class=HTMLResponse)
        async def root():
            return SIMPLE_UI
            
        @backend_app.get("/ui", response_class=HTMLResponse)
        async def ui():
            return SIMPLE_UI
        
        # The static files are already mounted in app.main, but we need to ensure the directory exists
        static_path = self.app_dir / "app" / "static"
        if not static_path.exists():
            logger.warning(f"Static directory doesn't exist: {static_path}")
        
        return backend_app
    
    def start_backend(self):
        """Start the FastAPI backend server"""
        try:
            app = self.create_fastapi_app()
            logger.info(f"Starting server on http://127.0.0.1:{self.backend_port}")
            uvicorn.run(
                app, 
                host="127.0.0.1", 
                port=self.backend_port, 
                log_level="info", 
                access_log=False
            )
        except Exception as e:
            logger.error(f"Failed to start server: {e}")
            input("Press Enter to exit...")
    
    def open_browser(self):
        """Open the application in the default browser"""
        time.sleep(3)  # Give server time to start
        try:
            print(f"🌐 Opening browser at {self.frontend_url}")
            webbrowser.open(self.frontend_url)
        except Exception as e:
            logger.warning(f"Could not open browser: {e}")
            print(f"💻 Manually open: {self.frontend_url}")
    
    def run(self):
        """Main application entry point"""
        print("🚀 Starting ElevateCRM Standalone...")
        print("=" * 50)
        
        # Setup environment
        self.setup_directories()
        
        # Start browser in background
        browser_thread = threading.Thread(target=self.open_browser, daemon=True)
        browser_thread.start()
        
        # Start server (this blocks)
        self.start_backend()

if __name__ == "__main__":
    launcher = ElevateCRMLauncher()
    launcher.run()