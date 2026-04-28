<template>
  <div class="virtual-table-example">
    <h3>维保计划列表（虚拟滚动）</h3>
    <p class="info">共 {{ items.length }} 条记录，使用虚拟滚动优化渲染性能</p>
    
    <div class="table-header">
      <div class="header-cell" style="width: 60px">序号</div>
      <div class="header-cell" style="width: 120px">项目编号</div>
      <div class="header-cell" style="flex: 1">项目名称</div>
      <div class="header-cell" style="width: 120px">开始日期</div>
      <div class="header-cell" style="width: 120px">结束日期</div>
      <div class="header-cell" style="width: 100px">客户单位</div>
      <div class="header-cell" style="width: 120px">操作</div>
    </div>
    
    <VirtualScroll
      :items="items"
      :item-height="50"
      :height="500"
      :get-item-key="(item: unknown, index: number) => (item as PlanItem).id ?? index"
    >
      <template #item="{ item, index }">
        <div
          class="table-row"
          :class="{ 'even-row': index % 2 === 0 }"
        >
          <div class="table-cell" style="width: 60px">{{ index + 1 }}</div>
          <div class="table-cell" style="width: 120px">{{ (item as PlanItem).projectId }}</div>
          <div class="table-cell" style="flex: 1">{{ (item as PlanItem).projectName }}</div>
          <div class="table-cell" style="width: 120px">{{ (item as PlanItem).startDate }}</div>
          <div class="table-cell" style="width: 120px">{{ (item as PlanItem).endDate }}</div>
          <div class="table-cell" style="width: 100px">{{ (item as PlanItem).clientName }}</div>
          <div class="table-cell action-cell" style="width: 120px">
            <a href="#" class="action-link" @click.prevent="$emit('view', item as PlanItem)">查看</a>
            <a href="#" class="action-link" @click.prevent="$emit('edit', item as PlanItem)">编辑</a>
          </div>
        </div>
      </template>
    </VirtualScroll>
  </div>
</template>

<script setup lang="ts">
import VirtualScroll from '@/components/VirtualScroll.vue'

interface PlanItem {
  id: number
  projectId: string
  projectName: string
  startDate: string
  endDate: string
  clientName: string
}

defineProps<{
  items: PlanItem[]
}>()

defineEmits<{
  'view': [item: PlanItem]
  'edit': [item: PlanItem]
}>()
</script>

<style scoped>
.virtual-table-example {
  background: var(--color-bg-card);
  border-radius: 8px;
  padding: 16px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
}

.virtual-table-example h3 {
  margin: 0 0 8px 0;
  font-size: 16px;
  color: #303133;
}

.info {
  margin: 0 0 16px 0;
  font-size: 13px;
  color: #909399;
}

.table-header {
  display: flex;
  background: var(--color-bg-page);
  border-bottom: 1px solid #ebeef5;
  font-weight: 600;
  color: #303133;
  font-size: 14px;
}

.header-cell {
  padding: 12px 16px;
  text-align: left;
  box-sizing: border-box;
}

.table-row {
  display: flex;
  border-bottom: 1px solid #ebeef5;
  font-size: 14px;
  color: #606266;
}

.table-row:hover {
  background: var(--color-bg-page);
}

.even-row {
  background: var(--color-bg-page);
}

.table-cell {
  padding: 12px 16px;
  text-align: left;
  box-sizing: border-box;
  display: flex;
  align-items: center;
}

.action-cell {
  display: flex;
  gap: 8px;
}

.action-link {
  color: #409eff;
  text-decoration: none;
  font-size: 13px;
}

.action-link:hover {
  text-decoration: underline;
}
</style>
