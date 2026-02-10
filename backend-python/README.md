# SSTCP Maintenance System Backend - Python

基于 FastAPI 的工程维保管理系统后端服务。

## 技术栈

- **Web 框架**: FastAPI 0.109.0
- **ORM**: SQLAlchemy 2.0.25
- **数据库**: MySQL 8.0
- **数据验证**: Pydantic 2.5.3
- **ASGI 服务器**: Uvicorn 0.27.0
- **数据库迁移**: Alembic 1.13.1
- **API 文档**: FastAPI 自动生成 (Swagger UI / ReDoc)

## 项目结构

```
backend-python/
├── app/
│   ├── api/
│   │   └── v1/
│   │       └── project_info.py      # API 路由层
│   ├── models/
│   │   └── project_info.py          # 数据模型
│   ├── schemas/
│   │   └── project_info.py          # Pydantic 模型（DTO）
│   ├── repositories/
│   │   └── project_info.py          # 数据访问层
│   ├── services/
│   │   └── project_info.py          # 业务逻辑层
│   ├── config.py                    # 配置管理
│   ├── database.py                  # 数据库连接
│   └── main.py                     # 应用入口
├── tests/                          # 测试目录
├── alembic/                        # 数据库迁移
├── pyproject.toml                  # Poetry 依赖管理
├── requirements.txt                 # Pip 依赖管理
└── README.md                       # 项目文档
```

## 快速开始

### 环境要求

- Python 3.11+
- MySQL 8.0+

### 安装依赖

使用 Poetry（推荐）：

```bash
cd backend-python
poetry install
```

或使用 pip：

```bash
pip install -r requirements.txt
```

### 配置数据库

创建 `.env` 文件：

```env
DATABASE_URL=mysql+pymysql://root:password@localhost:3306/sstcp_maintenance
DEBUG=True
```

### 运行应用

开发模式：

```bash
poetry run uvicorn app.main:app --reload --host 0.0.0.0 --port 8080
```

或使用 pip：

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8080
```

### 访问 API 文档

- Swagger UI: http://localhost:8080/docs
- ReDoc: http://localhost:8080/redoc
- OpenAPI JSON: http://localhost:8080/openapi.json

## API 端点

### 项目信息管理

- `GET /api/project-info` - 获取项目信息列表（分页）
- `GET /api/project-info/{id}` - 根据ID获取项目信息
- `POST /api/project-info` - 创建项目信息
- `PUT /api/project-info/{id}` - 更新项目信息
- `DELETE /api/project-info/{id}` - 删除项目信息
- `GET /api/project-info/all/list` - 获取所有项目信息（不分页）

## 开发指南

### 添加新的 API 端点

1. 在 `app/models/` 中创建数据模型
2. 在 `app/schemas/` 中创建 Pydantic 模型
3. 在 `app/repositories/` 中创建数据访问层
4. 在 `app/services/` 中创建业务逻辑层
5. 在 `app/api/v1/` 中创建 API 路由
6. 在 `app/main.py` 中注册路由

### 数据库迁移

```bash
# 创建迁移
alembic revision --autogenerate -m "描述"

# 执行迁移
alembic upgrade head

# 回滚迁移
alembic downgrade -1
```

## 测试

```bash
# 运行所有测试
pytest

# 运行测试并生成覆盖率报告
pytest --cov=app --cov-report=html
```

## 部署

### Docker 部署

```bash
# 构建镜像
docker build -t sstcp-maintenance-backend .

# 运行容器
docker run -p 8080:8080 sstcp-maintenance-backend
```

### 生产环境

使用 Gunicorn + Uvicorn workers：

```bash
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8080
```

## 性能优化

- 使用数据库连接池
- 启用响应缓存
- 使用异步数据库操作
- 配置适当的日志级别

## 安全性

- CORS 配置
- 输入验证
- SQL 注入防护（通过 ORM）
- XSS 防护
- HTTPS 支持（生产环境）

## 故障排除

### 数据库连接失败

检查 `.env` 文件中的数据库连接字符串是否正确。

### 端口被占用

修改启动命令中的 `--port` 参数或停止占用 8080 端口的进程。

## 贡献指南

1. Fork 项目
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

## 许可证

本项目采用 MIT 许可证。

## 联系方式

如有问题或建议，请联系开发团队。
