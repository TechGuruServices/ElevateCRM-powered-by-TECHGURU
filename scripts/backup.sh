#!/bin/bash

# ElevateCRM Database Backup Script
# This script creates automated backups of the PostgreSQL database

set -e

# Configuration
BACKUP_DIR="/backups"
DB_HOST="postgres"
DB_NAME="elevatecrm"
DB_USER="elevatecrm_user"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
BACKUP_FILE="elevatecrm_backup_${TIMESTAMP}.sql"
RETENTION_DAYS=30

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Logging function
log() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')] $1${NC}"
}

error() {
    echo -e "${RED}[$(date +'%Y-%m-%d %H:%M:%S')] ERROR: $1${NC}" >&2
}

warning() {
    echo -e "${YELLOW}[$(date +'%Y-%m-%d %H:%M:%S')] WARNING: $1${NC}"
}

# Create backup directory if it doesn't exist
mkdir -p "$BACKUP_DIR"

# Start backup process
log "Starting database backup for ElevateCRM..."

# Check if database is accessible
if ! pg_isready -h "$DB_HOST" -U "$DB_USER" -d "$DB_NAME" >/dev/null 2>&1; then
    error "Database is not accessible. Please check your connection."
    exit 1
fi

# Create database dump
log "Creating database dump..."
if pg_dump -h "$DB_HOST" -U "$DB_USER" -d "$DB_NAME" \
    --verbose \
    --clean \
    --if-exists \
    --create \
    --format=plain \
    > "$BACKUP_DIR/$BACKUP_FILE"; then
    log "Database dump created successfully: $BACKUP_FILE"
else
    error "Failed to create database dump"
    exit 1
fi

# Compress the backup
log "Compressing backup file..."
if gzip "$BACKUP_DIR/$BACKUP_FILE"; then
    log "Backup compressed successfully: ${BACKUP_FILE}.gz"
    BACKUP_FILE="${BACKUP_FILE}.gz"
else
    warning "Failed to compress backup file"
fi

# Calculate backup size
BACKUP_SIZE=$(du -h "$BACKUP_DIR/$BACKUP_FILE" | cut -f1)
log "Backup size: $BACKUP_SIZE"

# Clean up old backups
log "Cleaning up old backups (keeping last $RETENTION_DAYS days)..."
find "$BACKUP_DIR" -name "elevatecrm_backup_*.sql.gz" -mtime +$RETENTION_DAYS -delete
REMAINING_BACKUPS=$(find "$BACKUP_DIR" -name "elevatecrm_backup_*.sql.gz" | wc -l)
log "Remaining backups: $REMAINING_BACKUPS"

# Optional: Upload to cloud storage (uncomment to use)
# if [ -n "$AWS_BUCKET" ]; then
#     log "Uploading backup to S3..."
#     aws s3 cp "$BACKUP_DIR/$BACKUP_FILE" "s3://$AWS_BUCKET/backups/database/"
#     log "Backup uploaded to S3 successfully"
# fi

# Optional: Send notification (uncomment to use)
# if [ -n "$WEBHOOK_URL" ]; then
#     curl -X POST "$WEBHOOK_URL" \
#         -H "Content-Type: application/json" \
#         -d "{\"text\":\"ElevateCRM backup completed successfully. File: $BACKUP_FILE, Size: $BACKUP_SIZE\"}"
# fi

log "Backup process completed successfully!"
log "Backup location: $BACKUP_DIR/$BACKUP_FILE"

exit 0