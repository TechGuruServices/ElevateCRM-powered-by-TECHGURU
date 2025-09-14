#!/bin/bash

# ElevateCRM Production Deployment Script
# This script deploys ElevateCRM to production environment

set -e

# Configuration
PROJECT_NAME="elevatecrm"
DOCKER_COMPOSE_FILE="docker-compose.prod.yml"
ENV_FILE=".env.prod"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging functions
log() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')] $1${NC}"
}

info() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')] INFO: $1${NC}"
}

warning() {
    echo -e "${YELLOW}[$(date +'%Y-%m-%d %H:%M:%S')] WARNING: $1${NC}"
}

error() {
    echo -e "${RED}[$(date +'%Y-%m-%d %H:%M:%S')] ERROR: $1${NC}" >&2
}

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to check prerequisites
check_prerequisites() {
    log "Checking prerequisites..."
    
    # Check if Docker is installed
    if ! command_exists docker; then
        error "Docker is not installed. Please install Docker first."
        exit 1
    fi
    
    # Check if Docker Compose is installed
    if ! command_exists docker-compose && ! docker compose version >/dev/null 2>&1; then
        error "Docker Compose is not installed. Please install Docker Compose first."
        exit 1
    fi
    
    # Check if Git is installed
    if ! command_exists git; then
        warning "Git is not installed. Manual deployment only."
    fi
    
    # Check if environment file exists
    if [ ! -f "$ENV_FILE" ]; then
        warning "Environment file $ENV_FILE not found. Using default values."
        warning "Please create $ENV_FILE for production configuration."
    fi
    
    log "Prerequisites check completed."
}

# Function to pull latest code
pull_code() {
    if command_exists git && [ -d ".git" ]; then
        log "Pulling latest code from repository..."
        git fetch origin
        git reset --hard origin/main
        log "Code updated successfully."
    else
        info "Skipping code pull (not a git repository or git not installed)."
    fi
}

# Function to backup database
backup_database() {
    log "Creating database backup before deployment..."
    
    if docker-compose -f "$DOCKER_COMPOSE_FILE" ps postgres | grep -q "Up"; then
        # Run backup using our backup script
        docker-compose -f "$DOCKER_COMPOSE_FILE" run --rm backup
        log "Database backup completed."
    else
        warning "Database service not running. Skipping backup."
    fi
}

# Function to build and deploy
deploy() {
    log "Starting deployment process..."
    
    # Build images
    log "Building Docker images..."
    if docker-compose -f "$DOCKER_COMPOSE_FILE" build --no-cache; then
        log "Docker images built successfully."
    else
        error "Failed to build Docker images."
        exit 1
    fi
    
    # Stop existing services
    log "Stopping existing services..."
    docker-compose -f "$DOCKER_COMPOSE_FILE" down
    
    # Start services
    log "Starting services..."
    if docker-compose -f "$DOCKER_COMPOSE_FILE" up -d; then
        log "Services started successfully."
    else
        error "Failed to start services."
        exit 1
    fi
    
    # Wait for services to be ready
    log "Waiting for services to be ready..."
    sleep 30
    
    # Run database migrations
    log "Running database migrations..."
    if docker-compose -f "$DOCKER_COMPOSE_FILE" exec -T backend alembic upgrade head; then
        log "Database migrations completed."
    else
        error "Database migrations failed."
        exit 1
    fi
}

# Function to verify deployment
verify_deployment() {
    log "Verifying deployment..."
    
    # Check if all services are running
    SERVICES=("postgres" "redis" "backend" "frontend" "nginx")
    
    for service in "${SERVICES[@]}"; do
        if docker-compose -f "$DOCKER_COMPOSE_FILE" ps "$service" | grep -q "Up"; then
            log "✓ $service is running"
        else
            error "✗ $service is not running"
            return 1
        fi
    done
    
    # Check application health
    log "Checking application health..."
    
    # Wait for application to be ready
    sleep 10
    
    # Check backend health
    if curl -f -s http://localhost:8000/health >/dev/null; then
        log "✓ Backend health check passed"
    else
        error "✗ Backend health check failed"
        return 1
    fi
    
    # Check frontend
    if curl -f -s http://localhost:3000 >/dev/null; then
        log "✓ Frontend is accessible"
    else
        error "✗ Frontend is not accessible"
        return 1
    fi
    
    # Check nginx
    if curl -f -s http://localhost >/dev/null; then
        log "✓ Nginx is serving requests"
    else
        error "✗ Nginx is not responding"
        return 1
    fi
    
    log "Deployment verification completed successfully!"
}

# Function to show deployment info
show_info() {
    log "Deployment completed successfully!"
    echo ""
    info "Application URLs:"
    info "  Frontend: http://localhost"
    info "  API: http://localhost/api"
    info "  API Docs: http://localhost/api/docs"
    info "  Monitoring: http://localhost:3001 (Grafana)"
    echo ""
    info "To view logs: docker-compose -f $DOCKER_COMPOSE_FILE logs -f"
    info "To stop services: docker-compose -f $DOCKER_COMPOSE_FILE down"
    echo ""
}

# Function to rollback deployment
rollback() {
    warning "Rolling back deployment..."
    
    # Stop current services
    docker-compose -f "$DOCKER_COMPOSE_FILE" down
    
    # Restore from backup (manual process)
    warning "Please manually restore database from backup if needed."
    warning "Backup files are located in ./backups/"
    
    error "Rollback completed. Please investigate the deployment issue."
    exit 1
}

# Main deployment function
main() {
    log "Starting ElevateCRM production deployment..."
    
    # Trap to handle errors
    trap 'error "Deployment failed!"; rollback' ERR
    
    # Run deployment steps
    check_prerequisites
    pull_code
    backup_database
    deploy
    
    # Verify deployment
    if verify_deployment; then
        show_info
    else
        error "Deployment verification failed!"
        rollback
    fi
}

# Check if script is being run directly
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    # Parse command line arguments
    case "${1:-}" in
        "backup")
            backup_database
            ;;
        "verify")
            verify_deployment
            ;;
        "rollback")
            rollback
            ;;
        *)
            main "$@"
            ;;
    esac
fi