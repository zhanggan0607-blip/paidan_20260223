# Dockerfile 多阶段构建优化方案

## 📊 优化概览

本文档提供了 PC 前端、H5 前端和后端的 Dockerfile 多阶段构建优化方案，旨在减小镜像体积、提升构建效率。

---

## 🎯 优化目标

| 目标 | 当前 | 优化后 | 提升 |
|------|------|--------|------|
| PC 前端镜像大小 | ~200MB | ~50MB | 75% ↓ |
| H5 前端镜像大小 | ~180MB | ~45MB | 75% ↓ |
| 后端镜像大小 | ~500MB | ~150MB | 70% ↓ |
| 构建时间 | ~5分钟 | ~3分钟 | 40% ↓ |

---

## 📦 PC 前端 Dockerfile 优化

### 当前 Dockerfile 问题
- ❌ 未使用多阶段构建
- ❌ 包含不必要的构建工具
- ❌ 未优化层缓存

### 优化后的 Dockerfile

```dockerfile
# ==================== 构建阶段 ====================
FROM node:20.11-alpine3.19 AS builder

WORKDIR /app

# 设置环境变量
ENV NODE_ENV=production
ENV VITE_BUILD_MODE=production

# 先复制依赖文件，利用 Docker 缓存
COPY packages/shared/package.json ./packages/shared/
COPY package.json package-lock.json ./

# 安装共享包依赖
WORKDIR /app/packages/shared
RUN npm ci --only=production

# 安装主应用依赖
WORKDIR /app
RUN npm ci --only=production

# 复制源代码
COPY packages/shared ./packages/shared
COPY . .

# 构建
RUN npm run build

# ==================== 生产阶段 ====================
FROM nginx:1.25-alpine3.18

# 添加标签
LABEL maintainer="SSTCP Team"
LABEL version="1.0"
LABEL description="SSTCP PC Frontend"

# 安装 curl 用于健康检查
RUN apk add --no-cache curl

# 复制构建产物
COPY --from=builder /app/dist /usr/share/nginx/html

# 复制 nginx 配置
COPY docker/nginx-pc.conf /etc/nginx/nginx.conf

# 健康检查
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD curl -f http://localhost/ || exit 1

# 暴露端口
EXPOSE 80

# 启动 nginx
CMD ["nginx", "-g", "daemon off;"]
```

### 优化要点
1. ✅ 使用多阶段构建，分离构建和运行环境
2. ✅ 利用 Docker 缓存，先复制依赖文件
3. ✅ 使用 Alpine 基础镜像，减小体积
4. ✅ 添加健康检查
5. ✅ 添加标签信息

---

## 📱 H5 前端 Dockerfile 优化

### 当前 Dockerfile 问题
- ❌ 未使用多阶段构建
- ❌ 包含不必要的构建工具
- ❌ 未优化层缓存

### 优化后的 Dockerfile

```dockerfile
# ==================== 构建阶段 ====================
FROM node:20.11-alpine3.19 AS builder

WORKDIR /app

# 设置环境变量
ENV NODE_ENV=production
ENV VITE_BUILD_MODE=production

# 先复制依赖文件，利用 Docker 缓存
COPY packages/shared/package.json ./packages/shared/
COPY H5/package.json H5/package-lock.json ./H5/

# 安装共享包依赖
WORKDIR /app/packages/shared
RUN npm ci --only=production

# 安装 H5 应用依赖
WORKDIR /app/H5
RUN npm ci --only=production

# 复制源代码
COPY packages/shared ../packages/shared
COPY H5 .

# 构建
RUN npm run build

# ==================== 生产阶段 ====================
FROM nginx:1.25-alpine3.18

# 添加标签
LABEL maintainer="SSTCP Team"
LABEL version="1.0"
LABEL description="SSTCP H5 Frontend"

# 安装 curl 用于健康检查
RUN apk add --no-cache curl

# 复制构建产物
COPY --from=builder /app/H5/dist /usr/share/nginx/html

# 复制 nginx 配置
COPY H5/docker/nginx-h5.conf /etc/nginx/nginx.conf

# 健康检查
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD curl -f http://localhost/ || exit 1

# 暴露端口
EXPOSE 80

# 启动 nginx
CMD ["nginx", "-g", "daemon off;"]
```

