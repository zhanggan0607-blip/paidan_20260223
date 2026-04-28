<template>
  <div class="pagination-section">
    <div class="pagination-info">
      共 {{ total }} 条记录
    </div>
    <div class="pagination-controls">
      <button
        class="page-btn page-nav"
        :disabled="currentPage === 0"
        @click="$emit('update:currentPage', currentPage - 1)"
      >
        &lt;
      </button>
      <button
        v-for="page in displayPages"
        :key="page"
        class="page-btn page-num"
        :class="{ active: page === currentPage + 1 }"
        @click="$emit('update:currentPage', page - 1)"
      >
        {{ page }}
      </button>
      <button
        class="page-btn page-nav"
        :disabled="currentPage >= totalPages - 1"
        @click="$emit('update:currentPage', currentPage + 1)"
      >
        &gt;
      </button>
      <select
        id="pageSize"
        :value="pageSize"
        name="pageSize"
        class="page-select"
        @change="$emit('update:pageSize', Number(($event.target as HTMLSelectElement).value))"
      >
        <option value="10">10 条 / 页</option>
        <option value="20">20 条 / 页</option>
        <option value="50">50 条 / 页</option>
      </select>
      <div class="page-jump">
        <span>跳至</span>
        <input
          id="jumpPage"
          :value="jumpPage"
          name="jumpPage"
          type="number"
          class="page-input"
          min="1"
          :max="totalPages"
          @input="$emit('update:jumpPage', Number(($event.target as HTMLInputElement).value))"
        >
        <span>页</span>
        <button
          class="page-btn page-go"
          @click="$emit('jump')"
        >
          Go
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'

const props = defineProps<{
  total: number
  currentPage: number
  pageSize: number
  totalPages: number
  jumpPage: number
}>()

defineEmits<{
  'update:currentPage': [value: number]
  'update:pageSize': [value: number]
  'update:jumpPage': [value: number]
  'jump': []
}>()

const displayPages = computed(() => {
  const pages: number[] = []
  const start = Math.max(1, props.currentPage - 2)
  const end = Math.min(props.totalPages, props.currentPage + 4)
  for (let i = start; i <= end; i++) {
    pages.push(i)
  }
  return pages
})
</script>

<style scoped>
.pagination-section {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 15px 20px;
  background: var(--color-bg-card);
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
  margin-top: 20px;
}

.pagination-info {
  font-size: 14px;
  color: #606266;
}

.pagination-controls {
  display: flex;
  align-items: center;
  gap: 8px;
}

.page-btn {
  padding: 6px 12px;
  border: 1px solid #dcdfe6;
  background: var(--color-bg-card);
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
  transition: all 0.2s;
}

.page-btn:hover:not(:disabled) {
  border-color: #409eff;
  color: #409eff;
}

.page-btn:disabled {
  cursor: not-allowed;
  opacity: 0.5;
}

.page-btn.active {
  background: #409eff;
  border-color: #409eff;
  color: var(--color-bg-card);
}

.page-select {
  padding: 6px 10px;
  border: 1px solid #dcdfe6;
  border-radius: 4px;
  font-size: 14px;
}

.page-jump {
  display: flex;
  align-items: center;
  gap: 5px;
  font-size: 14px;
  color: #606266;
}

.page-input {
  width: 50px;
  padding: 6px 8px;
  border: 1px solid #dcdfe6;
  border-radius: 4px;
  text-align: center;
}

.page-go {
  background: #409eff;
  border-color: #409eff;
  color: var(--color-bg-card);
}
</style>
