#!/bin/bash

#===========================================
# SSTCP 维保系统 - 一键完整部署脚本
# 服务器: Ubuntu 22.04/20.04
# 使用方法: sudo bash deploy-all.sh
#===========================================

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

#===========================================
# 请修改以下配置信息
#===========================================
SERVER_IP="8.153.93.123"              # 服务器公网IP
DOMAIN="www.sstcp.top"                # 域名
DB_PASSWORD="YOUR_DB_PASSWORD"        # PostgreSQL数据库密码
JWT_SECRET="YOUR_JWT_SECRET"          # JWT加密密钥(至少32位)
ALIBABA_ACCESS_KEY_ID="YOUR_ACCESS_KEY_ID"        # 阿里云AccessKey ID
ALIBABA_ACCESS_KEY_SECRET="YOUR_ACCESS_KEY_SECRET"  # 阿里云AccessKey Secret
#===========================================

PROJECT_DIR="/var/www/sstcp"
BACKEND_DIR="$PROJECT_DIR/backend-python"

echo -e "${BLUE}"
echo "╔════════════════════════════════════════════════════════════╗"
echo "║                                                            ║"
echo "║         SSTCP 维保系统 - 一键部署脚本                      ║"
echo "║                                                            ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo -e "${NC}"

# 检查是否为root用户
if [ "$EUID" -ne 0 ]; then
    echo -e "${RED}错误: 请使用 sudo 运行此脚本${NC}"
    echo "使用方法: sudo bash deploy-all.sh"
    exit 1
fi

# 检查配置
if [[ "$ALIBABA_ACCESS_KEY_ID" == "YOUR_ACCESS_KEY_ID" ]] || [[ "$ALIBABA_ACCESS_KEY_SECRET" == "YOUR_ACCESS_KEY_SECRET" ]]; then
    echo -e "${RED}错误: 请先修改脚本中的配置信息！${NC}"
    echo "请编辑脚本，设置以下变量："
    echo "  - DB_PASSWORD: PostgreSQL数据库密码"
    echo "  - JWT_SECRET: JWT加密密钥"
    echo "  - ALIBABA_ACCESS_KEY_ID: 阿里云AccessKey ID"
    echo "  - ALIBABA_ACCESS_KEY_SECRET: 阿里云AccessKey Secret"
    exit 1
fi

echo -e "${YELLOW}部署配置:${NC}"
echo "  服务器IP: $SERVER_IP"
echo "  域名: $DOMAIN"
echo ""

read -p "确认以上配置正确？按回车继续..."

#===========================================
# Step 1: 安装基础环境
#===========================================
echo ""
echo -e "${BLUE}════════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}Step 1: 安装基础环境${NC}"
echo -e "${BLUE}════════════════════════════════════════════════════════════${NC}"

echo -e "${YELLOW}[1.1] 更新系统...${NC}"
apt update && apt upgrade -y

echo -e "${YELLOW}[1.2] 安装基础软件...${NC}"
apt install -y curl wget git unzip software-properties-common apt-transport-https ca-certificates

echo -e "${YELLOW}[1.3] 安装 Node.js 18...${NC}"
if ! command -v node &> /dev/null; then
    curl -fsSL https://deb.nodesource.com/setup_18.x | bash -
    apt install -y nodejs
fi
echo "  Node.js: $(node -v)"
echo "  npm: $(npm -v)"

echo -e "${YELLOW}[1.4] 安装 Python 3...${NC}"
apt install -y python3 python3-pip python3-venv
echo "  Python: $(python3 --version)"

echo -e "${YELLOW}[1.5] 安装 PostgreSQL...${NC}"
if ! command -v psql &> /dev/null; then
    apt install -y postgresql postgresql-contrib
fi
systemctl start postgresql
systemctl enable postgresql

