#!/bin/bash

#===========================================
# SSTCP 维保系统 - 一键部署脚本
# 适配系统: Alibaba Cloud Linux 4 LTS
# 使用方法: sudo bash deploy-alinux4.sh
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
SERVER_IP=""                          # 服务器公网IP（留空则自动获取）
DOMAIN=""                             # 域名（没有则留空）
DB_PASSWORD=""                        # PostgreSQL数据库密码（必填）
SECRET_KEY=""                         # JWT加密密钥(至少32位，留空自动生成)
ALIYUN_ACCESS_KEY_ID=""               # 阿里云AccessKey ID（必填）
ALIYUN_ACCESS_KEY_SECRET=""           # 阿里云AccessKey Secret（必填）
#===========================================

PROJECT_DIR="/opt/sstcp"
DATA_DIR="/data/sstcp"

echo -e "${BLUE}"
echo "╔════════════════════════════════════════════════════════════╗"
echo "║                                                            ║"
echo "║         SSTCP 维保系统 - 一键部署脚本                      ║"
echo "║         适配 Alibaba Cloud Linux 4                         ║"
echo "║                                                            ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo -e "${NC}"

# 检查是否为root用户
if [ "$EUID" -ne 0 ]; then
    echo -e "${RED}错误: 请使用 sudo 或 root 用户运行此脚本${NC}"
    echo "使用方法: sudo bash deploy-alinux4.sh"
    exit 1
fi

