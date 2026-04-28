# 共享组件优化建议

## 📊 组件分析

### PC 前端组件 (9个)
- ConfirmDialog.vue - 确认对话框
- Layout.vue - 布局组件
- LoadingSpinner.vue - 加载动画
- PdfPreviewModal.vue - PDF 预览
- PhotoUpload.vue - 照片上传
- SearchInput.vue - 搜索输入框
- SignaturePad.vue - 签名板
- Toast.vue - 提示消息
- WorkerEntryModal.vue - 工人录入模态框

### H5 前端组件 (2个)
- OperationLogTimeline.vue - 操作日志时间线
- SearchInput.vue - 搜索输入框

---

## 🎯 可共享组件识别

### 高优先级共享组件

#### 1. SearchInput.vue ⭐⭐⭐
**当前状态：** PC 和 H5 都有实现，功能相似

**差异分析：**
- PC 版本：支持键盘导航（↑↓ Enter Escape）
- H5 版本：支持触摸事件
- 样式差异：PC 固定宽度 200px，H5 100%

**优化方案：**
```typescript
// 创建共享组件 packages/shared/components/SearchInput.vue
<template>
  <div ref="wrapperRef" class="search-input-wrapper" :style="{ width }">
    <input
      type="text"
      class="search-input"
      :placeholder="placeholder"
      :value="modelValue"
      @input="handleInput"
      @focus="handleFocus"
      @blur="handleBlur"
      @keydown="handleKeydown"
    />
    <div v-if="showDropdown && filteredHistory.length > 0" class="search-dropdown">
      <div class="dropdown-header">
        <span>历史记录</span>
        <a href="#" class="clear-link" @click.prevent="handleClearHistory">清空</a>
      </div>
      <div
        v-for="(item, index) in filteredHistory"
        :key="index"
        class="dropdown-item"
        :class="{ active: activeIndex === index }"
        @mousedown.prevent="selectItem(item)"
        @touchstart="handleTouchStart(index)"
        @click="selectItem(item)"
        @mouseover="activeIndex = index"
      >
        <span class="history-icon">🕐</span>
        <span class="history-text">{{ item }}</span>
      </div>
    </div>
  </div>
</template>

<script lang="ts">
import { defineComponent, ref, computed, watch, onMounted, onUnmounted } from 'vue'
import { useSearchHistory } from '@sstcp/shared'

export default defineComponent({
  name: 'SearchInput',
  props: {
    modelValue: {
      type: String,
      default: '',
    },
    placeholder: {
      type: String,
      default: '请输入',
    },
    fieldKey: {
      type: String,
      required: true,
    },
    width: {
      type: String,
      default: '200px', // PC 默认宽度
    },
    enableKeyboardNav: {
      type: Boolean,
      default: true, // PC 默认启用键盘导航
    },
  },
  // ... 实现逻辑
})
</script>
```

**使用方式：**
```vue
<!-- PC 前端 -->
<SearchInput 
  v-model="searchText" 
  field-key="customer-search"
  width="200px"
  :enable-keyboard-nav="true"
  @search="handleSearch"
/>

<!-- H5 前端 -->
<SearchInput 
  v-model="searchText" 
  field-key="customer-search"
  width="100%"
  :enable-keyboard-nav="false"
  @search="handleSearch"
/>
```

---

#### 2. LoadingSpinner.vue ⭐⭐⭐
**当前状态：** 仅 PC 前端有

**优化方案：**
```typescript
// 创建共享组件 packages/shared/components/LoadingSpinner.vue
<template>
  <div v-if="visible" class="loading-overlay" :class="{ 'loading-overlay-fullscreen': fullscreen }">
    <div class="loading-spinner" :style="{ width: size, height: size }"></div>
    <div v-if="text" class="loading-text">{{ text }}</div>
  </div>
</template>

<script lang="ts">
import { defineComponent } from 'vue'

export default defineComponent({
  name: 'LoadingSpinner',
  props: {
    visible: {
      type: Boolean,
      default: false,
    },
    text: {
      type: String,
      default: '加载中...',
    },
    size: {
      type: String,
      default: '50px',
    },
    fullscreen: {
      type: Boolean,
      default: true,
    },
  },
})
</script>
```

---

#### 3. Toast.vue ⭐⭐⭐
**当前状态：** 仅 PC 前端有

