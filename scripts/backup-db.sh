#!/bin/bash

set -e

BACKUP_DIR="/opt/sstcp/backups"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="${BACKUP_DIR}/sstcp_backup_${TIMESTAMP}.sql.gz"
RETENTION_DAYS=30

mkdir -p ${BACKUP_DIR}

echo "🗄️ 开始数据库备份..."

if [ -n "$DATABASE_URL" ]; then
    PGHOST=$(echo $DATABASE_URL | sed -n 's/.*@\([^:\/]*\).*/\1/p')
    PGUSER=$(echo $DATABASE_URL | sed -n 's/.*\/\/\([^:]*\).*/\1/p')
    PGPASSWORD=$(echo $DATABASE_URL | sed -n 's/.*:\([^@]*\)@.*/\1/p')
    PGDB=$(echo $DATABASE_URL | sed -n 's/.*\/\([^?]*\).*/\1/p')
    PGPORT=$(echo $DATABASE_URL | sed -n 's/.*:\([0-9]*\)\/.*/\1/p')
    PGPORT=${PGPORT:-5432}

    PGPASSWORD=$PGPASSWORD pg_dump \
        -h $PGHOST \
        -p $PGPORT \
        -U $PGUSER \
        -d $PGDB \
        --no-owner \
        --no-privileges \
        | gzip > ${BACKUP_FILE}
else
    echo "❌ DATABASE_URL 环境变量未设置"
    exit 1
fi

BACKUP_SIZE=$(du -h ${BACKUP_FILE} | cut -f1)
echo "✅ 备份完成: ${BACKUP_FILE} (${BACKUP_SIZE})"

echo "🧹 清理${RETENTION_DAYS}天前的备份..."
find ${BACKUP_DIR} -name "sstcp_backup_*.sql.gz" -mtime +${RETENTION_DAYS} -delete

echo "🎉 数据库备份流程完成！"
