#!/bin/bash

set -e

echo "=========================================="
echo "    SSTCP 维保系统部署脚本"
echo "=========================================="

echo ""
echo "[1/6] 安装Docker..."
if ! command -v docker &> /dev/null; then
    apt update
    apt install -y docker.io docker-compose
    systemctl start docker
    systemctl enable docker
    echo "Docker安装完成"
else
    echo "Docker已安装"
fi

echo ""
echo "[2/6] 创建项目目录..."
mkdir -p /opt/sstcp
cd /opt/sstcp
echo "项目目录: /opt/sstcp"

echo ""
echo "[3/6] 设置环境变量..."
if [ ! -f .env ]; then
    cat > .env << 'EOF'
DB_USER=postgres
DB_PASSWORD=sstcp2024secret
SECRET_KEY=sstcp-secret-key-change-in-production-2024
DEBUG=False
ALIYUN_ACCESS_KEY_ID=
ALIYUN_ACCESS_KEY_SECRET=
ALIYUN_OCR_REGION_ID=cn-shanghai
EOF
    echo ".env文件已创建"
else
    echo ".env文件已存在"
fi

echo ""
echo "[4/6] 构建Docker镜像..."
docker-compose build --no-cache

echo ""
echo "[5/6] 启动Docker容器..."
docker-compose up -d

echo ""
echo "[6/6] 等待服务启动并初始化数据..."
sleep 15

echo ""
echo "正在初始化数据库数据..."
docker exec -i sstcp-db psql -U postgres -d tq < /opt/sstcp/backend-python/init_data.sql 2>/dev/null || echo "数据可能已存在，跳过初始化"

echo ""
echo "=========================================="
echo "    部署完成!"
echo "=========================================="
echo ""
echo "访问地址:"
echo "  PC端: http://你的服务器IP/"
echo "  H5端: http://你的服务器IP:81/"
echo "  API:  http://你的服务器IP/api/v1/"
echo ""
echo "数据库信息:"
echo "  主机: localhost:5432"
echo "  数据库: tq"
echo "  用户名: postgres"
echo "  密码: sstcp2024secret"
echo ""
echo "默认账户信息:"
echo "  管理员 - 用户名: 管理员, 密码: 000001"
echo "  部门经理 - 用户名: 部门经理, 密码: 000002"
echo "  运维员1 - 用户名: 运维员1, 密码: 000003"
echo "  运维员2 - 用户名: 运维员2, 密码: 000004"
echo "  材料员 - 用户名: 材料员, 密码: 000005"
echo ""
echo "常用命令:"
echo "  查看日志: docker-compose logs -f"
echo "  重启服务: docker-compose restart"
echo "  停止服务: docker-compose down"
echo ""
