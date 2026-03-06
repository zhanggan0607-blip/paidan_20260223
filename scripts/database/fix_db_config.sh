#!/bin/bash
echo "=== 修复数据库配置 ==="
cd /var/www/sstcp/backend-python

# 备份原配置
cp .env .env.backup

# 更新数据库连接
sed -i 's|DATABASE_URL=postgresql://postgres:123456@localhost:5432/tq|DATABASE_URL=postgresql://sstcp_user:Lily421020@localhost:5432/sstcp_maintenance|g' .env

echo "新配置:"
grep DATABASE_URL .env

echo ""
echo "=== 重启后端服务 ==="
pkill -f "uvicorn app.main:app" || true
sleep 2
cd /var/www/sstcp/backend-python
source venv/bin/activate
nohup venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8080 > /var/log/sstcp/backend-out.log 2>&1 &
sleep 3

echo ""
echo "=== 测试 API ==="
curl -s http://localhost:8080/api/v1/personnel | head -500
