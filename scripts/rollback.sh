#!/bin/bash

set -e

if [ -z "$1" ]; then
  echo "用法: ./rollback.sh <version>"
  echo "示例: ./rollback.sh v1.0.3"
  exit 1
fi

VERSION=$1
PRODUCTION_HOST="8.153.95.31"
PRODUCTION_USER="root"
DEPLOY_PATH="/opt/sstcp"

echo "🔄 开始回滚到版本 ${VERSION}..."

ssh ${PRODUCTION_USER}@${PRODUCTION_HOST} << EOF
  cd ${DEPLOY_PATH}

  sed -i "s/sstcp-frontend-pc:.*$/sstcp-frontend-pc:${VERSION}/g" docker-compose.yml
  sed -i "s/sstcp-frontend-h5:.*$/sstcp-frontend-h5:${VERSION}/g" docker-compose.yml
  sed -i "s/sstcp-backend:.*$/sstcp-backend:${VERSION}/g" docker-compose.yml

  docker-compose down
  docker-compose up -d
EOF

echo "🏥 健康检查..."
sleep 30
if curl -f http://${PRODUCTION_HOST}/api/v1/health; then
  echo "✅ 回滚成功！"
else
  echo "❌ 回滚失败！"
  exit 1
fi

echo "🎉 回滚完成！"
