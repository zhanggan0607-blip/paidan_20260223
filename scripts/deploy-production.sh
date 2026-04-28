#!/bin/bash

set -e

echo "🚀 开始部署到生产环境..."

PRODUCTION_HOST="8.153.95.31"
PRODUCTION_USER="root"
DEPLOY_PATH="/opt/sstcp"

echo "📥 拉取最新代码..."
ssh ${PRODUCTION_USER}@${PRODUCTION_HOST} << EOF
  cd ${DEPLOY_PATH}
  git pull origin main
EOF

echo "📦 拉取最新镜像..."
ssh ${PRODUCTION_USER}@${PRODUCTION_HOST} << EOF
  cd ${DEPLOY_PATH}
  docker-compose pull
EOF

echo "🗄️ 执行数据库迁移..."
ssh ${PRODUCTION_USER}@${PRODUCTION_HOST} << EOF
  cd ${DEPLOY_PATH}
  docker-compose run --rm backend alembic upgrade head
EOF

echo "🔄 重启服务..."
ssh ${PRODUCTION_USER}@${PRODUCTION_HOST} << EOF
  cd ${DEPLOY_PATH}
  docker-compose down
  docker-compose up -d
EOF

echo "🧹 清理旧镜像..."
ssh ${PRODUCTION_USER}@${PRODUCTION_HOST} << EOF
  docker system prune -f
EOF

echo "🏥 健康检查..."
sleep 30
if curl -f http://${PRODUCTION_HOST}/api/v1/health; then
  echo "✅ 部署成功！"
else
  echo "❌ 部署失败！"
  exit 1
fi

echo "🎉 生产环境部署完成！"
