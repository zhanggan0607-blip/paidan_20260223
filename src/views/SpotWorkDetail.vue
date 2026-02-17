<template>
  <div class="modal-overlay" @click.self="goBack">
    <div class="modal-container">
      <div class="modal-header">
        <h3 class="modal-title">零星用工工单详情</h3>
        <button class="modal-close" @click="goBack">×</button>
      </div>
      <div class="modal-body">
        <div class="form-grid">
          <div class="form-column">
            <div class="form-item">
              <label class="form-label">项目名称</label>
              <div class="form-value">{{ workData.project_name || '-' }}</div>
            </div>
            <div class="form-item">
              <label class="form-label">项目编号</label>
              <div class="form-value">{{ workData.project_id || '-' }}</div>
            </div>
            <div class="form-item">
              <label class="form-label">用工单编号</label>
              <div class="form-value">{{ workData.work_id || '-' }}</div>
            </div>
            <div class="form-item">
              <label class="form-label">客户单位</label>
              <div class="form-value">{{ workData.client_name || '-' }}</div>
            </div>
            <div class="form-item">
              <label class="form-label">客户联系人</label>
              <div class="form-value">{{ workData.client_contact || '-' }}</div>
            </div>
            <div class="form-item">
              <label class="form-label">联系人职位</label>
              <div class="form-value">{{ workData.client_contact_position || '-' }}</div>
            </div>
          </div>
          <div class="form-column">
            <div class="form-item">
              <label class="form-label">计划开始日期</label>
              <div class="form-value">{{ formatDate(workData.plan_start_date) }}</div>
            </div>
            <div class="form-item">
              <label class="form-label">计划结束日期</label>
              <div class="form-value">{{ formatDate(workData.plan_end_date) }}</div>
            </div>
            <div class="form-item">
              <label class="form-label">运维人员</label>
              <div class="form-value">{{ workData.maintenance_personnel || '-' }}</div>
            </div>
            <div class="form-item">
              <label class="form-label">客户联系方式</label>
              <div class="form-value">{{ workData.client_contact_info || '-' }}</div>
            </div>
            <div class="form-item">
              <label class="form-label">客户地址</label>
              <div class="form-value">{{ workData.address || '-' }}</div>
            </div>
            <div class="form-item">
              <label class="form-label">备注</label>
              <div class="form-value">{{ workData.remarks || '-' }}</div>
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

interface WorkData {
  id: number
  work_id: string
  project_id: string
  project_name: string
  plan_start_date: string
  plan_end_date: string
  client_name: string
  client_contact: string
  client_contact_info: string
  client_contact_position: string
  address: string
  maintenance_personnel: string
  status: string
  remarks?: string
}

export default defineComponent({
  name: 'SpotWorkDetail',
  setup() {
    const route = useRoute()
    const router = useRouter()
    const workData = ref<WorkData>({
      id: 0,
      work_id: '',
      project_id: '',
      project_name: '',
      plan_start_date: '',
      plan_end_date: '',
      client_name: '',
      client_contact: '',
      client_contact_info: '',
      client_contact_position: '',
      address: '',
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
            workData.value = {
              id: item.id,
              work_id: item.plan_id,
              project_id: item.project_id,
              project_name: item.project_name || item.plan_name,
              plan_start_date: item.plan_start_date,
              plan_end_date: item.plan_end_date,
              client_name: item.client_name || item.responsible_department || '',
              client_contact: item.client_contact || '',
              client_contact_info: item.client_contact_info || '',
              client_contact_position: item.client_contact_position || '',
              address: item.address || '',
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
      workData,
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
  width: 800px;
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
  min-height: 80px;
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
  border-radius: 3px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.15s;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.1);
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
