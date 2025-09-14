#!/bin/bash

# ElevateCRM Standalone Setup Script
# This script sets up the complete ElevateCRM application on a single machine

set -e

echo "🚀 ElevateCRM Standalone Setup Script"
echo "======================================"

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_step() {
    echo -e "${BLUE}[STEP]${NC} $1"
}

# Check if running as root
if [ "$EUID" -eq 0 ]; then
    print_error "Please do not run this script as root"
    exit 1
fi

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to install dependencies based on OS
install_dependencies() {
    print_step "Installing system dependencies..."
    
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        # Ubuntu/Debian
        if command_exists apt-get; then
            sudo apt-get update
            sudo apt-get install -y curl wget git python3 python3-pip python3-venv nodejs npm postgresql postgresql-contrib redis-server
        # CentOS/RHEL/Fedora
        elif command_exists yum; then
            sudo yum update -y
            sudo yum install -y curl wget git python3 python3-pip nodejs npm postgresql postgresql-server redis
        elif command_exists dnf; then
            sudo dnf update -y
            sudo dnf install -y curl wget git python3 python3-pip nodejs npm postgresql postgresql-server redis
        fi
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS
        if command_exists brew; then
            brew update
            brew install python@3.11 node postgresql redis
        else
            print_error "Homebrew is required on macOS. Please install it first."
            exit 1
        fi
    fi
}

# Function to check prerequisites
check_prerequisites() {
    print_step "Checking prerequisites..."
    
    # Check Node.js
    if command_exists node; then
        NODE_VERSION=$(node --version | cut -d'v' -f2 | cut -d'.' -f1)
        if [ "$NODE_VERSION" -lt 18 ]; then
            print_error "Node.js version 18+ is required. Found: $(node --version)"
            exit 1
        fi
        print_status "Node.js: $(node --version) ✓"
    else
        print_error "Node.js is not installed"
        exit 1
    fi
    
    # Check Python
    if command_exists python3; then
        PYTHON_VERSION=$(python3 --version | awk '{print $2}' | cut -d'.' -f1-2)
        if [[ "$PYTHON_VERSION" < "3.11" ]]; then
            print_warning "Python 3.11+ is recommended. Found: $(python3 --version)"
        else
            print_status "Python: $(python3 --version) ✓"
        fi
    else
        print_error "Python 3 is not installed"
        exit 1
    fi
    
    # Check npm
    if command_exists npm; then
        print_status "npm: $(npm --version) ✓"
    else
        print_error "npm is not installed"
        exit 1
    fi
}

# Function to setup database
setup_database() {
    print_step "Setting up database..."
    
    # Check if PostgreSQL is running
    if ! pgrep -x "postgres" > /dev/null; then
        print_warning "PostgreSQL is not running. Starting it..."
        if [[ "$OSTYPE" == "linux-gnu"* ]]; then
            sudo systemctl start postgresql
            sudo systemctl enable postgresql
        elif [[ "$OSTYPE" == "darwin"* ]]; then
            brew services start postgresql
        fi
    fi
    
    # Create database and user
    print_status "Creating database and user..."
    sudo -u postgres psql << EOF
CREATE DATABASE elevatecrm;
CREATE USER elevatecrm_user WITH PASSWORD 'elevatecrm_password';
GRANT ALL PRIVILEGES ON DATABASE elevatecrm TO elevatecrm_user;
\q
EOF
    
    # Enable extensions
    sudo -u postgres psql -d elevatecrm << EOF
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";
\q
EOF
    
    print_status "Database setup completed ✓"
}

# Function to setup Redis
setup_redis() {
    print_step "Setting up Redis..."
    
    # Check if Redis is running
    if ! pgrep -x "redis-server" > /dev/null; then
        print_warning "Redis is not running. Starting it..."
        if [[ "$OSTYPE" == "linux-gnu"* ]]; then
            sudo systemctl start redis
            sudo systemctl enable redis
        elif [[ "$OSTYPE" == "darwin"* ]]; then
            brew services start redis
        fi
    fi
    
    print_status "Redis setup completed ✓"
}

# Function to setup backend
setup_backend() {
    print_step "Setting up backend..."
    
    cd backend
    
    # Create virtual environment
    python3 -m venv .venv
    source .venv/bin/activate
    
    # Install dependencies
    pip install --upgrade pip
    pip install -r requirements.txt
    
    # Create environment file
    if [ ! -f .env ]; then
        cat > .env << EOF
# Database
DATABASE_URL=postgresql://elevatecrm_user:elevatecrm_password@localhost:5432/elevatecrm

# Security
SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_urlsafe(32))")
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

# Email (Optional - for production)
# SMTP_HOST=
# SMTP_PORT=587
# SMTP_USER=
# SMTP_PASSWORD=
# FROM_EMAIL=noreply@yourdomain.com
EOF
    fi
    
    # Run database migrations
    alembic upgrade head
    
    # Seed initial data
    python app/scripts/seed_data.py
    
    cd ..
    print_status "Backend setup completed ✓"
}

