# @sstcp/shared

SSTCP 维保管理系统共享代码库，提供类型定义、工具函数和 API 封装。

## 安装

```bash
# 在 monorepo 根目录
npm install

# 或直接引用
npm install file:../packages/shared
```

## 使用指南

### 类型定义

#### API 响应类型

```typescript
import type { ApiResponse, PaginatedResponse } from '@sstcp/shared/types/api'

// 标准响应
const response: ApiResponse<User> = {
  code: 200,
  message: 'success',
  data: { id: 1, name: '张三' }
}

// 分页响应
const pageResponse: PaginatedResponse<User> = {
  code: 200,
  message: 'success',
  data: {
    items: [...],
    total: 100,
    page: 0,
    size: 10
  }
}
```

#### 模型类型

```typescript
import type {
  WorkOrder,
  Personnel,
  ProjectInfo,
  SpotWork,
  TemporaryRepair,
  PeriodicInspection,
} from '@sstcp/shared/types/models'

// 使用示例
const workOrder: WorkOrder = {
  id: 1,
  work_order_no: 'XJ-PRJ001-20260305-001',
  project_id: 'PRJ001',
  project_name: '示例项目',
  status: 'pending',
  // ...
}
```

#### 权限类型

```typescript
import type { Permission, RolePermission } from '@sstcp/shared/types/permission'

// 权限检查
const hasPermission = (permission: Permission): boolean => {
  // ...
}
```

### 工具函数

#### 日期格式化

```typescript
import { formatDate, formatDateTime, formatCurrency } from '@sstcp/shared/utils/format'

// 日期格式化
formatDate('2026-03-05') // '2026-03-05'
formatDate(new Date()) // '2026-03-05'

// 日期时间格式化
formatDateTime('2026-03-05T10:30:00') // '2026-03-05 10:30:00'

// 货币格式化
formatCurrency(1234.56) // '¥1,234.56'
```

#### 状态工具

```typescript
import { getStatusLabel, getStatusColor, WORK_STATUS_CONFIG } from '@sstcp/shared/utils/status'

// 获取状态标签
getStatusLabel('pending') // '待处理'
getStatusLabel('completed') // '已完成'

// 获取状态颜色
getStatusColor('pending') // 'warning'
getStatusColor('completed') // 'success'

// 状态配置
WORK_STATUS_CONFIG.forEach((config) => {
  console.log(config.value, config.label, config.color)
})
```

#### 水印工具

```typescript
import { addWatermark } from '@sstcp/shared/utils/watermark'

// 添加水印
const watermarkedImage = await addWatermark(imageFile, {
  name: '张三',
  time: '2026-03-05 10:30:00',
  location: '31.2304,121.4737',
})
```

#### 安全存储

```typescript
import { secureStorage } from '@sstcp/shared/utils/secureStorage'

// 存储数据
secureStorage.setItem('token', 'xxx')

// 读取数据
const token = secureStorage.getItem('token')

// 删除数据
secureStorage.removeItem('token')
```

#### 搜索历史

```typescript
import { searchHistory } from '@sstcp/shared/utils/searchHistory'

// 添加搜索记录
searchHistory.add('project', '项目名称')

// 获取搜索历史
const history = searchHistory.get('project')

// 清除搜索历史
searchHistory.clear('project')
```

### API 端点

```typescript
import { API_ENDPOINTS } from '@sstcp/shared/api/endpoints'

// 工单相关
API_ENDPOINTS.WORK_ORDERS.LIST // '/work-orders'
API_ENDPOINTS.WORK_ORDERS.DETAIL(id) // `/work-orders/${id}`
API_ENDPOINTS.WORK_ORDERS.CREATE // '/work-orders'
API_ENDPOINTS.WORK_ORDERS.UPDATE(id) // `/work-orders/${id}`
API_ENDPOINTS.WORK_ORDERS.DELETE(id) // `/work-orders/${id}`

// 项目信息
API_ENDPOINTS.PROJECT_INFO.LIST // '/project-info'
API_ENDPOINTS.PROJECT_INFO.DETAIL(id) // `/project-info/${id}`

// 人员管理
API_ENDPOINTS.PERSONNEL.LIST // '/personnel'
API_ENDPOINTS.PERSONNEL.DETAIL(id) // `/personnel/${id}`

// 零星用工
API_ENDPOINTS.SPOT_WORK.LIST // '/spot-work'
API_ENDPOINTS.SPOT_WORK.DETAIL(id) // `/spot-work/${id}`

// 临时维修
API_ENDPOINTS.TEMPORARY_REPAIR.LIST // '/temporary-repair'
API_ENDPOINTS.TEMPORARY_REPAIR.DETAIL(id) // `/temporary-repair/${id}`
```

### 请求封装

```typescript
import { createRequest } from '@sstcp/shared/api/request'

// 创建请求实例
const request = createRequest({
  baseURL: 'http://localhost:8000',
  timeout: 30000,
  getToken: () => localStorage.getItem('token'),
  getUser: () => JSON.parse(localStorage.getItem('user') || 'null'),
})

// 使用示例
const response = await request.get('/work-orders')
const result = await request.post('/work-orders', { ...data })
```

## 目录结构

```
packages/shared/src/
├── api/
│   ├── endpoints.ts    # API 端点定义
│   ├── request.ts      # 请求封装工厂
│   └── index.ts        # 导出入口
├── types/
│   ├── api.ts          # API 类型定义
│   ├── permission.ts   # 权限类型定义
│   ├── models/         # 数据模型类型
│   │   ├── common.ts
│   │   ├── workOrder.ts
│   │   ├── personnel.ts
│   │   └── ...
│   └── index.ts        # 导出入口
├── utils/
│   ├── format.ts       # 格式化工具
│   ├── status.ts       # 状态工具
│   ├── watermark.ts    # 水印工具
│   ├── secureStorage.ts # 安全存储
│   ├── searchHistory.ts # 搜索历史
│   ├── errorMonitor.ts  # 错误监控
│   └── index.ts        # 导出入口
└── index.ts            # 主导出入口
```

## 导出配置

```json
{
  "exports": {
    ".": "./src/index.ts",
    "./types": "./src/types/index.ts",
    "./types/api": "./src/types/api.ts",
    "./types/permission": "./src/types/permission.ts",
    "./utils": "./src/utils/index.ts",
    "./utils/format": "./src/utils/format.ts",
    "./utils/status": "./src/utils/status.ts",
    "./utils/watermark": "./src/utils/watermark.ts",
    "./api": "./src/api/index.ts",
    "./api/endpoints": "./src/api/endpoints.ts",
    "./api/request": "./src/api/request.ts"
  }
}
```

## 开发

```bash
# 构建
npm run build

# 类型检查
npm run typecheck

# 生成 OpenAPI 类型
npm run generate:types
```

## 注意事项

1. 所有导出都使用 TypeScript 类型
2. 工具函数应保持纯函数特性
3. API 端点使用常量定义，避免硬编码
4. 类型定义应与后端模型保持一致
