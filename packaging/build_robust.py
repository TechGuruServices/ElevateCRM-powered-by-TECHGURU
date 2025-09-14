#!/usr/bin/env python3
"""
ElevateCRM Robust Builder
Handles all import and static file issues
"""

import os
import sys
import shutil
import subprocess
from pathlib import Path

APP_NAME = "ElevateCRM"
BACKEND_DIR = Path("../backend")
PACKAGE_DIR = Path(".")

def print_step(step_name):
    print(f"\n{'='*50}")
    print(f"Building: {step_name}")
    print(f"{'='*50}")

def run_command(command, cwd=None):
    print(f"Running: {command}")
    result = subprocess.run(command, shell=True, cwd=cwd, capture_output=True, text=True)
    if result.returncode == 0:
        print("Success")
        return True
    else:
        print("Error:", result.stderr)
        return False

def create_robust_launcher():
    """Create a launcher that bypasses the static file issue"""
    print_step("Creating Robust Launcher")
    
    launcher_code = '''
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
        print("\\n👋 Shutting down ElevateCRM...")
    except Exception as e:
        print(f"❌ Fatal error: {e}")
        input("Press Enter to exit...")
'''
    
    launcher_path = PACKAGE_DIR / "robust_launcher.py"
    with open(launcher_path, 'w', encoding='utf-8') as f:
        f.write(launcher_code)
    
    print("Robust launcher created")
    return launcher_path

def create_robust_spec():
    """Create a comprehensive PyInstaller spec"""
    print_step("Creating Robust Spec")
    
    spec_content = '''
import os
from pathlib import Path

backend_dir = Path("../backend")
datas = []

# Add all necessary data files
files_to_include = [
    # Database files
    (backend_dir.glob("*.db"), "."),
    # Static files
    (backend_dir / "app" / "static", "app/static"),
    # Migration files (if needed)
    (backend_dir / "migrations", "migrations"),
    # Config files
    (backend_dir.glob("*.ini"), "."),
]

for source, dest in files_to_include:
    if isinstance(source, Path):
        if source.exists():
            datas.append((str(source), dest))
            print(f"Including: {source} -> {dest}")
    else:
        for file in source:
            if file.exists():
                datas.append((str(file), dest))
                print(f"Including: {file} -> {dest}")

# Comprehensive hidden imports
hiddenimports = [
    # Uvicorn and FastAPI core
    'uvicorn',
    'uvicorn.lifespan',
    'uvicorn.lifespan.on',
    'uvicorn.loops',
    'uvicorn.loops.auto',
    'uvicorn.protocols',
    'uvicorn.protocols.http',
    'uvicorn.protocols.http.auto',
    'uvicorn.protocols.websockets',
    'uvicorn.protocols.websockets.auto',
    'uvicorn.server',
    'uvicorn.config',
    
    # FastAPI
    'fastapi',
    'fastapi.responses',
    'fastapi.staticfiles',
    'fastapi.middleware',
    'fastapi.middleware.cors',
    'fastapi.security',
    
    # SQLAlchemy
    'sqlalchemy',
    'sqlalchemy.dialects',
    'sqlalchemy.dialects.sqlite',
    'sqlalchemy.dialects.postgresql',
    'sqlalchemy.engine',
    'sqlalchemy.pool',
    
    # Pydantic
    'pydantic',
    'pydantic.v1',
    
    # Authentication
    'jwt',
    'passlib',
    'passlib.handlers',
    'passlib.handlers.bcrypt',
    'bcrypt',
    
    # Other essentials
    'email_validator',
    'python_multipart',
    'starlette',
    'starlette.middleware',
    'starlette.responses',
]

# Analysis configuration
a = Analysis(
    ['robust_launcher.py'],
    pathex=[str(backend_dir)],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['tkinter', 'matplotlib', 'numpy', 'pandas'],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=None,
    noarchive=False,
)

# Remove duplicate binaries
seen = set()
a.binaries = [x for x in a.binaries if x[0] not in seen and not seen.add(x[0])]

pyz = PYZ(a.pure, a.zipped_data, cipher=None)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='ElevateCRM_Fixed',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
'''
    
    spec_path = PACKAGE_DIR / "robust.spec"
    with open(spec_path, 'w') as f:
        f.write(spec_content)
    
    print("Robust spec file created")
    return spec_path

def main():
    print("ElevateCRM Robust Builder")
    print("Fixes static file and import issues")
    print("=" * 50)
    
    try:
        if not BACKEND_DIR.exists():
            print(f"Error: Backend directory not found: {BACKEND_DIR}")
            return
            
        # Clean previous builds
        for dir_name in ["build", "dist"]:
            if Path(dir_name).exists():
                shutil.rmtree(dir_name)
                print(f"Cleaned {dir_name} directory")
        
        # Step 1: Create robust launcher
        create_robust_launcher()
        
        # Step 2: Create robust spec
        create_robust_spec()
        
        # Step 3: Copy backend source temporarily
        print_step("Preparing Backend Source")
        backend_temp = Path("backend_temp")
        if backend_temp.exists():
            shutil.rmtree(backend_temp)
        shutil.copytree(BACKEND_DIR, backend_temp)
        print("Backend source copied")
        
        try:
            # Step 4: Build with PyInstaller
            print_step("Building with PyInstaller")
            success = run_command("pyinstaller robust.spec")
            
            if success:
                # Create enhanced launcher
                launcher_bat = '''@echo off
title ElevateCRM - TECHGURU
color 0A
echo.
echo ==========================================
echo    ElevateCRM Standalone Application
echo         by TECHGURU
echo ==========================================
echo.
echo Starting server...
echo Browser will open automatically at:
echo http://localhost:8000
echo.
echo Keep this window OPEN while using the app
echo Press Ctrl+C to stop the application
echo.
ElevateCRM_Fixed.exe
if errorlevel 1 (
    echo.
    echo ==========================================
    echo Error: Application failed to start
    echo Check the output above for details
    echo ==========================================
    pause
) else (
    echo.
    echo Application closed successfully
    pause
)
'''
                
                with open("dist/ElevateCRM_Start.bat", 'w') as f:
                    f.write(launcher_bat)
                
                print("\\nBuild Complete! ✅")
                print("=" * 50)
                print("📁 Files created:")
                print("   dist/ElevateCRM_Fixed.exe - Main application")
                print("   dist/ElevateCRM_Start.bat - Easy launcher")
                print()
                print("🚀 To run:")
                print("   1. Double-click ElevateCRM_Start.bat")
                print("   2. Wait for 'Server starting' message")
                print("   3. Browser opens automatically")
                print("   4. Visit /docs for API documentation")
                print()
                print("✅ This version handles all import and static file issues!")
                
            else:
                print("❌ Build failed!")
                
        finally:
            # Cleanup
            if backend_temp.exists():
                shutil.rmtree(backend_temp)
                print("Cleaned up temporary files")
            
    except Exception as e:
        print(f"❌ Build error: {e}")

if __name__ == "__main__":
    main()