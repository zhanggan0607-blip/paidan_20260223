#!/bin/bash

echo "========================================="
echo "SSTCP 服务器服务诊断"
echo "========================================="
echo ""

echo "1. 检查Docker服务状态..."
systemctl status docker --no-pager | head -20
echo ""

echo "2. 检查所有Docker容器..."
docker ps -a
echo ""

echo "3. 检查H5容器日志..."
docker logs sstcp-frontend-h5 --tail 50 2>&1
echo ""

echo "4. 检查后端容器日志..."
docker logs sstcp-backend --tail 30 2>&1
echo ""

echo "5. 检查端口监听状态..."
netstat -tlnp | grep -E ":(80|81|8000|443)\s"
echo ""

echo "6. 检查防火墙状态..."
ufw status
echo ""

echo "7. 测试本地服务..."
echo "   测试后端 (8000):"
curl -s -o /dev/null -w "HTTP状态码: %{http_code}\n" http://localhost:8000/api/ || echo "后端无响应"
echo ""
echo "   测试PC前端 (80):"
curl -s -o /dev/null -w "HTTP状态码: %{http_code}\n" http://localhost:80/ || echo "PC前端无响应"
echo ""
echo "   测试H5前端 (81):"
curl -s -o /dev/null -w "HTTP状态码: %{http_code}\n" http://localhost:81/ || echo "H5前端无响应"
echo ""

echo "8. 检查磁盘空间..."
df -h
echo ""

echo "9. 检查Docker镜像..."
docker images
echo ""

echo "========================================="
echo "诊断完成"
echo "========================================="
