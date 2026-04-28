<template>
  <div class="plan-items-table">
    <div class="section-title">
      {{ title }}（共 {{ items.length }} 条）
    </div>
    <div class="table-section-inner">
      <table class="inner-table">
        <thead>
          <tr>
            <th style="width: 50px">序号</th>
            <th>工单编号</th>
            <th>计划开始日期</th>
            <th>计划结束日期</th>
            <th>运维人员</th>
            <th>备注</th>
            <th>操作</th>
          </tr>
        </thead>
        <tbody>
          <tr
            v-for="(item, index) in items"
            :key="item.id || index"
          >
            <td class="text-center">
              {{ index + 1 }}
            </td>
            <td>
              <input
                :id="`plan_id_${index}`"
                :name="`plan_id_${index}`"
                v-model="item.plan_id"
                type="text"
                class="table-input"
                placeholder="请输入"
              >
            </td>
            <td>
              <input
                :id="`plan_start_date_${index}`"
                :name="`plan_start_date_${index}`"
                v-model="item.plan_start_date"
                type="date"
                class="table-input"
              >
            </td>
            <td>
              <input
                :id="`plan_end_date_${index}`"
                :name="`plan_end_date_${index}`"
                v-model="item.plan_end_date"
                type="date"
                class="table-input"
              >
            </td>
            <td>
              <select
                :id="`maintenance_personnel_${index}`"
                :name="`maintenance_personnel_${index}`"
                v-model="item.maintenance_personnel"
                class="table-input"
              >
                <option value="">请选择</option>
                <option
                  v-for="person in personnelList"
                  :key="person"
                  :value="person"
                >
                  {{ person }}
                </option>
              </select>
            </td>
            <td>
              <input
                :id="`remarks_${index}`"
                :name="`remarks_${index}`"
                v-model="item.remarks"
                type="text"
                class="table-input"
                placeholder="请输入"
              >
            </td>
            <td class="action-cell">
              <a
                href="#"
                class="action-link action-delete"
                @click.prevent="$emit('remove', index)"
              >删除</a>
            </td>
          </tr>
        </tbody>
      </table>
      <div class="table-actions">
        <button
          class="btn btn-add-small"
          @click="$emit('add')"
        >
          添加
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
export interface PlanItem {
  id?: number
  plan_id: string
  plan_start_date: string
  plan_end_date: string
  maintenance_personnel: string
  remarks: string
  plan_type?: string
  plan_status?: string
  status?: string
  execution_date?: string
  next_maintenance_date?: string
  completion_rate?: number
}

withDefaults(defineProps<{
  title?: string
  items: PlanItem[]
  personnelList: string[]
}>(), {
  title: '维保计划',
})

defineEmits<{
  'update:items': [items: PlanItem[]]
  'add': []
  'remove': [index: number]
}>()
</script>

<style scoped>
.plan-items-table {
  margin-top: 20px;
}

.section-title {
  font-size: 15px;
  font-weight: 600;
  color: #303133;
  margin-bottom: 12px;
  padding-left: 10px;
  border-left: 3px solid #67c23a;
}

.table-section-inner {
  background: var(--color-bg-page);
  border-radius: 6px;
  padding: 12px;
}

.inner-table {
  width: 100%;
  border-collapse: collapse;
  background: var(--color-bg-card);
  border-radius: 4px;
  overflow: hidden;
}

.inner-table th,
.inner-table td {
  padding: 10px 12px;
  text-align: left;
  border: 1px solid #ebeef5;
  font-size: 13px;
}

.inner-table th {
  background: var(--color-bg-page);
  font-weight: 600;
  color: #303133;
}

.text-center {
  text-align: center;
}

.table-input {
  width: 100%;
  padding: 6px 10px;
  border: 1px solid #dcdfe6;
  border-radius: 4px;
  font-size: 13px;
}

.action-cell {
  text-align: center;
}

.action-link {
  text-decoration: none;
  font-size: 13px;
  color: #f56c6c;
  cursor: pointer;
}

.action-link:hover {
  text-decoration: underline;
}

.table-actions {
  display: flex;
  gap: 10px;
  margin-top: 12px;
}

.btn {
  padding: 6px 16px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 13px;
  transition: all 0.2s;
}

.btn-add-small {
  background: #67c23a;
  color: white;
}

.btn-add-small:hover {
  background: #85ce61;
}
</style>
