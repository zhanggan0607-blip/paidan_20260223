#!/bin/bash
echo "=== 确保后端服务运行 ==="
ps aux | grep uvicorn | grep -v grep

# 如果没有运行，启动它
if ! pgrep -f "uvicorn app.main:app" > /dev/null; then
    echo "后端未运行，正在启动..."
    mkdir -p /var/log/sstcp
    cd /var/www/sstcp/backend-python
    nohup venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8080 >> /var/log/sstcp/backend-out.log 2>&1 &
    sleep 3
fi

echo ""
echo "=== 最终验证 ==="
curl -s http://localhost:8080/api/v1/project-info | head -300
