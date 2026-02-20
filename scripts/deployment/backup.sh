#!/bin/bash
# FörderScout AI - Backup Script
# Run via cron: 0 2 * * * /path/to/backup.sh

set -e

# Configuration
BACKUP_DIR="/opt/backups/foerderscout"
DATE=$(date +%Y%m%d_%H%M%S)
RETENTION_DAYS=30

# Database credentials (from environment or secrets)
POSTGRES_HOST="${POSTGRES_HOST:-postgres}"
POSTGRES_USER="${POSTGRES_USER:-foerderscout}"
POSTGRES_DB="${POSTGRES_DB:-foerderscout}"
POSTGRES_PASSWORD="${POSTGRES_PASSWORD}"

# S3 configuration (optional)
S3_BUCKET="${S3_BUCKET:-}"
AWS_REGION="${AWS_REGION:-eu-central-1}"

# Create backup directory
mkdir -p "${BACKUP_DIR}/postgres"
mkdir -p "${BACKUP_DIR}/redis"
mkdir -p "${BACKUP_DIR}/qdrant"

echo "=================================================="
echo "FörderScout AI - Backup Started"
echo "Date: $(date)"
echo "=================================================="

# =============================================================================
# PostgreSQL Backup
# =============================================================================
echo "📦 Backing up PostgreSQL..."

PGPASSWORD="${POSTGRES_PASSWORD}" pg_dump \
    -h "${POSTGRES_HOST}" \
    -U "${POSTGRES_USER}" \
    -d "${POSTGRES_DB}" \
    -F c \
    -f "${BACKUP_DIR}/postgres/foerderscout_${DATE}.dump"

# Compress
gzip "${BACKUP_DIR}/postgres/foerderscout_${DATE}.dump"

echo "✅ PostgreSQL backup complete: foerderscout_${DATE}.dump.gz"

# =============================================================================
# Redis Backup (if using RDB)
# =============================================================================
echo "📦 Backing up Redis..."

# Trigger Redis BGSAVE
docker exec foerderscout-redis redis-cli -a "${REDIS_PASSWORD}" BGSAVE

# Wait for save to complete
sleep 5

# Copy RDB file
docker cp foerderscout-redis:/data/dump.rdb "${BACKUP_DIR}/redis/redis_${DATE}.rdb"
gzip "${BACKUP_DIR}/redis/redis_${DATE}.rdb"

echo "✅ Redis backup complete: redis_${DATE}.rdb.gz"

# =============================================================================
# Qdrant Backup (snapshot)
# =============================================================================
echo "📦 Backing up Qdrant..."

# Create Qdrant snapshot via API
curl -X POST "http://localhost:6333/snapshots" \
    -H "Content-Type: application/json" \
    -o "${BACKUP_DIR}/qdrant/qdrant_snapshot_${DATE}.json"

# Copy Qdrant data directory
docker cp foerderscout-qdrant:/qdrant/storage "${BACKUP_DIR}/qdrant/storage_${DATE}"
tar -czvf "${BACKUP_DIR}/qdrant/qdrant_storage_${DATE}.tar.gz" \
    -C "${BACKUP_DIR}/qdrant" "storage_${DATE}"
rm -rf "${BACKUP_DIR}/qdrant/storage_${DATE}"

echo "✅ Qdrant backup complete"

# =============================================================================
# Upload to S3 (if configured)
# =============================================================================
if [ -n "${S3_BUCKET}" ]; then
    echo "📤 Uploading to S3..."
    
    aws s3 cp "${BACKUP_DIR}/postgres/foerderscout_${DATE}.dump.gz" \
        "s3://${S3_BUCKET}/postgres/foerderscout_${DATE}.dump.gz" \
        --region "${AWS_REGION}"
    
    aws s3 cp "${BACKUP_DIR}/redis/redis_${DATE}.rdb.gz" \
        "s3://${S3_BUCKET}/redis/redis_${DATE}.rdb.gz" \
        --region "${AWS_REGION}"
    
    aws s3 cp "${BACKUP_DIR}/qdrant/qdrant_storage_${DATE}.tar.gz" \
        "s3://${S3_BUCKET}/qdrant/qdrant_storage_${DATE}.tar.gz" \
        --region "${AWS_REGION}"
    
    echo "✅ S3 upload complete"
fi

# =============================================================================
# Cleanup old backups
# =============================================================================
echo "🧹 Cleaning up old backups (older than ${RETENTION_DAYS} days)..."

find "${BACKUP_DIR}/postgres" -type f -mtime +${RETENTION_DAYS} -delete
find "${BACKUP_DIR}/redis" -type f -mtime +${RETENTION_DAYS} -delete
find "${BACKUP_DIR}/qdrant" -type f -mtime +${RETENTION_DAYS} -delete

echo "✅ Cleanup complete"

# =============================================================================
# Summary
# =============================================================================
echo ""
echo "=================================================="
echo "Backup Complete!"
echo "Date: $(date)"
echo "=================================================="
echo ""
echo "Backup files:"
ls -lh "${BACKUP_DIR}/postgres/foerderscout_${DATE}.dump.gz"
ls -lh "${BACKUP_DIR}/redis/redis_${DATE}.rdb.gz"
ls -lh "${BACKUP_DIR}/qdrant/qdrant_storage_${DATE}.tar.gz"
echo ""
echo "Total backup size: $(du -sh ${BACKUP_DIR} | cut -f1)"
