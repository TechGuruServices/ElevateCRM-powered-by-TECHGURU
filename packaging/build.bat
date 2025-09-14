@echo off
title ElevateCRM Builder
echo.
echo ╔══════════════════════════════════════════════════════════════╗
echo ║                    ElevateCRM Builder                        ║
echo ║              Building Windows Executable                     ║
echo ╚══════════════════════════════════════════════════════════════╝
echo.

cd /d "%~dp0"

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python is not installed or not in PATH
    echo Please install Python 3.8+ and try again
    pause
    exit /b 1
)

REM Run the build script
echo 🔧 Starting build process...
python build_exe.py

if errorlevel 1 (
    echo.
    echo ❌ Build failed! Check the output above for errors.
    echo.
    pause
) else (
    echo.
    echo ✅ Build completed successfully!
    echo.
    echo Your executable is ready in the dist folder.
    echo.
    pause
)