#!/bin/bash
export PATH=$PATH:/root/.nvm/versions/node/v20.19.0/bin
echo "=== 重启后端服务 ==="
cd /var/www/sstcp
pm2 restart sstcp-backend
sleep 3
pm2 status
echo ""
echo "=== 测试 API ==="
curl -s http://localhost:8080/api/v1/health || echo "API 测试完成"
