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
              <label class="form-label">计划开始日期</label>
              <div class="form-value">{{ formatDate(workData.plan_start_date) }}</div>
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
              <label class="form-label">运维人员</label>
              <div class="form-value">{{ workData.maintenance_personnel || '-' }}</div>
            </div>
          </div>
          <div class="form-column">
            <div class="form-item">
              <label class="form-label">工单编号</label>
              <div class="form-value">{{ workData.work_id || '-' }}</div>
            </div>
            <div class="form-item">
              <label class="form-label">计划结束日期</label>
              <div class="form-value">{{ formatDate(workData.plan_end_date) }}</div>
            </div>
            <div class="form-item">
              <label class="form-label">客户地址</label>
              <div class="form-value">{{ workData.address || '-' }}</div>
            </div>
            <div class="form-item">
              <label class="form-label">客户联系方式</label>
              <div class="form-value">{{ workData.client_contact_info || '-' }}</div>
            </div>
            <div class="form-item">
              <label class="form-label">工天统计</label>
              <div class="form-value">{{ workData.work_days !== undefined ? workData.work_days + '工天' : '-' }}</div>
            </div>
          </div>
        </div>
        
        <div class="work-content-section">
          <label class="form-label">工作内容</label>
          <div class="form-value work-content">{{ workData.work_content || '-' }}</div>
        </div>
        
        <div class="status-section">
          <label class="form-label">状态</label>
          <div class="form-value">
            <span class="status-tag" :class="getStatusClass(workData.status)">{{ workData.status || '-' }}</span>
          </div>
        </div>
        
        <div class="form-item-full">
          <label class="form-label">现场图片</label>
          <div class="photo-grid" v-if="workData.photos && workData.photos.length > 0">
            <div 
              v-for="(photo, index) in workData.photos" 
              :key="index" 
              class="photo-item"
              @click="previewPhoto(photo)"
            >
              <img :src="photo" alt="现场图片" loading="lazy" />
            </div>
          </div>
          <div class="form-value" v-else>暂无现场图片</div>
        </div>
        
        <div class="form-item-full">
          <label class="form-label">班组签字</label>
          <div class="signature-container" v-if="workData.signature">
            <img :src="workData.signature" alt="班组签字" class="signature-image" />
          </div>
          <div class="form-value" v-else>暂无班组签字</div>
        </div>
        
        <div class="workers-section">
          <h4 class="section-title">施工人员详情</h4>
          <table class="workers-table" v-if="workers.length > 0">
            <thead>
              <tr>
                <th>序号</th>
                <th>姓名</th>
                <th>性别</th>
                <th>身份证号码</th>
                <th>住址</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="(worker, index) in workers" :key="worker.id">
                <td>{{ index + 1 }}</td>
                <td>{{ worker.name || '-' }}</td>
                <td>{{ worker.gender || '-' }}</td>
                <td>{{ worker.id_card_number || '-' }}</td>
                <td>{{ worker.address || '-' }}</td>
              </tr>
            </tbody>
          </table>
          <div class="form-value" v-else>暂无施工人员信息</div>
        </div>

        <div class="operation-log-section">
          <div class="section-title">内部确认区</div>
          <div class="timeline" v-if="operationLogs.length > 0">
            <div 
              v-for="(log, index) in operationLogs" 
              :key="log.id" 
              class="timeline-item"
              :class="{ 'last': index === operationLogs.length - 1 }"
            >
              <div class="timeline-dot"></div>
              <div class="timeline-content">
                <span class="timeline-time">{{ formatOperationTime(log.created_at) }}</span>
                <span class="timeline-operator">{{ log.operator_name }}</span>
                <span class="timeline-action">{{ log.operation_type_name }}</span>
              </div>
            </div>
          </div>
          <div class="no-logs" v-else>暂无操作记录</div>
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
import { spotWorkService } from '@/services/spotWork'
import type { SpotWorkWorker } from '@/types/api'
import apiClient from '@/utils/api'
import type { ApiResponse } from '@/types/api'

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
  work_content?: string
  worker_count?: number
  work_days?: number
  photos?: string[]
  signature?: string
}

