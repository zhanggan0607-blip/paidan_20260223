# 全局排序机制使用指南

## 📋 概述

本系统实现了**全局统一的自动排序机制**，通过请求拦截器自动对所有 API 响应数据进行排序，确保 PC 端和 H5 端的数据展示顺序完全一致。

## 🎯 核心特性

### 1. **全局自动化**
- ✅ 所有 API 响应数据自动排序
- ✅ 无需在每个页面手动调用排序函数
- ✅ PC 和 H5 端使用相同的排序逻辑

### 2. **智能时间戳提取**
自动从以下字段中提取时间戳（按优先级）：
1. `updated_at` - 最后更新时间
2. `created_at` - 创建时间
3. `last_activity` - 最后活动时间
4. `actual_completion_date` - 实际完成时间
5. `plan_end_date` - 计划结束时间
6. `plan_start_date` - 计划开始时间
7. `execution_date` - 执行时间
8. `deleted_at` - 删除时间

### 3. **灵活的配置系统**
- 可启用/禁用自动排序
- 可配置需要跳过的 API 路径
- 可注册自定义排序器
- 可动态更新排序配置

## 🚀 使用方式

### 方式一：全局自动排序（推荐）

全局排序拦截器已自动注册到 PC 和 H5 端的请求实例中，**无需任何额外配置**即可使用。

```typescript
// PC 端：src/api/request.ts
import { createSortInterceptor } from '@sstcp/shared'
createSortInterceptor(requestInstance.axiosInstance)

// H5 端：H5/src/api/request.ts
import { createSortInterceptor } from '@sstcp/shared'
createSortInterceptor(requestInstance.axiosInstance)
```

### 方式二：手动排序（针对特殊场景）

如果某些接口需要特殊的排序逻辑，可以手动调用排序函数：

```typescript
import { sortByTimestampDesc } from '@sstcp/shared'

// 基本用法
const sortedItems = sortByTimestampDesc(items)

// 带选项的用法
const sortedItems = sortByTimestampDesc(items, {
  secondarySortKey: 'id',  // 次要排序键
  ascending: false         // 是否升序（默认降序）
})

// 自定义时间戳提取
const sortedItems = sortByTimestampDesc(items, {
  getTimestamp: (item) => new Date(item.custom_date).getTime()
})
```

## ⚙️ 配置选项

### 获取当前配置

```typescript
import { getSortConfig } from '@sstcp/shared'

const config = getSortConfig()
console.log(config)
// {
//   enabled: true,
//   secondarySortKey: 'id',
//   ascending: false,
//   skipPaths: [...],
//   customSorters: {...}
// }
```

### 更新配置

```typescript
import { updateSortConfig } from '@sstcp/shared'

// 更新部分配置
updateSortConfig({
  secondarySortKey: 'updated_at',
  ascending: true
})
```

### 重置配置

```typescript
import { resetSortConfig } from '@sstcp/shared'

resetSortConfig()
```

## 🔧 高级用法

### 1. 跳过特定 API 的排序

某些接口（如统计、配置类）可能不需要排序：

```typescript
import { addSkipPath } from '@sstcp/shared'

// 添加需要跳过的路径
addSkipPath('/statistics')
addSkipPath('/config')
addSkipPath('/upload')
```

### 2. 注册自定义排序器

针对特定 API 需要特殊排序逻辑：

```typescript
import { registerCustomSorter } from '@sstcp/shared'

// 为特定 API 注册自定义排序器
registerCustomSorter('/work-plan/special-list', (data) => {
  // 自定义排序逻辑
  return data.sort((a, b) => {
    // 先按状态排序，再按时间排序
    if (a.status !== b.status) {
      return a.status.localeCompare(b.status)
    }
    return new Date(b.created_at).getTime() - new Date(a.created_at).getTime()
  })
})
```

### 3. 临时禁用/启用自动排序

```typescript
import { disableAutoSort, enableAutoSort } from '@sstcp/shared'

// 临时禁用
disableAutoSort()

// 执行不需要排序的操作
await request.get('/some-endpoint')

// 重新启用
enableAutoSort()
```