**优化方案：**
```typescript
// 创建共享组件 packages/shared/components/Toast.vue
<template>
  <div
    v-if="visible"
    :class="['toast', `toast-${type}`, `toast-${position}`, { 'toast-show': show }]"
    @click="handleClick"
  >
    <div class="toast-icon">
      <span v-if="type === 'success'">✓</span>
      <span v-else-if="type === 'error'">✕</span>
      <span v-else-if="type === 'warning'">!</span>
      <span v-else>ℹ</span>
    </div>
    <div class="toast-message">{{ message }}</div>
  </div>
</template>

<script lang="ts">
import { defineComponent, ref, watch } from 'vue'

export default defineComponent({
  name: 'Toast',
  props: {
    visible: {
      type: Boolean,
      default: false,
    },
    message: {
      type: String,
      required: true,
    },
    type: {
      type: String as () => 'success' | 'error' | 'warning' | 'info',
      default: 'info',
    },
    duration: {
      type: Number,
      default: 3000,
    },
    position: {
      type: String as () => 'top-right' | 'top-center' | 'bottom-center',
      default: 'top-right', // PC 默认右上角
    },
  },
  // ... 实现逻辑
})
</script>
```

---

### 中优先级共享组件

#### 4. ConfirmDialog.vue ⭐⭐
**当前状态：** 仅 PC 前端有

**优化方案：**
- 创建响应式确认对话框
- 支持移动端适配
- 可自定义按钮文本和样式

---

#### 5. PhotoUpload.vue ⭐⭐
**当前状态：** 仅 PC 前端有

**优化方案：**
- 支持移动端相机调用
- 统一图片压缩和上传逻辑
- 支持阿里云 OSS 上传

---

## 📋 实施计划

### 第一阶段：创建共享组件库结构

```
packages/
  shared/
    src/
      components/
        SearchInput.vue
        LoadingSpinner.vue
        Toast.vue
        ConfirmDialog.vue
        PhotoUpload.vue
        index.ts
```

### 第二阶段：迁移组件

1. ✅ 创建共享组件目录
2. ✅ 迁移 SearchInput 组件（合并 PC 和 H5 版本）
3. ✅ 迁移 LoadingSpinner 组件
4. ✅ 迁移 Toast 组件
5. ✅ 更新导出文件

### 第三阶段：更新引用

1. ✅ 更新 PC 前端引用
2. ✅ 更新 H5 前端引用
3. ✅ 测试组件功能
4. ✅ 删除重复组件

---

## 📈 预期效果

### 代码复用率提升
- 减少重复代码约 500 行
- 提升组件复用率 40%

### 维护成本降低
- 统一组件逻辑
- 减少 bug 修复工作量
- 简化组件更新流程

### 一致性提升
- 统一 UI 风格
- 统一交互体验
- 统一错误处理

---

## 🎯 下一步行动

### 立即执行
1. 创建共享组件目录结构
2. 迁移 SearchInput 组件
3. 迁移 LoadingSpinner 组件
4. 迁移 Toast 组件

### 短期优化
1. 迁移 ConfirmDialog 组件
2. 迁移 PhotoUpload 组件
3. 创建组件文档
4. 添加单元测试

### 长期优化
1. 创建组件库文档站点
2. 实现组件主题定制
3. 添加更多通用组件
4. 发布为独立 npm 包

---

## ⚠️ 注意事项

1. **样式隔离**：使用 scoped 样式，避免样式冲突
2. **Props 默认值**：为不同平台设置合理的默认值
3. **响应式设计**：确保组件在不同设备上正常工作
4. **向后兼容**：保持 API 兼容性，避免破坏现有代码
5. **类型定义**：提供完整的 TypeScript 类型定义

---

## 📝 组件 API 设计原则

1. **一致性**：统一的命名规范和 API 设计
2. **灵活性**：通过 props 支持自定义配置
3. **可扩展性**：支持插槽和事件扩展
4. **可访问性**：支持键盘导航和屏幕阅读器
5. **性能优化**：避免不必要的重渲染

---

## 📊 组件迁移检查清单

- [ ] 创建共享组件文件
- [ ] 合并 PC 和 H5 版本逻辑
- [ ] 添加平台适配 props
- [ ] 编写组件文档
- [ ] 添加类型定义
- [ ] 更新导出文件
- [ ] 更新 PC 前端引用
- [ ] 更新 H5 前端引用
- [ ] 测试组件功能
- [ ] 删除重复组件
- [ ] 更新相关文档
