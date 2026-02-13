#!/bin/bash
# Database Backup Script for Coin87
# Add to crontab: 0 3 * * * /opt/coin87/scripts/backup_db.sh

set -e

# Configuration
BACKUP_DIR="/opt/coin87/backups"
DB_NAME="coin87_db"
DB_USER="coin87_user"
RETENTION_DAYS=7
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="$BACKUP_DIR/coin87_backup_$TIMESTAMP.sql.gz"

# Create backup directory if not exists
mkdir -p $BACKUP_DIR

echo "================================"
echo "Starting database backup..."
echo "================================"

# Dump database and compress
pg_dump -U $DB_USER -d $DB_NAME | gzip > $BACKUP_FILE

# Check if backup was successful
if [ $? -eq 0 ]; then
    echo "✓ Backup created: $BACKUP_FILE"
    BACKUP_SIZE=$(du -h $BACKUP_FILE | cut -f1)
    echo "  Size: $BACKUP_SIZE"
else
    echo "✗ Backup failed!"
    exit 1
fi

# Delete old backups (keep last 7 days)
echo "Cleaning up old backups..."
find $BACKUP_DIR -name "coin87_backup_*.sql.gz" -mtime +$RETENTION_DAYS -delete
echo "✓ Old backups deleted (kept last $RETENTION_DAYS days)"

echo "================================"
echo "Backup complete!"
echo "================================"

# Optional: Upload to cloud storage
# Uncomment and configure rclone for Google Drive/S3
# rclone copy $BACKUP_FILE remote:coin87-backups/
