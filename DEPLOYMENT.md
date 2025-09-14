# Navigate to packaging folder
cd packaging

# Run the automated builder
build.bat# ElevateCRM Production Deployment Guide

This guide provides step-by-step instructions for deploying ElevateCRM in a production environment.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Environment Setup](#environment-setup)
3. [SSL/TLS Configuration](#ssltls-configuration)
4. [Database Setup](#database-setup)
5. [Deployment Options](#deployment-options)
6. [Monitoring Setup](#monitoring-setup)
7. [Backup Configuration](#backup-configuration)
8. [Security Hardening](#security-hardening)
9. [Troubleshooting](#troubleshooting)

## Prerequisites

### System Requirements

- **Operating System**: Ubuntu 20.04 LTS or newer, CentOS 8+, or RHEL 8+
- **Memory**: Minimum 4GB RAM (8GB+ recommended for production)
- **Storage**: Minimum 50GB SSD (100GB+ recommended)
- **CPU**: 2+ cores (4+ cores recommended)
- **Network**: Static IP address and domain name

### Software Requirements

- Docker Engine 20.10+
- Docker Compose 2.0+
- Git
- curl or wget
- Basic Linux administration knowledge

### Domain and SSL

- Registered domain name pointing to your server
- SSL certificate (Let's Encrypt recommended)

## Environment Setup

### 1. Server Preparation

```bash
# Update system packages
sudo apt update && sudo apt upgrade -y

# Install required packages
sudo apt install -y git curl wget vim htop

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/download/v2.20.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Logout and login again for group changes to take effect
```

### 2. Clone Repository

```bash
# Clone the repository
git clone https://github.com/yourusername/elevatecrm.git
cd elevatecrm

# Or upload your code manually if not using Git
```

### 3. Environment Configuration

```bash
# Copy environment templates
cp .env.example .env.prod
cp frontend/.env.example frontend/.env.local
cp backend/.env.example backend/.env

# Edit production environment file
nano .env.prod
```

#### Required Environment Variables

**Database Configuration:**

```bash
POSTGRES_PASSWORD=your_secure_database_password
DATABASE_URL=postgresql://elevatecrm_user:your_secure_database_password@postgres:5432/elevatecrm
```

**Security Configuration:**

```bash
SECRET_KEY=your_super_secret_jwt_key_minimum_32_characters
REDIS_PASSWORD=your_secure_redis_password
```

**Domain Configuration:**

```bash
ALLOWED_ORIGINS=https://yourdomain.com,https://www.yourdomain.com
NEXT_PUBLIC_API_URL=https://yourdomain.com
```

**Email Configuration (Optional):**

```bash
SMTP_HOST=smtp.yourmailprovider.com
SMTP_USER=noreply@yourdomain.com
SMTP_PASSWORD=your_email_password
```

## SSL/TLS Configuration

### Option 1: Let's Encrypt (Recommended)

```bash
# Install Certbot
sudo apt install -y certbot

# Obtain SSL certificate
sudo certbot certonly --standalone -d yourdomain.com -d www.yourdomain.com

# Create SSL directory and copy certificates
sudo mkdir -p ssl
sudo cp /etc/letsencrypt/live/yourdomain.com/fullchain.pem ssl/cert.pem
sudo cp /etc/letsencrypt/live/yourdomain.com/privkey.pem ssl/key.pem
sudo chown -R $USER:$USER ssl/
```

### Option 2: Custom SSL Certificate

```bash
# Create SSL directory
mkdir -p ssl

# Copy your SSL certificate files
cp your_certificate.pem ssl/cert.pem
cp your_private_key.pem ssl/key.pem
```

### Enable SSL in Nginx

Edit `nginx/conf.d/default.conf` and uncomment the SSL configuration sections.

## Database Setup

### PostgreSQL Configuration

The production setup uses PostgreSQL with the following optimizations:

1. **Connection Pooling**: Configured for high concurrency
2. **Row Level Security**: Enabled for multi-tenant isolation
3. **Backup Strategy**: Automated daily backups
4. **Performance Tuning**: Optimized for production workloads

### Initialize Database

```bash
# Start only the database service first
docker-compose -f docker-compose.prod.yml up -d postgres redis

# Wait for database to be ready
sleep 30

# Run database migrations
docker-compose -f docker-compose.prod.yml run --rm backend alembic upgrade head

# Optionally, seed with initial data
docker-compose -f docker-compose.prod.yml run --rm backend python -m app.scripts.seed_data
```

## Deployment Options

### Option 1: Quick Deployment

```bash
# Make deployment script executable
chmod +x scripts/deploy.sh

# Run deployment
./scripts/deploy.sh
```

### Option 2: Manual Deployment

```bash
# Build and start all services
docker-compose -f docker-compose.prod.yml build --no-cache
docker-compose -f docker-compose.prod.yml up -d

# Verify deployment
docker-compose -f docker-compose.prod.yml ps
```

### Option 3: Blue-Green Deployment

For zero-downtime deployments:

```bash
# Build new images with different tags
docker-compose -f docker-compose.prod.yml build --no-cache

# Deploy to staging environment first
docker-compose -f docker-compose.staging.yml up -d

# Test staging environment
# ... perform tests ...

# Switch traffic to new version
# ... update load balancer configuration ...

# Stop old version
docker-compose -f docker-compose.prod.yml down
```

## Monitoring Setup

### Prometheus and Grafana

The production setup includes monitoring with Prometheus and Grafana:

```bash
# Access Grafana dashboard
open http://yourdomain.com:3001

# Default login: admin / admin (change on first login)
```

### Health Checks

Monitor application health:

```bash
# Backend health
curl http://yourdomain.com/health

# Frontend health
curl http://yourdomain.com/api/health

# Database health
docker-compose -f docker-compose.prod.yml exec postgres pg_isready
```

### Log Management

```bash
# View all logs
docker-compose -f docker-compose.prod.yml logs -f

# View specific service logs
docker-compose -f docker-compose.prod.yml logs -f backend
docker-compose -f docker-compose.prod.yml logs -f frontend

# View last 100 lines
docker-compose -f docker-compose.prod.yml logs --tail=100 backend
```

## Backup Configuration

### Automated Backups

Set up automated daily backups:

```bash
# Make backup script executable
chmod +x scripts/backup.sh

# Add to crontab for daily backups at 2 AM
crontab -e

# Add this line:
0 2 * * * /path/to/elevatecrm/scripts/backup.sh
```

### Manual Backup

```bash
# Create immediate backup
docker-compose -f docker-compose.prod.yml run --rm backup

# List available backups
ls -la backups/
```

### Restore from Backup

```bash
# Stop services
docker-compose -f docker-compose.prod.yml down

# Restore database
gunzip -c backups/elevatecrm_backup_YYYYMMDD_HHMMSS.sql.gz | \
docker-compose -f docker-compose.prod.yml exec -T postgres psql -U elevatecrm_user -d elevatecrm

# Start services
docker-compose -f docker-compose.prod.yml up -d
```

## Security Hardening

### Firewall Configuration

```bash
# Configure UFW firewall
sudo ufw enable
sudo ufw default deny incoming
sudo ufw default allow outgoing

# Allow SSH
sudo ufw allow ssh

# Allow HTTP and HTTPS
sudo ufw allow 80
sudo ufw allow 443

# Allow specific monitoring ports (if needed)
sudo ufw allow from trusted_ip_range to any port 3001  # Grafana
sudo ufw allow from trusted_ip_range to any port 9090  # Prometheus
```

### Docker Security

```bash
# Run Docker daemon with security options
# Edit /etc/docker/daemon.json
{
  "log-driver": "json-file",
  "log-opts": {
    "max-size": "10m",
    "max-file": "3"
  },
  "userns-remap": "default"
}

# Restart Docker
sudo systemctl restart docker
```

### Regular Security Updates

```bash
# Create update script
cat > update-system.sh << 'EOF'
#!/bin/bash
sudo apt update
sudo apt upgrade -y
sudo apt autoremove -y
docker system prune -f
EOF

chmod +x update-system.sh

# Add to crontab for weekly updates
# 0 3 * * 0 /path/to/update-system.sh
```

## Performance Optimization

### System Optimization

```bash
# Optimize PostgreSQL
# Edit /etc/postgresql/postgresql.conf (if using external PostgreSQL)
shared_buffers = 256MB
effective_cache_size = 1GB
maintenance_work_mem = 64MB
checkpoint_completion_target = 0.9
wal_buffers = 16MB
default_statistics_target = 100
random_page_cost = 1.1
effective_io_concurrency = 200
```

### Application Optimization

```bash
# Enable HTTP/2 and compression in Nginx
# Already configured in nginx/conf.d/default.conf

# Optimize Docker images
docker system prune -a -f

# Monitor resource usage
docker stats
htop
```

## Troubleshooting

### Common Issues

#### 1. Services Won't Start

```bash
# Check service status
docker-compose -f docker-compose.prod.yml ps

# Check logs for errors
docker-compose -f docker-compose.prod.yml logs backend
docker-compose -f docker-compose.prod.yml logs frontend

# Check resource usage
docker stats
df -h
free -h
```

#### 2. Database Connection Issues

```bash
# Test database connection
docker-compose -f docker-compose.prod.yml exec postgres psql -U elevatecrm_user -d elevatecrm -c "SELECT 1;"

# Check database logs
docker-compose -f docker-compose.prod.yml logs postgres

# Verify environment variables
docker-compose -f docker-compose.prod.yml exec backend env | grep DATABASE_URL
```

#### 3. SSL Certificate Issues

```bash
# Check certificate validity
openssl x509 -in ssl/cert.pem -text -noout

# Test SSL configuration
curl -I https://yourdomain.com

# Check Nginx configuration
docker-compose -f docker-compose.prod.yml exec nginx nginx -t
```

#### 4. Performance Issues

```bash
# Monitor system resources
top
iostat 1
netstat -tuln

# Check application metrics
curl http://localhost:8000/metrics
curl http://localhost:3000/api/metrics

# Analyze slow queries (PostgreSQL)
docker-compose -f docker-compose.prod.yml exec postgres psql -U elevatecrm_user -d elevatecrm -c "
SELECT query, mean_exec_time, calls 
FROM pg_stat_statements 
ORDER BY mean_exec_time DESC 
LIMIT 10;"
```

### Emergency Procedures

#### Rollback Deployment

```bash
# Quick rollback using deployment script
./scripts/deploy.sh rollback

# Manual rollback
docker-compose -f docker-compose.prod.yml down
git checkout previous_working_commit
docker-compose -f docker-compose.prod.yml up -d
```

#### Emergency Backup

```bash
# Quick backup before emergency maintenance
docker-compose -f docker-compose.prod.yml run --rm backup
```

## Maintenance

### Regular Tasks

1. **Daily**: Check logs and health status
2. **Weekly**: Review monitoring metrics and alerts
3. **Monthly**: Update system packages and Docker images
4. **Quarterly**: Review and test backup/restore procedures

### Scaling Considerations

For high-traffic deployments:

1. **Horizontal Scaling**: Use multiple backend/frontend instances
2. **Database Scaling**: Consider read replicas
3. **Caching**: Implement Redis clustering
4. **Load Balancing**: Use external load balancer
5. **CDN**: Implement CDN for static assets

### Support

For additional support and documentation:

- Check the main README.md for development information
- Review application logs for specific error messages
- Monitor system metrics using Grafana dashboards
- Consult Docker and service-specific documentation

---

**Important**: Always test deployments in a staging environment before applying to production!