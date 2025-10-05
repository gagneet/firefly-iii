#!/bin/bash
# Firefly III Database Backup Script

BACKUP_DIR="/home/gagneet/firefly/backups"
DB_NAME="firefly_db"
DB_USER="fireflyuser"
DB_PASS="Gagneet\$5"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="$BACKUP_DIR/firefly_$TIMESTAMP.sql"

# Create backup
mysqldump -u "$DB_USER" -p"$DB_PASS" "$DB_NAME" > "$BACKUP_FILE" 2>&1

# Compress backup
gzip "$BACKUP_FILE"

# Delete backups older than 7 days
find "$BACKUP_DIR" -name "firefly_*.sql.gz" -mtime +7 -delete

# Log result
if [ $? -eq 0 ]; then
    echo "$(date): Backup completed successfully - $BACKUP_FILE.gz" >> "$BACKUP_DIR/backup.log"
else
    echo "$(date): Backup failed" >> "$BACKUP_DIR/backup.log"
fi
