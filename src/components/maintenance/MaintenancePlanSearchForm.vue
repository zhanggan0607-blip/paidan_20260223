<template>
  <div class="search-section">
    <div class="search-form">
      <div class="search-row">
        <div class="search-item">
          <label for="search_projectName" class="search-label">项目名称：</label>
          <SearchInput
              input-id="search_projectName"
            :model-value="projectName"
            field-key="MaintenancePlanManagement_projectName"
            placeholder="请输入项目名称"
            @update:model-value="$emit('update:projectName', $event)"
            @input="$emit('search')"
          />
        </div>
        <div class="search-item">
          <label for="search_clientName" class="search-label">客户名称：</label>
          <SearchInput
              input-id="search_clientName"
            :model-value="clientName"
            field-key="MaintenancePlanManagement_clientName"
            placeholder="请输入客户名称"
            @update:model-value="$emit('update:clientName', $event)"
            @input="$emit('search')"
          />
        </div>
      </div>
    </div>
    <div class="search-actions">
      <button
        class="btn btn-add"
        @click="$emit('add')"
      >
        + 新增维保计划
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import SearchInput from '@/components/SearchInput.vue'

defineProps<{
  projectName: string
  clientName: string
}>()

defineEmits<{
  'update:projectName': [value: string]
  'update:clientName': [value: string]
  'search': []
  'add': []
}>()
</script>

<style scoped>
.search-section {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 20px;
  padding: 15px 20px;
  background: var(--color-bg-card);
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
}

.search-form {
  flex: 1;
}

.search-row {
  display: flex;
  flex-wrap: wrap;
  gap: 15px;
}

.search-item {
  display: flex;
  align-items: center;
  gap: 8px;
}

.search-label {
  font-size: 14px;
  color: #606266;
  white-space: nowrap;
}

.search-actions {
  display: flex;
  gap: 10px;
}

.btn {
  padding: 8px 20px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
  transition: all 0.3s;
}

.btn-add {
  background: linear-gradient(135deg, var(--color-primary) 0%, var(--color-primary) 100%);
  color: white;
}

.btn-add:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
}
</style>
