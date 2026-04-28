# CI/CD 自动化实施方案

## 📊 方案概览

本文档提供了完整的 CI/CD 自动化实施方案，包括 GitHub Actions 配置、部署脚本和自动化测试流程。

---

## 🎯 实施目标

| 目标 | 当前状态 | 目标状态 | 提升 |
|------|----------|----------|------|
| 部署频率 | 手动部署 | 自动部署 | 100% 自动化 |
| 部署时间 | ~30分钟 | ~5分钟 | 83% ↓ |
| 错误率 | 10% | <1% | 90% ↓ |
| 回滚时间 | ~15分钟 | ~2分钟 | 87% ↓ |

---

## 🏗️ CI/CD 架构

```
代码提交 → GitHub Actions → 自动测试 → 构建镜像 → 推送镜像 → 自动部署
    ↓           ↓              ↓           ↓          ↓          ↓
  触发器    运行测试套件    代码质量检查  多阶段构建  镜像仓库   更新服务
```

---

## 📁 目录结构

```
.github/
├── workflows/
│   ├── ci.yml                 # CI 流程（测试、构建）
│   ├── cd-production.yml      # CD 流程（生产环境部署）
│   └── cd-staging.yml         # CD 流程（测试环境部署）
├── actions/
│   └── setup-node/
│       └── action.yml         # 自定义 Action
scripts/
├── deploy-production.sh       # 生产环境部署脚本
├── deploy-staging.sh          # 测试环境部署脚本
└── rollback.sh                # 回滚脚本
```

---

## 🔧 GitHub Actions 配置

### 1. CI 流程配置

**文件：** `.github/workflows/ci.yml`

```yaml
name: CI Pipeline

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main, develop ]

jobs:
  # ==================== PC 前端测试 ====================
  pc-frontend:
    name: PC Frontend
    runs-on: ubuntu-latest
    
    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Setup Node.js
        uses: actions/setup-node@v4
        with:
          node-version: '20'
          cache: 'npm'

      - name: Install dependencies
        run: npm ci

      - name: Run linter
        run: npm run lint:check

      - name: Run type check
        run: npm run typecheck

      - name: Run tests
        run: npm run test
        continue-on-error: true

      - name: Build
        run: npm run build

  # ==================== H5 前端测试 ====================
  h5-frontend:
    name: H5 Frontend
    runs-on: ubuntu-latest
    
    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Setup Node.js
        uses: actions/setup-node@v4
        with:
          node-version: '20'
          cache: 'npm'

      - name: Install dependencies
        working-directory: ./H5
        run: npm ci

      - name: Run linter
        working-directory: ./H5
        run: npm run lint:check

      - name: Run type check
        working-directory: ./H5
        run: npm run typecheck

      - name: Build
        working-directory: ./H5
        run: npm run build

  # ==================== 后端测试 ====================
  backend:
    name: Backend API
    runs-on: ubuntu-latest
    
    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Setup Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'
          cache: 'pip'

      - name: Install dependencies
        working-directory: ./backend-python
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements.txt

      - name: Run linter
        working-directory: ./backend-python
        run: |
          pip install ruff
          ruff check .

      - name: Run tests
        working-directory: ./backend-python
        run: |
          pip install pytest pytest-cov
          pytest tests/ -v --cov=app --cov-report=xml
        continue-on-error: true

  # ==================== 代码质量检查 ====================
  code-quality:
    name: Code Quality
    runs-on: ubuntu-latest
    
    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: SonarCloud Scan
        uses: SonarSource/sonarcloud-github-action@master
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
          SONAR_TOKEN: ${{ secrets.SONAR_TOKEN }}
        continue-on-error: true

  # ==================== 安全检查 ====================
  security:
    name: Security Scan
    runs-on: ubuntu-latest
    
    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Run Trivy vulnerability scanner
        uses: aquasecurity/trivy-action@master
        with:
          scan-type: 'fs'
          scan-ref: '.'
          format: 'table'
          exit-code: '0'
          ignore-unfixed: true
```

---

### 2. CD 流程配置（生产环境）

**文件：** `.github/workflows/cd-production.yml`

