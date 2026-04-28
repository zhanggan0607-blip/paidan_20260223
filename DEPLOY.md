# SSTCP 项目 Docker 部署指南

## 部署包内容

- `deploy.zip` (215.94 MB) - 包含所有必要的Docker镜像和配置文件

## 部署步骤

### 步骤1: 上传部署包到服务器

使用以下任一方法上传 `deploy.zip` 到服务器:

#### 方法A: 使用WinSCP (推荐)
1. 打开 WinSCP
2. 连接服务器:
   - 主机: `8.153.95.31`
   - 用户名: `root`
   - 密码: `<SERVER_PASSWORD>`
3. 上传 `deploy.zip` 到 `/opt/sstcp/` 目录

#### 方法B: 使用scp命令
```bash
scp deploy.zip root@8.153.95.31:/opt/sstcp/
```

### 步骤2: SSH登录服务器并解压

```bash
ssh root@8.153.95.31
# 密码: <SERVER_PASSWORD>

cd /opt/sstcp
unzip -o deploy.zip
```

### 步骤3: 加载Docker镜像

```bash
docker load -i sstcp-backend.tar
docker load -i sstcp-frontend-pc.tar
docker load -i sstcp-frontend-h5.tar
```

### 步骤4: 拉取nginx镜像

```bash
docker pull nginx:1.25-alpine3.18
```

### 步骤5: 停止旧容器并清理

```bash
docker-compose down --remove-orphans
docker image prune -f
```

### 步骤6: 启动服务

```bash
docker-compose up -d
```

### 步骤7: 检查服务状态

```bash
docker-compose ps
```

### 步骤8: 清理临时文件

```bash
rm -f *.tar deploy.zip
```

## 一键部署脚本

或者使用一键部署脚本:

```bash
cd /opt/sstcp
chmod +x docker/deploy-server.sh
./docker/deploy-server.sh
```

## 访问地址

部署完成后，可以通过以下地址访问:

- **PC端**: http://8.153.95.31
- **H5端**: http://8.153.95.31/h5/
- **API文档**: http://8.153.95.31/api/docs
- **健康检查**: http://8.153.95.31/api/v1/health

## 数据库配置

服务已配置连接到测试数据库:
- 主机: `host.docker.internal:5432` (容器内访问宿主机)
- 数据库: `sstcp_test`
- 用户名: `sstcp_user`
- 密码: `Sstcp@2026`

## 环境变量

如需修改环境变量,编辑 `docker-compose.yml` 文件:

```yaml
environment:
  - SECRET_KEY=your-secret-key
  - DATABASE_URL=postgresql://user:password@host:5432/dbname
  - CORS_ORIGINS=http://your-domain.com
```

## 故障排查

