# ElevateCRM Windows Executable Packaging Guide

This guide shows you how to package ElevateCRM as a standalone Windows executable (.exe) file.

## 📦 Packaging Options

### Option 1: PyInstaller + Static Frontend (Recommended)
- Packages Python backend as .exe
- Includes built Next.js frontend as static files
- Single executable with embedded web server
- **File Size**: ~150-200MB
- **Startup Time**: Fast (2-3 seconds)

### Option 2: Electron Application
- Packages entire app in Electron wrapper
- Full Node.js environment included
- **File Size**: ~300-400MB
- **Startup Time**: Medium (3-5 seconds)

### Option 3: Tauri Application
- Rust-based packaging (lighter than Electron)
- Uses system webview
- **File Size**: ~50-100MB
- **Startup Time**: Very fast (1-2 seconds)

## 🚀 Quick Start - PyInstaller Method

### Prerequisites
```bash
pip install pyinstaller
pip install auto-py-to-exe  # Optional GUI tool
```

### Step 1: Run the automated build script
```bash
cd packaging
python build_exe.py
```

### Step 2: Find your executable
The packaged application will be in:
```
packaging/dist/ElevateCRM/ElevateCRM.exe
```

## 🔧 Manual Packaging Process

### Step 1: Prepare Frontend Build

First, we need to build the frontend for production:

```bash
cd frontend
npm run build
npm run export  # Creates static files
```

### Step 2: Install PyInstaller Dependencies

```bash
pip install pyinstaller
pip install pyinstaller[encryption]  # For advanced security
```

### Step 3: Run PyInstaller

```bash
cd packaging
pyinstaller elevatecrm.spec
```

### Step 4: Test the Executable

```bash
cd dist/ElevateCRM
ElevateCRM.exe
```

## 📁 Package Structure

After packaging, your application structure will be:
```
ElevateCRM.exe           # Main executable
├── _internal/           # PyInstaller internals
├── frontend/            # Static web files
├── database/            # SQLite database files
├── uploads/             # User uploads directory
├── logs/                # Application logs
└── config/              # Configuration files
```

## 🎯 Advanced Options

### Option A: Single File Executable
```bash
pyinstaller --onefile elevatecrm_launcher.py
```

### Option B: Add Custom Icon
```bash
pyinstaller --icon=techguru_icon.ico elevatecrm_launcher.py
```

### Option C: Hide Console Window
```bash
pyinstaller --windowed elevatecrm_launcher.py
```

### Option D: All Combined
```bash
pyinstaller --onefile --windowed --icon=techguru_icon.ico elevatecrm_launcher.py
```

## 🔒 Security Features

### Code Obfuscation
```bash
pip install pyarmor
pyarmor gen elevatecrm_launcher.py
```

### Encryption
```bash
pyinstaller --key=your-secret-key elevatecrm.spec
```

## 📦 Creating an Installer

### Using NSIS (Nullsoft Scriptable Install System)

1. Download NSIS: https://nsis.sourceforge.io/
2. Run the installer script:
```bash
makensis elevatecrm_installer.nsi
```

### Using Inno Setup

1. Download Inno Setup: https://jrsoftware.org/isinfo.php
2. Compile the installer script:
```bash
iscc elevatecrm_installer.iss
```

## 🐛 Troubleshooting

### Common Issues

**Issue**: "ImportError: No module named 'xyz'"
**Solution**: Add missing modules to the .spec file

**Issue**: Frontend files not found
**Solution**: Ensure frontend build completed successfully

**Issue**: Database connection errors
**Solution**: Check SQLite file permissions and paths

**Issue**: Large file size
**Solution**: Use `--exclude-module` to remove unused libraries

### Debug Mode
Run with debug flag to see detailed error messages:
```bash
ElevateCRM.exe --debug
```

## 🔧 Customization

### Environment Variables
The packaged app reads from `config/settings.env`:
```
ELEVATECRM_PORT=8080
ELEVATECRM_DEBUG=false
ELEVATECRM_DATA_DIR=./data
```

### Database Location
By default, SQLite database is stored in:
```
%APPDATA%/ElevateCRM/database/
```

### Logs Location
Application logs are stored in:
```
%APPDATA%/ElevateCRM/logs/
```

## 📊 Performance Optimization

### Reduce Startup Time
1. Use `--lazy-imports` flag
2. Remove unused Python modules
3. Optimize database initialization

### Reduce File Size
1. Exclude development dependencies
2. Compress static assets
3. Use UPX compression:
```bash
pyinstaller --upx-dir=/path/to/upx elevatecrm.spec
```

## 🔄 Auto-Update System

The packaged application includes an auto-update feature:

1. Checks for updates on startup
2. Downloads updates in background
3. Prompts user to restart for updates
4. Maintains user data during updates

### Update Server Setup
```python
# Update server endpoint
UPDATE_URL = "https://updates.elevatecrm.com/check"
```

## 🌐 Distribution Options

### Option 1: Direct Distribution
- Share the .exe file directly
- Include installation instructions
- Provide troubleshooting guide

### Option 2: Microsoft Store
- Package as MSIX for Microsoft Store
- Automatic updates and security
- Wider distribution reach

### Option 3: Third-party Platforms
- Distribute via software repositories
- Include in business software catalogs
- Partner with system integrators

## 📋 Deployment Checklist

- [ ] Frontend built and optimized
- [ ] Backend dependencies installed
- [ ] Database schema ready
- [ ] Icons and assets included
- [ ] Configuration files prepared
- [ ] Executable tested on clean Windows machine
- [ ] Installer created and tested
- [ ] Documentation prepared
- [ ] Digital signature applied (optional)
- [ ] Update mechanism configured

## 🎯 Next Steps

1. **Run the build script**: `python packaging/build_exe.py`
2. **Test the executable**: Run on a clean Windows machine
3. **Create installer**: Use the provided NSIS script
4. **Distribute**: Share with your users!

The packaged ElevateCRM will be a professional, standalone Windows application that your users can install and run without any technical knowledge required!