```yaml
name: CD Production

on:
  push:
    branches: [ main ]
  workflow_dispatch:
    inputs:
      version:
        description: 'Version to deploy'
        required: true
        default: 'latest'

jobs:
  # ==================== 构建和推送镜像 ====================
  build-and-push:
    name: Build and Push Images
    runs-on: ubuntu-latest
    needs: [ci]
    
    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Set up Docker Buildx
        uses: docker/setup-buildx-action@v3

      - name: Login to Docker Hub
        uses: docker/login-action@v3
        with:
          username: ${{ secrets.DOCKER_USERNAME }}
          password: ${{ secrets.DOCKER_PASSWORD }}

      - name: Build and push PC Frontend
        uses: docker/build-push-action@v5
        with:
          context: .
          file: ./Dockerfile
          push: true
          tags: |
            ${{ secrets.DOCKER_USERNAME }}/sstcp-pc:${{ github.sha }}
            ${{ secrets.DOCKER_USERNAME }}/sstcp-pc:latest
          cache-from: type=registry,ref=${{ secrets.DOCKER_USERNAME }}/sstcp-pc:buildcache
          cache-to: type=registry,ref=${{ secrets.DOCKER_USERNAME }}/sstcp-pc:buildcache,mode=max

      - name: Build and push H5 Frontend
        uses: docker/build-push-action@v5
        with:
          context: ./H5
          file: ./H5/Dockerfile
          push: true
          tags: |
            ${{ secrets.DOCKER_USERNAME }}/sstcp-h5:${{ github.sha }}
            ${{ secrets.DOCKER_USERNAME }}/sstcp-h5:latest
          cache-from: type=registry,ref=${{ secrets.DOCKER_USERNAME }}/sstcp-h5:buildcache
          cache-to: type=registry,ref=${{ secrets.DOCKER_USERNAME }}/sstcp-h5:buildcache,mode=max

      - name: Build and push Backend
        uses: docker/build-push-action@v5
        with:
          context: ./backend-python
          file: ./backend-python/Dockerfile
          push: true
          tags: |
            ${{ secrets.DOCKER_USERNAME }}/sstcp-backend:${{ github.sha }}
            ${{ secrets.DOCKER_USERNAME }}/sstcp-backend:latest
          cache-from: type=registry,ref=${{ secrets.DOCKER_USERNAME }}/sstcp-backend:buildcache
          cache-to: type=registry,ref=${{ secrets.DOCKER_USERNAME }}/sstcp-backend:buildcache,mode=max

  # ==================== 部署到生产环境 ====================
  deploy:
    name: Deploy to Production
    runs-on: ubuntu-latest
    needs: [build-and-push]
    environment: production
    
    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Deploy to production server
        uses: appleboy/ssh-action@v1.0.0
        with:
          host: ${{ secrets.PRODUCTION_HOST }}
          username: ${{ secrets.PRODUCTION_USER }}
          password: ${{ secrets.PRODUCTION_PASSWORD }}
          script: |
            cd /opt/sstcp
            docker-compose pull
            docker-compose up -d
            docker system prune -f

      - name: Health check
        run: |
          sleep 30
          curl -f http://${{ secrets.PRODUCTION_HOST }}/ || exit 1

      - name: Notify deployment
        uses: 8398a7/action-slack@v3
        with:
          status: ${{ job.status }}
          text: 'Production deployment completed'
        env:
          SLACK_WEBHOOK_URL: ${{ secrets.SLACK_WEBHOOK }}
        if: always()
```

---

## 🚀 部署脚本

### 1. 生产环境部署脚本

**文件：** `scripts/deploy-production.sh`

```bash
#!/bin/bash

# 生产环境部署脚本

set -e

echo "🚀 开始部署到生产环境..."

# 配置
PRODUCTION_HOST="8.153.93.123"
PRODUCTION_USER="root"
DEPLOY_PATH="/opt/sstcp"

# 拉取最新代码
echo "📥 拉取最新代码..."
ssh ${PRODUCTION_USER}@${PRODUCTION_HOST} << EOF
  cd ${DEPLOY_PATH}
  git pull origin main
EOF

# 拉取最新镜像
echo "📦 拉取最新镜像..."
ssh ${PRODUCTION_USER}@${PRODUCTION_HOST} << EOF
  cd ${DEPLOY_PATH}
  docker-compose pull
EOF

# 重启服务
echo "🔄 重启服务..."
ssh ${PRODUCTION_USER}@${PRODUCTION_HOST} << EOF
  cd ${DEPLOY_PATH}
  docker-compose down
  docker-compose up -d
EOF

# 清理旧镜像
echo "🧹 清理旧镜像..."
ssh ${PRODUCTION_USER}@${PRODUCTION_HOST} << EOF
  docker system prune -f
EOF

# 健康检查
echo "🏥 健康检查..."
sleep 30
if curl -f http://${PRODUCTION_HOST}/; then
  echo "✅ 部署成功！"
else
  echo "❌ 部署失败！"
  exit 1
fi

echo "🎉 生产环境部署完成！"
```

