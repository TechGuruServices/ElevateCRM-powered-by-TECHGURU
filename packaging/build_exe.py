#!/usr/bin/env python3
"""
ElevateCRM Automated Build Script
Packages the entire ElevateCRM application as a Windows executable
"""

import os
import sys
import shutil
import subprocess
import json
from pathlib import Path

# Configuration
APP_NAME = "ElevateCRM"
APP_VERSION = "1.0.0"
BUILD_DIR = Path("dist")
PACKAGE_DIR = Path("packaging")
FRONTEND_DIR = Path("../frontend")
BACKEND_DIR = Path("../backend")

def print_step(step_name):
    """Print a formatted step header"""
    print(f"\n{'='*60}")
    print(f"🔧 {step_name}")
    print(f"{'='*60}")

def run_command(command, cwd=None, check=True):
    """Run a shell command with error handling"""
    print(f"Running: {command}")
    try:
        result = subprocess.run(
            command, 
            shell=True, 
            cwd=cwd, 
            check=check,
            capture_output=True,
            text=True
        )
        if result.stdout:
            print(result.stdout)
        return result
    except subprocess.CalledProcessError as e:
        print(f"❌ Error running command: {e}")
        if e.stderr:
            print(f"Error output: {e.stderr}")
        return None

def check_prerequisites():
    """Check if all required tools are installed"""
    print_step("Checking Prerequisites")
    
    required_tools = [
        ("python", "Python interpreter"),
        ("npm", "Node.js package manager"),
        ("pip", "Python package manager")
    ]
    
    missing_tools = []
    
    for tool, description in required_tools:
        result = run_command(f"{tool} --version", check=False)
        if result and result.returncode == 0:
            print(f"✅ {description}: Found")
        else:
            print(f"❌ {description}: Not found")
            missing_tools.append(tool)
    
    if missing_tools:
        print(f"\n❌ Missing required tools: {', '.join(missing_tools)}")
        print("Please install them before continuing.")
        sys.exit(1)
    
    print("\n✅ All prerequisites met!")

def install_python_dependencies():
    """Install required Python packages"""
    print_step("Installing Python Dependencies")
    
    packages = [
        "pyinstaller",
        "pyinstaller[encryption]",
        "pyarmor",  # For code obfuscation
        "upx-ucl"   # For compression
    ]
    
    for package in packages:
        print(f"Installing {package}...")
        result = run_command(f"pip install {package}", check=False)
        if result and result.returncode == 0:
            print(f"✅ {package} installed successfully")
        else:
            print(f"⚠️ Failed to install {package} (continuing anyway)")

def build_frontend():
    """Build the Next.js frontend for production"""
    print_step("Building Frontend")
    
    if not FRONTEND_DIR.exists():
        print(f"❌ Frontend directory not found: {FRONTEND_DIR}")
        return False
    
    # Install frontend dependencies
    print("📦 Installing frontend dependencies...")
    result = run_command("npm install", cwd=FRONTEND_DIR)
    if not result or result.returncode != 0:
        print("❌ Failed to install frontend dependencies")
        return False
    
    # Create Next.js config for static export
    next_config = """
/** @type {import('next').NextConfig} */
const nextConfig = {
  output: 'export',
  trailingSlash: true,
  skipTrailingSlashRedirect: true,
  distDir: 'dist',
  images: {
    unoptimized: true
  }
}

module.exports = nextConfig
"""
    
    config_path = FRONTEND_DIR / "next.config.js"
    with open(config_path, 'w') as f:
        f.write(next_config)
    
    # Build frontend
    print("🏗️ Building frontend for production...")
    result = run_command("npm run build", cwd=FRONTEND_DIR)
    if not result or result.returncode != 0:
        print("❌ Frontend build failed")
        return False
    
    print("✅ Frontend built successfully")
    return True

