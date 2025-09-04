#!/bin/bash
# NanoQuant Recovery Script

# Configuration
BACKUP_DIR="/backups/nanoquant"
DATE=${1:-$(date +%Y%m%d_%H%M%S)}

# Check if backup exists
if [ ! -f "$BACKUP_DIR/nanoquant-db-$DATE.sql" ]; then
    echo "Backup not found for date: $DATE"
    echo "Available backups:"
    ls $BACKUP_DIR/nanoquant-db-*.sql
    exit 1
fi

# Stop services
echo "Stopping services..."
docker-compose down

# Restore database
echo "Restoring database..."
docker exec -i nanoquant-db psql -U nanoquant nanoquant < $BACKUP_DIR/nanoquant-db-$DATE.sql

# Restore user data
echo "Restoring user data..."
cp $BACKUP_DIR/nanoquant-users-$DATE.json /app/nanoquant_users.json

# Restore models (if stored locally)
if [ -f "$BACKUP_DIR/nanoquant-models-$DATE.tar.gz" ]; then
    echo "Restoring models..."
    tar -xzf $BACKUP_DIR/nanoquant-models-$DATE.tar.gz -C /
fi

# Restore output files
if [ -f "$BACKUP_DIR/nanoquant-output-$DATE.tar.gz" ]; then
    echo "Restoring output files..."
    tar -xzf $BACKUP_DIR/nanoquant-output-$DATE.tar.gz -C /
fi

# Restore logs
if [ -f "$BACKUP_DIR/nanoquant-logs-$DATE.tar.gz" ]; then
    echo "Restoring logs..."
    tar -xzf $BACKUP_DIR/nanoquant-logs-$DATE.tar.gz -C /
fi

# Start services
echo "Starting services..."
docker-compose up -d

echo "Recovery completed successfully!"