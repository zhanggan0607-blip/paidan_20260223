#!/bin/bash

#===========================================
# SSTCP 维保系统 - SSL证书配置脚本
# 使用 Let's Encrypt 免费证书
#===========================================

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

DOMAIN="www.sstcp.top"

echo -e "${BLUE}============================================${NC}"
echo -e "${BLUE}    SSL证书配置 - Let's Encrypt${NC}"
echo -e "${BLUE}============================================${NC}"

# 安装 Certbot
echo -e "${GREEN}[1/3] 安装 Certbot...${NC}"
apt install -y certbot python3-certbot-nginx

# 申请证书
echo -e "${GREEN}[2/3] 申请SSL证书...${NC}"
echo -e "${YELLOW}请确保域名已解析到服务器IP${NC}"
certbot --nginx -d $DOMAIN -d sstcp.top --non-interactive --agree-tos --email admin@sstcp.top --redirect

# 设置自动续期
echo -e "${GREEN}[3/3] 配置自动续期...${NC}"
systemctl enable certbot.timer
systemctl start certbot.timer

# 重启Nginx
systemctl restart nginx

echo ""
echo -e "${GREEN}============================================${NC}"
echo -e "${GREEN}    SSL证书配置完成！${NC}"
echo -e "${GREEN}============================================${NC}"
echo ""
echo -e "${YELLOW}HTTPS访问地址:${NC}"
echo "  PC端:  https://${DOMAIN}"
echo "  H5端:  https://${DOMAIN}/h5"
echo ""
echo -e "${YELLOW}证书自动续期已配置，有效期90天${NC}"