def create_launcher_script():
    """Create the main launcher script"""
    print_step("Creating Launcher Script")
    
    launcher_code = '''
import os
import sys
import threading
import webbrowser
import time
import subprocess
from pathlib import Path
import uvicorn
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ElevateCRMLauncher:
    def __init__(self):
        self.app_dir = Path(sys.executable).parent if getattr(sys, 'frozen', False) else Path(__file__).parent
        self.frontend_dir = self.app_dir / "frontend" / "dist"
        self.backend_port = 8000
        self.frontend_url = f"http://localhost:{self.backend_port}"
        
    def setup_directories(self):
        """Create necessary directories"""
        dirs = ["data", "logs", "uploads", "config"]
        for dir_name in dirs:
            (self.app_dir / dir_name).mkdir(exist_ok=True)
    
    def create_fastapi_app(self):
        """Create FastAPI app with static file serving"""
        from app.main import app as backend_app
        
        # Mount static files
        if self.frontend_dir.exists():
            backend_app.mount("/", StaticFiles(directory=str(self.frontend_dir), html=True), name="frontend")
        
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
        logger.info("🚀 Starting ElevateCRM...")
        
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
    
    launcher_path = PACKAGE_DIR / "elevatecrm_launcher.py"
    with open(launcher_path, 'w') as f:
        f.write(launcher_code)
    
    print("✅ Launcher script created")
    return launcher_path

def create_pyinstaller_spec():
    """Create PyInstaller spec file"""
    print_step("Creating PyInstaller Specification")
    
    spec_content = f'''
# -*- mode: python ; coding: utf-8 -*-
import os
from pathlib import Path

# Paths
backend_dir = Path("../backend")
frontend_dist = Path("../frontend/dist")

# Data files to include
datas = []

# Add frontend dist files
if frontend_dist.exists():
    datas.append((str(frontend_dist), "frontend/dist"))

# Add backend static files
static_dir = backend_dir / "app" / "static"
if static_dir.exists():
    datas.append((str(static_dir), "app/static"))

# Add database files
db_files = list(backend_dir.glob("*.db"))
for db_file in db_files:
    datas.append((str(db_file), "."))

# Hidden imports (modules that PyInstaller might miss)
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
    'fastapi.staticfiles',
    'sqlalchemy',
    'sqlalchemy.dialects.sqlite',
    'pydantic',
    'jwt',
    'passlib',
    'passlib.handlers.bcrypt',
    'bcrypt',
    'python-multipart',
    'email_validator',
]

# Analysis
a = Analysis(
    ['elevatecrm_launcher.py'],
    pathex=[],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={{}},
    runtime_hooks=[],
    excludes=['tkinter', 'matplotlib', 'numpy', 'scipy'],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=None,
    noarchive=False,
)

# Remove unnecessary files to reduce size
a.binaries = [x for x in a.binaries if not x[0].startswith('tk')]
a.binaries = [x for x in a.binaries if not x[0].startswith('tcl')]

