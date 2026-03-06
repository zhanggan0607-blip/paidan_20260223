# 脚本管理目录

本目录统一管理项目所有脚本文件，按功能分类组织。

## 目录结构

```
scripts/
├── install/      # 安装相关脚本
├── database/     # 数据库相关脚本
├── deploy/       # 部署相关脚本
├── nginx/        # Nginx 配置脚本
├── check/        # 检查相关脚本
├── monitor/      # 监控相关脚本
├── service/      # 服务管理脚本
└── utils/        # 工具脚本
```

## 各目录说明

### install/ - 安装脚本

| 脚本                     | 说明                   |
| ------------------------ | ---------------------- |
| `install_postgresql.ps1` | 安装 PostgreSQL 数据库 |
| `install_nginx.ps1`      | 安装 Nginx 服务器      |
| `install_venv.ps1`       | 安装 Python 虚拟环境   |
| `setup_postgresql.ps1`   | 配置 PostgreSQL        |

### database/ - 数据库脚本

| 脚本                             | 说明               |
| -------------------------------- | ------------------ |
| `create_db.ps1` / `create_db.sh` | 创建数据库         |
| `create_db2.ps1`                 | 创建数据库（备用） |
| `create_tables.ps1`              | 创建数据表         |
| `init_db.ps1`                    | 初始化数据库       |
| `setup_db_password.ps1`          | 设置数据库密码     |
| `grant_db.sh`                    | 授权数据库访问     |
| `import_db.sh`                   | 导入数据库         |
| `debug_db.sh`                    | 调试数据库         |
| `verify_db.sh`                   | 验证数据库连接     |
| `run_create_db.ps1`              | 执行创建数据库     |
| `run_create_tables.ps1`          | 执行创建表         |
| `fix_db_config.sh`               | 修复数据库配置     |

### deploy/ - 部署脚本

| 脚本                 | 说明               |
| -------------------- | ------------------ |
| `deploy.sh`          | 主部署脚本         |
| `deploy_backend.ps1` | 部署后端服务       |
| `deploy_pc.ps1`      | 部署 PC 端前端     |
| `upload_h5.ps1`      | 上传 H5 移动端文件 |

### nginx/ - Nginx 脚本

| 脚本               | 说明               |
| ------------------ | ------------------ |
| `setup_nginx.ps1`  | 配置 Nginx         |
| `setup_nginx2.ps1` | 配置 Nginx（备用） |
| `update_nginx.ps1` | 更新 Nginx 配置    |

### check/ - 检查脚本

| 脚本                 | 说明             |
| -------------------- | ---------------- |
| `check_backend.ps1`  | 检查后端服务状态 |
| `check_services.ps1` | 检查所有服务状态 |
| `check_nginx.ps1`    | 检查 Nginx 状态  |
| `check_firewall.ps1` | 检查防火墙配置   |
| `check_dirs.ps1`     | 检查目录结构     |
| `check_status.sh`    | 检查服务状态     |
| `check_data.sh`      | 检查数据状态     |

### monitor/ - 监控脚本

| 脚本                    | 说明         |
| ----------------------- | ------------ |
| `analyze_logs.py`       | 分析日志文件 |
| `service_monitor.py`    | 服务监控程序 |
| `setup_monitor_task.py` | 设置监控任务 |

### service/ - 服务管理脚本

| 脚本                    | 说明             |
| ----------------------- | ---------------- |
| `start_backend.ps1`     | 启动后端服务     |
| `restart_backend.sh`    | 重启后端服务     |
| `ensure_backend.sh`     | 确保后端服务运行 |
| `find_pm2.sh`           | 查找 PM2 进程    |
| `start_all_services.py` | 启动所有服务     |
| `stop_all_services.py`  | 停止所有服务     |

### utils/ - 工具脚本

| 脚本              | 说明         |
| ----------------- | ------------ |
| `set_password.sh` | 设置密码     |
| `verify_h5.sh`    | 验证 H5 部署 |
| `qc`              | 快速命令脚本 |

## 使用说明

### Windows 环境

使用 PowerShell 执行 `.ps1` 脚本：

```powershell
# 从项目根目录执行
.\scripts\install\install_postgresql.ps1
.\scripts\database\create_db.ps1
.\scripts\deploy\deploy_backend.ps1
```

### Linux 环境

使用 Bash 执行 `.sh` 脚本：

```bash
# 从项目根目录执行
./scripts/database/create_db.sh
./scripts/deploy/deploy.sh
./scripts/service/restart_backend.sh
```

### Python 脚本

```bash
python scripts/monitor/service_monitor.py
python scripts/service/start_all_services.py
```
