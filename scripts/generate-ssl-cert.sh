#!/bin/bash
set -e

SERVER_IP="${1:-8.153.95.31}"
SERVER_DOMAIN="${2:-paidan.sstcp.top}"
DEPLOY_DIR="${3:-/opt/sstcp/v2.0.0}"
SSL_DIR="${DEPLOY_DIR}/ssl"

echo "=== 生成自签名SSL证书 ==="
echo "服务器IP: ${SERVER_IP}"
echo "服务器域名: ${SERVER_DOMAIN}"
echo "部署目录: ${DEPLOY_DIR}"

mkdir -p "${SSL_DIR}"

if [ -f "${SSL_DIR}/cert.pem" ] && [ -f "${SSL_DIR}/key.pem" ]; then
    echo "SSL证书已存在，跳过生成"
    echo "  证书: ${SSL_DIR}/cert.pem"
    echo "  私钥: ${SSL_DIR}/key.pem"
    echo "如需重新生成，请先删除现有证书文件"
    exit 0
fi

openssl req -x509 -nodes -days 3650 \
    -newkey rsa:2048 \
    -keyout "${SSL_DIR}/key.pem" \
    -out "${SSL_DIR}/cert.pem" \
    -subj "/CN=${SERVER_DOMAIN}" \
    -addext "subjectAltName=IP:${SERVER_IP},DNS:${SERVER_DOMAIN},DNS:www.${SERVER_DOMAIN},DNS:localhost" \
    -addext "basicConstraints=CA:FALSE" \
    -addext "keyUsage=digitalSignature,keyEncipherment" \
    -addext "extendedKeyUsage=serverAuth"

chmod 644 "${SSL_DIR}/cert.pem"
chmod 600 "${SSL_DIR}/key.pem"

echo ""
echo "=== SSL证书生成完成 ==="
echo "  证书: ${SSL_DIR}/cert.pem"
echo "  私钥: ${SSL_DIR}/key.pem"
echo "  有效期: 10年"
echo "  适用IP: ${SERVER_IP}"
echo "  适用域名: ${SERVER_DOMAIN}, www.${SERVER_DOMAIN}"
echo ""
echo "注意: 自签名证书浏览器会显示安全警告，但不影响加密传输"
echo "      如需正式证书，请使用Let's Encrypt(需要域名)或购买商业证书"
