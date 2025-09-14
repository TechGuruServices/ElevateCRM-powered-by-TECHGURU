#!/bin/bash

# ElevateCRM Deployment Validation Script
# Validates configuration and environment before deployment

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
ENV_FILE=".env.prod"
FRONTEND_ENV_FILE="frontend/.env.local"
BACKEND_ENV_FILE="backend/.env"
DOCKER_COMPOSE_FILE="docker-compose.prod.yml"

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

success() {
    echo -e "${GREEN}✓ $1${NC}"
}

fail() {
    echo -e "${RED}✗ $1${NC}"
}

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to check environment variable
check_env_var() {
    local file="$1"
    local var="$2"
    local description="$3"
    
    if [ -f "$file" ] && grep -q "^${var}=" "$file"; then
        local value=$(grep "^${var}=" "$file" | cut -d'=' -f2- | sed 's/^"//' | sed 's/"$//')
        if [ -n "$value" ] && [ "$value" != "your-" ] && [ "$value" != "change_this" ]; then
            success "$description is configured"
            return 0
        else
            fail "$description has default/empty value"
            return 1
        fi
    else
        fail "$description is not configured"
        return 1
    fi
}

# Function to validate passwords
validate_password() {
    local password="$1"
    local name="$2"
    
    if [ ${#password} -lt 12 ]; then
        fail "$name password is too short (minimum 12 characters)"
        return 1
    fi
    
    if [[ "$password" =~ [a-z] ]] && [[ "$password" =~ [A-Z] ]] && [[ "$password" =~ [0-9] ]]; then
        success "$name password meets complexity requirements"
        return 0
    else
        fail "$name password does not meet complexity requirements (needs upper, lower, and numbers)"
        return 1
    fi
}

# Function to check system requirements
check_system_requirements() {
    log "Checking system requirements..."
    
    local errors=0
    
    # Check available memory
    local memory_gb=$(free -g | awk '/^Mem:/{print $2}')
    if [ "$memory_gb" -ge 4 ]; then
        success "Memory: ${memory_gb}GB (minimum 4GB)"
    else
        fail "Memory: ${memory_gb}GB (minimum 4GB required)"
        ((errors++))
    fi
    
    # Check available disk space
    local disk_gb=$(df -BG . | awk 'NR==2{print $4}' | sed 's/G//')
    if [ "$disk_gb" -ge 20 ]; then
        success "Disk space: ${disk_gb}GB available (minimum 20GB)"
    else
        fail "Disk space: ${disk_gb}GB available (minimum 20GB required)"
        ((errors++))
    fi
    
    # Check CPU cores
    local cpu_cores=$(nproc)
    if [ "$cpu_cores" -ge 2 ]; then
        success "CPU cores: ${cpu_cores} (minimum 2)"
    else
        fail "CPU cores: ${cpu_cores} (minimum 2 recommended)"
        ((errors++))
    fi
    
    return $errors
}

# Function to check software dependencies
check_dependencies() {
    log "Checking software dependencies..."
    
    local errors=0
    
    # Check Docker
    if command_exists docker; then
        local docker_version=$(docker --version | awk '{print $3}' | sed 's/,//')
        success "Docker is installed: $docker_version"
        
        # Check if Docker is running
        if docker info >/dev/null 2>&1; then
            success "Docker daemon is running"
        else
            fail "Docker daemon is not running"
            ((errors++))
        fi
    else
        fail "Docker is not installed"
        ((errors++))
    fi
    
    # Check Docker Compose
    if command_exists docker-compose || docker compose version >/dev/null 2>&1; then
        if command_exists docker-compose; then
            local compose_version=$(docker-compose --version | awk '{print $3}' | sed 's/,//')
            success "Docker Compose is installed: $compose_version"
        else
            local compose_version=$(docker compose version --short)
            success "Docker Compose is installed: $compose_version"
        fi
    else
        fail "Docker Compose is not installed"
        ((errors++))
    fi
    
    # Check Git (optional)
    if command_exists git; then
        local git_version=$(git --version | awk '{print $3}')
        success "Git is installed: $git_version"
    else
        warning "Git is not installed (optional for manual deployments)"
    fi
    
    return $errors
}

# Function to check configuration files
check_configuration() {
    log "Checking configuration files..."
    
    local errors=0
    
    # Check Docker Compose file
    if [ -f "$DOCKER_COMPOSE_FILE" ]; then
        success "Production Docker Compose file exists"
        
        # Validate Docker Compose syntax
        if docker-compose -f "$DOCKER_COMPOSE_FILE" config >/dev/null 2>&1; then
            success "Docker Compose file syntax is valid"
        else
            fail "Docker Compose file has syntax errors"
            ((errors++))
        fi
    else
        fail "Production Docker Compose file not found: $DOCKER_COMPOSE_FILE"
        ((errors++))
    fi
    
    # Check environment files
    if [ -f "$ENV_FILE" ]; then
        success "Main environment file exists: $ENV_FILE"
    else
        fail "Main environment file not found: $ENV_FILE"
        ((errors++))
    fi
    
    if [ -f "$FRONTEND_ENV_FILE" ]; then
        success "Frontend environment file exists: $FRONTEND_ENV_FILE"
    else
        warning "Frontend environment file not found: $FRONTEND_ENV_FILE"
    fi
    
    if [ -f "$BACKEND_ENV_FILE" ]; then
        success "Backend environment file exists: $BACKEND_ENV_FILE"
    else
        warning "Backend environment file not found: $BACKEND_ENV_FILE"
    fi
    
    return $errors
}

# Function to validate environment variables
validate_environment() {
    log "Validating environment variables..."
    
    local errors=0
    
    # Check critical environment variables
    if ! check_env_var "$ENV_FILE" "SECRET_KEY" "JWT Secret Key"; then
        ((errors++))
    fi
    
    if ! check_env_var "$ENV_FILE" "POSTGRES_PASSWORD" "PostgreSQL Password"; then
        ((errors++))
    fi
    
    if ! check_env_var "$ENV_FILE" "REDIS_PASSWORD" "Redis Password"; then
        ((errors++))
    fi
    
    # Validate password strength
    if [ -f "$ENV_FILE" ]; then
        local postgres_pwd=$(grep "^POSTGRES_PASSWORD=" "$ENV_FILE" 2>/dev/null | cut -d'=' -f2- | sed 's/^"//' | sed 's/"$//')
        local redis_pwd=$(grep "^REDIS_PASSWORD=" "$ENV_FILE" 2>/dev/null | cut -d'=' -f2- | sed 's/^"//' | sed 's/"$//')
        
        if [ -n "$postgres_pwd" ]; then
            if ! validate_password "$postgres_pwd" "PostgreSQL"; then
                ((errors++))
            fi
        fi
        
        if [ -n "$redis_pwd" ]; then
            if ! validate_password "$redis_pwd" "Redis"; then
                ((errors++))
            fi
        fi
    fi
    
    return $errors
}

# Function to check SSL configuration
check_ssl() {
    log "Checking SSL configuration..."
    
    local errors=0
    
    if [ -f "ssl/cert.pem" ] && [ -f "ssl/key.pem" ]; then
        success "SSL certificate files found"
        
        # Check certificate validity
        if openssl x509 -in ssl/cert.pem -checkend 86400 -noout >/dev/null 2>&1; then
            local expiry=$(openssl x509 -in ssl/cert.pem -enddate -noout | cut -d'=' -f2)
            success "SSL certificate is valid (expires: $expiry)"
        else
            fail "SSL certificate is expired or will expire within 24 hours"
            ((errors++))
        fi
        
        # Check if private key matches certificate
        local cert_hash=$(openssl x509 -in ssl/cert.pem -pubkey -noout -outform pem | sha256sum)
        local key_hash=$(openssl pkey -in ssl/key.pem -pubout -outform pem | sha256sum)
        
        if [ "$cert_hash" = "$key_hash" ]; then
            success "SSL certificate and private key match"
        else
            fail "SSL certificate and private key do not match"
            ((errors++))
        fi
    else
        warning "SSL certificate files not found (ssl/cert.pem, ssl/key.pem)"
        warning "Application will run with HTTP only"
    fi
    
    return $errors
}

# Function to check network connectivity
check_network() {
    log "Checking network connectivity..."
    
    local errors=0
    
    # Check if ports are available
    local ports=(80 443 5432 6379 8000 3000)
    
    for port in "${ports[@]}"; do
        if ! netstat -tuln 2>/dev/null | grep -q ":$port "; then
            success "Port $port is available"
        else
            fail "Port $port is already in use"
            ((errors++))
        fi
    done
    
    # Check internet connectivity
    if curl -s --connect-timeout 5 http://google.com >/dev/null; then
        success "Internet connectivity is available"
    else
        warning "Internet connectivity check failed (may affect Docker image pulls)"
    fi
    
    return $errors
}

# Function to generate security recommendations
security_recommendations() {
    log "Security recommendations:"
    
    info "1. Use strong, unique passwords for all services"
    info "2. Enable firewall and restrict access to necessary ports only"
    info "3. Keep SSL certificates up to date"
    info "4. Regularly update system packages and Docker images"
    info "5. Monitor application logs for suspicious activity"
    info "6. Set up automated backups"
    info "7. Use fail2ban to prevent brute force attacks"
    info "8. Consider using a reverse proxy/CDN service"
}

# Main validation function
main() {
    log "Starting ElevateCRM deployment validation..."
    echo ""
    
    local total_errors=0
    
    # Run all checks
    check_system_requirements
    total_errors=$((total_errors + $?))
    echo ""
    
    check_dependencies
    total_errors=$((total_errors + $?))
    echo ""
    
    check_configuration
    total_errors=$((total_errors + $?))
    echo ""
    
    validate_environment
    total_errors=$((total_errors + $?))
    echo ""
    
    check_ssl
    total_errors=$((total_errors + $?))
    echo ""
    
    check_network
    total_errors=$((total_errors + $?))
    echo ""
    
    # Display results
    if [ $total_errors -eq 0 ]; then
        log "✅ All checks passed! Ready for deployment."
        echo ""
        security_recommendations
        echo ""
        info "To deploy, run: ./scripts/deploy.sh"
    else
        error "❌ $total_errors validation errors found. Please fix before deployment."
        echo ""
        error "Fix the issues above and run this script again."
        exit 1
    fi
}

# Run validation
main "$@"