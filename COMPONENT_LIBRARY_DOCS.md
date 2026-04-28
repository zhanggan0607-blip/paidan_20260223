# SSTCP 共享组件库文档

## 📚 文档概览

本文档提供了 SSTCP 项目共享组件库的完整使用指南，包括组件 API、示例代码和最佳实践。

---

## 🎯 组件列表

| 组件名称 | 说明 | 适用平台 |
|---------|------|----------|
| [SearchInput](#searchinput) | 搜索输入框组件 | PC / H5 |
| [LoadingSpinner](#loadingspinner) | 加载动画组件 | PC / H5 |
| [Toast](#toast) | 提示消息组件 | PC / H5 |

---

## 🔧 快速开始

### 安装

组件已包含在 `@sstcp/shared` 包中，无需额外安装。

### 使用方式

```typescript
// 方式 1：按需导入
import { SearchInput, LoadingSpinner, Toast } from '@sstcp/shared'

// 方式 2：导入所有组件
import * as Components from '@sstcp/shared'
const { SearchInput, LoadingSpinner, Toast } = Components
```

---

## 📦 组件详细文档

---

## SearchInput

搜索输入框组件，支持历史记录、键盘导航和触摸事件。

### 基础用法

```vue
<template>
  <SearchInput
    v-model="searchText"
    field-key="customer-search"
    placeholder="搜索客户..."
    @search="handleSearch"
  />
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { SearchInput } from '@sstcp/shared'

const searchText = ref('')

const handleSearch = (query: string) => {
  console.log('搜索:', query)
  // 执行搜索逻辑
}
</script>
```

### Props

| 参数 | 说明 | 类型 | 默认值 | 必填 |
|------|------|------|--------|------|
| `modelValue` | 输入值（支持 v-model） | `string` | `''` | 否 |
| `placeholder` | 占位符文本 | `string` | `'请输入'` | 否 |
| `fieldKey` | 字段标识（用于历史记录存储） | `string` | - | **是** |
| `width` | 输入框宽度 | `string` | `'200px'` | 否 |
| `enableKeyboardNav` | 是否启用键盘导航 | `boolean` | `true` | 否 |

### Events

| 事件名 | 说明 | 回调参数 |
|--------|------|----------|
| `update:modelValue` | 输入值变化时触发 | `(value: string)` |
| `search` | 执行搜索时触发 | `(query: string)` |
| `input` | 输入时触发 | `(value: string)` |

### 平台差异

#### PC 端使用

```vue
<template>
  <SearchInput
    v-model="searchText"
    field-key="customer-search"
    width="200px"
    :enable-keyboard-nav="true"
    @search="handleSearch"
  />
</template>
```

**特点：**
- ✅ 支持键盘导航（↑↓ Enter Escape）
- ✅ 固定宽度 200px
- ✅ 鼠标悬停高亮

#### H5 端使用

```vue
<template>
  <SearchInput
    v-model="searchText"
    field-key="customer-search"
    width="100%"
    :enable-keyboard-nav="false"
    @search="handleSearch"
  />
</template>
```

**特点：**
- ✅ 全宽显示（100%）
- ✅ 触摸事件优化
- ✅ 禁用键盘导航（移动端不需要）

### 高级用法

#### 自定义宽度

```vue
<template>
  <SearchInput
    v-model="searchText"
    field-key="project-search"
    width="300px"
    placeholder="搜索项目..."
    @search="handleSearch"
  />
</template>
```

#### 禁用键盘导航

```vue
<template>
  <SearchInput
    v-model="searchText"
    field-key="personnel-search"
    :enable-keyboard-nav="false"
    @search="handleSearch"
  />
</template>
```

### 样式定制

组件使用 scoped 样式，如需定制，可以通过深度选择器：

```vue
<style>
/* 修改输入框样式 */
:deep(.search-input) {
  border-radius: 8px;
  border-color: #1890ff;
}

/* 修改下拉菜单样式 */
:deep(.search-dropdown) {
  border-radius: 8px;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.2);
}
</style>
```

---

## LoadingSpinner

加载动画组件，支持全屏和局部加载模式。

### 基础用法

```vue
<template>
  <LoadingSpinner
    :visible="loading"
    text="加载中..."
  />
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { LoadingSpinner } from '@sstcp/shared'

const loading = ref(false)

const fetchData = async () => {
  loading.value = true
  try {
    // 执行异步操作
    await api.getData()
  } finally {
    loading.value = false
  }
}
</script>
```

### Props

| 参数 | 说明 | 类型 | 默认值 | 必填 |
|------|------|------|--------|------|
| `visible` | 是否显示加载动画 | `boolean` | `false` | 否 |
| `text` | 加载文本 | `string` | `'加载中...'` | 否 |
| `size` | 加载图标大小 | `string` | `'50px'` | 否 |
| `fullscreen` | 是否全屏显示 | `boolean` | `true` | 否 |

### 使用场景

#### 全屏加载

```vue
<template>
  <LoadingSpinner
    :visible="loading"
    text="正在加载数据..."
    size="50px"
    :fullscreen="true"
  />
</template>
```

**适用场景：**
- 页面初始化加载
- 大量数据请求
- 路由切换

#### 局部加载

```vue
<template>
  <div class="card">
    <LoadingSpinner
      :visible="loading"
      text="加载中..."
      size="30px"
      :fullscreen="false"
    />
    <div v-if="!loading">
      <!-- 内容 -->
    </div>
  </div>
</template>

<style scoped>
.card {
  position: relative;
  min-height: 200px;
}
</style>
```

**适用场景：**
- 卡片内容加载
- 表格数据加载
- 组件内部加载

### 高级用法

#### 自定义大小

```vue
<template>
  <!-- 小尺寸 -->
  <LoadingSpinner
    :visible="loading"
    size="30px"
  />
  
  <!-- 中等尺寸 -->
  <LoadingSpinner
    :visible="loading"
    size="50px"
  />
  
  <!-- 大尺寸 -->
  <LoadingSpinner
    :visible="loading"
    size="80px"
  />
</template>
```

#### 动态文本

```vue
<template>
  <LoadingSpinner
    :visible="loading"
    :text="loadingText"
  />
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { LoadingSpinner } from '@sstcp/shared'

const loading = ref(false)
const loadingStage = ref(0)

const loadingText = computed(() => {
  const stages = [
    '正在加载数据...',
    '正在处理数据...',
    '正在渲染页面...'
  ]
  return stages[loadingStage.value] || '加载中...'
})

const loadData = async () => {
  loading.value = true
  loadingStage.value = 0
  
  await api.getData()
  loadingStage.value = 1
  
  await api.processData()
  loadingStage.value = 2
  
  loading.value = false
}
</script>
```

### 样式定制

```vue
<style>
/* 修改加载动画颜色 */
:deep(.loading-spinner) {
  border-top-color: #1890ff;
  border-right-color: #1890ff;
}

/* 修改加载文本样式 */
:deep(.loading-text) {
  color: #1890ff;
  font-size: 18px;
}

/* 修改遮罩层背景 */
:deep(.loading-overlay) {
  background: rgba(255, 255, 255, 0.95);
}
</style>
```

---

## Toast

提示消息组件，支持多种类型和位置。

### 基础用法

```vue
<template>
  <Toast
    :visible="toast.visible"
    :message="toast.message"
    :type="toast.type"
  />
</template>

<script setup lang="ts">
import { reactive } from 'vue'
import { Toast } from '@sstcp/shared'

const toast = reactive({
  visible: false,
  message: '',
  type: 'info' as 'success' | 'error' | 'warning' | 'info'
})

const showToast = (message: string, type: typeof toast.type = 'info') => {
  toast.message = message
  toast.type = type
  toast.visible = true
}

// 使用示例
showToast('操作成功！', 'success')
showToast('操作失败！', 'error')
showToast('请注意！', 'warning')
showToast('提示信息', 'info')
</script>
```

### Props

| 参数 | 说明 | 类型 | 默认值 | 必填 |
|------|------|------|--------|------|
| `visible` | 是否显示提示 | `boolean` | `false` | 否 |
| `message` | 提示消息内容 | `string` | - | **是** |
| `type` | 提示类型 | `'success' \| 'error' \| 'warning' \| 'info'` | `'info'` | 否 |
| `duration` | 显示时长（毫秒） | `number` | `3000` | 否 |
| `position` | 显示位置 | `'top-right' \| 'top-center' \| 'bottom-center'` | `'top-right'` | 否 |

### 提示类型

#### 成功提示

```vue
<template>
  <Toast
    :visible="true"
    message="操作成功！"
    type="success"
  />
</template>
```

**样式：** 绿色背景，✓ 图标

#### 错误提示

```vue
<template>
  <Toast
    :visible="true"
    message="操作失败！"
    type="error"
  />
</template>
```

**样式：** 红色背景，✕ 图标

#### 警告提示

```vue
<template>
  <Toast
    :visible="true"
    message="请注意！"
    type="warning"
  />
</template>
```

**样式：** 橙色背景，! 图标

#### 信息提示

```vue
<template>
  <Toast
    :visible="true"
    message="提示信息"
    type="info"
  />
</template>
```

**样式：** 蓝色背景，ℹ 图标

### 显示位置

#### 右上角（PC 默认）

```vue
<template>
  <Toast
    :visible="true"
    message="提示消息"
    position="top-right"
  />
</template>
```

#### 顶部居中（H5 推荐）

```vue
<template>
  <Toast
    :visible="true"
    message="提示消息"
    position="top-center"
  />
</template>
```

#### 底部居中

```vue
<template>
  <Toast
    :visible="true"
    message="提示消息"
    position="bottom-center"
  />
</template>
```

### 高级用法

#### 自定义显示时长

```vue
<template>
  <!-- 快速提示 -->
  <Toast
    :visible="true"
    message="操作成功"
    :duration="1500"
  />
  
  <!-- 长时间提示 -->
  <Toast
    :visible="true"
    message="请仔细阅读提示内容"
    :duration="5000"
  />
</template>
```

#### 封装 Toast 服务

```typescript
// src/utils/toast.ts
import { reactive } from 'vue'
import { Toast } from '@sstcp/shared'

const toast = reactive({
  visible: false,
  message: '',
  type: 'info' as 'success' | 'error' | 'warning' | 'info',
  duration: 3000,
  position: 'top-right' as 'top-right' | 'top-center' | 'bottom-center'
})

export const useToast = () => {
  const show = (
    message: string,
    type: typeof toast.type = 'info',
    duration: number = 3000,
    position: typeof toast.position = 'top-right'
  ) => {
    toast.message = message
    toast.type = type
    toast.duration = duration
    toast.position = position
    toast.visible = true
  }

  const success = (message: string) => show(message, 'success')
  const error = (message: string) => show(message, 'error')
  const warning = (message: string) => show(message, 'warning')
  const info = (message: string) => show(message, 'info')

  return {
    toast,
    show,
    success,
    error,
    warning,
    info
  }
}
```

**使用示例：**

```vue
<template>
  <Toast
    :visible="toast.visible"
    :message="toast.message"
    :type="toast.type"
    :duration="toast.duration"
    :position="toast.position"
  />
  
  <button @click="handleSuccess">成功</button>
  <button @click="handleError">错误</button>
</template>

<script setup lang="ts">
import { Toast } from '@sstcp/shared'
import { useToast } from '@/utils/toast'

const { toast, success, error } = useToast()

const handleSuccess = () => {
  success('操作成功！')
}

const handleError = () => {
  error('操作失败！')
}
</script>
```

### 样式定制

```vue
<style>
/* 修改提示框样式 */
:deep(.toast) {
  border-radius: 12px;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.2);
}

/* 修改成功提示样式 */
:deep(.toast-success) {
  background: #52c41a;
}

/* 修改图标样式 */
:deep(.toast-icon) {
  font-size: 20px;
}

/* 修改消息文本样式 */
:deep(.toast-message) {
  font-size: 16px;
}
</style>
```

---

## 🎯 最佳实践

### 1. 组件导入

```typescript
// ✅ 推荐：按需导入
import { SearchInput, LoadingSpinner, Toast } from '@sstcp/shared'

// ❌ 不推荐：导入整个库
import * as Shared from '@sstcp/shared'
```

### 2. 平台适配

```vue
<template>
  <!-- PC 端 -->
  <SearchInput
    v-model="search"
    field-key="search"
    width="200px"
    :enable-keyboard-nav="true"
  />
  
  <!-- H5 端 -->
  <SearchInput
    v-model="search"
    field-key="search"
    width="100%"
    :enable-keyboard-nav="false"
  />
</template>
```

### 3. 状态管理

```typescript
// ✅ 推荐：使用 reactive 管理状态
const toast = reactive({
  visible: false,
  message: '',
  type: 'info'
})

// ❌ 不推荐：使用多个 ref
const toastVisible = ref(false)
const toastMessage = ref('')
const toastType = ref('info')
```

### 4. 错误处理

```typescript
// ✅ 推荐：完整的错误处理
const fetchData = async () => {
  loading.value = true
  try {
    const data = await api.getData()
    success('数据加载成功')
    return data
  } catch (error) {
    error('数据加载失败')
    throw error
  } finally {
    loading.value = false
  }
}

// ❌ 不推荐：缺少错误处理
const fetchData = async () => {
  loading.value = true
  const data = await api.getData()
  loading.value = false
  return data
}
```

---

## 📊 组件对比

| 特性 | SearchInput | LoadingSpinner | Toast |
|------|-------------|----------------|-------|
| PC 支持 | ✅ | ✅ | ✅ |
| H5 支持 | ✅ | ✅ | ✅ |
| 键盘导航 | ✅ | ❌ | ❌ |
| 触摸事件 | ✅ | ❌ | ✅ |
| 自定义样式 | ✅ | ✅ | ✅ |
| 响应式 | ✅ | ✅ | ✅ |

---

## 🎊 总结

SSTCP 共享组件库提供了 3 个高质量的通用组件，支持 PC 和 H5 双平台。通过统一的 API 设计和灵活的配置选项，可以满足各种业务场景的需求。

**核心优势：**
- ✅ 跨平台支持
- ✅ 统一的 API 设计
- ✅ 完整的 TypeScript 类型
- ✅ 灵活的样式定制
- ✅ 详细的文档和示例

**使用建议：**
1. 根据平台选择合适的配置
2. 使用 TypeScript 获得类型提示
3. 遵循最佳实践
4. 及时反馈问题和建议
