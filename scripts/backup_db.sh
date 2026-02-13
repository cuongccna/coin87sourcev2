#!/bin/bash
# Database Backup Script for LARAI.VN
# Runs daily at 2:00 AM via cron

set -e

# Configuration
BACKUP_DIR="/var/www/backups"
DB_NAME="coin87v2_db"
DB_USER="coin87v2_user"
RETENTION_DAYS=7
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="$BACKUP_DIR/${DB_NAME}_${TIMESTAMP}.sql.gz"

# Create backup directory if not exists
mkdir -p $BACKUP_DIR

echo "================================"
echo "🗄️  Starting database backup..."
echo "================================"

# Dump database and compress (with password)
export PGPASSWORD='Cuongnv123456'
pg_dump -U $DB_USER -h localhost -d $DB_NAME | gzip > $BACKUP_FILE
unset PGPASSWORD

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
find $BACKUP_DIR -name "${DB_NAME}_*.sql.gz" -mtime +$RETENTION_DAYS -delete
echo "✓ Old backups deleted (kept last $RETENTION_DAYS days)"

# List recent backups
echo ""
echo "Recent backups:"
ls -lh $BACKUP_DIR/*.sql.gz 2>/dev/null | tail -n 5 || echo "No backups found"

echo "================================"
echo "Backup complete!"
echo "================================"

# Optional: Upload to cloud storage
# Uncomment and configure rclone for Google Drive/S3
# rclone copy $BACKUP_FILE remote:coin87-backups/
