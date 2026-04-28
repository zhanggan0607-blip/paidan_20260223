<template>
  <div class="table-section">
    <table class="data-table">
      <thead>
        <tr>
          <th>序号</th>
          <th>项目编号</th>
          <th>项目名称</th>
          <th>开始日期</th>
          <th>结束日期</th>
          <th>维保计划数</th>
          <th>客户单位</th>
          <th>地址</th>
          <th>操作</th>
        </tr>
      </thead>
      <tbody>
        <tr
          v-for="(item, index) in data"
          :key="item.project_id"
          :class="{ 'even-row': index % 2 === 0 }"
        >
          <td>{{ startIndex + index + 1 }}</td>
          <td>{{ item.project_id }}</td>
          <td>{{ item.project_name }}</td>
          <td>{{ formatDate(item.plan_start_date) }}</td>
          <td>{{ formatDate(item.plan_end_date) }}</td>
          <td>{{ item.plan_count }}</td>
          <td>{{ item.client_name || '-' }}</td>
          <td>{{ item.address || '-' }}</td>
          <td class="action-cell">
            <a
              href="#"
              class="action-link action-view"
              @click.prevent="$emit('view', item)"
            >查看</a>
            <a
              href="#"
              class="action-link action-edit"
              @click.prevent="$emit('edit', item)"
            >编辑计划</a>
            <a
              href="#"
              class="action-link action-delete"
              @click.prevent="$emit('delete', item)"
            >删除</a>
          </td>
        </tr>
      </tbody>
    </table>
  </div>
</template>

<script setup lang="ts">
import type { MaintenancePlanDisplay } from '@/services/maintenancePlan'

defineProps<{
  data: MaintenancePlanDisplay[]
  startIndex: number
}>()

defineEmits<{
  'view': [item: MaintenancePlanDisplay]
  'edit': [item: MaintenancePlanDisplay]
  'delete': [item: MaintenancePlanDisplay]
}>()

const formatDate = (date: string | undefined): string => {
  if (!date) return '-'
  try {
    const d = new Date(date)
    return d.toLocaleDateString('zh-CN')
  } catch {
    return date
  }
}
</script>

<style scoped>
.table-section {
  background: var(--color-bg-card);
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
  overflow: hidden;
}

.data-table {
  width: 100%;
  border-collapse: collapse;
}

.data-table th,
.data-table td {
  padding: 12px 16px;
  text-align: left;
  border-bottom: 1px solid #ebeef5;
}

.data-table th {
  background: var(--color-bg-page);
  font-weight: 600;
  color: #303133;
  font-size: 14px;
}

.data-table td {
  font-size: 14px;
  color: #606266;
}

.even-row {
  background: var(--color-bg-page);
}

.action-cell {
  display: flex;
  gap: 8px;
}

.action-link {
  text-decoration: none;
  font-size: 13px;
  padding: 2px 8px;
  border-radius: 3px;
  transition: all 0.2s;
}

.action-view {
  color: #409eff;
}

.action-view:hover {
  background: #ecf5ff;
}

.action-edit {
  color: #67c23a;
}

.action-edit:hover {
  background: #f0f9eb;
}

.action-delete {
  color: #f56c6c;
}

.action-delete:hover {
  background: #fef0f0;
}
</style>
