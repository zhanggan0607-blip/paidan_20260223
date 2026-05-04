# 构建配置优化建议

## 📊 当前状态分析

### Docker Compose 文件问题

**发现重复文件：**
- `docker-compose.server.yml` - 使用镜像 `sstcp-backend:v1.0.1`
- `docker-compose-server.yml` - 使用镜像 `sstcp-paidan260120-backend:latest`

**问题：**
1. 两个文件功能相似，容易混淆
2. 使用不同的镜像命名规范
3. 数据库配置不一致

**建议：**
- ✅ 保留 `docker-compose-server.yml` 作为生产环境配置
- ✅ 删除 `docker-compose.server.yml`（重复文件）
- ✅ 统一镜像命名规范：`sstcp-{service}:latest`

---

### .dockerignore 优化

**当前配置：**
```
node_modules
dist
.git
.gitignore
*.md
.env.local
.env.*.local
*.log
.vscode
.idea
*.tar
*.zip
__pycache__
*.pyc
.pytest_cache
.coverage
htmlcov
.tox
.hypothesis
*.egg-info
.eggs
*.egg
.venv
venv
ENV
env
.trash
```

**建议添加：**
```
# 测试文件
**/*.test.ts
**/*.test.js
**/*.spec.ts
**/*.spec.js
**/tests/**
**/__tests__/**

# 文档
docs/
*.md
!README.md

# CI/CD
.github/
.gitlab-ci.yml
.travis.yml

# 开发工具
.eslintrc.*
.prettierrc*
tsconfig*.json
vite.config.*

# 临时文件
*.tmp
*.temp
.DS_Store
Thumbs.db

# 构建产物
build/
coverage/
.nyc_output/

# 其他
.dockerignore
Dockerfile*
docker-compose*.yml
```

---

### Vite 配置优化

#### PC 前端 (vite.config.ts)

**当前配置优点：**
- ✅ 已配置代码分割
- ✅ 已配置 gzip 压缩
- ✅ 已配置路径别名

**建议优化：**
```typescript
build: {
  outDir: 'dist',
  sourcemap: false,
  chunkSizeWarningLimit: 1000,
  minify: 'terser',
  terserOptions: {
    compress: {
      drop_console: true,
      drop_debugger: true,
      pure_funcs: ['console.log', 'console.info', 'console.debug']
    }
  },
  rollupOptions: {
    output: {
      manualChunks: {
        'vue-vendor': ['vue', 'vue-router'],
        'element-plus': ['element-plus', '@element-plus/icons-vue'],
        'axios': ['axios']
      },
      chunkFileNames: 'assets/js/[name]-[hash].js',
      entryFileNames: 'assets/js/[name]-[hash].js',
      assetFileNames: 'assets/[ext]/[name]-[hash].[ext]'
    }
  }
}
```

#### H5 前端 (H5/vite.config.ts)

**当前配置优点：**
- ✅ 已配置 terser 压缩
- ✅ 已配置自动清理 console.log
- ✅ 已配置代码分割
- ✅ 已配置自动导入

**无需修改** - 配置已经很完善

---

### Dockerfile 优化

#### PC 前端 Dockerfile

**当前配置优点：**
- ✅ 使用多阶段构建
- ✅ 使用 Alpine 基础镜像

**建议优化：**
```dockerfile
FROM node:20.11-alpine3.19 AS builder

WORKDIR /app

# 先复制依赖文件，利用 Docker 缓存
COPY packages/shared/package.json ./packages/shared/
COPY package.json ./

# 安装共享包依赖
WORKDIR /app/packages/shared
RUN npm install --only=production

# 安装主应用依赖
WORKDIR /app
RUN npm install --only=production

# 复制源代码
COPY packages/shared ./packages/shared
COPY . .

# 构建
RUN npm run build

# 生产阶段
FROM nginx:1.25-alpine3.18

# 添加标签
LABEL maintainer="SSTCP Team"
LABEL version="1.0"
LABEL description="SSTCP PC Frontend"

# 复制构建产物
COPY --from=builder /app/dist /usr/share/nginx/html

# 复制 nginx 配置
COPY docker/nginx-pc.conf /etc/nginx/nginx.conf

# 健康检查
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD wget --quiet --tries=1 --spider http://localhost/ || exit 1

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
```

#### 后端 Dockerfile

**当前配置优点：**
- ✅ 使用 Python slim 镜像
- ✅ 使用清华镜像源加速

**建议优化：**
```dockerfile
FROM python:3.11-slim-bookworm AS builder

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV TZ=Asia/Shanghai

# 安装构建依赖
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# 复制依赖文件
COPY requirements.txt .

# 安装 Python 依赖
RUN pip install --no-cache-dir -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

# 生产阶段
FROM python:3.11-slim-bookworm

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV TZ=Asia/Shanghai

# 只安装运行时依赖
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    curl \
    && rm -rf /var/lib/apt/lists/*

# 从构建阶段复制 Python 包
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# 复制应用代码
COPY . .

# 创建上传目录
RUN mkdir -p /app/uploads

# 添加标签
LABEL maintainer="SSTCP Team"
LABEL version="1.0"
LABEL description="SSTCP Backend API"

# 健康检查
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
  CMD curl -f http://localhost:8000/api/v1/health || exit 1

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

---

## 📋 优化清单

### 立即执行（高优先级）

1. ✅ 删除重复的 `docker-compose.server.yml`
2. ✅ 优化 `.dockerignore` 配置
3. ✅ 为 PC 前端添加 terser 压缩配置
4. ✅ 为 Dockerfile 添加健康检查

### 短期优化（中优先级）

1. 统一 Docker Compose 配置
2. 优化 Dockerfile 多阶段构建
3. 添加构建缓存优化
4. 标准化环境变量配置

### 长期优化（低优先级）

1. 实现 CI/CD 自动构建
2. 添加镜像安全扫描
3. 优化镜像大小
4. 实现多架构构建

---

## 📈 预期效果

### 构建时间优化
- Docker 缓存优化：减少 30-50% 构建时间
- 多阶段构建：减小镜像体积 40-60%

### 代码质量提升
- 自动清理 console.log：生产环境更干净
- 代码分割：优化加载性能

### 运维效率提升
- 健康检查：快速发现问题
- 统一配置：减少配置错误
- 标准化部署：提升部署效率

---

## 🎯 下一步行动

1. 执行立即优化项
2. 测试构建流程
3. 验证生产环境部署
4. 更新部署文档
