#!/usr/bin/env python3
"""
ElevateCRM Backend-Only Executable Builder
Creates a standalone .exe with embedded static UI
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
    print(f"\n{'='*60}")
    print(f"🔧 {step_name}")
    print(f"{'='*60}")

def run_command(command, cwd=None):
    print(f"Running: {command}")
    result = subprocess.run(command, shell=True, cwd=cwd, capture_output=True, text=True)
    if result.returncode == 0:
        print("✅ Success")
        if result.stdout:
            print(result.stdout)
    else:
        print("❌ Error")
        if result.stderr:
            print(result.stderr)
    return result.returncode == 0

def create_launcher_with_ui():
    """Create launcher that includes the HTML UI"""
    print_step("Creating Standalone Launcher")
    
    launcher_code = '''
import os
import sys
import threading
import webbrowser
import time
from pathlib import Path
import uvicorn
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Embedded HTML UI
EMBEDDED_UI = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ElevateCRM - TECHGURU</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
        .glassmorphism {
            background: rgba(255, 255, 255, 0.1);
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255, 255, 255, 0.2);
        }
        body {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
        }
    </style>
</head>
<body class="font-sans">
    <div class="min-h-screen flex items-center justify-center p-4">
        <div class="glassmorphism rounded-2xl p-8 max-w-md w-full">
            <div class="text-center mb-8">
                <h1 class="text-3xl font-bold text-white mb-2">ElevateCRM</h1>
                <p class="text-blue-100">by TECHGURU</p>
            </div>
            
            <div class="space-y-4">
                <button onclick="window.location.href='/docs'" 
                        class="w-full bg-blue-600 hover:bg-blue-700 text-white font-bold py-3 px-4 rounded-lg transition duration-200">
                    📚 API Documentation
                </button>
                
                <button onclick="window.location.href='/api/v1/health'" 
                        class="w-full bg-green-600 hover:bg-green-700 text-white font-bold py-3 px-4 rounded-lg transition duration-200">
                    ❤️ Health Check
                </button>
                
                <button onclick="openManagement()" 
                        class="w-full bg-purple-600 hover:bg-purple-700 text-white font-bold py-3 px-4 rounded-lg transition duration-200">
                    ⚙️ CRM Management
                </button>
            </div>
            
            <div class="mt-8 text-center text-blue-100 text-sm">
                <p>🌐 Server running on localhost:8000</p>
                <p>📱 Standalone Windows Application</p>
            </div>
        </div>
    </div>
    
    <script>
        function openManagement() {
            alert('CRM Management UI would be available in the full web version.\\n\\nFor now, use the API Documentation to interact with the system.');
        }
    </script>
</body>
</html>"""

class ElevateCRMLauncher:
    def __init__(self):
        self.app_dir = Path(sys.executable).parent if getattr(sys, 'frozen', False) else Path(__file__).parent
        self.backend_port = 8000
        self.frontend_url = f"http://localhost:{self.backend_port}"
        
    def setup_directories(self):
        """Create necessary directories"""
        dirs = ["data", "logs", "uploads", "config"]
        for dir_name in dirs:
            (self.app_dir / dir_name).mkdir(exist_ok=True)
    
    def create_fastapi_app(self):
        """Create FastAPI app with embedded UI"""
        from app.main import app as backend_app
        
        @backend_app.get("/", response_class=HTMLResponse)
        async def root():
            return EMBEDDED_UI
            
        @backend_app.get("/ui", response_class=HTMLResponse)
        async def ui():
            return EMBEDDED_UI
        
        return backend_app
    
    def start_backend(self):
        """Start the FastAPI backend server"""
        try:
            app = self.create_fastapi_app()
            uvicorn.run(
                app,
                host="127.0.0.1",
                port=self.backend_port,
                log_level="info",
                access_log=False
            )
        except Exception as e:
            logger.error(f"Failed to start backend: {e}")
    
    def open_browser(self):
        """Open the application in the default browser"""
        time.sleep(3)  # Wait for server to start
        try:
            webbrowser.open(self.frontend_url)
            logger.info(f"Opened application in browser: {self.frontend_url}")
        except Exception as e:
            logger.error(f"Failed to open browser: {e}")
    
    def run(self):
        """Main application entry point"""
        logger.info("🚀 Starting ElevateCRM Standalone...")
        
        # Setup
        self.setup_directories()
        
        # Start browser in separate thread
        browser_thread = threading.Thread(target=self.open_browser, daemon=True)
        browser_thread.start()
        
        # Start backend (this blocks)
        logger.info(f"🌐 Server starting on {self.frontend_url}")
        self.start_backend()