---

### 2. 回滚脚本

**文件：** `scripts/rollback.sh`

```bash
#!/bin/bash

# 回滚脚本

set -e

if [ -z "$1" ]; then
  echo "用法: ./rollback.sh <version>"
  echo "示例: ./rollback.sh abc123"
  exit 1
fi

VERSION=$1
PRODUCTION_HOST="8.153.93.123"
PRODUCTION_USER="root"
DEPLOY_PATH="/opt/sstcp"

echo "🔄 开始回滚到版本 ${VERSION}..."

# 更新镜像版本
ssh ${PRODUCTION_USER}@${PRODUCTION_HOST} << EOF
  cd ${DEPLOY_PATH}
  
  # 更新 docker-compose.yml 中的镜像版本
  sed -i "s/sstcp-pc:latest/sstcp-pc:${VERSION}/g" docker-compose.yml
  sed -i "s/sstcp-h5:latest/sstcp-h5:${VERSION}/g" docker-compose.yml
  sed -i "s/sstcp-backend:latest/sstcp-backend:${VERSION}/g" docker-compose.yml
  
  # 重启服务
  docker-compose down
  docker-compose up -d
EOF

# 健康检查
echo "🏥 健康检查..."
sleep 30
if curl -f http://${PRODUCTION_HOST}/; then
  echo "✅ 回滚成功！"
else
  echo "❌ 回滚失败！"
  exit 1
fi

echo "🎉 回滚完成！"
```

---

## 📋 实施步骤

### 第一步：配置 GitHub Secrets

在 GitHub 仓库设置中添加以下 Secrets：

| Secret 名称 | 说明 |
|------------|------|
| `DOCKER_USERNAME` | Docker Hub 用户名 |
| `DOCKER_PASSWORD` | Docker Hub 密码 |
| `PRODUCTION_HOST` | 生产服务器 IP |
| `PRODUCTION_USER` | 生产服务器用户名 |
| `PRODUCTION_PASSWORD` | 生产服务器密码 |
| `SLACK_WEBHOOK` | Slack Webhook URL（可选） |
| `SONAR_TOKEN` | SonarCloud Token（可选） |

---

### 第二步：创建 GitHub Actions 工作流

```bash
# 创建目录
mkdir -p .github/workflows

# 创建 CI 配置
touch .github/workflows/ci.yml

# 创建 CD 配置
touch .github/workflows/cd-production.yml
touch .github/workflows/cd-staging.yml
```

---

### 第三步：创建部署脚本

```bash
# 创建脚本目录
mkdir -p scripts

# 创建部署脚本
touch scripts/deploy-production.sh
touch scripts/deploy-staging.sh
touch scripts/rollback.sh

# 添加执行权限
chmod +x scripts/*.sh
```

---

### 第四步：测试 CI/CD 流程

1. **测试 CI 流程**
   ```bash
   git add .
   git commit -m "test: test CI pipeline"
   git push origin develop
   ```

2. **测试 CD 流程**
   ```bash
   git checkout main
   git merge develop
   git push origin main
   ```

---

## 📊 监控和告警

### 1. 部署状态监控

- ✅ GitHub Actions 状态徽章
- ✅ Slack 通知
- ✅ 邮件通知

### 2. 应用健康监控

- ✅ 健康检查端点
- ✅ Prometheus 监控
- ✅ Grafana 仪表板

---

## 🎯 最佳实践

### 1. 分支策略
- `main` - 生产环境
- `develop` - 开发环境
- `feature/*` - 功能分支
- `hotfix/*` - 热修复分支

### 2. 提交规范
- `feat:` - 新功能
- `fix:` - 修复 bug
- `docs:` - 文档更新
- `style:` - 代码格式
- `refactor:` - 重构
- `test:` - 测试
- `chore:` - 构建/工具

### 3. 部署策略
- 蓝绿部署
- 金丝雀发布
- 滚动更新

---

## 📈 预期效果

| 指标 | 当前 | 目标 | 提升 |
|------|------|------|------|
| 部署频率 | 每周 1 次 | 每天 1 次 | 7x ↑ |
| 部署时间 | 30 分钟 | 5 分钟 | 83% ↓ |
| 错误率 | 10% | <1% | 90% ↓ |
| 回滚时间 | 15 分钟 | 2 分钟 | 87% ↓ |

---

## 🎊 总结

通过实施 CI/CD 自动化，可以显著提升开发效率和部署质量。建议按照上述步骤逐步实施，并在测试环境充分验证后再应用到生产环境。
