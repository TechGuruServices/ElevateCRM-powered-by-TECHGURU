# ElevateCRM Windows Setup Script
# Run this script as Administrator in PowerShell

param(
    [switch]$SkipDependencies = $false,
    [switch]$DevMode = $false
)

# Set error action preference
$ErrorActionPreference = "Stop"

# Color functions
function Write-ColorOutput($ForegroundColor) {
    $fc = $host.UI.RawUI.ForegroundColor
    $host.UI.RawUI.ForegroundColor = $ForegroundColor
    if ($args) {
        Write-Output $args
    }
    else {
        $input | Write-Output
    }
    $host.UI.RawUI.ForegroundColor = $fc
}

function Write-Status($message) {
    Write-ColorOutput Green "[INFO] $message"
}

function Write-Warning($message) {
    Write-ColorOutput Yellow "[WARNING] $message"
}

function Write-Error($message) {
    Write-ColorOutput Red "[ERROR] $message"
}

function Write-Step($message) {
    Write-ColorOutput Cyan "[STEP] $message"
}

# Check if running as administrator
function Test-Administrator {
    $currentPrincipal = New-Object Security.Principal.WindowsPrincipal([Security.Principal.WindowsIdentity]::GetCurrent())
    return $currentPrincipal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
}

# Function to check if command exists
function Test-CommandExists($command) {
    try {
        Get-Command $command -ErrorAction Stop | Out-Null
        return $true
    }
    catch {
        return $false
    }
}

# Function to install Chocolatey
function Install-Chocolatey {
    if (-not (Test-CommandExists "choco")) {
        Write-Step "Installing Chocolatey..."
        Set-ExecutionPolicy Bypass -Scope Process -Force
        [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072
        iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))
        refreshenv
        Write-Status "Chocolatey installed successfully ✓"
    }
    else {
        Write-Status "Chocolatey already installed ✓"
    }
}

# Function to install dependencies
function Install-Dependencies {
    if ($SkipDependencies) {
        Write-Warning "Skipping dependency installation"
        return
    }
    
    Write-Step "Installing system dependencies..."
    
    # Install Chocolatey first
    Install-Chocolatey
    
    # Install dependencies via Chocolatey
    $packages = @(
        "nodejs",
        "python",
        "git",
        "postgresql",
        "redis-64"
    )
    
    foreach ($package in $packages) {
        Write-Status "Installing $package..."
        try {
            choco install $package -y
        }
        catch {
            Write-Warning "Failed to install $package, continuing..."
        }
    }
    
    # Refresh environment variables
    refreshenv
    
    Write-Status "Dependencies installation completed ✓"
}

# Function to check prerequisites
function Test-Prerequisites {
    Write-Step "Checking prerequisites..."
    
    # Check Node.js
    if (Test-CommandExists "node") {
        $nodeVersion = (node --version).Substring(1).Split('.')[0]
        if ([int]$nodeVersion -lt 18) {
            Write-Error "Node.js version 18+ is required. Found: $(node --version)"
            exit 1
        }
        Write-Status "Node.js: $(node --version) ✓"
    }
    else {
        Write-Error "Node.js is not installed"
        exit 1
    }
    
    # Check Python
    if (Test-CommandExists "python") {
        $pythonVersion = (python --version).Split(' ')[1]
        Write-Status "Python: $pythonVersion ✓"
    }
    else {
        Write-Error "Python is not installed"
        exit 1
    }
    
    # Check npm
    if (Test-CommandExists "npm") {
        Write-Status "npm: $(npm --version) ✓"
    }
    else {
        Write-Error "npm is not installed"
        exit 1
    }
}

# Function to setup PostgreSQL
function Setup-Database {
    Write-Step "Setting up PostgreSQL database..."
    
    # Start PostgreSQL service
    try {
        Start-Service postgresql-x64-14 -ErrorAction SilentlyContinue
        Set-Service -Name postgresql-x64-14 -StartupType Automatic
    }
    catch {
        Write-Warning "Could not start PostgreSQL service automatically"
    }
    
    # Create database and user
    $createDbScript = @"
CREATE DATABASE elevatecrm;
CREATE USER elevatecrm_user WITH PASSWORD 'elevatecrm_password';
GRANT ALL PRIVILEGES ON DATABASE elevatecrm TO elevatecrm_user;
"@
    
    $createDbScript | Out-File -FilePath "create_db.sql" -Encoding UTF8
    
    try {
        psql -U postgres -f create_db.sql
        Remove-Item "create_db.sql"
        Write-Status "Database setup completed ✓"
    }
    catch {
        Write-Warning "Database setup failed. Please create manually:"
        Write-Host $createDbScript
    }
}

# Function to setup Redis
function Setup-Redis {
    Write-Step "Setting up Redis..."
    
    try {
        Start-Service Redis -ErrorAction SilentlyContinue
        Set-Service -Name Redis -StartupType Automatic
        Write-Status "Redis setup completed ✓"
    }
    catch {
        Write-Warning "Could not start Redis service automatically"
    }
}

