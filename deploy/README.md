# SSTCP 维保系统 - 部署指南

## 服务器信息

| 项目 | 值 |
|------|-----|
| 服务器IP | 8.153.93.123 |
| 域名 | www.sstcp.top |
| 操作系统 | Ubuntu 22.04/20.04 |

---

## 快速部署

### 步骤1: 登录服务器

1. 登录阿里云控制台
2. 进入 ECS 实例列表
3. 点击"远程连接"

### 步骤2: 切换到 root 用户

```bash
sudo su
```

### 步骤3: 下载部署脚本

```bash
cd /tmp
wget https://raw.githubusercontent.com/zhanggan0607-blip/paidan_20260223/master/deploy/deploy-all.sh
```

### 步骤4: 修改配置信息

```bash
nano deploy-all.sh
```

修改以下配置：

```bash
SERVER_IP="8.153.93.123"              # 服务器公网IP
DOMAIN="www.sstcp.top"                # 域名
DB_PASSWORD="你的数据库密码"           # PostgreSQL数据库密码
JWT_SECRET="你的JWT密钥"              # JWT加密密钥(至少32位)
ALIBABA_ACCESS_KEY_ID="你的AccessKeyID"        # 阿里云AccessKey ID
ALIBABA_ACCESS_KEY_SECRET="你的AccessKeySecret"  # 阿里云AccessKey Secret
```

### 步骤5: 执行部署

```bash
chmod +x deploy-all.sh
bash deploy-all.sh
```

---

## 部署后配置

### 1. 配置域名解析

在阿里云控制台 → 域名 → 解析设置：

| 记录类型 | 主机记录 | 记录值 |
|----------|----------|--------|
| A | @ | 8.153.93.123 |
| A | www | 8.153.93.123 |

### 2. 配置安全组

在阿里云控制台 → ECS → 安全组，开放端口：

| 端口 | 协议 | 说明 |
|------|------|------|
| 22 | TCP | SSH |
| 80 | TCP | HTTP |
| 443 | TCP | HTTPS |

### 3. 配置SSL证书

确保域名解析生效后，运行：

```bash
cd /tmp
wget https://raw.githubusercontent.com/zhanggan0607-blip/paidan_20260223/master/deploy/setup-ssl.sh
chmod +x setup-ssl.sh
bash setup-ssl.sh
```

---

## 访问地址

| 服务 | HTTP | HTTPS |
|------|------|-------|
| PC端 | http://8.153.93.123 | https://www.sstcp.top |
| H5端 | http://8.153.93.123/h5 | https://www.sstcp.top/h5 |
| API文档 | http://8.153.93.123/api/docs | https://www.sstcp.top/api/docs |

---

## 常用运维命令

### 服务管理

```bash
# 查看后端状态
pm2 status

# 查看后端日志
pm2 logs sstcp-backend

# 重启后端
pm2 restart sstcp-backend

# 停止后端
pm2 stop sstcp-backend

# 查看Nginx状态
systemctl status nginx

# 重启Nginx
systemctl restart nginx

# 查看PostgreSQL状态
systemctl status postgresql
```

### 更新代码

```bash
cd /var/www/sstcp

# 拉取最新代码
git pull

# 更新PC端
npm install --legacy-peer-deps
npm run build

# 更新H5端
cd H5
npm install --legacy-peer-deps
npm run build

# 重启后端
cd /var/www/sstcp
pm2 restart sstcp-backend
```

### 查看日志

```bash
# 后端日志
tail -f /var/log/sstcp/backend-out.log
tail -f /var/log/sstcp/backend-error.log

# Nginx日志
tail -f /var/log/nginx/access.log
tail -f /var/log/nginx/error.log
```

---

## 故障排查

### 后端无法启动

```bash
# 检查数据库连接
sudo -u postgres psql -d sstcp_maintenance -c "SELECT 1;"

# 检查端口占用
netstat -tlnp | grep 8080

# 手动启动测试
cd /var/www/sstcp/backend-python
source venv/bin/activate
uvicorn app.main:app --host 0.0.0.0 --port 8080
```

### Nginx 502 错误

```bash
# 检查后端是否运行
pm2 status

# 检查Nginx配置
nginx -t

# 查看错误日志
tail -f /var/log/nginx/error.log
```

### 数据库连接失败

```bash
# 检查PostgreSQL状态
systemctl status postgresql

# 检查数据库配置
sudo -u postgres psql -c "\l"

# 重置数据库密码
sudo -u postgres psql -c "ALTER USER sstcp_user WITH PASSWORD '新密码';"
```

---

## 联系支持

如有问题，请查看日志文件或联系技术支持。
