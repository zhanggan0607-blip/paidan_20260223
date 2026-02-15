<template>
  <div class="modal-overlay" @click.self="goBack">
    <div class="modal-container">
      <div class="modal-header">
        <h3 class="modal-title">临时维修工单详情</h3>
        <button class="modal-close" @click="goBack">×</button>
      </div>
      <div class="modal-body">
        <div class="form-grid">
          <div class="form-column">
            <div class="form-item">
              <label class="form-label">项目名称</label>
              <div class="form-value">{{ repairData.project_name || '-' }}</div>
            </div>
            <div class="form-item">
              <label class="form-label">项目编号</label>
              <div class="form-value">{{ repairData.project_id || '-' }}</div>
            </div>
            <div class="form-item">
              <label class="form-label">维修单编号</label>
              <div class="form-value">{{ repairData.repair_id || '-' }}</div>
            </div>
            <div class="form-item">
              <label class="form-label">客户单位</label>
              <div class="form-value">{{ repairData.client_name || '-' }}</div>
            </div>
          </div>
          <div class="form-column">
            <div class="form-item">
              <label class="form-label">计划开始日期</label>
              <div class="form-value">{{ formatDate(repairData.plan_start_date) }}</div>
            </div>
            <div class="form-item">
              <label class="form-label">计划结束日期</label>
              <div class="form-value">{{ formatDate(repairData.plan_end_date) }}</div>
            </div>
            <div class="form-item">
              <label class="form-label">运维人员</label>
              <div class="form-value">{{ repairData.maintenance_personnel || '-' }}</div>
            </div>
            <div class="form-item">
              <label class="form-label">维修内容</label>
              <div class="form-value">{{ repairData.remarks || '-' }}</div>
            </div>
          </div>
        </div>
      </div>
      <div class="modal-footer">
        <button class="btn btn-cancel" @click="goBack">关闭</button>
      </div>
    </div>
  </div>
</template>

<script lang="ts">
import { defineComponent, ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { maintenancePlanService } from '@/services/maintenancePlan'

interface RepairData {
  id: number
  repair_id: string
  project_id: string
  project_name: string
  plan_start_date: string
  plan_end_date: string
  client_name: string
  maintenance_personnel: string
  status: string
  remarks?: string
}

export default defineComponent({
  name: 'TemporaryRepairDetail',
  setup() {
    const route = useRoute()
    const router = useRouter()
    const repairData = ref<RepairData>({
      id: 0,
      repair_id: '',
      project_id: '',
      project_name: '',
      plan_start_date: '',
      plan_end_date: '',
      client_name: '',
      maintenance_personnel: '',
      status: '',
      remarks: ''
    })

    const formatDate = (dateStr: string) => {
      if (!dateStr) return '-'
      const date = new Date(dateStr)
      return `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}-${String(date.getDate()).padStart(2, '0')}`
    }

    const goBack = () => {
      router.back()
    }

    const loadData = async () => {
      const id = route.query.id as string
      if (id) {
        try {
          const response = await maintenancePlanService.getById(parseInt(id))
          if (response.code === 200) {
            const item = response.data
            repairData.value = {
              id: item.id,
              repair_id: item.plan_id,
              project_id: item.project_id,
              project_name: item.project_name || item.plan_name,
              plan_start_date: item.plan_start_date,
              plan_end_date: item.plan_end_date,
              client_name: item.responsible_department || '',
              maintenance_personnel: item.responsible_person || '',
              status: item.plan_status || '待执行',
              remarks: item.remarks || ''
            }
          }
        } catch (error) {
          console.error('加载数据失败:', error)
        }
      }
    }

    onMounted(() => {
      loadData()
    })

    return {
      repairData,
      formatDate,
      goBack
    }
  }
})
</script>

<style scoped>
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal-container {
  background: #fff;
  border-radius: 8px;
  width: 900px;
  max-width: 95vw;
  max-height: 90vh;
  overflow-y: auto;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px 24px;
  border-bottom: 1px solid #e0e0e0;
}

.modal-title {
  font-size: 18px;
  font-weight: 600;
  color: #333;
  margin: 0;
}

.modal-close {
  width: 32px;
  height: 32px;
  border: none;
  background: none;
  font-size: 24px;
  color: #999;
  cursor: pointer;
  transition: color 0.15s;
  display: flex;
  align-items: center;
  justify-content: center;
}

.modal-close:hover {
  color: #333;
}

.modal-body {
  padding: 24px;
}

.form-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 24px 40px;
  align-items: start;
}

.form-column {
  display: flex;
  flex-direction: column;
}

.form-item {
  display: flex;
  flex-direction: column;
  gap: 8px;
  min-height: 90px;
  padding: 4px 0;
}

.form-label {
  font-size: 14px;
  font-weight: 500;
  color: #424242;
}

.form-value {
  padding: 8px 12px;
  background: #f5f5f5;
  border: 1px solid #e0e0e0;
  border-radius: 3px;
  font-size: 14px;
  color: #333;
  min-height: 36px;
  display: flex;
  align-items: center;
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  padding: 20px 24px;
  border-top: 1px solid #e0e0e0;
}

.btn {
  padding: 8px 16px;
  border: none;
  border-radius: 4px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-cancel {
  background: #fff;
  color: #666;
  border: 1px solid #e0e0e0;
}

.btn-cancel:hover:not(:disabled) {
  background: #f5f5f5;
}
</style>
