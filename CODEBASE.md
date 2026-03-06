# SSTCP 维保管理系统 - 代码库指南

## 仓库结构

```
SSTCP-paidan260120/
├── src/                    # PC 端前端源码（Vue 3 + Vite + Element Plus）
├── H5/                     # 移动端前端源码（Vue 3 + Vite + Vant）
├── packages/shared/        # 共享代码库（类型、工具、API）
├── backend-python/         # 后端服务（FastAPI + PostgreSQL）
├── scripts/                # 部署和运维脚本
├── deploy/                 # 部署配置
├── docker/                 # Docker 配置
└── .github/workflows/      # CI/CD 配置
```

## 技术栈

### 前端

- **PC 端**: Vue 3 + Vite + Element Plus + TypeScript
- **H5 端**: Vue 3 + Vite + Vant + TypeScript
- **共享库**: TypeScript（类型定义、工具函数、API 封装）

### 后端

- **框架**: FastAPI (Python 3.11+)
- **数据库**: PostgreSQL
- **ORM**: SQLAlchemy
- **迁移**: Alembic

## 环境要求

- Node.js >= 20.0.0
- npm >= 10.0.0
- Python >= 3.11
- PostgreSQL >= 14

## 快速开始

### 安装依赖

```bash
# 安装 PC 端和共享库依赖
npm install

# 安装 H5 端依赖
cd H5 && npm install

# 安装后端依赖
cd backend-python
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或 .\venv\Scripts\activate  # Windows
pip install -r requirements.txt
```

### 本地开发

```bash
# 启动 PC 端开发服务器（端口 3000）
npm run dev

# 启动 H5 端开发服务器（端口 5180）
npm run dev:h5

# 启动后端开发服务器（端口 8080）
npm run dev:backend
```

### 构建生产版本

```bash
# 构建所有前端
npm run build:all

# 单独构建
npm run build:pc      # PC 端
npm run build:h5      # H5 端
npm run build:shared  # 共享库
```

### 代码质量检查

```bash
# 运行所有 lint 检查
npm run lint:all

# 单独检查
npm run lint          # PC 端
cd H5 && npm run lint # H5 端

# 类型检查
npm run typecheck:all
```

## CI/CD 流程

### 工作流结构

```
┌─────────┐   ┌─────────┐   ┌──────────────┐
│ lint-pc │   │ lint-h5 │   │ lint-backend │
└────┬────┘   └────┬────┘   └──────┬───────┘
     │             │               │
     └──────┬──────┘               │
            │                      │
     ┌──────▼──────┐               │
     │test-frontend│               │
     └──────┬──────┘               │
            │               ┌──────▼───────┐
     ┌──────┴──────┐        │test-backend  │
     │             │        └──────┬───────┘
┌────▼────┐   ┌────▼────┐         │
│build-pc │   │build-h5 │         │
└────┬────┘   └────┬────┘         │
     └──────┬──────┘              │
            │                     │
     ┌──────▼─────────────────────▼──────┐
     │            deploy                  │
     └────────────────────────────────────┘
```

### 触发条件

- Push 到 `master` 或 `develop` 分支
- Pull Request 到 `master` 分支
- 手动触发

### 部署

- 仅 `master` 分支触发部署
- 自动构建并部署到生产服务器

## 共享库使用

### 导入类型

```typescript
import type { ApiResponse, PaginatedResponse } from '@sstcp/shared/types/api'
import type { WorkOrder, Personnel } from '@sstcp/shared/types/models'
```

### 导入工具函数

```typescript
import { formatDateTime, formatCurrency } from '@sstcp/shared/utils/format'
import { getStatusLabel, getStatusColor } from '@sstcp/shared/utils/status'
import { addWatermark } from '@sstcp/shared/utils/watermark'
```

### 导入 API 端点

```typescript
import { API_ENDPOINTS } from '@sstcp/shared/api/endpoints'

// 使用示例
const url = API_ENDPOINTS.WORK_ORDERS.LIST
```

## 目录说明

### PC 端 (`src/`)

```
src/
├── api/           # API 请求封装
├── components/    # 公共组件
├── config/        # 配置文件（常量、权限）
├── router/        # 路由配置
├── services/      # 业务服务层
├── stores/        # 状态管理
├── styles/        # 全局样式
├── types/         # 类型定义
├── utils/         # 工具函数
└── views/         # 页面组件
```

### H5 端 (`H5/src/`)

```
H5/src/
├── api/           # API 请求封装
├── components/    # 公共组件
├── composables/   # 组合式函数
├── config/        # 配置文件
├── router/        # 路由配置
├── services/      # 业务服务层
├── stores/        # 状态管理（Pinia）
├── styles/        # 全局样式
├── types/         # 类型定义
├── utils/         # 工具函数
└── views/         # 页面组件
```

### 后端 (`backend-python/app/`)

```
backend-python/app/
├── api/v1/        # API 路由
├── models/        # 数据库模型
├── schemas/       # Pydantic 模型
├── services/      # 业务逻辑层
├── repositories/  # 数据访问层
├── utils/         # 工具函数
└── middleware/    # 中间件
```

## 常见问题

### 1. 依赖安装失败

```bash
# 清除缓存并重新安装
rm -rf node_modules package-lock.json
npm install
```

### 2. TypeScript 类型错误

```bash
# 重新构建共享库
cd packages/shared && npm run build
```

### 3. 后端数据库迁移

```bash
cd backend-python
alembic upgrade head
```

### 4. 端口冲突

- PC 端默认端口: 3000
- H5 端默认端口: 5180
- 后端默认端口: 8080

可在 `vite.config.ts` 中修改前端端口。

## 编码规范

### 命名约定

- 组件文件: PascalCase（如 `UserList.vue`）
- 工具函数: camelCase（如 `formatDate.ts`）
- 常量: UPPER_SNAKE_CASE（如 `API_ENDPOINTS`）

### 注释规范

- 函数必须有注释说明功能
- 复杂逻辑需要行内注释
- 使用中文注释

### Git 提交规范

- `feat:` 新功能
- `fix:` 修复 bug
- `docs:` 文档更新
- `refactor:` 重构
- `test:` 测试相关
- `chore:` 构建/工具相关

## 相关链接

- [Vue 3 文档](https://vuejs.org/)
- [Element Plus 文档](https://element-plus.org/)
- [Vant 文档](https://vant-ui.github.io/vant/)
- [FastAPI 文档](https://fastapi.tiangolo.com/)
