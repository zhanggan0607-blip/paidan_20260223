#!/bin/bash

echo "=== 开始数据库迁移 ==="

echo "[1/5] 检查备份文件..."
ls -la /tmp/db_backup_tq.dump

echo "[2/5] 列出现有数据库..."
sudo -u postgres psql -c "SELECT datname FROM pg_database WHERE datistemplate = false;"

echo "[3/5] 创建/重置 sstcp_maintenance 数据库..."
sudo -u postgres psql -c "DROP DATABASE IF EXISTS sstcp_maintenance;"
sudo -u postgres psql -c "CREATE DATABASE sstcp_maintenance OWNER postgres;"

echo "[4/5] 导入数据..."
sudo -u postgres pg_restore -d sstcp_maintenance -v /tmp/db_backup_tq.dump 2>&1

echo "[5/5] 创建用户并授权..."
sudo -u postgres psql -c "DROP USER IF EXISTS sstcp_user;"
sudo -u postgres psql -c "CREATE USER sstcp_user WITH PASSWORD 'Lily421020';"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE sstcp_maintenance TO sstcp_user;"
sudo -u postgres psql -d sstcp_maintenance -c "GRANT ALL ON ALL TABLES IN SCHEMA public TO sstcp_user;"
sudo -u postgres psql -d sstcp_maintenance -c "GRANT ALL ON ALL SEQUENCES IN SCHEMA public TO sstcp_user;"
sudo -u postgres psql -d sstcp_maintenance -c "ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO sstcp_user;"
sudo -u postgres psql -d sstcp_maintenance -c "ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO sstcp_user;"

echo "=== 迁移完成 ==="
echo "验证表结构:"
sudo -u postgres psql -d sstcp_maintenance -c "SELECT table_name FROM information_schema.tables WHERE table_schema = 'public' ORDER BY table_name;"
