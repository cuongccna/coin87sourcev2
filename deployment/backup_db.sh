#!/bin/bash
# Database Backup Script for Coin87
# Run daily via cron: 0 3 * * * /home/coin87/scripts/backup_db.sh

# Configuration
DB_NAME="coin87v2_db"
DB_USER="coin87v2_user"
BACKUP_DIR="/home/coin87/backups/database"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
BACKUP_FILE="$BACKUP_DIR/coin87_backup_$TIMESTAMP.sql.gz"
RETENTION_DAYS=7

# Create backup directory if not exists
mkdir -p "$BACKUP_DIR"

# Export password (read from .env or hardcode securely)
export PGPASSWORD="Cuongnv123456"

# Create backup
echo "[$(date)] Starting database backup..."
pg_dump -h localhost -U "$DB_USER" -d "$DB_NAME" -F p | gzip > "$BACKUP_FILE"

# Check if backup was successful
if [ $? -eq 0 ]; then
    echo "[$(date)] Backup successful: $BACKUP_FILE"
    
    # Get file size
    SIZE=$(du -h "$BACKUP_FILE" | cut -f1)
    echo "[$(date)] Backup size: $SIZE"
    
    # Delete old backups (older than RETENTION_DAYS)
    echo "[$(date)] Cleaning old backups (older than $RETENTION_DAYS days)..."
    find "$BACKUP_DIR" -name "coin87_backup_*.sql.gz" -mtime +$RETENTION_DAYS -delete
    
    # Count remaining backups
    COUNT=$(ls -1 "$BACKUP_DIR"/coin87_backup_*.sql.gz 2>/dev/null | wc -l)
    echo "[$(date)] Total backups retained: $COUNT"
    
else
    echo "[$(date)] ERROR: Backup failed!"
    exit 1
fi

# Optional: Upload to cloud storage (uncomment if using rclone)
# echo "[$(date)] Uploading to cloud storage..."
# rclone copy "$BACKUP_FILE" gdrive:coin87-backups/
# if [ $? -eq 0 ]; then
#     echo "[$(date)] Cloud upload successful"
# else
#     echo "[$(date)] WARNING: Cloud upload failed"
# fi

echo "[$(date)] Backup process completed"