interface OperationLogItem {
  id: number
  work_order_type: string
  work_order_id: number
  work_order_no: string
  operator_name: string
  operator_id: number | null
  operation_type_code: string
  operation_type_name: string
  operation_remark: string | null
  created_at: string
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
      remarks: '',
      worker_count: 0,
      work_days: 0,
      photos: [],
      signature: ''
    })
    const workers = ref<SpotWorkWorker[]>([])
    const operationLogs = ref<OperationLogItem[]>([])
    const loadingLogs = ref(false)

    const formatDate = (dateStr: string) => {
      if (!dateStr) return '-'
      const date = new Date(dateStr)
      return `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}-${String(date.getDate()).padStart(2, '0')}`
    }

    /**
     * 格式化操作时间
     */
    const formatOperationTime = (dateStr: string) => {
      if (!dateStr) return '-'
      const date = new Date(dateStr)
      const year = date.getFullYear()
      const month = String(date.getMonth() + 1).padStart(2, '0')
      const day = String(date.getDate()).padStart(2, '0')
      const hours = String(date.getHours()).padStart(2, '0')
      const minutes = String(date.getMinutes()).padStart(2, '0')
      return `${year}-${month}-${day} ${hours}:${minutes}`
    }

    /**
     * 获取状态样式类
     */
    const getStatusClass = (status: string) => {
      const statusMap: Record<string, string> = {
        '未进行': 'status-pending',
        '待确认': 'status-waiting',
        '已确认': 'status-confirmed',
        '已完成': 'status-completed',
        '已退回': 'status-returned',
        '已取消': 'status-cancelled'
      }
      return statusMap[status] || ''
    }

    /**
     * 预览图片
     */
    const previewPhoto = (photo: string) => {
      window.open(photo, '_blank')
    }

    /**
     * 获取操作日志
     */
    const fetchOperationLogs = async (workOrderId: number) => {
      if (!workOrderId) return
      loadingLogs.value = true
      try {
        const response = await apiClient.get(`/work-order-operation-log?work_order_type=spot_work&work_order_id=${workOrderId}`) as unknown as ApiResponse<OperationLogItem[]>
        if (response.code === 200) {
          operationLogs.value = response.data || []
        }
      } catch (error) {
        console.error('获取操作日志失败:', error)
        operationLogs.value = []
      } finally {
        loadingLogs.value = false
      }
    }

    const goBack = () => {
      router.back()
    }

    const loadData = async () => {
      const id = route.query.id as string
      if (id) {
        try {
          const response = await spotWorkService.getById(parseInt(id))
          if (response.code === 200) {
            const item = response.data
            workData.value = {
              id: item.id,
              work_id: item.work_id,
              project_id: item.project_id,
              project_name: item.project_name,
              plan_start_date: item.plan_start_date,
              plan_end_date: item.plan_end_date,
              client_name: item.client_name || '',
              client_contact: item.client_contact || '',
              client_contact_info: item.client_contact_info || '',
              client_contact_position: item.client_contact_position || '',
              address: item.address || '',
              maintenance_personnel: item.maintenance_personnel || '',
              status: item.status || '未进行',
              remarks: item.remarks || '',
              work_content: item.work_content || '',
              worker_count: item.worker_count || 0,
              work_days: item.work_days || 0,
              photos: item.photos || [],
              signature: item.signature || ''
            }
            workers.value = item.workers || []
            fetchOperationLogs(item.id)
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
      workers,
      operationLogs,
      loadingLogs,
      formatDate,
      formatOperationTime,
      getStatusClass,
      previewPhoto,
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

.work-content-section {
  margin-top: 16px;
  padding-top: 16px;
  border-top: 1px solid #e0e0e0;
}

.work-content-section .form-label {
  margin-bottom: 8px;
}

.form-item-full {
  margin-top: 16px;
  padding-top: 16px;
  border-top: 1px solid #e0e0e0;
}

.form-item-full .form-label {
  font-size: 14px;
  font-weight: 500;
  color: #424242;
  margin-bottom: 8px;
  display: block;
}

.form-value.work-content {
  min-height: 80px;
  align-items: flex-start;
  white-space: pre-wrap;
  word-break: break-word;
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

.workers-section {
  margin-top: 24px;
  padding-top: 20px;
  border-top: 1px solid #e0e0e0;
}

.section-title {
  font-size: 16px;
  font-weight: 600;
  color: #333;
  margin: 0 0 16px 0;
}

.workers-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 14px;
}

.workers-table th {
  background: #f5f5f5;
  padding: 10px 12px;
  text-align: left;
  font-weight: 500;
  color: #333;
  border: 1px solid #e0e0e0;
}

.workers-table td {
  padding: 10px 12px;
  border: 1px solid #e0e0e0;
  color: #666;
}

.workers-table tbody tr:hover {
  background: #fafafa;
}

.operation-log-section {
  margin-top: 20px;
  padding-top: 20px;
  border-top: 1px solid #e0e0e0;
}

.timeline {
  position: relative;
  padding-left: 24px;
}

.timeline::before {
  content: '';
  position: absolute;
  left: 8px;
  top: 0;
  bottom: 0;
  width: 2px;
  background: #e0e0e0;
}

.timeline-item {
  position: relative;
  padding-bottom: 16px;
}

.timeline-item.last {
  padding-bottom: 0;
}

.timeline-dot {
  position: absolute;
  left: -20px;
  top: 4px;
  width: 12px;
  height: 12px;
  border-radius: 50%;
  background: #1976d2;
  border: 2px solid #fff;
  box-shadow: 0 0 0 2px #1976d2;
}

.timeline-content {
  display: flex;
  align-items: center;
  gap: 12px;
  flex-wrap: wrap;
}

.timeline-time {
  font-size: 14px;
  color: #666;
  font-family: monospace;
}

.timeline-operator {
  font-size: 14px;
  color: #333;
  font-weight: 500;
}

.timeline-action {
  font-size: 13px;
  color: #1976d2;
  background: #e3f2fd;
  padding: 2px 8px;
  border-radius: 4px;
}

.no-logs {
  text-align: center;
  color: #999;
  font-size: 14px;
  padding: 20px 0;
}

.status-section {
  margin-top: 16px;
  padding-top: 16px;
  border-top: 1px solid #e0e0e0;
}

.status-tag {
  display: inline-block;
  padding: 4px 12px;
  border-radius: 4px;
  font-size: 14px;
  font-weight: 500;
}

.status-pending {
  background: #fff3cd;
  color: #856404;
}

.status-waiting {
  background: #e3f2fd;
  color: #1976d2;
}

.status-confirmed {
  background: #e8f5e9;
  color: #2e7d32;
}

.status-completed {
  background: #f3e5f5;
  color: #7b1fa2;
}

.status-returned {
  background: #ffebee;
  color: #c62828;
}

.status-cancelled {
  background: #f5f5f5;
  color: #757575;
}

.photos-section {
  margin-top: 16px;
  padding-top: 16px;
  border-top: 1px solid #e0e0e0;
}

.photo-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 12px;
  margin-top: 8px;
}

.photo-item {
  aspect-ratio: 1;
  border-radius: 8px;
  overflow: hidden;
  cursor: pointer;
  border: 1px solid #e0e0e0;
  transition: transform 0.2s;
}

.photo-item:hover {
  transform: scale(1.05);
}

.photo-item img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.signature-section {
  margin-top: 16px;
  padding-top: 16px;
  border-top: 1px solid #e0e0e0;
}

.signature-container {
  margin-top: 8px;
  padding: 16px;
  background: #fafafa;
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  display: inline-block;
}

.signature-image {
  max-width: 300px;
  max-height: 150px;
  object-fit: contain;
}
</style>