pyz = PYZ(a.pure, a.zipped_data, cipher=None)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='{APP_NAME}',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,  # Set to True for debugging
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='../techguru_logo.ico'  # Add icon if available
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='{APP_NAME}',
)
'''
    
    spec_path = PACKAGE_DIR / "elevatecrm.spec"
    with open(spec_path, 'w') as f:
        f.write(spec_content)
    
    print("✅ PyInstaller spec file created")
    return spec_path

def create_icon():
    """Create or copy application icon"""
    print_step("Setting Up Application Icon")
    
    # Look for existing icon
    icon_sources = [
        Path("../techguru_logo.ico"),
        Path("../frontend/public/techguru-logo.png"),
        Path("../backend/app/static/techguru-logo.png")
    ]
    
    for icon_source in icon_sources:
        if icon_source.exists():
            # Copy to packaging directory
            icon_dest = PACKAGE_DIR / "techguru_logo.ico"
            if icon_source.suffix == ".png":
                # Convert PNG to ICO (requires PIL)
                try:
                    from PIL import Image
                    img = Image.open(icon_source)
                    img.save(icon_dest, format='ICO', sizes=[(16,16), (32,32), (48,48), (64,64)])
                    print("✅ Icon converted and copied")
                    return icon_dest
                except ImportError:
                    print("⚠️ PIL not available for icon conversion")
            else:
                shutil.copy2(icon_source, icon_dest)
                print("✅ Icon copied")
                return icon_dest
    
    print("⚠️ No icon found, using default")
    return None

def build_executable():
    """Build the executable using PyInstaller"""
    print_step("Building Executable")
    
    # Clean previous builds
    if BUILD_DIR.exists():
        shutil.rmtree(BUILD_DIR)
    
    build_dir = Path("build")
    if build_dir.exists():
        shutil.rmtree(build_dir)
    
    # Run PyInstaller
    spec_file = PACKAGE_DIR / "elevatecrm.spec"
    result = run_command(f"pyinstaller {spec_file}", cwd=PACKAGE_DIR)
    
    if not result or result.returncode != 0:
        print("❌ PyInstaller build failed")
        return False
    
    print("✅ Executable built successfully")
    return True

def create_installer_script():
    """Create NSIS installer script"""
    print_step("Creating Installer Script")
    
    nsis_script = f'''
; ElevateCRM Installer Script
; Generated by build_exe.py

!define APP_NAME "{APP_NAME}"
!define APP_VERSION "{APP_VERSION}"
!define PUBLISHER "TECHGURU"
!define WEB_SITE "https://techguru.com"
!define APP_DIR "dist\\{APP_NAME}"

!include "MUI2.nsh"

; Settings
Name "${{APP_NAME}} ${{APP_VERSION}}"
OutFile "{APP_NAME}_Setup_${{APP_VERSION}}.exe"
InstallDir "$PROGRAMFILES\\${{PUBLISHER}}\\${{APP_NAME}}"
InstallDirRegKey HKLM "Software\\${{PUBLISHER}}\\${{APP_NAME}}" "Install_Dir"
RequestExecutionLevel admin

; Interface Settings
!define MUI_ABORTWARNING
!define MUI_ICON "techguru_logo.ico"
!define MUI_UNICON "techguru_logo.ico"

; Pages
!insertmacro MUI_PAGE_WELCOME
!insertmacro MUI_PAGE_LICENSE "..\\LICENSE"
!insertmacro MUI_PAGE_DIRECTORY
!insertmacro MUI_PAGE_INSTFILES
!insertmacro MUI_PAGE_FINISH

!insertmacro MUI_UNPAGE_WELCOME
!insertmacro MUI_UNPAGE_CONFIRM
!insertmacro MUI_UNPAGE_INSTFILES
!insertmacro MUI_UNPAGE_FINISH

; Languages
!insertmacro MUI_LANGUAGE "English"

; Installation Section
Section "MainSection" SEC01
    SetOutPath "$INSTDIR"
    SetOverwrite ifnewer
    
    ; Copy all files
    File /r "${{APP_DIR}}\\*.*"
    
    ; Create shortcuts
    CreateDirectory "$SMPROGRAMS\\${{PUBLISHER}}"
    CreateShortCut "$SMPROGRAMS\\${{PUBLISHER}}\\${{APP_NAME}}.lnk" "$INSTDIR\\${{APP_NAME}}.exe"
    CreateShortCut "$DESKTOP\\${{APP_NAME}}.lnk" "$INSTDIR\\${{APP_NAME}}.exe"
    
    ; Registry entries
    WriteRegStr HKLM "Software\\${{PUBLISHER}}\\${{APP_NAME}}" "Install_Dir" "$INSTDIR"
    WriteRegStr HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\${{APP_NAME}}" "DisplayName" "${{APP_NAME}}"
    WriteRegStr HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\${{APP_NAME}}" "UninstallString" '"$INSTDIR\\uninstall.exe"'
    WriteRegDWORD HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\${{APP_NAME}}" "NoModify" 1
    WriteRegDWORD HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\${{APP_NAME}}" "NoRepair" 1
    WriteUninstaller "uninstall.exe"
