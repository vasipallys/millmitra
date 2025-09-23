#!/bin/bash
# Automated Database Backup Script
# Generated on 2025-07-30T14:18:45.432524

BACKUP_DIR="$(dirname "$0")"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
DB_NAME="rice_mill_erp"
DB_USER="rice_mill_user"
BACKUP_FILE="$BACKUP_DIR/rice_mill_backup_$TIMESTAMP.sql"

echo "Starting database backup at $(date)"

# Create backup
pg_dump -U $DB_USER -h localhost -d $DB_NAME > "$BACKUP_FILE"

if [ $? -eq 0 ]; then
    echo "Backup completed successfully: $BACKUP_FILE"
    
    # Compress backup
    gzip "$BACKUP_FILE"
    echo "Backup compressed: $BACKUP_FILE.gz"
    
    # Remove backups older than 30 days
    find "$BACKUP_DIR" -name "rice_mill_backup_*.sql.gz" -mtime +30 -delete
    echo "Old backups cleaned up"
else
    echo "Backup failed!"
    exit 1
fi

echo "Backup process completed at $(date)"
