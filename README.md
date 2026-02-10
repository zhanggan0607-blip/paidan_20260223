# SSTCP 工程维保管理系统

基于 Vue 3 + FastAPI 的工程维保管理系统。

## 项目结构

```
SSTCP-paidan260120/
├── backend-python/          # Python 后端服务
│   ├── app/               # 应用代码
│   ├── tests/             # 测试代码
│   └── ...               # 配置文件和文档
├── src/                  # Vue 3 前端应用
│   ├── components/        # 组件
│   ├── router/           # 路由
│   ├── styles/           # 样式
│   └── views/            # 页面
├── package.json          # 前端依赖
├── vite.config.ts        # Vite 配置
└── index.html           # 入口文件
```

## 技术栈

### 前端
- Vue 3
- TypeScript
- Vite
- Vue Router

### 后端
- Python 3.11+
- FastAPI
- SQLAlchemy
- PyMySQL
- Pydantic

## 快速开始

### 前端启动

```bash
# 安装依赖
npm install

# 开发模式
npm run dev

# 构建生产版本
npm run build

# 预览生产版本
npm run preview
```

### 后端启动

```bash
cd backend-python

# 安装依赖
pip install -r requirements.txt

# 配置数据库
cp .env.example .env

# 启动服务
uvicorn app.main:app --reload --host 0.0.0.0 --port 8080
```

## 访问地址

- 前端开发服务器: http://localhost:5173
- 后端API服务: http://localhost:8080
- API文档: http://localhost:8080/docs

## 功能模块

- 项目信息管理
- 巡检事项管理
- 维保计划管理
- 项目超期提醒
- 项目临期提醒

## 开发文档

- 后端API文档: [backend-python/API_DOCUMENTATION.md](backend-python/API_DOCUMENTATION.md)
- 后端迁移指南: [backend-python/MIGRATION_GUIDE.md](backend-python/MIGRATION_GUIDE.md)
- 后端迁移总结: [backend-python/MIGRATION_SUMMARY.md](backend-python/MIGRATION_SUMMARY.md)

## 许可证

MIT