# Function to setup backend
function Setup-Backend {
    Write-Step "Setting up backend..."
    
    Push-Location backend
    
    try {
        # Create virtual environment
        python -m venv .venv
        
        # Activate virtual environment
        & ".\.venv\Scripts\Activate.ps1"
        
        # Install dependencies
        python -m pip install --upgrade pip
        pip install -r requirements.txt
        
        # Create environment file
        if (-not (Test-Path ".env")) {
            $envContent = @"
# Database
DATABASE_URL=postgresql://elevatecrm_user:elevatecrm_password@localhost:5432/elevatecrm

# Security
SECRET_KEY=$([System.Web.Security.Membership]::GeneratePassword(32, 0))
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# Redis
REDIS_URL=redis://localhost:6379

# Environment
ENVIRONMENT=development
DEBUG=true

# CORS
ALLOWED_ORIGINS=http://localhost:3000,http://127.0.0.1:3000

# File Storage (Local for standalone)
UPLOAD_DIR=./uploads
MAX_FILE_SIZE=10485760
"@
            $envContent | Out-File -FilePath ".env" -Encoding UTF8
        }
        
        # Run database migrations
        try {
            alembic upgrade head
            Write-Status "Database migrations completed ✓"
        }
        catch {
            Write-Warning "Database migrations failed. Run manually: alembic upgrade head"
        }
        
        # Seed initial data
        try {
            python app/scripts/seed_data.py
            Write-Status "Initial data seeded ✓"
        }
        catch {
            Write-Warning "Data seeding failed. Run manually: python app/scripts/seed_data.py"
        }
        
        Write-Status "Backend setup completed ✓"
    }
    finally {
        Pop-Location
    }
}

# Function to setup frontend
function Setup-Frontend {
    Write-Step "Setting up frontend..."
    
    Push-Location frontend
    
    try {
        # Install dependencies
        npm install
        
        # Create environment file
        if (-not (Test-Path ".env.local")) {
            $envContent = @"
# API Configuration
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_APP_NAME=ElevateCRM
NEXT_PUBLIC_APP_VERSION=1.0.0

# Features
NEXT_PUBLIC_ENABLE_ANALYTICS=false
NEXT_PUBLIC_ENABLE_SENTRY=false

# Environment
NODE_ENV=production
"@
            $envContent | Out-File -FilePath ".env.local" -Encoding UTF8
        }
        
        # Build the application
        if (-not $DevMode) {
            npm run build
            Write-Status "Frontend build completed ✓"
        }
        
        Write-Status "Frontend setup completed ✓"
    }
    finally {
        Pop-Location
    }
}

# Function to create start script
function New-StartScript {
    Write-Step "Creating start script..."
    
    $startScript = @"
@echo off
echo 🚀 Starting ElevateCRM...

REM Start backend
cd backend
call .venv\Scripts\activate
start "ElevateCRM Backend" uvicorn app.main:app --host 0.0.0.0 --port 8000
cd ..

REM Wait for backend to start
timeout /t 5 /nobreak > nul

REM Start frontend
cd frontend
start "ElevateCRM Frontend" npm start
cd ..

echo ✅ ElevateCRM is starting...
echo Frontend: http://localhost:3000
echo Backend API: http://localhost:8000
echo API Documentation: http://localhost:8000/docs
echo.
echo Press any key to stop all services
pause > nul

REM Kill processes
taskkill /F /IM python.exe 2>nul
taskkill /F /IM node.exe 2>nul
echo ✅ All services stopped
"@
    
    $startScript | Out-File -FilePath "start.bat" -Encoding ASCII
    Write-Status "Start script created ✓"
}

# Function to create stop script
function New-StopScript {
    Write-Step "Creating stop script..."
    
    $stopScript = @"
@echo off
echo 🛑 Stopping ElevateCRM services...

taskkill /F /IM python.exe 2>nul
taskkill /F /IM node.exe 2>nul

echo ✅ All services stopped
pause
"@
    
    $stopScript | Out-File -FilePath "stop.bat" -Encoding ASCII
    Write-Status "Stop script created ✓"
}

# Main installation process
function Start-Installation {
    Write-Status "Starting ElevateCRM Windows installation..."
    
    # Check if running as administrator
    if (-not (Test-Administrator)) {
        Write-Error "This script must be run as Administrator. Please restart PowerShell as Administrator and try again."
        exit 1
    }
    
    # Check if we're in the right directory
    if (-not (Test-Path "frontend") -or -not (Test-Path "backend")) {
        Write-Error "Please run this script from the ElevateCRM root directory"
        exit 1
    }
    
    # Ask user for confirmation
    Write-Host ""
    Write-Warning "This script will:"
    Write-Host "  1. Install system dependencies via Chocolatey"
    Write-Host "  2. Setup PostgreSQL database"
    Write-Host "  3. Setup Redis cache"
    Write-Host "  4. Install backend dependencies"
    Write-Host "  5. Install frontend dependencies"
    Write-Host "  6. Create configuration files"
    Write-Host "  7. Build the application"
    Write-Host ""
    
    $confirmation = Read-Host "Do you want to continue? (y/N)"
    if ($confirmation -ne 'y' -and $confirmation -ne 'Y') {
        Write-Status "Installation cancelled"
        exit 0
    }
    
    # Run installation steps
    try {
        Install-Dependencies
        Test-Prerequisites
        Setup-Database
        Setup-Redis
        Setup-Backend
        Setup-Frontend
        New-StartScript
        New-StopScript
        
        Write-Host ""
        Write-Status "🎉 ElevateCRM installation completed successfully!"
        Write-Host ""
        Write-Host "To start the application:"
        Write-Host "  .\start.bat"
        Write-Host ""
        Write-Host "To stop the application:"
        Write-Host "  .\stop.bat"
        Write-Host ""
        Write-Host "Access URLs:"
        Write-Host "  Frontend: http://localhost:3000"
        Write-Host "  Backend API: http://localhost:8000"
        Write-Host "  API Docs: http://localhost:8000/docs"
        Write-Host ""
        Write-Host "Default login credentials:"
        Write-Host "  Email: admin@techguru.com"
        Write-Host "  Password: admin123"
        Write-Host ""
        Write-Warning "Please change the default password after first login!"
    }
    catch {
        Write-Error "Installation failed: $($_.Exception.Message)"
        exit 1
    }
}

# Run main installation
Start-Installation