---

## 🐍 后端 Dockerfile 优化

### 当前 Dockerfile 问题
- ❌ 未使用多阶段构建
- ❌ 包含构建工具（gcc 等）
- ❌ 未优化 Python 包安装

### 优化后的 Dockerfile

```dockerfile
# ==================== 构建阶段 ====================
FROM python:3.11-slim-bookworm AS builder

WORKDIR /app

# 设置环境变量
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

# ==================== 生产阶段 ====================
FROM python:3.11-slim-bookworm

WORKDIR /app

# 设置环境变量
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

# 暴露端口
EXPOSE 8000

# 启动应用
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### 优化要点
1. ✅ 使用多阶段构建，分离构建和运行环境
2. ✅ 只保留运行时依赖，移除构建工具
3. ✅ 使用 slim 基础镜像
4. ✅ 添加健康检查
5. ✅ 使用清华镜像源加速

---

## 🔧 构建优化建议

### 1. 使用 .dockerignore

确保 `.dockerignore` 文件配置正确，排除不必要的文件：

```
node_modules
dist
.git
*.md
.env.local
*.log
.vscode
.idea
__pycache__
*.pyc
.pytest_cache
.coverage
```

### 2. 利用构建缓存

- 将不经常变化的层放在前面（如依赖安装）
- 将经常变化的层放在后面（如源代码）

### 3. 使用多阶段构建

- 构建阶段：包含构建工具和依赖
- 生产阶段：只包含运行时必需的文件

### 4. 优化基础镜像

- 使用 Alpine 或 slim 镜像
- 定期更新基础镜像版本

---

## 📊 预期效果

### 镜像大小对比

| 服务 | 当前大小 | 优化后大小 | 减少 |
|------|----------|------------|------|
| PC 前端 | ~200MB | ~50MB | 150MB |
| H5 前端 | ~180MB | ~45MB | 135MB |
| 后端 | ~500MB | ~150MB | 350MB |
| **总计** | **~880MB** | **~245MB** | **635MB** |

### 构建时间对比

| 服务 | 当前时间 | 优化后时间 | 减少 |
|------|----------|------------|------|
| PC 前端 | ~2分钟 | ~1分钟 | 1分钟 |
| H5 前端 | ~1.5分钟 | ~45秒 | 45秒 |
| 后端 | ~1.5分钟 | ~1分钟 | 30秒 |
| **总计** | **~5分钟** | **~2.75分钟** | **2.25分钟** |

---

## 🚀 实施步骤

### 第一步：备份现有 Dockerfile
```bash
cp Dockerfile Dockerfile.backup
cp H5/Dockerfile H5/Dockerfile.backup
cp backend-python/Dockerfile backend-python/Dockerfile.backup
```

### 第二步：更新 Dockerfile
将优化后的 Dockerfile 内容复制到相应文件中。

### 第三步：构建测试
```bash
# PC 前端
docker build -t sstcp-pc:test .

# H5 前端
docker build -t sstcp-h5:test H5/

# 后端
docker build -t sstcp-backend:test backend-python/
```

### 第四步：验证功能
```bash
# 运行容器并测试
docker run -d -p 8080:80 sstcp-pc:test
docker run -d -p 8081:80 sstcp-h5:test
docker run -d -p 8000:8000 sstcp-backend:test
```

### 第五步：检查镜像大小
```bash
docker images | grep sstcp
```

---

## ⚠️ 注意事项

1. **测试充分**：在生产环境使用前，充分测试所有功能
2. **备份数据**：确保重要数据已备份
3. **逐步实施**：建议先在测试环境验证，再应用到生产环境
4. **监控性能**：部署后监控应用性能和资源使用情况

---

## 📋 检查清单

- [ ] 备份现有 Dockerfile
- [ ] 更新 PC 前端 Dockerfile
- [ ] 更新 H5 前端 Dockerfile
- [ ] 更新后端 Dockerfile
- [ ] 构建测试镜像
- [ ] 验证功能正常
- [ ] 检查镜像大小
- [ ] 更新部署文档
- [ ] 通知团队成员

---

## 🎯 总结

通过实施多阶段构建优化，可以显著减小镜像体积和提升构建效率。建议按照上述步骤逐步实施，并在测试环境充分验证后再应用到生产环境。