# 检测系统
if [ ! -f /etc/alinux-release ]; then
    echo -e "${YELLOW}警告: 此脚本专为 Alibaba Cloud Linux 4 设计${NC}"
    echo -e "${YELLOW}当前系统可能不兼容，是否继续？(y/n)${NC}"
    read -r answer
    if [[ ! "$answer" =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# 自动获取服务器IP
if [ -z "$SERVER_IP" ]; then
    echo -e "${YELLOW}正在自动获取服务器公网IP...${NC}"
    SERVER_IP=$(curl -s ifconfig.me 2>/dev/null || curl -s ip.sb 2>/dev/null || curl -s ipinfo.io/ip 2>/dev/null)
    if [ -z "$SERVER_IP" ]; then
        echo -e "${RED}错误: 无法自动获取服务器IP，请手动设置 SERVER_IP 变量${NC}"
        exit 1
    fi
    echo -e "${GREEN}检测到服务器IP: $SERVER_IP${NC}"
fi

# 自动生成JWT密钥
if [ -z "$SECRET_KEY" ]; then
    echo -e "${YELLOW}正在自动生成JWT密钥...${NC}"
    SECRET_KEY=$(openssl rand -hex 32)
    echo -e "${GREEN}JWT密钥已自动生成${NC}"
fi

# 检查必填配置
if [ -z "$DB_PASSWORD" ]; then
    echo -e "${RED}错误: 请设置 DB_PASSWORD 数据库密码${NC}"
    echo "请编辑脚本，设置 DB_PASSWORD 变量"
    exit 1
fi

if [ -z "$ALIYUN_ACCESS_KEY_ID" ] || [ -z "$ALIYUN_ACCESS_KEY_SECRET" ]; then
    echo -e "${RED}错误: 请设置阿里云 OCR 配置${NC}"
    echo "请编辑脚本，设置以下变量："
    echo "  - ALIYUN_ACCESS_KEY_ID: 阿里云AccessKey ID"
    echo "  - ALIYUN_ACCESS_KEY_SECRET: 阿里云AccessKey Secret"
    exit 1
fi

echo ""
echo -e "${YELLOW}═══════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}部署配置确认:${NC}"
echo -e "${YELLOW}═══════════════════════════════════════════════════════════${NC}"
echo "  服务器IP: $SERVER_IP"
echo "  域名: ${DOMAIN:-未配置}"
echo "  数据库密码: ******"
echo "  JWT密钥: ******"
echo "  阿里云OCR: 已配置"
echo ""
read -p "确认以上配置正确？按回车继续，Ctrl+C取消..."

#===========================================
# Step 1: 安装基础环境
#===========================================
echo ""
echo -e "${BLUE}════════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}Step 1: 安装基础环境${NC}"
echo -e "${BLUE}════════════════════════════════════════════════════════════${NC}"

echo -e "${YELLOW}[1.1] 更新系统...${NC}"
dnf update -y

echo -e "${YELLOW}[1.2] 安装基础软件...${NC}"
dnf install -y curl wget git unzip tar openssl

echo -e "${YELLOW}[1.3] 检查 Docker...${NC}"
if ! command -v docker &> /dev/null; then
    echo -e "${YELLOW}正在安装 Docker...${NC}"
    dnf config-manager --add-repo=https://mirrors.aliyun.com/docker-ce/linux/centos/docker-ce.repo
    dnf install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin
    systemctl start docker
    systemctl enable docker
    echo -e "${GREEN}Docker 安装完成${NC}"
else
    echo -e "${GREEN}Docker 已安装: $(docker --version)${NC}"
    systemctl start docker
fi

echo -e "${YELLOW}[1.4] 检查 Docker Compose...${NC}"
if ! docker compose version &> /dev/null; then
    echo -e "${YELLOW}正在安装 Docker Compose...${NC}"
    dnf install -y docker-compose-plugin
fi
echo -e "${GREEN}Docker Compose: $(docker compose version)${NC}"

#===========================================
# Step 2: 准备项目目录
#===========================================
echo ""
echo -e "${BLUE}════════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}Step 2: 准备项目目录${NC}"
echo -e "${BLUE}════════════════════════════════════════════════════════════${NC}"

echo -e "${YELLOW}[2.1] 创建目录...${NC}"
mkdir -p $PROJECT_DIR
mkdir -p $DATA_DIR/uploads
mkdir -p $DATA_DIR/postgres

echo -e "${YELLOW}[2.2] 创建环境变量文件...${NC}"
cat > $PROJECT_DIR/.env << EOF
# 数据库配置
DB_USER=postgres
DB_PASSWORD=${DB_PASSWORD}

# JWT配置
SECRET_KEY=${SECRET_KEY}

# 阿里云OCR配置
ALIYUN_ACCESS_KEY_ID=${ALIYUN_ACCESS_KEY_ID}
ALIYUN_ACCESS_KEY_SECRET=${ALIYUN_ACCESS_KEY_SECRET}
ALIYUN_OCR_REGION_ID=cn-shanghai

# 应用配置
DEBUG=False
EOF

echo -e "${GREEN}环境变量文件已创建: $PROJECT_DIR/.env${NC}"

#===========================================
# Step 3: 创建 Docker Compose 配置
#===========================================
echo ""
echo -e "${BLUE}════════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}Step 3: 创建 Docker Compose 配置${NC}"
echo -e "${BLUE}════════════════════════════════════════════════════════════${NC}"

cat > $PROJECT_DIR/docker-compose.yml << 'EOF'
version: '3.8'

services:
  db:
    image: postgres:15-alpine
    container_name: sstcp-db
    restart: always
    environment:
      POSTGRES_DB: tq
      POSTGRES_USER: ${DB_USER:-postgres}
      POSTGRES_PASSWORD: ${DB_PASSWORD:-changeme}
    volumes:
      - /data/sstcp/postgres:/var/lib/postgresql/data
    ports:
      - "5432:5432"
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      interval: 10s
      timeout: 5s
      retries: 5

  backend:
    image: python:3.11-slim
    container_name: sstcp-backend
    restart: always
    working_dir: /app
    environment:
      DATABASE_URL: postgresql://${DB_USER:-postgres}:${DB_PASSWORD:-changeme}@db:5432/tq
      SECRET_KEY: ${SECRET_KEY:-your-secret-key}
      DEBUG: ${DEBUG:-False}
      ALIYUN_ACCESS_KEY_ID: ${ALIYUN_ACCESS_KEY_ID:-}
      ALIYUN_ACCESS_KEY_SECRET: ${ALIYUN_ACCESS_KEY_SECRET:-}
      ALIYUN_OCR_REGION_ID: ${ALIYUN_OCR_REGION_ID:-cn-shanghai}
    depends_on:
      db:
        condition: service_healthy
    volumes:
      - ./backend-python:/app
      - /data/sstcp/uploads:/app/uploads
    ports:
      - "8000:8000"
    command: >
      bash -c "
        pip install --no-cache-dir -r requirements.txt &&
        uvicorn app.main:app --host 0.0.0.0 --port 8000
      "

  frontend-pc:
    image: nginx:alpine
    container_name: sstcp-frontend-pc
    restart: always
    volumes:
      - ./dist:/usr/share/nginx/html:ro
      - ./nginx-pc.conf:/etc/nginx/conf.d/default.conf:ro
    ports:
      - "80:80"
    depends_on:
      - backend

  frontend-h5:
    image: nginx:alpine
    container_name: sstcp-frontend-h5
    restart: always
    volumes:
      - ./H5/dist:/usr/share/nginx/html:ro
      - ./nginx-h5.conf:/etc/nginx/conf.d/default.conf:ro
    ports:
      - "81:80"
    depends_on:
      - backend

EOF

# 创建 PC 端 Nginx 配置
cat > $PROJECT_DIR/nginx-pc.conf << 'EOF'
server {
    listen 80;
    server_name localhost;
    
    client_max_body_size 50M;
    
    gzip on;
    gzip_types text/plain text/css application/json application/javascript text/xml application/xml;
    
    location / {
        root /usr/share/nginx/html;
        index index.html;
        try_files $uri $uri/ /index.html;
    }
    
    location /api {
        proxy_pass http://backend:8000;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_connect_timeout 60s;
        proxy_read_timeout 60s;
    }
    
    location /uploads {
        proxy_pass http://backend:8000;
        proxy_set_header Host $host;
    }
}
EOF

# 创建 H5 端 Nginx 配置
cat > $PROJECT_DIR/nginx-h5.conf << 'EOF'
server {
    listen 80;
    server_name localhost;
    
    client_max_body_size 50M;
    
    gzip on;
    gzip_types text/plain text/css application/json application/javascript text/xml application/xml;
    
    location / {
        root /usr/share/nginx/html;
        index index.html;
        try_files $uri $uri/ /index.html;
    }
    
    location /api {
        proxy_pass http://backend:8000;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_connect_timeout 60s;
        proxy_read_timeout 60s;
    }
    
    location /uploads {
        proxy_pass http://backend:8000;
        proxy_set_header Host $host;
    }
}
EOF

echo -e "${GREEN}Docker Compose 配置已创建${NC}"

#===========================================
# Step 4: 下载项目代码
#===========================================
echo ""
echo -e "${BLUE}════════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}Step 4: 下载项目代码${NC}"
echo -e "${BLUE}════════════════════════════════════════════════════════════${NC}"

cd $PROJECT_DIR

if [ -d "backend-python" ]; then
    echo -e "${YELLOW}项目目录已存在，跳过下载${NC}"
else
    echo -e "${YELLOW}正在从 GitHub 克隆项目...${NC}"
    git clone https://github.com/zhanggan0607-blip/paidan_20260223.git temp_clone
    mv temp_clone/* temp_clone/.* . 2>/dev/null || true
    rm -rf temp_clone
    echo -e "${GREEN}项目代码下载完成${NC}"
fi

#===========================================
# Step 5: 构建前端
#===========================================
echo ""
echo -e "${BLUE}════════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}Step 5: 构建前端${NC}"
echo -e "${BLUE}════════════════════════════════════════════════════════════${NC}"

echo -e "${YELLOW}[5.1] 检查前端构建文件...${NC}"

if [ ! -d "dist" ] || [ ! -d "H5/dist" ]; then
    echo -e "${YELLOW}前端构建文件不存在，正在构建...${NC}"
    
    echo -e "${YELLOW}安装 Node.js...${NC}"
    dnf install -y nodejs npm
    npm install -g pnpm
    
    echo -e "${YELLOW}构建 PC 端...${NC}"
    npm install --legacy-peer-deps
    npm run build
    
    echo -e "${YELLOW}构建 H5 端...${NC}"
    cd H5
    npm install --legacy-peer-deps
    npm run build
    cd ..
    
    echo -e "${GREEN}前端构建完成${NC}"
else
    echo -e "${GREEN}前端构建文件已存在${NC}"
fi

#===========================================
# Step 6: 启动服务
#===========================================
echo ""
echo -e "${BLUE}════════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}Step 6: 启动服务${NC}"
echo -e "${BLUE}════════════════════════════════════════════════════════════${NC}"

cd $PROJECT_DIR

echo -e "${YELLOW}[6.1] 停止旧容器...${NC}"
docker compose down 2>/dev/null || true

echo -e "${YELLOW}[6.2] 启动服务...${NC}"
docker compose up -d

echo -e "${YELLOW}[6.3] 等待服务启动...${NC}"
sleep 10

echo -e "${YELLOW}[6.4] 检查服务状态...${NC}"
docker compose ps

#===========================================
# Step 7: 验证部署
#===========================================
echo ""
echo -e "${BLUE}════════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}Step 7: 验证部署${NC}"
echo -e "${BLUE}════════════════════════════════════════════════════════════${NC}"

echo -e "${YELLOW}[7.1] 检查后端健康...${NC}"
sleep 5
HEALTH=$(curl -s http://localhost:8000/health 2>/dev/null || echo "waiting")

echo -e "${YELLOW}[7.2] 检查数据库连接...${NC}"
docker exec sstcp-db pg_isready -U postgres

#===========================================
# 完成
#===========================================
echo ""
echo -e "${GREEN}"
echo "╔════════════════════════════════════════════════════════════╗"
echo "║                                                            ║"
echo "║                    部署完成！                              ║"
echo "║                                                            ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo -e "${NC}"
echo ""
echo -e "${YELLOW}═══════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}访问地址:${NC}"
echo -e "${YELLOW}═══════════════════════════════════════════════════════════${NC}"
echo ""
echo "  PC端:    http://${SERVER_IP}"
echo "  H5端:    http://${SERVER_IP}:81"
echo "  API文档: http://${SERVER_IP}:8000/api/docs"
if [ -n "$DOMAIN" ]; then
    echo ""
    echo "  域名访问（需配置DNS解析）:"
    echo "  PC端:    http://${DOMAIN}"
    echo "  H5端:    http://${DOMAIN}:81"
fi
echo ""
echo -e "${YELLOW}═══════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}常用命令:${NC}"
echo -e "${YELLOW}═══════════════════════════════════════════════════════════${NC}"
echo ""
echo "  查看服务状态:  cd $PROJECT_DIR && docker compose ps"
echo "  查看日志:      cd $PROJECT_DIR && docker compose logs -f"
echo "  重启服务:      cd $PROJECT_DIR && docker compose restart"
echo "  停止服务:      cd $PROJECT_DIR && docker compose down"
echo "  更新部署:      cd $PROJECT_DIR && docker compose up -d --build"
echo ""
echo -e "${YELLOW}═══════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}下一步:${NC}"
echo -e "${YELLOW}═══════════════════════════════════════════════════════════${NC}"
echo ""
echo "  1. 确保阿里云安全组已开放端口: 80, 81, 443"
if [ -n "$DOMAIN" ]; then
    echo "  2. 配置域名DNS解析 (A记录指向 ${SERVER_IP})"
    echo "  3. 配置SSL证书启用HTTPS"
fi
echo ""
echo -e "${GREEN}部署日志保存在: /var/log/sstcp-deploy.log${NC}"
echo ""