# Function to setup frontend
setup_frontend() {
    print_step "Setting up frontend..."
    
    cd frontend
    
    # Install dependencies
    npm install
    
    # Create environment file
    if [ ! -f .env.local ]; then
        cat > .env.local << EOF
# API Configuration
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_APP_NAME=ElevateCRM
NEXT_PUBLIC_APP_VERSION=1.0.0

# Features
NEXT_PUBLIC_ENABLE_ANALYTICS=false
NEXT_PUBLIC_ENABLE_SENTRY=false

# Environment
NODE_ENV=production
EOF
    fi
    
    # Build the application
    npm run build
    
    cd ..
    print_status "Frontend setup completed ✓"
}

# Function to create start script
create_start_script() {
    print_step "Creating start script..."
    
    cat > start.sh << 'EOF'
#!/bin/bash

# ElevateCRM Start Script
echo "🚀 Starting ElevateCRM..."

# Start backend
cd backend
source .venv/bin/activate
uvicorn app.main:app --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!
cd ..

# Start frontend
cd frontend
npm start &
FRONTEND_PID=$!
cd ..

echo "✅ ElevateCRM is starting..."
echo "Frontend: http://localhost:3000"
echo "Backend API: http://localhost:8000"
echo "API Documentation: http://localhost:8000/docs"
echo ""
echo "Press Ctrl+C to stop all services"

# Function to cleanup on exit
cleanup() {
    echo ""
    echo "🛑 Stopping ElevateCRM..."
    kill $BACKEND_PID 2>/dev/null
    kill $FRONTEND_PID 2>/dev/null
    exit 0
}

trap cleanup SIGINT

# Wait for processes
wait
EOF
    
    chmod +x start.sh
    print_status "Start script created ✓"
}

# Function to create stop script
create_stop_script() {
    print_step "Creating stop script..."
    
    cat > stop.sh << 'EOF'
#!/bin/bash

echo "🛑 Stopping ElevateCRM services..."

# Kill backend processes
pkill -f "uvicorn app.main:app"

# Kill frontend processes
pkill -f "npm start"
pkill -f "next start"

echo "✅ All services stopped"
EOF
    
    chmod +x stop.sh
    print_status "Stop script created ✓"
}

# Function to create systemd service (optional)
create_systemd_service() {
    if [[ "$OSTYPE" == "linux-gnu"* ]] && command_exists systemctl; then
        print_step "Creating systemd service..."
        
        CURRENT_DIR=$(pwd)
        CURRENT_USER=$(whoami)
        
        sudo tee /etc/systemd/system/elevatecrm.service > /dev/null << EOF
[Unit]
Description=ElevateCRM Application
After=network.target postgresql.service redis.service

[Service]
Type=forking
User=$CURRENT_USER
WorkingDirectory=$CURRENT_DIR
ExecStart=$CURRENT_DIR/start.sh
ExecStop=$CURRENT_DIR/stop.sh
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF
        
        sudo systemctl daemon-reload
        print_status "Systemd service created ✓"
        print_status "To start on boot: sudo systemctl enable elevatecrm"
    fi
}

# Main installation process
main() {
    print_status "Starting ElevateCRM standalone installation..."
    
    # Check if we're in the right directory
    if [ ! -f "package.json" ] && [ ! -d "frontend" ] && [ ! -d "backend" ]; then
        print_error "Please run this script from the ElevateCRM root directory"
        exit 1
    fi
    
    # Ask user for confirmation
    echo ""
    print_warning "This script will:"
    echo "  1. Install system dependencies (requires sudo)"
    echo "  2. Setup PostgreSQL database"
    echo "  3. Setup Redis cache"
    echo "  4. Install backend dependencies"
    echo "  5. Install frontend dependencies"
    echo "  6. Create configuration files"
    echo "  7. Build the application"
    echo ""
    read -p "Do you want to continue? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        print_status "Installation cancelled"
        exit 0
    fi
    
    # Run installation steps
    install_dependencies
    check_prerequisites
    setup_database
    setup_redis
    setup_backend
    setup_frontend
    create_start_script
    create_stop_script
    create_systemd_service
    
    echo ""
    print_status "🎉 ElevateCRM installation completed successfully!"
    echo ""
    echo "To start the application:"
    echo "  ./start.sh"
    echo ""
    echo "To stop the application:"
    echo "  ./stop.sh"
    echo ""
    echo "Access URLs:"
    echo "  Frontend: http://localhost:3000"
    echo "  Backend API: http://localhost:8000"
    echo "  API Docs: http://localhost:8000/docs"
    echo ""
    echo "Default login credentials:"
    echo "  Email: admin@techguru.com"
    echo "  Password: admin123"
    echo ""
    print_warning "Please change the default password after first login!"
}

# Run main function
main "$@"