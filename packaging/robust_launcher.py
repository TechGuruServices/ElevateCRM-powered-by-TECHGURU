
import os
import sys
import threading
import webbrowser
import time
from pathlib import Path
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Add current directory to Python path for imports
current_dir = Path(__file__).parent if not getattr(sys, 'frozen', False) else Path(sys.executable).parent
sys.path.insert(0, str(current_dir))

# Simple HTML UI
SIMPLE_UI = """<!DOCTYPE html>
<html>
<head>
    <title>ElevateCRM - TECHGURU</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 0; padding: 40px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); min-height: 100vh; }
        .container { max-width: 700px; margin: 0 auto; background: rgba(255,255,255,0.95); padding: 40px; border-radius: 20px; box-shadow: 0 10px 30px rgba(0,0,0,0.2); }
        h1 { color: #333; text-align: center; margin-bottom: 10px; font-size: 2.5em; }
        .subtitle { text-align: center; color: #666; margin-bottom: 30px; font-size: 1.2em; }
        .button { display: inline-block; padding: 15px 30px; background: linear-gradient(45deg, #007bff, #0056b3); color: white; text-decoration: none; border-radius: 10px; margin: 10px; transition: all 0.3s; font-weight: bold; }
        .button:hover { transform: translateY(-3px); box-shadow: 0 6px 20px rgba(0,123,255,0.4); }
        .info { background: linear-gradient(45deg, #e7f3ff, #f0f8ff); padding: 25px; border-radius: 15px; margin: 30px 0; border-left: 5px solid #007bff; }
        .status { color: #28a745; font-weight: bold; font-size: 1.1em; }
        .grid { display: grid; grid-template-columns: 1fr 1fr; gap: 15px; margin: 30px 0; }
        .feature { background: #f8f9fa; padding: 15px; border-radius: 10px; text-align: center; }
        ul li { margin-bottom: 10px; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🚀 ElevateCRM</h1>
        <p class="subtitle">by TECHGURU</p>
        
        <div class="info">
            <div class="status">✅ Server Status: Running on localhost:8000</div>
            <div><strong>📱 Mode:</strong> Standalone Windows Application</div>
            <div><strong>💾 Database:</strong> SQLite (Local Storage)</div>
            <div><strong>🔐 Security:</strong> JWT Authentication Enabled</div>
        </div>
        
        <div style="text-align: center; margin: 40px 0;">
            <a href="/docs" class="button">📚 API Documentation</a>
            <a href="/api/v1/health" class="button">❤️ Health Check</a>
        </div>
        
        <div class="grid">
            <div class="feature">
                <h4>👥 Customer Management</h4>
                <p>/api/v1/customers/</p>
            </div>
            <div class="feature">
                <h4>📦 Inventory Tracking</h4>
                <p>/api/v1/products/</p>
            </div>
            <div class="feature">
                <h4>📝 Order Processing</h4>
                <p>/api/v1/orders/</p>
            </div>
            <div class="feature">
                <h4>🔐 Authentication</h4>
                <p>/api/v1/auth/</p>
            </div>
        </div>
        
        <h3>🎯 Getting Started</h3>
        <ul>
            <li><strong>API Docs:</strong> Click "API Documentation" for full Swagger interface</li>
            <li><strong>Health Check:</strong> Verify all services are running properly</li>
            <li><strong>Authentication:</strong> Create user accounts and get JWT tokens</li>
            <li><strong>Data Management:</strong> Use the API endpoints to manage your business data</li>
        </ul>
        
        <div style="margin-top: 40px; padding: 20px; background: #ffe6e6; border-radius: 10px; text-align: center;">
            <strong>⚠️ Important:</strong> Keep the console window open while using ElevateCRM
        </div>
    </div>
</body>
</html>"""

