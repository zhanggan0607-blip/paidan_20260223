# 数据库配置指南

## 问题说明

当前后端服务无法启动，原因是数据库连接失败。错误信息：
```
sqlalchemy.exc.OperationalError: (psycopg2.OperationalError)
```

## 解决方案

### 方案 1：使用 PostgreSQL（推荐用于生产环境）

1. **确认 PostgreSQL 服务运行**
   - 检查 PostgreSQL 服务是否已启动
   - 确认端口号（默认是 5432）

2. **更新 `.env` 文件**
   
   打开 `backend-python/.env` 文件，修改第 7 行：
   ```env
   # 修改前
   DATABASE_URL=postgresql://postgres:your_password@localhost:5432/tq
   
   # 修改后（替换为实际值）
   DATABASE_URL=postgresql://postgres:您的密码@localhost:5432/tq
   ```

3. **参数说明**
   - `postgres`：数据库用户名
   - `您的密码`：替换为真实的数据库密码
   - `localhost`：数据库主机地址（如果是远程数据库，替换为实际 IP）
   - `5432`：数据库端口
   - `tq`：数据库名称

4. **重启后端服务**
   - 保存 `.env` 文件后，服务会自动重新加载
   - 或者手动重启：`Ctrl+C` 停止，然后重新运行启动命令

### 方案 2：使用 SQLite（推荐用于开发环境）

如果您想快速启动项目进行测试，可以使用 SQLite（无需额外配置）：

1. **备份当前配置**
   ```bash
   cd backend-python
   cp .env .env.postgresql.backup
   ```

2. **使用 SQLite 配置**
   
   方法 1：复制 SQLite 配置文件
   ```bash
   cp .env.sqlite .env
   ```
   
   方法 2：手动修改 `.env` 文件
   ```env
   DATABASE_URL=sqlite:///./sstcp_maintenance.db
   ```

3. **重启后端服务**

### 方案 3：使用 MySQL（如果您有 MySQL 数据库）

1. **确认 MySQL 服务运行**

2. **更新 `.env` 文件**
   ```env
   DATABASE_URL=mysql+pymysql://root:您的密码@localhost:3306/sstcp_maintenance
   ```

3. **参数说明**
   - `root`：数据库用户名
   - `您的密码`：替换为真实的数据库密码
   - `localhost`：数据库主机地址
   - `3306`：MySQL 默认端口
   - `sstcp_maintenance`：数据库名称

## 验证配置

配置完成后，检查后端服务是否正常启动：

1. **查看终端输出**
   - 应该看到类似以下的成功信息：
   ```
   INFO:     Application startup complete.
   INFO:     Uvicorn running on http://0.0.0.0:8080
   ```

2. **测试 API**
   - 打开浏览器访问：http://localhost:8080/docs
   - 应该能看到 API 文档页面

3. **测试健康检查**
   - 访问：http://localhost:8080/health
   - 应该返回：`{"status": "healthy"}`

## 常见问题

### Q: PostgreSQL 端口不是 5432？
A: 修改 `.env` 文件中的端口号为实际端口。

### Q: 数据库用户名不是 postgres？
A: 修改 `.env` 文件中的用户名为实际用户名。

### Q: 数据库名称不是 tq？
A: 修改 `.env` 文件中的数据库名称为实际名称。

### Q: 如何创建 PostgreSQL 数据库？
A: 使用以下命令创建数据库：
```bash
# 连接到 PostgreSQL
psql -U postgres

# 创建数据库
CREATE DATABASE tq;

# 创建用户（如果需要）
CREATE USER your_user WITH PASSWORD 'your_password';

# 授权
GRANT ALL PRIVILEGES ON DATABASE tq TO your_user;
```

### Q: 如何创建 MySQL 数据库？
A: 使用以下命令创建数据库：
```bash
# 连接到 MySQL
mysql -u root -p

# 创建数据库
CREATE DATABASE sstcp_maintenance;

# 创建用户（如果需要）
CREATE USER 'your_user'@'localhost' IDENTIFIED BY 'your_password';

# 授权
GRANT ALL PRIVILEGES ON sstcp_maintenance.* TO 'your_user'@'localhost';
FLUSH PRIVILEGES;
```

## 快速启动（使用 SQLite）

如果您只是想快速测试项目，直接执行：

```bash
cd backend-python
cp .env.sqlite .env
python -m uvicorn app.main:app --host 0.0.0.0 --port 8080 --reload
```

这样无需配置数据库即可启动项目！
