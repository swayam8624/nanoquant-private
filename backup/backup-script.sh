#!/bin/bash
# NanoQuant Backup Script

# Configuration
BACKUP_DIR="/backups/nanoquant"
DATE=$(date +%Y%m%d_%H%M%S)
RETENTION_DAYS=30

# Create backup directory
mkdir -p $BACKUP_DIR

# Backup database
echo "Backing up database..."
docker exec nanoquant-db pg_dump -U nanoquant nanoquant > $BACKUP_DIR/nanoquant-db-$DATE.sql

# Backup user data
echo "Backing up user data..."
cp /app/nanoquant_users.json $BACKUP_DIR/nanoquant-users-$DATE.json

# Backup models (if stored locally)
if [ -d "/home/nanoquant/models" ]; then
    echo "Backing up models..."
    tar -czf $BACKUP_DIR/nanoquant-models-$DATE.tar.gz /home/nanoquant/models
fi

# Backup output files
if [ -d "/home/nanoquant/output" ]; then
    echo "Backing up output files..."
    tar -czf $BACKUP_DIR/nanoquant-output-$DATE.tar.gz /home/nanoquant/output
fi

# Backup logs
if [ -d "/app/logs" ]; then
    echo "Backing up logs..."
    tar -czf $BACKUP_DIR/nanoquant-logs-$DATE.tar.gz /app/logs
fi

# Upload to cloud storage (AWS S3 example)
if command -v aws &> /dev/null; then
    echo "Uploading backups to S3..."
    aws s3 sync $BACKUP_DIR s3://nanoquant-backups/
fi

# Clean up old backups
echo "Cleaning up old backups..."
find $BACKUP_DIR -name "nanoquant-*" -mtime +$RETENTION_DAYS -delete

echo "Backup completed successfully!"