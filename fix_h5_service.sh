#!/bin/bash

echo "========================================="
echo "SSTCP H5服务修复脚本"
echo "========================================="
echo ""

echo "步骤1: 检查容器网络信息..."
BACKEND_IP=$(docker inspect sstcp-backend-new --format='{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' 2>/dev/null)
echo "后端容器IP: $BACKEND_IP"

H5_IP=$(docker inspect sstcp-frontend-h5-new --format='{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' 2>/dev/null)
echo "H5容器IP: $H5_IP"
echo ""

if [ -z "$BACKEND_IP" ]; then
    echo "错误: 无法获取后端容器IP"
    exit 1
fi

echo "步骤2: 备份原nginx配置..."
docker exec sstcp-frontend-h5-new cp /etc/nginx/conf.d/default.conf /etc/nginx/conf.d/default.conf.backup 2>/dev/null
echo "配置已备份"
echo ""

echo "步骤3: 修复nginx配置..."
docker exec sstcp-frontend-h5-new sed -i "s|proxy_pass http://backend:8000|proxy_pass http://$BACKEND_IP:8000|g" /etc/nginx/conf.d/default.conf
echo "配置已更新"
echo ""

echo "步骤4: 验证nginx配置..."
docker exec sstcp-frontend-h5-new nginx -t
if [ $? -eq 0 ]; then
    echo "Nginx配置验证成功"
else
    echo "Nginx配置验证失败，恢复备份..."
    docker exec sstcp-frontend-h5-new cp /etc/nginx/conf.d/default.conf.backup /etc/nginx/conf.d/default.conf
    exit 1
fi
echo ""

echo "步骤5: 重启H5容器..."
docker restart sstcp-frontend-h5-new
sleep 3
echo ""

echo "步骤6: 检查容器状态..."
docker ps | grep sstcp-frontend-h5-new
echo ""

echo "步骤7: 测试H5服务..."
curl -s -o /dev/null -w "HTTP状态码: %{http_code}\n" http://localhost:81/ || echo "H5服务无响应"
echo ""

echo "步骤8: 查看H5容器日志..."
docker logs sstcp-frontend-h5-new 2>&1 | tail -20
echo ""

echo "========================================="
echo "修复完成！"
echo "========================================="