echo -e "${YELLOW}[1.6] 配置 PostgreSQL 数据库...${NC}"
sudo -u postgres psql -c "CREATE DATABASE sstcp_maintenance;" 2>/dev/null || echo "  数据库已存在"
sudo -u postgres psql -c "CREATE USER sstcp_user WITH ENCRYPTED PASSWORD '$DB_PASSWORD';" 2>/dev/null || echo "  用户已存在"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE sstcp_maintenance TO sstcp_user;" 2>/dev/null || true
sudo -u postgres psql -d sstcp_maintenance -c "GRANT ALL ON SCHEMA public TO sstcp_user;" 2>/dev/null || true
sudo -u postgres psql -d sstcp_maintenance -c "ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO sstcp_user;" 2>/dev/null || true

echo -e "${YELLOW}[1.7] 安装 Nginx...${NC}"
if ! command -v nginx &> /dev/null; then
    apt install -y nginx
fi
systemctl start nginx
systemctl enable nginx

echo -e "${YELLOW}[1.8] 安装 Tesseract OCR...${NC}"
apt install -y tesseract-ocr tesseract-ocr-chi-sim

echo -e "${YELLOW}[1.9] 安装 PM2...${NC}"
npm install -g pm2

#===========================================
# Step 2: 部署项目
#===========================================
echo ""
echo -e "${BLUE}════════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}Step 2: 部署项目${NC}"
echo -e "${BLUE}════════════════════════════════════════════════════════════${NC}"

echo -e "${YELLOW}[2.1] 创建项目目录...${NC}"
mkdir -p $PROJECT_DIR
mkdir -p /var/log/sstcp
chown -R www-data:www-data /var/log/sstcp

echo -e "${YELLOW}[2.2] 克隆项目代码...${NC}"
cd /var/www
if [ -d "sstcp" ]; then
    echo "  项目目录已存在，更新代码..."
    cd sstcp
    git fetch --all
    git reset --hard origin/master
else
    git clone https://github.com/zhanggan0607-blip/paidan_20260223.git sstcp
    cd sstcp
fi

echo -e "${YELLOW}[2.3] 配置后端环境...${NC}"
cd $BACKEND_DIR

if [ ! -d "venv" ]; then
    python3 -m venv venv
fi

source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

cat > .env << EOF
DATABASE_URL=postgresql://sstcp_user:${DB_PASSWORD}@localhost:5432/sstcp_maintenance
SECRET_KEY=${JWT_SECRET}
ALIBABA_ACCESS_KEY_ID=${ALIBABA_ACCESS_KEY_ID}
ALIBABA_ACCESS_KEY_SECRET=${ALIBABA_ACCESS_KEY_SECRET}
CORS_ORIGINS=["http://${SERVER_IP}","http://${DOMAIN}","https://${DOMAIN}"]
APP_NAME=SSTCP维保系统
APP_VERSION=1.0.0
EOF

echo -e "${YELLOW}[2.4] 构建 PC 端前端...${NC}"
cd $PROJECT_DIR
npm install --legacy-peer-deps
npm run build

echo -e "${YELLOW}[2.5] 构建 H5 端前端...${NC}"
cd $PROJECT_DIR/H5
npm install --legacy-peer-deps
npm run build

#===========================================
# Step 3: 配置服务
#===========================================
echo ""
echo -e "${BLUE}════════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}Step 3: 配置服务${NC}"
echo -e "${BLUE}════════════════════════════════════════════════════════════${NC}"

echo -e "${YELLOW}[3.1] 配置 PM2...${NC}"
cd $PROJECT_DIR

cat > ecosystem.config.js << 'EOFPM2'
module.exports = {
  apps: [
    {
      name: 'sstcp-backend',
      cwd: '/var/www/sstcp/backend-python',
      script: '/var/www/sstcp/backend-python/venv/bin/uvicorn',
      args: 'app.main:app --host 0.0.0.0 --port 8080',
      interpreter: 'none',
      env: {
        NODE_ENV: 'production'
      },
      autorestart: true,
      watch: false,
      max_memory_restart: '500M',
      error_file: '/var/log/sstcp/backend-error.log',
      out_file: '/var/log/sstcp/backend-out.log',
      log_date_format: 'YYYY-MM-DD HH:mm:ss',
      merge_logs: true
    }
  ]
}
EOFPM2

