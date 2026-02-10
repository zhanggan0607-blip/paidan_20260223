# 前端API集成文档

## 概述

本文档说明了SSTCP维护系统前端与后端API的集成实现，包括axios配置、请求拦截器、响应拦截器、错误处理和所有CRUD操作的实现。

## 架构设计

### 技术栈
- **前端**: Vue 3 + TypeScript + Vite
- **后端**: Python FastAPI + PostgreSQL
- **HTTP客户端**: Axios
- **API基础URL**: http://localhost:8080/api

### 目录结构
```
src/
├── components/
│   ├── LoadingSpinner.vue      # 加载状态组件
│   └── Toast.vue              # 错误提示组件
├── services/
│   └── projectInfo.ts          # API服务层
├── utils/
│   └── api.ts                  # Axios配置和拦截器
└── views/
    └── ProjectInfoManagement.vue # 项目信息管理页面
```

## 核心功能实现

### 1. Axios配置与拦截器

**文件**: [src/utils/api.ts](file:///d:\共享文件\SSTCP-paidan260120\src\utils\api.ts)

#### 功能特性

##### 请求拦截器
- ✅ 自动添加认证令牌（从localStorage读取）
- ✅ 统一设置Content-Type为application/json
- ✅ 请求超时处理（10秒）

##### 响应拦截器
- ✅ 统一响应数据格式（自动返回response.data）
- ✅ 错误状态码处理
  - 401: 未授权，自动清除token
  - 403: 没有权限
  - 404: 资源不存在
  - 422: 参数验证失败
  - 500: 服务器内部错误
- ✅ 网络错误处理
- ✅ 请求配置错误处理

#### 配置代码
```typescript
const apiClient = axios.create({
  baseURL: 'http://localhost:8080/api',
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
})
```

### 2. API服务层

**文件**: [src/services/projectInfo.ts](file:///d:\共享文件\SSTCP-paidan260120\src\services\projectInfo.ts)

#### 接口定义

```typescript
export interface ProjectInfo {
  id: number
  project_id: string
  project_name: string
  completion_date: string
  maintenance_end_date: string
  maintenance_period: string
  client_name: string
  address: string
  project_abbr?: string
  client_contact?: string
  client_contact_position?: string
  client_contact_info?: string
  created_at: string
  updated_at: string
}

export interface ApiResponse<T> {
  code: number
  message: string
  data: T
}

export interface PaginatedResponse {
  code: number
  message: string
  data: {
    content: ProjectInfo[]
    totalElements: number
    totalPages: number
    size: number
    number: number
    first: boolean
    last: boolean
  }
}
```

#### API方法

| 方法 | 端点 | 功能 | HTTP方法 |
|------|--------|------|----------|
| getList | /project-info | 获取项目列表（分页） | GET |
| getById | /project-info/{id} | 根据ID获取项目 | GET |
| create | /project-info | 创建新项目 | POST |
| update | /project-info/{id} | 更新项目 | PUT |
| delete | /project-info/{id} | 删除项目 | DELETE |
| getAll | /project-info/all/list | 获取所有项目（不分页） | GET |

#### 使用示例
```typescript
// 获取分页列表
const response = await projectInfoService.getList({
  page: 0,
  size: 10,
  project_name: '智慧城市',
  client_name: '上海'
})

// 创建项目
const response = await projectInfoService.create({
  project_id: 'PRJ001',
  project_name: '测试项目',
  completion_date: '2026-01-26',
  maintenance_end_date: '2027-01-26',
  maintenance_period: '1年',
  client_name: '测试客户',
  address: '测试地址'
})

// 更新项目
const response = await projectInfoService.update(1, {
  project_id: 'PRJ001',
  project_name: '更新后的项目',
  // ... 其他字段
})

// 删除项目
const response = await projectInfoService.delete(1)
```

### 3. UI组件

#### LoadingSpinner组件

**文件**: [src/components/LoadingSpinner.vue](file:///d:\共享文件\SSTCP-paidan260120\src\components\LoadingSpinner.vue)

**功能**:
- 显示加载动画（旋转圆圈）
- 可自定义加载文本
- 全屏覆盖层

**使用**:
```vue
<LoadingSpinner :visible="loading" text="加载中..." />
```

#### Toast组件

**文件**: [src/components/Toast.vue](file:///d:\共享文件\SSTCP-paidan260120\src\components\Toast.vue)

**功能**:
- 支持4种类型：success、error、warning、info
- 自动3秒后消失
- 可自定义显示时长
- 点击可关闭

**使用**:
```vue
<Toast 
  :visible="toast.visible" 
  :message="toast.message" 
  :type="toast.type" 
/>
```

### 4. 项目信息管理页面

**文件**: [src/views/ProjectInfoManagement.vue](file:///d:\共享文件\SSTCP-paidan260120\src\views\ProjectInfoManagement.vue)

#### 实现的功能

##### 数据加载
- ✅ 页面加载时自动获取数据
- ✅ 分页切换时自动加载
- ✅ 搜索时自动加载
- ✅ 显示加载状态

##### 增删改查操作

**创建项目（POST）**:
- ✅ 表单验证（必填字段检查）
- ✅ 调用POST /api/project-info
- ✅ 保存中状态显示
- ✅ 成功后显示提示并刷新列表
- ✅ 错误处理和友好提示

**更新项目（PUT）**:
- ✅ 表单验证
- ✅ 调用PUT /api/project-info/{id}
- ✅ 保存中状态显示
- ✅ 成功后显示提示并刷新列表
- ✅ 错误处理和友好提示

**删除项目（DELETE）**:
- ✅ 确认对话框
- ✅ 调用DELETE /api/project-info/{id}
- ✅ 成功后显示提示并刷新列表
- ✅ 错误处理和友好提示

**查看项目（GET）**:
- ✅ 只读模式显示
- ✅ 调用GET /api/project-info/{id}
- ✅ 日期格式化显示

**搜索功能**:
- ✅ 项目名称模糊搜索
- ✅ 客户名称模糊搜索
- ✅ 实时搜索（防抖）
- ✅ 搜索后重置到第一页

**分页功能**:
- ✅ 页码切换
- ✅ 每页大小切换（10/20/50）
- ✅ 跳转到指定页
- ✅ 显示总记录数和总页数

#### 错误处理

所有API调用都包含完整的错误处理：

```typescript
try {
  const response = await projectInfoService.getList()
  if (response.code === 200) {
    // 处理成功响应
    projectData.value = response.data.content
    totalElements.value = response.data.totalElements
    totalPages.value = response.data.totalPages
  } else {
    // 显示错误提示
    showToast(response.message || '加载数据失败', 'error')
  }
} catch (error: any) {
  console.error('加载数据失败:', error)
  showToast(error.message || '加载数据失败，请检查网络连接', 'error')
} finally {
  loading.value = false
}
```

## API端点说明

### GET /api/project-info
获取项目列表，支持分页和搜索

**请求参数**:
- `page`: 页码（从0开始）
- `size`: 每页大小（1-100）
- `project_name`: 项目名称（模糊查询，可选）
- `client_name`: 客户名称（模糊查询，可选）

**响应格式**:
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "content": [...],
    "totalElements": 100,
    "totalPages": 10,
    "size": 10,
    "number": 0,
    "first": true,
    "last": false
  }
}
```

### GET /api/project-info/{id}
根据ID获取单个项目信息

**响应格式**:
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "id": 1,
    "project_id": "PRJ001",
    "project_name": "智慧城市综合管理平台",
    // ... 其他字段
  }
}
```

### POST /api/project-info
创建新项目

**请求体**:
```json
{
  "project_id": "PRJ001",
  "project_name": "智慧城市综合管理平台",
  "completion_date": "2026-01-26T00:00:00",
  "maintenance_end_date": "2027-01-26T00:00:00",
  "maintenance_period": "1年",
  "client_name": "北京市人民政府",
  "address": "北京市东城区长安街1号",
  "project_abbr": "智慧城市",
  "client_contact": "张三",
  "client_contact_position": "经理",
  "client_contact_info": "13800138000"
}
```

**响应格式**:
```json
{
  "code": 200,
  "message": "创建成功",
  "data": {
    "id": 7,
    // ... 其他字段
  }
}
```

**状态码**: 201 Created

### PUT /api/project-info/{id}
更新项目信息

**请求体**: 同POST请求体

**响应格式**: 同POST请求

**状态码**: 200 OK

### DELETE /api/project-info/{id}
删除项目

**响应格式**:
```json
{
  "code": 200,
  "message": "删除成功",
  "data": null
}
```

**状态码**: 200 OK

### GET /api/project-info/all/list
获取所有项目（不分页）

**响应格式**:
```json
{
  "code": 200,
  "message": "success",
  "data": [...]
}
```

## 错误处理机制

### HTTP状态码处理

| 状态码 | 处理方式 | 用户提示 |
|---------|---------|---------|
| 200 | 成功 | 操作成功 |
| 201 | 创建成功 | 创建成功 |
| 401 | 未授权 | 未授权，请重新登录 |
| 403 | 权限不足 | 没有权限访问此资源 |
| 404 | 资源不存在 | 请求的资源不存在 |
| 422 | 参数验证失败 | 参数验证失败（显示具体错误） |
| 500 | 服务器错误 | 服务器内部错误 |

### 网络错误处理

- ✅ 请求超时（10秒）
- ✅ 网络连接失败
- ✅ 请求配置错误
- ✅ 服务器无响应

### 表单验证

所有表单提交前都进行验证：

**必填字段**:
- 项目名称
- 项目编号
- 开始日期
- 结束日期
- 维保周期
- 客户单位
- 客户地址

**验证规则**:
- 字段不能为空
- 字段不能只包含空格
- 项目编号唯一性（后端验证）

## 数据流程

### 创建项目流程

```
用户填写表单
    ↓
点击保存按钮
    ↓
表单验证
    ↓
显示"保存中..."
    ↓
调用 POST /api/project-info
    ↓
等待响应
    ↓
成功？→ 显示"创建成功"提示 → 关闭弹窗 → 刷新列表
失败？→ 显示错误提示 → 保持弹窗打开
```

### 更新项目流程

```
用户点击编辑
    ↓
填充表单数据
    ↓
用户修改表单
    ↓
点击保存按钮
    ↓
表单验证
    ↓
显示"保存中..."
    ↓
调用 PUT /api/project-info/{id}
    ↓
等待响应
    ↓
成功？→ 显示"更新成功"提示 → 关闭弹窗 → 刷新列表
失败？→ 显示错误提示 → 保持弹窗打开
```

### 删除项目流程

```
用户点击删除
    ↓
显示确认对话框
    ↓
用户确认
    ↓
调用 DELETE /api/project-info/{id}
    ↓
等待响应
    ↓
成功？→ 显示"删除成功"提示 → 刷新列表
失败？→ 显示错误提示
```

## 性能优化

### 请求优化
- ✅ 请求超时设置（10秒）
- ✅ 自动取消未完成的请求
- ✅ 防抖处理搜索输入

### 用户体验优化
- ✅ 加载状态显示
- ✅ 保存中状态显示
- ✅ 友好的错误提示
- ✅ 操作成功提示
- ✅ 自动关闭提示（3秒后）
- ✅ 点击提示可关闭

## 测试指南

### 功能测试清单

- [ ] 页面加载时自动获取数据
- [ ] 分页功能正常工作
- [ ] 搜索功能正常工作
- [ ] 创建项目成功
- [ ] 编辑项目成功
- [ ] 删除项目成功
- [ ] 查看项目详情
- [ ] 网络错误时显示友好提示
- [ ] 表单验证正常工作
- [ ] 加载状态正确显示
- [ ] Toast提示正确显示和消失

### 测试步骤

1. **加载测试**
   - 访问 http://localhost:3000
   - 检查页面是否自动加载数据
   - 检查加载动画是否显示

2. **创建测试**
   - 点击"新增项目信息"按钮
   - 填写表单（故意留空一些必填字段）
   - 点击"保存"按钮
   - 验证错误提示是否正确显示
   - 填写完整表单
   - 点击"保存"按钮
   - 验证成功提示是否显示
   - 验证列表是否刷新
   - 检查数据库中是否有新记录

3. **编辑测试**
   - 点击某个项目的"编辑"按钮
   - 修改一些字段
   - 点击"保存"按钮
   - 验证成功提示是否显示
   - 验证列表是否更新
   - 检查数据库中记录是否更新

4. **删除测试**
   - 点击某个项目的"删除"按钮
   - 点击"确定"
   - 验证成功提示是否显示
   - 验证列表是否更新
   - 检查数据库中记录是否删除

5. **搜索测试**
   - 在"项目名称"输入框中输入关键词
   - 验证搜索结果是否正确
   - 在"客户名称"输入框中输入关键词
   - 验证搜索结果是否正确

6. **分页测试**
   - 点击不同的页码
   - 验证分页是否正常工作
   - 更改每页大小
   - 验证分页是否正常工作

7. **错误处理测试**
   - 停止后端服务
   - 尝试执行操作
   - 验证错误提示是否正确显示
   - 启动后端服务
   - 验证操作是否恢复正常

## 故障排查

### 常见问题

#### 1. CORS错误
**症状**: 浏览器控制台显示CORS错误

**解决方案**:
- 确保后端CORS配置正确
- 检查后端app/config.py中的cors_origins设置
- 确保前端请求的origin在允许列表中

#### 2. 网络错误
**症状**: 显示"网络错误，请检查网络连接"

**解决方案**:
- 检查后端服务是否运行
- 检查端口8080是否被占用
- 检查防火墙设置
- 检查API基础URL是否正确

#### 3. 参数验证失败
**症状**: 显示"参数验证失败"提示

**解决方案**:
- 检查必填字段是否都已填写
- 检查字段格式是否正确
- 检查维保周期是否在允许的值列表中
- 查看浏览器控制台的具体错误信息

#### 4. 404错误
**症状**: 显示"请求的资源不存在"

**解决方案**:
- 检查API端点是否正确
- 检查项目ID是否存在
- 检查后端路由配置

#### 5. 500错误
**症状**: 显示"服务器内部错误"

**解决方案**:
- 查看后端日志
- 检查数据库连接
- 检查后端代码逻辑错误

## 安全考虑

### 认证
- ✅ Token存储在localStorage
- ✅ 请求时自动添加Authorization头
- ✅ 401错误时自动清除token

### 数据验证
- ✅ 前端表单验证
- ✅ 后端参数验证
- ✅ SQL注入防护（使用ORM）

### HTTPS
- ⚠️ 当前使用HTTP（仅开发环境）
- ⚠️ 生产环境应使用HTTPS

## 部署说明

### 开发环境
- 前端: http://localhost:3000
- 后端: http://localhost:8080
- 数据库: PostgreSQL (localhost:5432/tq)

### 生产环境
需要修改的配置：

1. **API基础URL**
   ```typescript
   // src/utils/api.ts
   const API_BASE_URL = 'https://your-domain.com/api'
   ```

2. **CORS配置**
   ```python
   # backend-python/app/config.py
   cors_origins = ["https://your-frontend-domain.com"]
   ```

3. **数据库连接**
   ```env
   # backend-python/.env
   DATABASE_URL=postgresql://user:password@your-db-host:5432/database_name
   ```

## 维护建议

### 日志记录
- 前端错误已记录到浏览器控制台
- 后端错误已记录到服务器日志
- 建议添加前端错误上报系统

### 监控
- 建议添加APM（应用性能监控）
- 建议添加错误追踪（如Sentry）
- 监控API响应时间

### 备份
- 定期备份PostgreSQL数据库
- 建议使用pg_dump工具
- 备份脚本示例：
  ```bash
  pg_dump -U postgres -d tq > backup_$(date +%Y%m%d).sql
  ```

## 总结

本次前端API集成实现了：

✅ **完整的axios配置和拦截器**
- 请求拦截器（自动添加token）
- 响应拦截器（统一错误处理）
- 超时处理
- 网络错误处理

✅ **API服务层**
- 类型安全的TypeScript接口
- 完整的CRUD操作
- 分页和搜索支持

✅ **UI组件**
- LoadingSpinner组件
- Toast组件
- 友好的用户反馈

✅ **项目信息管理页面**
- 完整的增删改查功能
- 表单验证
- 错误处理
- 加载状态管理

✅ **RESTful API集成**
- GET /api/project-info（分页列表）
- GET /api/project-info/{id}（单个项目）
- POST /api/project-info（创建）
- PUT /api/project-info/{id}（更新）
- DELETE /api/project-info/{id}（删除）
- GET /api/project-info/all/list（全部列表）

✅ **用户体验优化**
- 加载状态显示
- 操作成功/失败提示
- 自动关闭提示
- 表单验证

现在前端已经完全连接到后端API，所有操作都会真实地保存到PostgreSQL数据库中！

---

**文档版本**: 1.0.0
**最后更新**: 2026-01-26
**维护者**: SSTCP技术团队