## 📊 默认排序行为

### 默认配置

```typescript
{
  enabled: true,              // 启用自动排序
  secondarySortKey: 'id',     // 时间戳相同时按 id 排序
  ascending: false,           // 降序（最新的在前）
  skipPaths: [                // 默认跳过的路径
    '/auth/',
    '/user/',
    '/statistics',
    '/config/',
    '/upload/',
  ],
  customSorters: {}           // 自定义排序器
}
```

### 处理的数据结构

全局排序拦截器会自动处理以下响应格式：

```typescript
// 格式 1：直接数组
{
  code: 200,
  data: [item1, item2, ...]
}

// 格式 2：分页对象
{
  code: 200,
  data: {
    content: [item1, item2, ...],
    totalElements: 100,
    totalPages: 10
  }
}

// 格式 3：包含多个数组的对象
{
  code: 200,
  data: {
    list1: [item1, item2, ...],
    list2: [item3, item4, ...]
  }
}
```

## 🎨 实际应用示例

### 示例 1：工单列表查询

```typescript
// PC 端或 H5 端的工单查询页面
const response = await workOrderService.getList({ page: 0, size: 20 })

// 自动排序后，最新的工单会显示在最前面
console.log(response.data.content)
// 已按 updated_at 降序排列
```

### 示例 2：巡检记录查询

```typescript
// 定期巡检查询
const response = await periodicInspectionService.getList({
  page: 0,
  size: 20,
  project_name: '某项目'
})

// 自动排序，最近的巡检记录在前
console.log(response.data.content)
```

### 示例 3：临时维修查询

```typescript
// 临时维修查询
const response = await temporaryRepairService.getList({
  page: 0,
  size: 20
})

// 自动排序，最近的维修记录在前
console.log(response.data.content)
```

## ✅ 最佳实践

1. **默认使用全局自动排序**：99% 的场景下，全局自动排序已经足够
2. **特殊情况使用自定义排序器**：如果某个接口需要特殊排序，使用 `registerCustomSorter`
3. **避免手动排序**：除非必要，不要在每个页面手动调用排序函数
4. **合理配置跳过路径**：统计类、配置类接口应该添加到跳过列表
5. **测试排序效果**：确保排序逻辑符合业务需求

## 🔍 调试技巧

### 查看排序配置

```typescript
import { getSortConfig } from '@sstcp/shared'
console.log('当前排序配置:', getSortConfig())
```

### 临时禁用排序进行对比

```typescript
import { disableAutoSort, enableAutoSort } from '@sstcp/shared'

// 禁用排序
disableAutoSort()
const data1 = await request.get('/api/list')

// 启用排序
enableAutoSort()
const data2 = await request.get('/api/list')

console.log('未排序:', data1)
console.log('已排序:', data2)
```

### 检查时间戳提取

```typescript
import { getSortTimestamp } from '@sstcp/shared'

const item = { created_at: '2024-01-01', updated_at: '2024-01-02' }
const timestamp = getSortTimestamp(item)
console.log('提取的时间戳:', timestamp)
```

## 📝 注意事项

1. **性能考虑**：排序在客户端执行，对于大数据集（>1000 条）建议在后端排序
2. **时间格式**：确保时间字段是有效的 ISO 8601 格式
3. **空值处理**：时间字段为空时会自动使用其他字段或返回 0
4. **类型安全**：所有排序函数都有完整的 TypeScript 类型支持

## 🆘 常见问题

**Q: 为什么我的数据没有排序？**
A: 检查是否将 API 路径添加到了 skipPaths，或者检查数据中是否有有效的时间字段。

**Q: 如何修改默认排序字段？**
A: 使用 `updateSortConfig({ secondarySortKey: 'updated_at' })`。

**Q: 可以按多个字段排序吗？**
A: 可以注册自定义排序器实现复杂的多字段排序。

**Q: 排序会影响性能吗？**
A: 对于小数据集（<1000 条）影响可忽略，大数据集建议在后端排序。

---

**最后更新**: 2026-04-11
**版本**: v1.0.0