if __name__ == "__main__":
    launcher = ElevateCRMLauncher()
    launcher.run()
'''
    
    launcher_path = PACKAGE_DIR / "elevatecrm_standalone.py"
    with open(launcher_path, 'w') as f:
        f.write(launcher_code)
    
    print("✅ Standalone launcher created")
    return launcher_path

def create_simple_spec():
    """Create simplified PyInstaller spec"""
    print_step("Creating PyInstaller Spec")
    
    spec_content = f'''
# ElevateCRM Standalone Spec
import os
from pathlib import Path

backend_dir = Path("../backend")

# Data files to include
datas = []

# Add database files
db_files = list(backend_dir.glob("*.db"))
for db_file in db_files:
    datas.append((str(db_file), "."))

# Add static files if they exist
static_dir = backend_dir / "app" / "static"
if static_dir.exists():
    datas.append((str(static_dir), "app/static"))

# Hidden imports
hiddenimports = [
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
    'fastapi',
    'fastapi.responses',
    'sqlalchemy',
    'sqlalchemy.dialects.sqlite',
    'pydantic',
    'jwt',
    'passlib',
    'passlib.handlers.bcrypt',
    'bcrypt',
]

a = Analysis(
    ['elevatecrm_standalone.py'],
    pathex=[str(backend_dir)],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={{}},
    runtime_hooks=[],
    excludes=['tkinter', 'matplotlib'],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=None,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=None)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='{APP_NAME}_Standalone',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
'''
    
    spec_path = PACKAGE_DIR / "elevatecrm_standalone.spec"
    with open(spec_path, 'w') as f:
        f.write(spec_content)
    
    print("✅ Spec file created")
    return spec_path

def build_standalone():
    """Build the standalone executable"""
    print_step("Building Standalone Executable")
    
    # Clean previous builds
    build_dir = Path("build")
    dist_dir = Path("dist")
    
    if build_dir.exists():
        shutil.rmtree(build_dir)
    if dist_dir.exists():
        shutil.rmtree(dist_dir)
    
    # Copy backend source
    print("📂 Copying backend source...")
    backend_copy = Path("backend_temp")
    if backend_copy.exists():
        shutil.rmtree(backend_copy)
    shutil.copytree(BACKEND_DIR, backend_copy)
    
    try:
        # Build with PyInstaller
        spec_file = "elevatecrm_standalone.spec"
        success = run_command(f"pyinstaller {spec_file}")
        
        if success:
            print("✅ Executable built successfully")
            
            # Create user-friendly launcher
            launcher_bat = f'''@echo off
title {APP_NAME} Standalone
echo.
echo 🚀 Starting {APP_NAME}...
echo.
echo 🌐 Opening browser at http://localhost:8000
echo.
echo ⚠️  Keep this window open while using the application
echo 🛑 Press Ctrl+C to stop the application
echo.
"{APP_NAME}_Standalone.exe"
pause
'''
            
            launcher_path = dist_dir / f"{APP_NAME}_Launcher.bat"
            with open(launcher_path, 'w') as f:
                f.write(launcher_bat)
            
            return True
        else:
            print("❌ Build failed")
            return False
            
    finally:
        # Cleanup
        if backend_copy.exists():
            shutil.rmtree(backend_copy)

def main():
    print(f"""
╔══════════════════════════════════════════════════════════════╗
║                ElevateCRM Standalone Builder                 ║
║                  Backend + Embedded UI                      ║
╚══════════════════════════════════════════════════════════════╝
""")
    
    try:
        # Check if backend exists
        if not BACKEND_DIR.exists():
            print(f"❌ Backend directory not found: {BACKEND_DIR}")
            sys.exit(1)
            
        # Step 1: Create launcher
        create_launcher_with_ui()
        
        # Step 2: Create spec
        create_simple_spec()
        
        # Step 3: Build
        if build_standalone():
            print_step("Build Complete!")
            print(f"""
✅ Standalone executable created!

📁 Location: dist/{APP_NAME}_Standalone.exe
🚀 Launcher: dist/{APP_NAME}_Launcher.bat

📋 How to use:
   1. Double-click {APP_NAME}_Launcher.bat
   2. Browser opens automatically at http://localhost:8000
   3. Access API docs at /docs
   4. Keep the console window open

📦 Distribution:
   Copy the entire 'dist' folder to share your application
   
🎯 File size: ~40-80 MB (complete CRM backend + UI)
""")
        else:
            print("❌ Build failed")
            sys.exit(1)
            
    except Exception as e:
        print(f"❌ Build failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()