class ElevateCRMLauncher:
    def __init__(self):
        self.app_dir = current_dir
        self.backend_port = 8000
        self.frontend_url = f"http://localhost:{self.backend_port}"
        
    def setup_directories(self):
        """Create necessary directories"""
        dirs = ["data", "logs", "uploads"]
        for dir_name in dirs:
            dir_path = self.app_dir / dir_name
            dir_path.mkdir(parents=True, exist_ok=True)
            logger.info(f"Created directory: {dir_path}")
    
    def create_minimal_app(self):
        """Create a minimal FastAPI app that works without complex imports"""
        try:
            from fastapi import FastAPI
            from fastapi.responses import HTMLResponse, JSONResponse
            import uvicorn
            
            app = FastAPI(
                title="ElevateCRM Standalone",
                description="TECHGURU CRM + Inventory Management",
                version="1.0.0"
            )
            
            @app.get("/", response_class=HTMLResponse)
            async def root():
                return SIMPLE_UI
                
            @app.get("/ui", response_class=HTMLResponse)
            async def ui():
                return SIMPLE_UI
            
            @app.get("/api/v1/health")
            async def health():
                return {
                    "status": "healthy",
                    "service": "elevatecrm-standalone",
                    "mode": "standalone",
                    "version": "1.0.0",
                    "database": "sqlite",
                    "port": self.backend_port
                }
            
            @app.get("/docs-redirect")
            async def docs_redirect():
                return {"message": "API documentation available at /docs"}
            
            logger.info("Minimal FastAPI app created successfully")
            return app
            
        except Exception as e:
            logger.error(f"Failed to create minimal app: {e}")
            return None
    
    def create_full_app(self):
        """Try to create the full backend app"""
        try:
            # Try to import the full backend
            os.environ.setdefault("DATABASE_URL", f"sqlite:///{self.app_dir}/data/elevatecrm.db")
            os.environ.setdefault("SECRET_KEY", "standalone-secret-key-change-in-production")
            os.environ.setdefault("DEBUG", "true")
            
            from app.main import app as backend_app
            
            # Override root route
            @backend_app.get("/", response_class=HTMLResponse)
            async def root():
                return SIMPLE_UI
                
            logger.info("Full backend app loaded successfully")
            return backend_app
            
        except Exception as e:
            logger.warning(f"Could not load full backend, using minimal app: {e}")
            return None
    
    def start_backend(self):
        """Start the backend server"""
        try:
            # Try full app first, fallback to minimal
            app = self.create_full_app()
            if app is None:
                app = self.create_minimal_app()
            
            if app is None:
                print("❌ Could not create any app!")
                input("Press Enter to exit...")
                return
            
            print(f"🌐 Starting server on http://127.0.0.1:{self.backend_port}")
            
            import uvicorn
            uvicorn.run(
                app, 
                host="127.0.0.1", 
                port=self.backend_port, 
                log_level="info"
            )
            
        except Exception as e:
            logger.error(f"Failed to start server: {e}")
            print(f"❌ Server failed to start: {e}")
            input("Press Enter to exit...")
    
    def open_browser(self):
        """Open browser after delay"""
        time.sleep(3)
        try:
            print(f"🌐 Opening browser at {self.frontend_url}")
            webbrowser.open(self.frontend_url)
        except Exception as e:
            print(f"⚠️ Could not open browser automatically: {e}")
            print(f"💻 Please open manually: {self.frontend_url}")
    
    def run(self):
        """Main entry point"""
        print("🚀 Starting ElevateCRM Standalone Application")
        print("=" * 60)
        print(f"📁 Working directory: {self.app_dir}")
        print(f"🌐 Server will start on: {self.frontend_url}")
        print("=" * 60)
        
        self.setup_directories()
        
        # Start browser in background
        browser_thread = threading.Thread(target=self.open_browser, daemon=True)
        browser_thread.start()
        
        # Start server (blocking)
        self.start_backend()

if __name__ == "__main__":
    try:
        launcher = ElevateCRMLauncher()
        launcher.run()
    except KeyboardInterrupt:
        print("\n👋 Shutting down ElevateCRM...")
    except Exception as e:
        print(f"❌ Fatal error: {e}")
        input("Press Enter to exit...")
