# SSTCP 维保管理系统 — 全面架构审查报告

> 审查日期：2026-04-30
> 审查范围：前端架构（PC/H5）、后端架构、API架构、安全防护、性能优化、监控告警、扩展性设计
> 项目版本：后端 2.0.7 / 前端 2.0.7 / 共享包 1.0.0

---

## 目录

- [一、审查概览](#一审查概览)
- [二、项目架构全景](#二项目架构全景)
- [三、前端架构审查](#三前端架构审查)
  - [3.1 PC端架构](#31-pc端架构)
  - [3.2 H5端架构](#32-h5端架构)
  - [3.3 共享包架构](#33-共享包架构)
- [四、后端架构审查](#四后端架构审查)
  - [4.1 分层架构](#41-分层架构)
  - [4.2 数据库设计](#42-数据库设计)
  - [4.3 认证与授权](#43-认证与授权)
  - [4.4 中间件体系](#44-中间件体系)
  - [4.5 错误处理机制](#45-错误处理机制)
- [五、API架构审查](#五api架构审查)
- [六、安全防护机制审查](#六安全防护机制审查)
- [七、性能优化评估](#七性能优化评估)
- [八、日志与监控体系评估](#八日志与监控体系评估)
- [九、扩展性设计评估](#九扩展性设计评估)
- [十、部署与CI/CD审查](#十部署与cicd审查)
- [十一、核心问题TOP 10](#十一核心问题top-10)
- [十二、架构重构方案](#十二架构重构方案)
- [十三、架构优势总结](#十三架构优势总结)

---

## 一、审查概览

| 维度 | 评分 | 说明 |
|------|------|------|
| **技术栈选型** | A | Vue3 + Vite + FastAPI + PostgreSQL 现代化技术栈，选型合理 |
| **代码共享** | A- | Monorepo + shared包设计优秀，但非真正monorepo |
| **分层架构** | B+ | 前后端分层清晰，部分路由绕过Service层 |
| **类型安全** | B- | strictNullChecks/noImplicitAny关闭，TS价值大打折扣 |
| **安全防护** | C+ | JWT/OSS/上传验证完善，但CSP/CSRF/密钥泄露问题严重 |
| **性能优化** | B | 构建优化/缓存/虚拟滚动已实现，但缺少CDN/SSR/查询优化 |
| **监控告警** | C | Prometheus已集成但未配置Grafana/告警，日志非结构化 |
| **扩展性** | C+ | 单体架构，无水平扩展/读写分离/服务拆分设计 |
| **环境配置** | C | 缺少.env文件体系，密钥硬编码，多环境部署不便 |
| **代码整洁** | B | 存在重构残留、重复缓存实现、FIXME未处理 |

---

## 二、项目架构全景

### 2.1 系统架构图

```
                    Internet
                       |
                  [Nginx :80/:443]
                   /     |     \
                  /      |      \
    /api/ --> [Backend:8000]    /h5/ --> [H5 Frontend:80]
    /uploads/ --> [Backend]     / --> [PC Frontend:80]
                  |
          [Alibaba Cloud RDS]     [Alibaba Cloud OSS]
          [Alibaba Cloud OCR]     [Redis (Token黑名单/缓存)]
```

### 2.2 技术栈总览

| 端 | 框架 | UI库 | 构建 | 语言 |
|----|------|------|------|------|
| PC前端 | Vue 3.5 + Pinia 2.3 | Element Plus 2.9 | Vite 6 | TypeScript 5.6 |
| H5前端 | Vue 3.5 + Pinia 2.2 | Vant 4.8 | Vite 6 | TypeScript 5.6 |
| 后端 | FastAPI 0.109 | - | Uvicorn | Python 3.11 |
| 数据库 | PostgreSQL (RDS) | - | Alembic迁移 | SQLAlchemy 2.0 |
| 共享包 | @sstcp/shared | - | 无构建产物 | TypeScript |

### 2.3 项目目录结构

```
paidan/
├── .github/workflows/          # CI/CD配置
│   ├── ci.yml                  # 持续集成（4个并行Job）
│   └── cd-production.yml       # 持续部署
├── .husky/                     # Git钩子
├── H5/                         # H5移动端
│   ├── src/
│   │   ├── api/                # API请求封装（3个文件）
│   │   ├── components/         # 公共组件（1个）
│   │   ├── composables/        # 组合式函数（2个）
│   │   ├── config/             # 常量与权限配置
│   │   ├── router/             # 路由（28条）
│   │   ├── services/           # API服务层（21个）
│   │   ├── stores/             # 状态管理（userStore）
│   │   ├── styles/             # 全局样式（CSS变量体系）
│   │   ├── types/              # 类型定义
│   │   ├── utils/              # 工具函数
│   │   └── views/              # 页面视图（28个）
│   ├── Dockerfile              # 多阶段构建
│   └── package.json
├── backend-python/             # Python后端
│   ├── alembic/                # 数据库迁移（8个版本）
│   ├── app/
│   │   ├── api/v1/             # API路由层（30个路由文件）
│   │   ├── middleware/          # 中间件（CSP、限流）
│   │   ├── models/             # 数据模型层（22个模型）
│   │   ├── repositories/       # 数据访问层（17个仓库）
│   │   ├── schemas/            # 数据传输对象（14个Schema）
│   │   ├── services/           # 业务逻辑层（17个服务）
│   │   ├── utils/              # 工具类（8个）
│   │   ├── websocket/          # WebSocket管理
│   │   ├── auth.py             # JWT认证模块
│   │   ├── config.py           # 配置管理
│   │   ├── database.py         # 数据库连接
│   │   ├── dependencies.py     # 依赖注入
│   │   ├── exceptions.py       # 自定义异常
│   │   └── main.py             # 主入口（699行）
│   ├── tests/                  # 测试目录
│   ├── Dockerfile              # 多阶段构建
│   └── pyproject.toml
├── docker/                     # Docker配置
│   ├── docker-compose-server.yml
│   ├── nginx.conf              # 主Nginx配置
│   ├── nginx-pc.conf           # PC端Nginx
│   ├── nginx-h5.conf           # H5端Nginx
│   └── nginx-test.conf         # 测试环境Nginx
├── packages/shared/            # 共享代码包
│   ├── src/
│   │   ├── api/                # 端点定义 + 请求封装
│   │   ├── components/         # 共享Vue组件（3个）
│   │   ├── config/             # 常量配置
│   │   ├── services/           # 服务工厂
│   │   ├── types/              # 类型定义（13个业务模型）
│   │   └── utils/              # 工具函数（8个模块）
│   └── package.json
├── scripts/                    # 运维脚本
│   ├── deploy-docker-all.ps1   # 全量部署脚本
│   ├── deploy-production.sh    # 生产部署
│   ├── rollback.sh             # 回滚脚本
│   ├── backup-db.sh            # 数据库备份
│   └── generate-ssl-cert.sh    # SSL证书生成
├── src/                        # PC前端
│   ├── api/                    # API请求封装
│   ├── components/             # 通用组件 + 业务组件
│   ├── composables/            # 组合式函数（5个）
│   ├── config/                 # 常量与权限配置
│   ├── router/                 # 路由（25条）
│   ├── services/               # API服务层（16个）
│   ├── stores/                 # 状态管理（userStore）
│   ├── styles/                 # 全局样式
│   ├── types/                  # 类型定义
│   ├── utils/                  # 工具函数
│   └── views/                  # 页面视图（28个）
├── docker-compose.yml          # 本地开发
├── docker-compose-server.yml   # 生产部署
└── package.json
```

---

## 三、前端架构审查

### 3.1 PC端架构

#### 技术栈与依赖

| 类别 | 技术 | 版本 |
|------|------|------|
| 框架 | Vue 3 | ^3.5.13 |
| 构建工具 | Vite | ^6.0.5 |
| 路由 | Vue Router | ^4.5.0 |
| 状态管理 | Pinia | ^2.3.1 |
| UI框架 | Element Plus | ^2.9.1 |
| HTTP客户端 | Axios | ^1.7.9 |
| 语言 | TypeScript | ~5.6.3 |
| 测试 | Vitest + @vue/test-utils | ^2.1.0 |
| 共享包 | @sstcp/shared (本地monorepo) | file:./packages/shared |

#### 构建配置特征

- **Gzip压缩**：生产构建自动生成 `.gz` 文件，阈值10KB
- **代码分割策略**：
  - `vue-vendor`：Vue核心三件套 (vue/vue-router/pinia)
  - `element-plus`：UI库独立chunk
  - `axios`：HTTP库独立chunk
- **生产优化**：移除 `console.log/info/debug`，使用 terser 压缩
- **静态资源分类**：JS → `assets/js/`，其他按扩展名分目录

#### 路由配置

- 使用 `createWebHistory()` (HTML5 History模式)
- **扁平路由结构**：所有业务页面共用 `Layout` 组件
- **路由懒加载**：所有页面组件使用 `() => import()` 动态导入
- **权限控制**：通过 `meta.permission` 字段标记，路由守卫校验
- **路由守卫逻辑**：未登录→登录页 → 根路径→角色默认页 → 强制改密 → 权限检查
- **路由总数**：25个业务路由 + 2个独立路由

#### 状态管理

- **未使用Pinia**：虽然安装了Pinia，但 `userStore` 采用原生Vue响应式 + 模块单例模式
- **持久化**：使用 `localStorage` 存储token和用户信息
- **跨标签页同步**：监听 `storage` 事件
- **权限方法**：内置 `isAdmin()`、`isManager()`、`canShowMenu()` 等

#### Composables清单

| Composable | 功能 |
|-----------|------|
| `useToast` | 全局Toast消息（单例模式） |
| `useAbortController` | 请求取消管理（自动清理） |
| `usePageState` | 页面加载/保存/模态框状态 |
| `useApiCache` | API响应缓存（TTL + LRU） |
| `useOnlineStatusWebSocket` | WebSocket在线状态（自动重连+心跳） |

#### PC端问题清单

| 严重度 | 问题 | 位置 |
|--------|------|------|
| 🔴 高 | **三套缓存实现重复**：`utils/apiCache.ts`、`utils/cache.ts`、`composables/useApiCache.ts` 功能高度重叠 | src/utils/ + src/composables/ |
| 🔴 高 | **userStore未使用Pinia**：安装了Pinia但用原生Vue响应式，失去DevTools集成 | src/stores/userStore.ts |
| 🔴 高 | **缺少环境变量文件**：无 `.env` / `.env.development` / `.env.production` | 根目录 |
| 🟡 中 | **TypeScript配置过于宽松**：`strictNullChecks: false`、`noImplicitAny: false` | tsconfig.app.json |
| 🟡 中 | **Element Plus图标全量注册**：遍历注册所有图标组件，增加包体积 | src/main.ts |
| 🟡 中 | **重构残留文件**：`MaintenancePlanManagementRefactored.vue`、`spotWork-refactored.ts` | src/views/ + src/services/ |
| 🟡 中 | **FIXME未处理**：`request.ts` 中标注的 `X-User-Name/X-User-Role` 头应移除 | src/api/request.ts |
| 🟡 中 | **Layout.vue过于庞大**：约740行，包含菜单/心跳/面包屑/用户菜单 | src/components/Layout.vue |
| 🟡 中 | **路由未命名**：大部分路由缺少 `name` 属性 | src/router/index.ts |
| 🟢 低 | **App.vue使用Options API**：与项目Composition API风格不一致 | src/App.vue |
| 🟢 低 | **services层无索引文件**：16个service文件没有 `index.ts` 统一导出 | src/services/ |

---

### 3.2 H5端架构

#### 技术栈与依赖

| 类别 | 技术 | 版本 |
|------|------|------|
| 框架 | Vue 3 | ^3.5.0 |
| 构建工具 | Vite | ^6.0.5 |
| UI组件库 | Vant 4 | ^4.8.0 |
| 路由 | Vue Router 4 | ^4.4.0 |
| 状态管理 | Pinia | ^2.2.0 |
| HTTP客户端 | Axios | ^1.7.7 |
| 自动导入 | unplugin-auto-import + unplugin-vue-components | - |

#### 移动端适配方案

当前方案为 **固定像素 + CSS变量**：

```css
html { font-size: 16px; }          /* 根字号固定16px */
#app { max-width: var(--app-max-width: 430px); }
```

**评估**：这不是真正的移动端自适应方案。`rem` 单位不会随屏幕宽度变化，在不同屏幕宽度手机上显示效果完全相同。如需适配不同设备，应引入 `postcss-px-to-viewport`。

#### 钉钉免登集成

- 检测钉钉环境 → 获取authCode → 后端认证 → 自动登录
- 动态加载钉钉JSAPI
- UA检测判断钉钉环境

#### H5端问题清单

| 严重度 | 问题 | 位置 |
|--------|------|------|
| 🔴 高 | **移动端无真正的自适应方案**：`html { font-size: 16px }` 固定值，rem等于px | src/styles/variables.css |
| 🔴 高 | **缺少Token有效性验证**：启动时不调 `/auth/me`，过期token仍显示已登录 | src/stores/userStore.ts |
| 🟡 中 | **userStore单例与Pinia Store大量代码重复**：两种模式并存 | src/stores/userStore.ts |
| 🟡 中 | **`<keep-alive>` 无限制**：包裹所有路由组件，无 `include/exclude` | src/App.vue |
| 🟡 中 | **缺少404路由** | src/router/index.ts |
| 🟡 中 | **`.env` 和 `.env.production` 内容完全相同** | H5/目录 |
| 🟡 中 | **`onUnauthorized` 使用 `window.location.href` 硬跳转**：丢失应用状态 | H5/src/api/request.ts |
| 🟢 低 | **Vant组件全局注册不必要**：Dialog/Toast/ImagePreview 支持函数式调用 | H5/src/main.ts |
| 🟢 低 | **`style.css` 大量 `!important` 覆盖Vant样式** | H5/src/style.css |
| 🟢 低 | **测试覆盖不足**：仅3个测试文件 | H5/src/ |

---

### 3.3 共享包架构

#### 包结构

```
packages/shared/src/
├── api/                # API端点定义 + Axios请求封装
├── components/         # 共享Vue组件（SearchInput/LoadingSpinner/Toast）
├── config/             # 常量配置
├── services/           # 服务工厂（createBaseService/createSubmitApproveService）
├── types/              # 类型定义（13个业务模型 + API类型 + 权限类型）
└── utils/              # 工具函数（8个模块）
```

#### 核心能力

- **API端点集中管理**：20+模块的API路径常量，使用 `as const` 确保类型安全
- **请求封装工厂**：`createRequest()` 支持JWT自动注入、Token主动/被动刷新、请求排队
- **服务工厂**：`createBaseService<T>()` 和 `createSubmitApproveService<T>()` 减少两端重复代码
- **权限体系**：5种角色 + 角色等级 + 完整权限判断函数
- **图片水印/压缩**：跨端共用的图片处理工具

#### 共享包问题清单

| 严重度 | 问题 | 位置 |
|--------|------|------|
| 🔴 高 | **无构建产物**：`main` 直接指向 `src/index.ts`，每次消费端启动都重新编译 | packages/shared/package.json |
| 🟡 中 | **两套搜索历史API并存**：全局搜索历史和按字段键搜索历史功能重叠 | src/utils/searchHistory.ts |
| 🟡 中 | **排序代码重复**：`getSortTimestamp` 在 sort.ts 和 sortInterceptor.ts 中各实现一遍 | src/utils/ |
| 🟡 中 | **组件使用Options API**：与项目其他部分Composition API风格不一致 | src/components/ |
| 🟡 中 | **组件UI框架耦合不足**：共享组件无法自动适配Element Plus/Vant | src/components/ |
| 🟢 低 | **重复导出**：`export * from './components'` 出现了两次 | src/index.ts |

---

## 四、后端架构审查

### 4.1 分层架构

```
API路由层 (30个路由文件)
    ↓
Service层 (17个服务 + BaseService事务管理)
    ↓
Repository层 (17个仓库 + BaseRepository泛型CRUD)
    ↓
Model层 (22个模型 + SoftDeleteMixin)
```

#### BaseRepository泛型CRUD

提供标准CRUD操作：`find_by_id`、`find_all_unpaginated`、`create`、`update`、`delete`、`exists_by_id`、`count`、`find_by_field`、`exists_by_field`。create/update/delete只执行flush不commit，事务由Service层管理。

#### BaseService事务管理

提供 `commit()`、`rollback()`、`flush()`、`execute_in_transaction()` 方法，统一事务管理，异常自动回滚。

### 4.2 数据库设计

#### 连接池配置

| 参数 | 同步引擎 | 异步引擎 |
|------|----------|----------|
| 驱动 | psycopg2 | asyncpg |
| 池大小 | 10 + 20溢出 | 5 + 10溢出 |
| 回收时间 | 30分钟 | 30分钟 |
| 连接前检测 | pool_pre_ping=True | pool_pre_ping=True |
| 策略 | LIFO | LIFO |

#### 模型清单（22个模型）

| 模型 | 表名 | 主要特征 |
|------|------|---------|
| Personnel | personnel | 人员信息，含钉钉字段 |
| ProjectInfo | project_info | 项目信息，多对多关系中心 |
| MaintenancePlan | maintenance_plan | 维保计划，关联3种工单 |
| PeriodicInspection | periodic_inspection | 定期巡检单，SoftDelete |
| TemporaryRepair | temporary_repair | 临时维修单，SoftDelete |
| SpotWork | spot_work | 零星用工单，SoftDelete |
| UploadedFile | uploaded_file | 文件上传，OSS/DB双存储 |
| SparePartsStock | spare_parts_stock | 备品备件库存 |
| Customer | customer | 客户信息 |
| WorkOrderOperationLog | work_order_operation_log | 工单操作日志 |
| OnlineUser | online_user | 在线用户 |

#### 数据库设计问题

| 严重度 | 问题 | 位置 |
|--------|------|------|
| 🟡 中 | **photos字段用Text存储JSON数组**：应使用PostgreSQL JSONB类型 | models/spot_work.py等 |
| 🟡 中 | **signature字段用Text存储Base64**：大量图片数据存数据库影响查询性能 | models/ |
| 🟡 中 | **模型to_dict()大量重复代码**：应使用Pydantic的 `from_attributes=True` | models/*.py |
| 🟢 低 | **模型内部import json**：应移到文件顶部 | models/spot_work.py等 |

### 4.3 认证与授权

#### JWT认证

| 参数 | 值 |
|------|------|
| 算法 | HS256 |
| Access Token有效期 | 30分钟 |
| Refresh Token有效期 | 15天 |
| Token黑名单 | Redis优先 + 内存降级（最大10000条，LRU淘汰） |
| 密码哈希 | bcrypt，截断72字节 |

#### 权限依赖注入

| 依赖函数 | 权限要求 |
|---------|---------|
| `get_current_user_info` | 可选认证 |
| `get_current_user_required` | 必须认证 |
| `get_manager_user` | 管理员/部门经理/主管 |
| `get_admin_user` | 仅超级管理员 |
| `get_material_manager_user` | 管理员/部门经理/材料员 |

#### 认证问题

| 严重度 | 问题 | 位置 |
|--------|------|------|
| 🔴 高 | **Token黑名单内存模式**：多进程部署时不共享 | app/auth.py |
| 🔴 高 | **auth.py和dependencies.py中JWT解码逻辑重复** | app/auth.py + app/dependencies.py |
| 🟡 中 | **角色信息在JWT中固定**：修改角色后旧Token不即时生效 | app/api/v1/auth.py |
| 🟡 中 | **默认密码策略薄弱**：手机号后6位或"123456" | app/api/v1/auth.py |
| 🟡 中 | **密码最小长度仅6位** | app/api/v1/auth.py |
| 🟡 中 | **登录锁定基于内存**：服务重启后状态丢失 | app/api/v1/auth.py |

### 4.4 中间件体系

#### 中间件栈（按注册顺序）

1. **CORS中间件** — 允许指定域名跨域访问
2. **GZip中间件** — 响应压缩（>1KB）
3. **CSP中间件** — 内容安全策略
4. **RateLimitMiddleware** — 请求限流（仅生产环境）
5. **自定义HTTP中间件** — 请求日志 + 安全响应头

#### 限流配置

| 环境 | 每分钟限制 | 每小时限制 |
|------|-----------|-----------|
| 生产 | 300次 | 5000次 |
| 开发 | 不启用 | 不启用 |

#### 中间件问题

| 严重度 | 问题 | 位置 |
|--------|------|------|
| 🔴 高 | **限流中间件内存存储**：多进程部署时不共享 | middleware/rate_limit.py |
| 🟡 中 | **CSP策略包含 `unsafe-inline`/`unsafe-eval`**：严重削弱XSS防护 | middleware/csp.py |
| 🟡 中 | **限流仅非Debug模式启用**：生产误配DEBUG=True时限流失效 | app/main.py |
| 🟡 中 | **客户端识别依赖X-Forwarded-For**：可被伪造 | middleware/rate_limit.py |

### 4.5 错误处理机制

#### 自定义异常体系

```
BusinessException (基类, code=500)
├── NotFoundException (404)
├── ValidationException (400)
├── DuplicateException (409)
├── ForbiddenException (403)
└── UnauthorizedException (401)
```

#### 全局异常处理器（4层）

1. `BusinessException` → 业务异常（40x/50x）
2. `StarletteHTTPException` → HTTP异常
3. `RequestValidationError` → 参数验证失败（422）
4. `Exception` → 未捕获异常（500，隐藏内部信息，返回错误ID追踪）

#### 统一响应格式

```python
ApiResponse: {code, message, data}
PaginatedResponse: {code, message, data: {items, total, page, size, ...}}
```

#### 错误处理问题

| 严重度 | 问题 | 位置 |
|--------|------|------|
| 🟡 中 | **异常响应格式不统一**：混用HTTPException和BusinessException | app/main.py |
| 🟡 中 | **PaginatedResponse包含两套分页字段**：兼容Spring风格但增加维护成本 | schemas/common.py |

### 4.6 后端整体问题清单

| 严重度 | 问题 | 位置 |
|--------|------|------|
| 🔴 高 | **main.py过于臃肿（699行）**：包含文件服务、迁移端点、常量定义 | app/main.py |
| 🔴 高 | **部分路由绕过Service层**：auth.py和work_order.py直接操作数据库 | app/api/v1/ |
| 🔴 高 | **Token黑名单内存模式**：多进程部署时不共享 | app/auth.py |
| 🔴 高 | **限流中间件内存存储**：多进程部署时不共享 | app/middleware/rate_limit.py |
| 🟡 中 | **auth.py和dependencies.py中JWT解码逻辑重复** | app/auth.py + app/dependencies.py |
| 🟡 中 | **模型to_dict()大量重复代码** | app/models/ |
| 🟡 中 | **photos字段用Text存储JSON数组** | app/models/ |
| 🟡 中 | **work_order.py大量原始SQL拼接** | app/api/v1/work_order.py |
| 🟡 中 | **版本号不一致**：pyproject.toml(1.0.3) vs config.py(2.0.7) | pyproject.toml |
| 🟡 中 | **CacheService.delete_pattern使用KEYS命令** | app/services/cache.py |
| 🟡 中 | **部分配置字段使用os.getenv绕过pydantic** | app/config.py |
| 🟢 低 | **PersonnelService使用print而非logger** | app/services/personnel.py |
| 🟢 低 | **PaginatedResponse包含两套分页字段** | app/schemas/common.py |
| 🟢 低 | **日志格式非结构化** | app/utils/logging_config.py |

---

## 五、API架构审查

### 5.1 接口设计评估

| 方面 | 评估 | 说明 |
|------|------|------|
| RESTful规范 | ✅ 良好 | 统一前缀 `/api/v1`，资源路径清晰 |
| 统一响应格式 | ✅ 良好 | `ApiResponse<T>` + `PaginatedResponse<T>` |
| 版本管理 | ✅ 良好 | URL路径版本 `/api/v1` |
| API文档 | ✅ 良好 | FastAPI自动生成OpenAPI文档 |
| 批量操作 | ✅ 良好 | 批量上传 `/upload/batch` |
| 错误码 | ⚠️ 待改进 | 混用HTTPException和BusinessException |

### 5.2 API路由清单（30个路由模块）

| 路由模块 | 前缀 | 主要功能 |
|---------|------|---------|
| auth | /auth | 登录/登出/改密/刷新Token |
| dingtalk_auth | /dingtalk | 钉钉免登/同步通讯录 |
| personnel | /personnel | 人员CRUD |
| personnel_async | /personnel | 人员异步查询 |
| project_info | /project-info | 项目信息CRUD |
| maintenance_plan | /maintenance-plan | 维保计划CRUD |
| periodic_inspection | /periodic-inspection | 定期巡检CRUD |
| temporary_repair | /temporary-repair | 临时维修CRUD |
| spot_work | /spot-work | 零星用工CRUD |
| work_order | /work-order | 工单合并查询(UNION ALL) |
| work_plan | /work-plan | 工作计划CRUD |
| spare_parts | /spare-parts | 备品备件 |
| repair_tools | /repair-tools | 维修工具 |
| customer | /customer | 客户管理 |
| upload | /upload | 文件上传（单文件/批量/Base64） |
| ocr | /ocr | OCR身份证识别 |
| export_pdf | /export-pdf | PDF导出 |
| statistics | /statistics | 统计数据 |
| websocket | /ws | WebSocket实时通信 |

### 5.3 文件上传API

- **单文件上传**：`POST /upload/` — 10MB限制，filetype双重验证
- **批量上传**：`POST /upload/batch` — 最多9张，统一返回成功/失败列表
- **Base64上传**：`POST /upload/base64` — 支持Data URI格式
- **安全措施**：文件名清洗（防路径遍历）、UUID存储名、图片自动压缩、类型白名单

---

## 六、安全防护机制审查

### 6.1 安全风险矩阵

| 审查项 | 风险等级 | 关键发现 |
|--------|----------|----------|
| **敏感信息泄露** | 🔴 严重 | `.env.local`/`.env.test`包含真实阿里云AccessKey和数据库密码 |
| **CSRF防护** | 🔴 高 | 完全缺失 |
| **CSP策略** | 🟡 中 | `unsafe-inline`/`unsafe-eval`使XSS防护严重削弱 |
| **限流策略** | 🟡 中 | 仅内存存储，Debug模式跳过限流 |
| **SQL注入** | 🟡 中 | work_order.py使用f-string拼接SQL |
| **XSS防护** | 🟡 中 | CSP削弱 + 缺少输出转义 |
| **CORS配置** | 🟡 中 | `allow_headers=["*"]` 过于宽松 |
| **JWT认证** | 🟢 低 | 实现完善，默认密码策略需加强 |
| **文件上传** | 🟢 低 | filetype验证 + 文件名清洗 + 大小限制 |
| **HTTPS/SSL** | 🟢 低 | TLS1.2+1.3 + HSTS + 安全响应头 |
| **OSS安全** | 🟢 低 | 凭证管理规范，默认公开URL有风险 |

### 6.2 紧急安全问题详情

#### 🔴 P0 - 敏感信息泄露

以下文件包含真实密钥和密码：

| 文件 | 泄露内容 |
|------|----------|
| `backend-python/.env.local` | 阿里云OCR AccessKey ID/Secret |
| `.env.test` | RDS生产数据库密码 + 阿里云OSS密钥 |
| `docker/docker-compose-server.yml` | 硬编码数据库密码和默认SECRET_KEY |
| `scripts/deploy-docker-all.ps1` | 硬编码服务器IP和数据库密码 |

**紧急建议**：
1. 立即轮换所有已泄露的阿里云AccessKey和数据库密码
2. 检查Git历史，确认敏感文件是否曾被提交
3. 将硬编码凭据改为环境变量引用

#### 🔴 P0 - CSRF防护缺失

- 项目完全没有CSRF防护措施
- Bearer Token认证在一定程度上降低了CSRF风险
- 建议添加 `SameSite` Cookie策略或CSRF Token作为深度防御

#### 🟡 P1 - CSP策略削弱

```python
script-src 'self' 'unsafe-inline' 'unsafe-eval' https://g.alicdn.com
style-src 'self' 'unsafe-inline' https://g.alicdn.com
```

`unsafe-inline` 和 `unsafe-eval` 基本上使CSP对XSS的防护失效。建议改用nonce或hash方式允许内联脚本。

### 6.3 安全响应头评估

| 响应头 | 状态 | 值 |
|--------|------|------|
| Strict-Transport-Security | ✅ | max-age=63072000; includeSubDomains |
| X-Content-Type-Options | ✅ | nosniff |
| X-Frame-Options | ✅ | SAMEORIGIN |
| X-XSS-Protection | ✅ | 1; mode=block |
| Referrer-Policy | ✅ | strict-origin-when-cross-origin |
| Content-Security-Policy | ⚠️ | 包含unsafe-inline/unsafe-eval |
| Permissions-Policy | ❌ | 缺失 |

---

## 七、性能优化评估

### 7.1 性能优化现状

| 方面 | 当前状态 | 评估 |
|------|----------|------|
| **构建优化** | 代码分割 + Gzip + Tree-shaking + console移除 | ✅ 良好 |
| **数据库连接池** | 同步10+20溢出，异步5+10溢出 | ✅ 合理 |
| **缓存策略** | Redis缓存 + 前端ApiCache(TTL/LRU) + @cache_result装饰器 | ✅ 基本完善 |
| **虚拟滚动** | VirtualScroll组件已实现 | ✅ 良好 |
| **路由懒加载** | PC和H5所有路由均使用动态import | ✅ 良好 |
| **图片优化** | 后端自动压缩(质量85, max 1920×1920) + 水印 | ✅ 良好 |
| **CDN加速** | OSS CDN域名已配置 | ✅ 良好 |
| **工单查询优化** | work_order.py使用UNION ALL在数据库层面合并 | ✅ 良好 |
| **N+1查询** | 未检测和优化 | ❌ 缺失 |
| **SSR/SSG** | 未实现 | ❌ 缺失（非必需） |
| **Service Worker** | 未实现 | ❌ 缺失 |

### 7.2 性能优化建议

| 优先级 | 建议 | 预期收益 |
|--------|------|----------|
| 🔴 高 | 检测并优化N+1查询（特别是列表页关联查询） | 数据库查询性能提升 |
| 🟡 中 | PersonnelService批量更新替代逐条更新 | 大数据量场景性能提升 |
| 🟡 中 | CacheService.delete_pattern改用SCAN替代KEYS | Redis性能提升 |
| 🟡 中 | Dockerfile缓存分层优化（先COPY package.json） | 构建速度提升 |
| 🟢 低 | Element Plus图标按需导入 | 包体积减少 |
| 🟢 低 | H5端引入postcss-px-to-viewport | 多设备适配 |

---

## 八、日志与监控体系评估

### 8.1 日志系统

| 方面 | 当前状态 | 评估 |
|------|----------|------|
| **日志框架** | Python RotatingFileHandler(10MB×10) + 控制台 | ✅ 基本完善 |
| **请求追踪** | request_id贯穿日志 | ✅ 良好 |
| **级别控制** | DEBUG模式输出DEBUG，生产输出INFO | ✅ 合理 |
| **第三方库降级** | uvicorn.access和sqlalchemy.engine设为WARNING | ✅ 合理 |
| **结构化日志** | 文本格式，非JSON | ❌ 不利于采集 |
| **日志聚合** | 无ELK/Loki方案 | ❌ 缺失 |

### 8.2 监控体系

| 方面 | 当前状态 | 评估 |
|------|----------|------|
| **Prometheus** | prometheus-fastapi-instrumentator已集成 | ✅ 已集成 |
| **健康检查** | `/api/v1/health` 端点 + Docker HEALTHCHECK | ✅ 完善 |
| **WebSocket监控** | ConnectionManager管理连接状态 | ✅ 基本完善 |
| **Grafana** | 未配置 | ❌ 缺失 |
| **告警通知** | 无告警规则和通知渠道 | ❌ 缺失 |
| **前端监控** | 无Sentry/异常上报 | ❌ 缺失 |

### 8.3 监控改进建议

| 优先级 | 建议 | 预期收益 |
|--------|------|----------|
| 🔴 高 | 配置Grafana连接Prometheus，创建监控仪表盘 | 可视化监控 |
| 🔴 高 | 配置告警规则（CPU/内存/错误率/响应时间） | 主动发现问题 |
| 🟡 中 | 日志改为JSON格式 + ELK/Loki采集 | 日志分析效率 |
| 🟡 中 | 集成Sentry前端异常上报 | 前端问题追踪 |
| 🟢 低 | 添加APM全链路追踪 | 性能瓶颈定位 |

---

## 九、扩展性设计评估

| 方面 | 当前状态 | 评估 | 建议 |
|------|----------|------|------|
| **水平扩展** | 单实例部署，内存状态不共享 | ❌ 不支持 | Token黑名单/限流改用Redis |
| **负载均衡** | Nginx反向代理但仅单后端 | ❌ 缺失 | 配置多后端upstream |
| **服务拆分** | 单体FastAPI应用 | ❌ 未拆分 | 按业务域拆分（当前非必需） |
| **读写分离** | 未实现 | ❌ 缺失 | RDS只读副本 + SQLAlchemy读写路由 |
| **消息队列** | 未引入 | ❌ 缺失 | 适合异步任务（PDF生成、通知等） |
| **配置中心** | pydantic-settings + .env | ⚠️ 基本满足 | 考虑Nacos/Apollo |
| **API网关** | Nginx充当简单网关 | ⚠️ 功能有限 | 当前够用，后续可引入Kong |

---

## 十、部署与CI/CD审查

### 10.1 Docker配置

| 容器 | 基础镜像 | 构建方式 | 安全特性 |
|------|----------|----------|----------|
| PC前端 | node:22-alpine → nginx:1.25-alpine | 多阶段构建 | 非root用户、健康检查 |
| H5前端 | node:22-alpine → nginx:1.25-alpine | 多阶段构建 | 非root用户、健康检查 |
| 后端 | python:3.11-slim → python:3.11-slim | 多阶段构建 | 非root用户、健康检查、中文字体 |

#### Docker问题

| 严重度 | 问题 | 位置 |
|--------|------|------|
| 🔴 高 | **PC Dockerfile无构建缓存分层**：`COPY . .` 在 `npm install` 之前 | Dockerfile |
| 🔴 高 | **H5 Dockerfile `|| true` 隐藏错误**：shared包安装失败被静默忽略 | H5/Dockerfile |
| 🟡 中 | **5个docker-compose文件**：功能重叠，维护困难 | 根目录 + docker/ |

### 10.2 CI/CD配置

#### CI Pipeline（4个并行Job）

1. **PC Frontend**：Node 20、npm ci、lint、typecheck、build
2. **H5 Frontend**：Node 20、npm ci、typecheck、build
3. **Backend**：Python 3.11、pip install、ruff lint、pytest + coverage
4. **Security Scan**：Trivy漏洞扫描

#### CD Production

1. 依赖CI的4个Job全部通过
2. 构建并推送3个Docker镜像到Docker Hub
3. SSH部署到生产服务器
4. 健康检查
5. Slack通知

#### CI/CD问题

| 严重度 | 问题 | 位置 |
|--------|------|------|
| 🟡 中 | **lint设置continue-on-error**：代码质量门禁降低 | ci.yml |
| 🟡 中 | **未运行前端测试**：CI只运行后端pytest | ci.yml |
| 🟡 中 | **CD跨workflow依赖可能不生效** | cd-production.yml |

### 10.3 Nginx配置

| 特性 | 状态 | 说明 |
|------|------|------|
| HTTP→HTTPS重定向 | ✅ | 301永久重定向 |
| TLS版本 | ✅ | TLSv1.2 + TLSv1.3 |
| HSTS | ✅ | max-age=63072000（2年） |
| WebSocket支持 | ✅ | Upgrade/Connection头 |
| Gzip压缩 | ✅ | 已启用 |
| 静态资源缓存 | ✅ | proxy_cache 1天 |
| API文档屏蔽 | ✅ | 测试环境屏蔽/docs/redoc |
| 上传大小限制 | ✅ | 50MB |

---

## 十一、核心问题TOP 10

| 排名 | 问题 | 严重度 | 影响范围 |
|------|------|--------|----------|
| 1 | 敏感信息泄露（阿里云Key/数据库密码硬编码在配置文件和部署脚本中） | 🔴 P0 | 安全 |
| 2 | CSRF防护完全缺失 | 🔴 P0 | 安全 |
| 3 | CSP策略包含unsafe-inline/unsafe-eval，XSS防护失效 | 🔴 P1 | 安全 |
| 4 | Token黑名单/限流基于内存，多实例部署不共享 | 🔴 P1 | 扩展性 |
| 5 | TypeScript严格检查几乎全部关闭 | 🟡 P2 | 代码质量 |
| 6 | 三套缓存实现重复 | 🟡 P2 | 可维护性 |
| 7 | main.py过于臃肿（699行） | 🟡 P2 | 可维护性 |
| 8 | 部分路由绕过Service层直接操作数据库 | 🟡 P2 | 架构一致性 |
| 9 | 缺少监控告警和日志聚合 | 🟡 P2 | 可观测性 |
| 10 | 非真正monorepo，依赖管理分散 | 🟢 P3 | 开发效率 |

---

## 十二、架构重构方案

### 12.1 重构目标

1. **安全加固**：消除密钥泄露、加强CSP/CSRF防护、收紧CORS
2. **类型安全**：开启TypeScript严格模式，统一缓存实现
3. **可扩展性**：支持水平扩展、引入Redis共享状态、数据库读写分离
4. **可观测性**：完善监控告警、结构化日志、前端异常上报
5. **代码质量**：清理技术债务、统一架构模式、完善测试覆盖

### 12.2 实施步骤

#### 第一阶段：紧急修复（1-2周）

| 步骤 | 内容 | 风险 | 预期收益 |
|------|------|------|----------|
| 1.1 | 轮换所有泄露密钥：阿里云AccessKey、数据库密码、SECRET_KEY | 低 | 消除严重安全隐患 |
| 1.2 | 密钥外部化：将deploy脚本和docker-compose中的硬编码凭据改为环境变量 | 低 | 防止后续泄露 |
| 1.3 | 检查Git历史：确认敏感文件是否曾被提交，必要时清理 | 中 | 彻底消除泄露 |
| 1.4 | 收紧CORS：`allow_headers` 从 `["*"]` 改为具体列表 | 低 | 降低跨域攻击风险 |
| 1.5 | 修复H5 Dockerfile `|| true`：不应静默忽略shared包安装失败 | 低 | 防止构建隐患 |

#### 第二阶段：安全加固（2-3周）

| 步骤 | 内容 | 风险 | 预期收益 |
|------|------|------|----------|
| 2.1 | 加强CSP策略：移除 `unsafe-inline`/`unsafe-eval`，改用nonce/hash | 中（需测试兼容性） | 有效防XSS |
| 2.2 | 添加CSRF防护：SameSite Cookie + CSRF Token双重防御 | 低 | 深度防御 |
| 2.3 | 限流改用Redis：替换内存限流，支持多实例 | 低 | 支持水平扩展 |
| 2.4 | Token黑名单改用Redis：替换内存黑名单 | 低 | 支持多实例 |
| 2.5 | 加强密码策略：最小8位 + 复杂度要求 + 强制修改期限 | 低 | 防暴力破解 |
| 2.6 | 添加Permissions-Policy头 | 低 | 限制浏览器功能 |

#### 第三阶段：架构优化（3-4周）

| 步骤 | 内容 | 风险 | 预期收益 |
|------|------|------|----------|
| 3.1 | 拆分main.py：文件服务→files路由，迁移端点→migration路由，常量→config | 低 | 代码可维护性 |
| 3.2 | 统一缓存实现：合并三套缓存为一套，基于shared包 | 中 | 减少重复代码 |
| 3.3 | userStore统一为Pinia：PC端迁移到Pinia defineStore | 中 | DevTools集成 |
| 3.4 | 开启TypeScript严格模式：先开启 `strictNullChecks`，逐步开启其他 | 中（需修复类型错误） | 类型安全 |
| 3.5 | 模型to_dict()迁移到Pydantic：使用 `from_attributes=True` | 中 | 减少重复代码 |
| 3.6 | photos字段改用JSONB：数据库迁移 + 模型更新 | 中 | 查询性能提升 |
| 3.7 | 重构路由遵循分层：auth.py/work_order.py通过Service层访问 | 中 | 架构一致性 |
| 3.8 | 添加环境变量文件体系：`.env.development` / `.env.staging` / `.env.production` | 低 | 多环境部署 |

#### 第四阶段：可观测性与扩展性（4-6周）

| 步骤 | 内容 | 风险 | 预期收益 |
|------|------|------|----------|
| 4.1 | 配置Grafana：连接Prometheus，创建监控仪表盘 | 低 | 可视化监控 |
| 4.2 | 配置告警规则：CPU/内存/错误率/响应时间阈值告警 | 低 | 主动发现问题 |
| 4.3 | 结构化日志：JSON格式 + ELK/Loki采集 | 中 | 日志分析效率 |
| 4.4 | 前端异常上报：集成Sentry | 低 | 前端问题追踪 |
| 4.5 | Nginx负载均衡：配置多后端upstream | 中 | 水平扩展 |
| 4.6 | 数据库读写分离：RDS只读副本 + SQLAlchemy读写路由 | 中 | 查询性能提升 |
| 4.7 | 引入pnpm workspaces：统一管理3个前端包依赖 | 中 | 依赖管理效率 |

#### 第五阶段：持续优化（长期）

| 步骤 | 内容 | 风险 | 预期收益 |
|------|------|------|----------|
| 5.1 | 完善测试覆盖：核心业务逻辑单元测试 + API集成测试 | 低 | 代码质量保障 |
| 5.2 | 前端测试纳入CI：ci.yml添加vitest步骤 | 低 | 持续质量保障 |
| 5.3 | Dockerfile缓存优化：先COPY package.json再npm install | 低 | 构建速度提升 |
| 5.4 | 清理技术债务：重构残留文件、FIXME、重复代码 | 低 | 代码整洁度 |
| 5.5 | H5移动端适配：引入postcss-px-to-viewport | 中 | 多设备适配 |
| 5.6 | API文档中英统一：统一为中文或英文 | 低 | 文档一致性 |

### 12.3 资源需求评估

| 阶段 | 人力 | 时间 | 外部依赖 |
|------|------|------|----------|
| 第一阶段 | 1人 | 1-2周 | 阿里云密钥轮换 |
| 第二阶段 | 1-2人 | 2-3周 | Redis部署 |
| 第三阶段 | 2人 | 3-4周 | 无 |
| 第四阶段 | 2人 | 4-6周 | Grafana/Sentry/ELK |
| 第五阶段 | 1-2人 | 持续 | 无 |

### 12.4 风险评估

| 风险 | 概率 | 影响 | 缓解措施 |
|------|------|------|----------|
| CSP收紧导致前端功能异常 | 中 | 高 | 先在report-only模式观察，逐步收紧 |
| TypeScript严格模式引发大量类型错误 | 高 | 中 | 逐文件开启，新代码强制执行 |
| 数据库JSONB迁移数据丢失 | 低 | 高 | 先备份，在测试环境验证 |
| Redis单点故障 | 低 | 高 | 配置Redis哨兵或集群模式 |
| 密钥轮换影响在线服务 | 中 | 高 | 在低峰期操作，准备回滚方案 |

### 12.5 预期收益分析

| 收益维度 | 短期（1-2月） | 中期（3-6月） | 长期（6月+） |
|----------|---------------|---------------|--------------|
| **安全性** | 消除密钥泄露、加强认证 | CSP/CSRF防护完善 | 全面安全合规 |
| **可维护性** | main.py拆分、缓存统一 | 分层架构一致、类型安全 | 技术债务清零 |
| **可扩展性** | Redis共享状态 | 负载均衡、读写分离 | 微服务拆分基础 |
| **可观测性** | 结构化日志 | Grafana监控+告警 | 全链路追踪 |
| **开发效率** | 环境变量体系 | pnpm workspaces | CI/CD完善 |

---

## 十三、架构优势总结

1. **Monorepo共享包设计** — 类型、API端点、权限、工具函数跨PC/H5端复用，是项目最大的架构亮点
2. **后端四层分离** — API → Service → Repository → Model 职责清晰，BaseRepository/BaseService减少重复代码
3. **双引擎数据库** — 同时支持同步(psycopg2)和异步(asyncpg)操作，提供渐进式迁移路径
4. **完善的认证体系** — JWT双Token + 自动刷新 + 黑名单 + 登录锁定 + 密码迁移
5. **构建优化完善** — 代码分割、Gzip压缩、Tree-shaking、虚拟滚动均已实现
6. **OSS双存储降级** — OSS优先，数据库降级，保证可用性
7. **钉钉免登集成** — 自动检测环境、获取授权码、后端认证，流程完整
8. **Docker最佳实践** — 多阶段构建、非root用户、健康检查、国内镜像源
9. **安全响应头完整** — HSTS/X-Content-Type-Options/X-Frame-Options/X-XSS-Protection
10. **请求追踪** — request_id贯穿日志，便于问题排查

---

> **审查结论**：项目架构设计合理，Monorepo共享方案和分层架构是亮点。主要问题集中在安全防护（密钥泄露、CSRF缺失、CSP削弱）、类型安全（TS严格模式关闭）、可扩展性（内存状态不共享）三个方面。建议按照五阶段重构方案逐步优化，优先处理P0级别的安全问题。
