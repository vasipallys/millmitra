#!/usr/bin/env python3
"""
Database Security and Backup Setup Script
=========================================
"""

import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path

def setup_postgresql_security():
    """Configure PostgreSQL security settings"""
    print("[INFO] Setting up PostgreSQL security...")
    
    # Create database user with limited privileges
    commands = [
        "CREATE USER rice_mill_user WITH ENCRYPTED PASSWORD 'CHANGE_THIS_PASSWORD';",
        "CREATE DATABASE rice_mill_erp OWNER rice_mill_user;",
        "GRANT CONNECT ON DATABASE rice_mill_erp TO rice_mill_user;",
        "GRANT USAGE ON SCHEMA public TO rice_mill_user;",
        "GRANT CREATE ON SCHEMA public TO rice_mill_user;",
        "ALTER USER rice_mill_user SET default_transaction_isolation TO 'read committed';",
        "ALTER USER rice_mill_user SET timezone TO 'UTC';"
    ]
    
    print("Execute these commands in PostgreSQL as superuser:")
    for cmd in commands:
        print(f"  {cmd}")
    
    return commands

def setup_backup_strategy():
    """Set up automated database backup"""
    backup_dir = Path("backups")
    backup_dir.mkdir(exist_ok=True)
    
    backup_script = backup_dir / "backup_database.sh"
    
    backup_content = f"""#!/bin/bash
# Automated Database Backup Script
# Generated on {datetime.now().isoformat()}

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
"""
    
    with open(backup_script, 'w') as f:
        f.write(backup_content)
    
    # Make script executable
    os.chmod(backup_script, 0o755)
    
    print(f"[SUCCESS] Backup script created: {backup_script}")
    print("[INFO] Set up cron job for daily backups:")
    print(f"   0 2 * * * {backup_script.absolute()}")
    
    return backup_script

if __name__ == "__main__":
    print("[INFO] Database Security Setup")
    print("=" * 50)
    
    setup_postgresql_security()
    setup_backup_strategy()
    
    print("\n[INFO] Next Steps:")
    print("1. Execute the PostgreSQL commands as superuser")
    print("2. Update DATABASE_URL in .env with the actual password")
    print("3. Set up the cron job for automated backups")
    print("4. Test database connection and backup script")
