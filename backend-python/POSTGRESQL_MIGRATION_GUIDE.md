# MySQL 到 PostgreSQL 迁移指南

本文档详细说明如何将 SSTCP 维护系统从 MySQL 数据库迁移到 PostgreSQL 数据库。

## 目录

1. [前置条件](#前置条件)
2. [安装 PostgreSQL](#安装-postgresql)
3. [配置 PostgreSQL 数据库](#配置-postgresql-数据库)
4. [安装 Python 依赖](#安装-python-依赖)
5. [执行数据迁移](#执行数据迁移)
6. [验证迁移结果](#验证迁移结果)
7. [切换到 PostgreSQL](#切换到-postgresql)
8. [回滚方案](#回滚方案)
9. [常见问题](#常见问题)

---

## 前置条件

在开始迁移之前，请确保：

- ✅ 已安装 Python 3.8+
- ✅ 当前系统运行 MySQL 数据库（包含现有数据）
- ✅ 有足够的磁盘空间（至少是当前 MySQL 数据库大小的 3 倍）
- ✅ 备份了 MySQL 数据库
- ✅ 停止了应用程序的写入操作（避免数据不一致）

---

## 安装 PostgreSQL

### Windows 系统

1. **下载 PostgreSQL 安装程序**

   访问 [PostgreSQL 官方网站](https://www.postgresql.org/download/windows/) 下载最新版本的安装程序。

2. **运行安装程序**

   - 双击下载的安装程序
   - 选择安装路径（默认：`C:\Program Files\PostgreSQL\16`）
   - 设置超级用户密码（建议：`postgres`）
   - 选择端口（默认：`5432`）
   - 选择区域设置（建议：`Chinese, Simplified, China`）
   - 完成安装

3. **验证安装**

   打开命令提示符或 PowerShell，运行：

   ```bash
   psql --version
   ```

   应该显示 PostgreSQL 版本信息。

4. **添加到系统 PATH**

   如果 `psql` 命令不可用，将 PostgreSQL 的 `bin` 目录添加到系统 PATH：
   - `C:\Program Files\PostgreSQL\16\bin`

### Linux 系统

```bash
sudo apt update
sudo apt install postgresql postgresql-contrib
sudo systemctl start postgresql
sudo systemctl enable postgresql
```

### macOS 系统

```bash
brew install postgresql
brew services start postgresql
```

---

## 配置 PostgreSQL 数据库

### 1. 连接到 PostgreSQL

```bash
psql -U postgres
```

输入安装时设置的密码。

### 2. 创建数据库

```sql
CREATE DATABASE sstcp_maintenance;
```

### 3. 创建专用用户（可选但推荐）

```sql
CREATE USER sstcp_user WITH PASSWORD 'your_secure_password';
GRANT ALL PRIVILEGES ON DATABASE sstcp_maintenance TO sstcp_user;
```

### 4. 验证数据库创建

```sql
\l
```

应该能看到 `sstcp_maintenance` 数据库。

### 5. 退出 PostgreSQL

```sql
\q
```

---

## 安装 Python 依赖

### 1. 安装 PostgreSQL Python 驱动

在 `backend-python` 目录下运行：

```bash
cd backend-python
pip install psycopg2-binary==2.9.9
```

或者更新所有依赖：

```bash
pip install -r requirements.txt
```

### 2. 验证安装

```bash
python -c "import psycopg2; print(psycopg2.__version__)"
```

应该显示 psycopg2 版本信息。

---

## 执行数据迁移

### 1. 备份 MySQL 数据（重要！）

```bash
mysqldump -u root -p sstcp_maintenance > mysql_backup_$(date +%Y%m%d_%H%M%S).sql
```

### 2. 配置迁移脚本

编辑 `scripts/migrate_to_postgresql.py`，修改数据库连接信息：

```python
mysql_url = "mysql+pymysql://root:your_mysql_password@localhost:3306/sstcp_maintenance"
postgres_url = "postgresql://postgres:your_postgres_password@localhost:5432/sstcp_maintenance"
```

### 3. 运行迁移脚本

```bash
cd backend-python
python scripts/migrate_to_postgresql.py
```

### 4. 迁移过程

迁移脚本会执行以下步骤：

1. 连接到 MySQL 和 PostgreSQL 数据库
2. 在 PostgreSQL 中创建表结构
3. 从 MySQL 读取数据并写入 PostgreSQL
4. 验证数据完整性
5. 关闭数据库连接

### 5. 预期输出

```
============================================================
MySQL 到 PostgreSQL 数据迁移工具
============================================================
MySQL连接: mysql+pymysql://root:root@localhost:3306/sstcp_maintenance
PostgreSQL连接: postgresql://postgres:postgres@localhost:5432/sstcp_maintenance
============================================================
连接到MySQL数据库...
连接到PostgreSQL数据库...
数据库连接成功!
在PostgreSQL中创建表结构...
表结构创建成功!
开始迁移project_info表数据...
从MySQL读取到 100 条记录
已迁移 100/100 条记录
project_info表迁移完成! 共迁移 100 条记录
验证数据迁移...
MySQL记录数: 100
PostgreSQL记录数: 100
数据验证通过! 记录数一致
============================================================
数据迁移成功完成!
============================================================
```

---

## 验证迁移结果

### 1. 检查 PostgreSQL 数据

```bash
psql -U postgres -d sstcp_maintenance -c "SELECT COUNT(*) FROM project_info;"
```

### 2. 检查表结构

```bash
psql -U postgres -d sstcp_maintenance -c "\d project_info"
```

### 3. 检查数据完整性

```bash
psql -U postgres -d sstcp_maintenance -c "SELECT * FROM project_info LIMIT 5;"
```

### 4. 对比 MySQL 和 PostgreSQL 数据

```bash
# MySQL
mysql -u root -p -e "SELECT COUNT(*) FROM sstcp_maintenance.project_info;"

# PostgreSQL
psql -U postgres -d sstcp_maintenance -c "SELECT COUNT(*) FROM project_info;"
```

---

## 切换到 PostgreSQL

### 1. 更新环境配置

有两种方式：

#### 方式一：修改 .env 文件

编辑 `.env` 文件：

```env
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/sstcp_maintenance
```

#### 方式二：使用 PostgreSQL 配置文件

```bash
cp .env.postgresql .env
```

### 2. 重启后端服务

```bash
cd backend-python
uvicorn app.main:app --reload --host 0.0.0.0 --port 8080
```

### 3. 验证应用功能

- 访问 API 文档：http://localhost:8080/docs
- 测试 CRUD 操作
- 检查数据读写是否正常

---

## 回滚方案

如果迁移后出现问题，可以回滚到 MySQL：

### 1. 停止应用

```bash
Ctrl+C
```

### 2. 恢复 MySQL 配置

编辑 `.env` 文件：

```env
DATABASE_URL=mysql+pymysql://root:root@localhost:3306/sstcp_maintenance
```

### 3. 重启应用

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8080
```

### 4. 从备份恢复 MySQL 数据（如果需要）

```bash
mysql -u root -p sstcp_maintenance < mysql_backup_YYYYMMDD_HHMMSS.sql
```

---

## 常见问题

### Q1: 连接 PostgreSQL 时提示 "connection refused"

**原因**: PostgreSQL 服务未启动或端口配置错误。

**解决方案**:
```bash
# Windows
net start postgresql-x64-16

# Linux
sudo systemctl start postgresql

# macOS
brew services start postgresql
```

### Q2: 迁移脚本提示 "authentication failed"

**原因**: 数据库密码错误。

**解决方案**:
- 检查 `migrate_to_postgresql.py` 中的数据库连接字符串
- 确认 PostgreSQL 用户密码正确

### Q3: 数据迁移后记录数不一致

**原因**: 迁移过程中有数据写入或删除。

**解决方案**:
- 确保迁移期间停止应用写入操作
- 重新执行迁移脚本

### Q4: psycopg2 安装失败

**原因**: 缺少系统依赖。

**解决方案**:

**Windows**: 使用预编译的二进制包
```bash
pip install psycopg2-binary
```

**Linux**:
```bash
sudo apt install libpq-dev
pip install psycopg2-binary
```

**macOS**:
```bash
brew install postgresql
pip install psycopg2-binary
```

### Q5: 应用启动后连接数据库失败

**原因**: 数据库 URL 配置错误或数据库未创建。

**解决方案**:
- 检查 `.env` 文件中的 `DATABASE_URL`
- 确认 PostgreSQL 数据库已创建
- 检查 PostgreSQL 服务是否运行

---

## 性能优化建议

迁移到 PostgreSQL 后，可以考虑以下优化：

### 1. 创建索引

```sql
CREATE INDEX idx_project_info_project_id ON project_info(project_id);
CREATE INDEX idx_project_info_client_name ON project_info(client_name);
CREATE INDEX idx_project_info_project_name ON project_info(project_name);
```

### 2. 配置连接池

在 `app/database.py` 中调整连接池参数：

```python
engine = create_engine(
    settings.database_url,
    echo=settings.debug,
    pool_pre_ping=True,
    pool_recycle=3600,
    pool_size=10,
    max_overflow=20,
)
```

### 3. 启用查询缓存

在 PostgreSQL 配置文件中启用：

```ini
shared_buffers = 256MB
effective_cache_size = 1GB
```

---

## 技术支持

如果在迁移过程中遇到问题，请：

1. 检查日志文件
2. 查看错误信息
3. 参考本文档的常见问题部分
4. 联系技术支持团队

---

## 附录

### A. 数据库连接字符串格式

**MySQL**:
```
mysql+pymysql://username:password@host:port/database
```

**PostgreSQL**:
```
postgresql://username:password@host:port/database
```

### B. 有用的 PostgreSQL 命令

```bash
# 连接到数据库
psql -U username -d database

# 列出所有数据库
\l

# 列出所有表
\dt

# 查看表结构
\d table_name

# 执行 SQL 文件
\i filename.sql

# 退出
\q
```

### C. 迁移检查清单

- [ ] 已安装 PostgreSQL
- [ ] 已创建数据库和用户
- [ ] 已备份 MySQL 数据
- [ ] 已安装 Python 依赖
- [ ] 已配置迁移脚本
- [ ] 已执行数据迁移
- [ ] 已验证数据完整性
- [ ] 已更新应用配置
- [ ] 已重启应用
- [ ] 已验证应用功能

---

**文档版本**: 1.0.0
**最后更新**: 2026-01-26
**维护者**: SSTCP 技术团队