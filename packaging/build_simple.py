#!/usr/bin/env python3
"""
ElevateCRM Simple Executable Builder
Creates a standalone .exe for the backend API
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

def create_simple_launcher():
    """Create simple launcher script"""
    print_step("Creating Launcher")
    
    launcher_code = '''
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
'''
    
    launcher_path = PACKAGE_DIR / "simple_launcher.py"
    with open(launcher_path, 'w', encoding='utf-8') as f:
        f.write(launcher_code)
    
    print("Launcher created")
    return launcher_path

def create_pyinstaller_spec():
    """Create PyInstaller spec file"""
    print_step("Creating Spec File")
    
    spec_content = '''
import os
from pathlib import Path

backend_dir = Path("../backend")
datas = []

# Add database if exists
db_files = list(backend_dir.glob("*.db"))
for db_file in db_files:
    datas.append((str(db_file), "."))

hiddenimports = [
    'uvicorn',
    'uvicorn.lifespan',
    'uvicorn.lifespan.on',
    'uvicorn.loops',
    'uvicorn.loops.auto',
    'uvicorn.protocols',
    'uvicorn.protocols.http',
    'uvicorn.protocols.http.auto',
    'fastapi',
    'fastapi.responses',
    'sqlalchemy',
    'sqlalchemy.dialects.sqlite',
    'pydantic',
    'jwt',
    'passlib',
    'bcrypt',
]

a = Analysis(
    ['simple_launcher.py'],
    pathex=[str(backend_dir)],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['tkinter'],
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
    name='ElevateCRM',
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
    
    spec_path = PACKAGE_DIR / "simple.spec"
    with open(spec_path, 'w') as f:
        f.write(spec_content)
    
    print("Spec file created")
    return spec_path

def main():
    print("ElevateCRM Standalone Builder")
    print("=" * 40)
    
    try:
        if not BACKEND_DIR.exists():
            print(f"Error: Backend directory not found: {BACKEND_DIR}")
            return
            
        # Step 1: Create launcher
        create_simple_launcher()
        
        # Step 2: Create spec
        create_pyinstaller_spec()
        
        # Step 3: Copy backend temporarily
        print_step("Preparing Backend")
        backend_temp = Path("backend_temp")
        if backend_temp.exists():
            shutil.rmtree(backend_temp)
        shutil.copytree(BACKEND_DIR, backend_temp)
        
        # Step 4: Build
        print_step("Building Executable")
        success = run_command("pyinstaller simple.spec")
        
        # Cleanup
        if backend_temp.exists():
            shutil.rmtree(backend_temp)
            
        if success:
            # Create launcher batch file
            launcher_bat = '''@echo off
title ElevateCRM
echo Starting ElevateCRM...
echo.
echo Browser will open automatically
echo Keep this window open while using the app
echo.
ElevateCRM.exe
pause
'''
            
            with open("dist/ElevateCRM_Start.bat", 'w') as f:
                f.write(launcher_bat)
            
            print("\nBuild Complete!")
            print("=" * 40)
            print("Executable: dist/ElevateCRM.exe")
            print("Launcher: dist/ElevateCRM_Start.bat")
            print("\nTo use:")
            print("1. Double-click ElevateCRM_Start.bat")
            print("2. Browser opens at http://localhost:8000")
            print("3. Visit /docs for API documentation")
            
        else:
            print("Build failed!")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()