echo -e "${YELLOW}[3.2] 配置 Nginx...${NC}"

cat > /etc/nginx/sites-available/sstcp << EOFNGINX
upstream backend {
    server 127.0.0.1:8080;
}

server {
    listen 80;
    server_name ${SERVER_IP} ${DOMAIN} sstcp.top;
    
    client_max_body_size 50M;
    
    # Gzip 压缩
    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_proxied any;
    gzip_types text/plain text/css text/xml text/javascript application/javascript application/json application/xml;
    
    # 安全头
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    
    # PC端前端
    location / {
        root /var/www/sstcp/dist;
        index index.html;
        try_files \$uri \$uri/ /index.html;
    }
    
    # H5移动端
    location /h5 {
        alias /var/www/sstcp/H5/dist;
        index index.html;
        try_files \$uri \$uri/ /h5/index.html;
    }
    
    # API 代理
    location /api {
        proxy_pass http://backend;
        proxy_http_version 1.1;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_connect_timeout 60s;
        proxy_read_timeout 60s;
        proxy_buffering off;
    }
    
    # 上传文件代理
    location /uploads {
        proxy_pass http://backend;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
    }
    
    # 健康检查
    location /health {
        proxy_pass http://backend;
        proxy_set_header Host \$host;
    }
    
    # 静态资源缓存
    location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg|woff|woff2|ttf|eot)$ {
        root /var/www/sstcp/dist;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }
    
    # 禁止访问隐藏文件
    location ~ /\. {
        deny all;
    }
}
EOFNGINX

ln -sf /etc/nginx/sites-available/sstcp /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default

nginx -t

#===========================================
# Step 4: 启动服务
#===========================================
echo ""
echo -e "${BLUE}════════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}Step 4: 启动服务${NC}"
echo -e "${BLUE}════════════════════════════════════════════════════════════${NC}"

echo -e "${YELLOW}[4.1] 重启 Nginx...${NC}"
systemctl restart nginx

echo -e "${YELLOW}[4.2] 启动后端服务...${NC}"
cd $PROJECT_DIR
pm2 delete sstcp-backend 2>/dev/null || true
pm2 start ecosystem.config.js
pm2 save

# 设置 PM2 开机自启
echo -e "${YELLOW}[4.3] 配置开机自启...${NC}"
pm2 startup systemd -u root --hp /root 2>/dev/null || true

#===========================================
# 完成
#===========================================
echo ""
echo -e "${GREEN}"
echo "╔════════════════════════════════════════════════════════════╗"
echo "║                                                            ║"
echo "║              部署完成！                                    ║"
echo "║                                                            ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo -e "${NC}"
echo ""
echo -e "${YELLOW}访问地址:${NC}"
echo "  PC端:  http://${SERVER_IP}  或  http://${DOMAIN}"
echo "  H5端:  http://${SERVER_IP}/h5  或  http://${DOMAIN}/h5"
echo "  API文档: http://${SERVER_IP}/api/docs"
echo ""
echo -e "${YELLOW}常用命令:${NC}"
echo "  查看后端状态: pm2 status"
echo "  查看后端日志: pm2 logs sstcp-backend"
echo "  重启后端: pm2 restart sstcp-backend"
echo "  查看Nginx状态: systemctl status nginx"
echo ""
echo -e "${YELLOW}下一步:${NC}"
echo "  1. 在阿里云控制台配置域名解析 (A记录指向 ${SERVER_IP})"
echo "  2. 配置SSL证书启用HTTPS"
echo "  3. 配置阿里云安全组开放 80 和 443 端口"
echo ""