SectionEnd

; Uninstaller Section
Section "Uninstall"
    ; Remove registry keys
    DeleteRegKey HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\${{APP_NAME}}"
    DeleteRegKey HKLM "Software\\${{PUBLISHER}}\\${{APP_NAME}}"
    
    ; Remove files and uninstaller
    Delete "$INSTDIR\\uninstall.exe"
    RMDir /r "$INSTDIR"
    
    ; Remove shortcuts
    Delete "$SMPROGRAMS\\${{PUBLISHER}}\\${{APP_NAME}}.lnk"
    Delete "$DESKTOP\\${{APP_NAME}}.lnk"
    RMDir "$SMPROGRAMS\\${{PUBLISHER}}"
SectionEnd
'''
    
    installer_path = PACKAGE_DIR / "elevatecrm_installer.nsi"
    with open(installer_path, 'w') as f:
        f.write(nsis_script)
    
    print("✅ NSIS installer script created")
    return installer_path

def create_batch_launchers():
    """Create convenient batch files for users"""
    print_step("Creating Batch Launchers")
    
    # Simple launcher batch file
    launcher_bat = f'''@echo off
title {APP_NAME}
echo Starting {APP_NAME}...
echo.
echo Opening your web browser...
echo If the browser doesn't open automatically, go to: http://localhost:8000
echo.
echo Press Ctrl+C to stop the application
echo.
cd /d "%~dp0"
"{APP_NAME}.exe"
pause
'''
    
    launcher_path = BUILD_DIR / APP_NAME / f"{APP_NAME}_Launcher.bat"
    with open(launcher_path, 'w') as f:
        f.write(launcher_bat)
    
    # Debug launcher
    debug_bat = f'''@echo off
title {APP_NAME} Debug Mode
echo Starting {APP_NAME} in DEBUG mode...
echo.
cd /d "%~dp0"
"{APP_NAME}.exe" --debug
pause
'''
    
    debug_path = BUILD_DIR / APP_NAME / f"{APP_NAME}_Debug.bat"
    with open(debug_path, 'w') as f:
        f.write(debug_bat)
    
    print("✅ Batch launchers created")

def main():
    """Main build process"""
    print(f"""
╔══════════════════════════════════════════════════════════════╗
║                    ElevateCRM Builder                        ║
║              Building Windows Executable                     ║
╚══════════════════════════════════════════════════════════════╝
""")
    
    try:
        # Step 1: Prerequisites
        check_prerequisites()
        
        # Step 2: Install Python dependencies
        install_python_dependencies()
        
        # Step 3: Build frontend
        if not build_frontend():
            print("❌ Build failed at frontend step")
            sys.exit(1)
        
        # Step 4: Create launcher script
        create_launcher_script()
        
        # Step 5: Create icon
        create_icon()
        
        # Step 6: Create PyInstaller spec
        create_pyinstaller_spec()
        
        # Step 7: Build executable
        if not build_executable():
            print("❌ Build failed at executable creation")
            sys.exit(1)
        
        # Step 8: Create additional files
        create_batch_launchers()
        create_installer_script()
        
        print_step("Build Complete!")
        print(f"""
✅ Build completed successfully!

📁 Your executable is located at:
   {BUILD_DIR / APP_NAME / f'{APP_NAME}.exe'}

🚀 To run your application:
   1. Navigate to the dist/{APP_NAME} folder
   2. Double-click {APP_NAME}.exe
   3. Your web browser will open automatically

📦 To create an installer:
   1. Install NSIS (https://nsis.sourceforge.io/)
   2. Run: makensis elevatecrm_installer.nsi

🎯 Distribution ready!
""")
        
    except KeyboardInterrupt:
        print("\n❌ Build cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Build failed with error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()