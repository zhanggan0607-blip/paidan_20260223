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
              <span class="form-label">项目名称</span>
              <div class="form-value">{{ workData.project_name || '暂无数据' }}</div>
            </div>
            <div class="form-item">
              <span class="form-label">计划开始日期</span>
              <div class="form-value">{{ formatDate(workData.plan_start_date) }}</div>
            </div>
            <div class="form-item">
              <span class="form-label">客户单位</span>
              <div class="form-value">{{ workData.client_name || '暂无数据' }}</div>
            </div>
            <div class="form-item">
              <span class="form-label">客户联系人</span>
              <div class="form-value">{{ workData.client_contact || '暂无数据' }}</div>
            </div>
            <div class="form-item">
              <span class="form-label">运维人员</span>
              <div class="form-value">{{ workData.maintenance_personnel || '暂无数据' }}</div>
            </div>
          </div>
          <div class="form-column">
            <div class="form-item">
              <span class="form-label">工单编号</span>
              <div class="form-value">{{ workData.work_id || '暂无数据' }}</div>
            </div>
            <div class="form-item">
              <span class="form-label">计划结束日期</span>
              <div class="form-value">{{ formatDate(workData.plan_end_date) }}</div>
            </div>
            <div class="form-item">
              <span class="form-label">客户地址</span>
              <div class="form-value">{{ workData.address || '暂无数据' }}</div>
            </div>
            <div class="form-item">
              <span class="form-label">客户联系方式</span>
              <div class="form-value">{{ workData.client_contact_info || '暂无数据' }}</div>
            </div>
            <div class="form-item">
              <span class="form-label">工天统计</span>
              <div class="form-value">
                {{ workData.work_days !== undefined ? workData.work_days + '工天' : '-' }}
              </div>
            </div>
          </div>
        </div>

        <div class="work-content-section">
          <span class="form-label">工作内容</span>
          <div class="form-value work-content">{{ workData.work_content || '暂无数据' }}</div>
        </div>

        <div class="status-section">
          <span class="form-label">状态</span>
          <div class="form-value">
            <span class="status-tag" :class="getStatusClass(workData.status)">{{
              workData.status || '暂无数据'
            }}</span>
          </div>
        </div>

        <div class="form-item-full">
          <span class="form-label">现场图片</span>
          <div v-if="workData.photos && workData.photos.length > 0" class="photo-grid">
            <div
              v-for="(photo, index) in workData.photos"
              :key="index"
              class="photo-item"
              @click="previewPhoto(photo)"
            >
              <img :src="photo" alt="现场图片" loading="lazy" />
            </div>
          </div>
          <div v-else class="form-value">暂无数据</div>
        </div>

        <div class="form-item-full">
          <span class="form-label">班组签字</span>
          <div v-if="workData.signature" class="signature-container">
            <img :src="workData.signature" alt="班组签字" class="signature-image" />
          </div>
          <div v-else class="form-value">暂无数据</div>
        </div>

        <div class="workers-section">
          <h4 class="section-title">施工人员详情</h4>
          <table v-if="workers.length > 0" class="workers-table">
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
                <td>{{ worker.name || '暂无数据' }}</td>
                <td>{{ worker.gender || '暂无数据' }}</td>
                <td>{{ worker.id_card_number || '暂无数据' }}</td>
                <td>{{ worker.address || '暂无数据' }}</td>
              </tr>
            </tbody>
          </table>
          <div v-else class="form-value">暂无数据</div>
        </div>

        <div class="operation-log-section">
          <div class="section-title">内部确认区</div>
          <div v-if="operationLogs.length > 0" class="timeline">
            <div
              v-for="(log, index) in operationLogs"
              :key="log.id"
              class="timeline-item"
              :class="{ last: index === operationLogs.length - 1 }"
            >
              <div class="timeline-dot"></div>
              <div class="timeline-content">
                <span class="timeline-time">{{ formatOperationTime(log.created_at) }}</span>
                <span class="timeline-operator">{{ log.operator_name }}</span>
                <span class="timeline-action">{{ log.operation_type_name }}</span>
              </div>
            </div>
          </div>
          <div v-else class="no-logs">暂无数据</div>
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
import request from '@/api/request'
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
      signature: '',
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
      if (status === '执行中') {
        return 'status-pending'
      }
      if (status === '待确认') {
        return 'status-waiting'
      }
      if (status === '已完成') {
        return 'status-completed'
      }
      if (status === '已退回') {
        return 'status-returned'
      }
      return ''
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
        const response = (await request.get(
          `/work-order-operation-log?work_order_type=spot_work&work_order_id=${workOrderId}`
        )) as unknown as ApiResponse<OperationLogItem[]>
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
              status: item.status || '执行中',
              remarks: item.remarks || '',
              work_content: item.work_content || '',
              worker_count: item.worker_count || 0,
              work_days: item.work_days || 0,
              photos: Array.isArray(item.photos) ? item.photos : (typeof item.photos === 'string' ? JSON.parse(item.photos) : []),
              signature: item.signature || '',
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
      goBack,
    }
  },
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
  background: var(--color-bg-card);
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
  border-bottom: 1px solid var(--color-border);
}

.modal-title {
  font-size: 18px;
  font-weight: 600;
  color: var(--color-text-primary);
  margin: 0;
}

.modal-close {
  width: 32px;
  height: 32px;
  border: none;
  background: none;
  font-size: 24px;
  color: var(--color-text-placeholder);
  cursor: pointer;
  transition: color 0.15s;
  display: flex;
  align-items: center;
  justify-content: center;
}

.modal-close:hover {
  color: var(--color-text-primary);
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
  color: var(--color-text-regular);
}

.form-value {
  padding: 8px 12px;
  background: var(--color-bg-page);
  border: 1px solid var(--color-border);
  border-radius: 3px;
  font-size: 14px;
  color: var(--color-text-primary);
  min-height: 36px;
  display: flex;
  align-items: center;
}

.work-content-section {
  margin-top: 16px;
  padding-top: 16px;
  border-top: 1px solid var(--color-border);
}

.work-content-section .form-label {
  margin-bottom: 8px;
}

.form-item-full {
  margin-top: 16px;
  padding-top: 16px;
  border-top: 1px solid var(--color-border);
}

.form-item-full .form-label {
  font-size: 14px;
  font-weight: 500;
  color: var(--color-text-regular);
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
  border-top: 1px solid var(--color-border);
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
  background: var(--color-bg-card);
  color: var(--color-text-secondary);
  border: 1px solid var(--color-border);
}

.btn-cancel:hover:not(:disabled) {
  background: var(--color-bg-page);
}

.workers-section {
  margin-top: 24px;
  padding-top: 20px;
  border-top: 1px solid var(--color-border);
}

.section-title {
  font-size: 16px;
  font-weight: 600;
  color: var(--color-text-primary);
  margin: 0 0 16px 0;
}

.workers-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 14px;
}

.workers-table th {
  background: var(--color-bg-page);
  padding: 10px 12px;
  text-align: left;
  font-weight: 500;
  color: var(--color-text-primary);
  border: 1px solid var(--color-border);
}

.workers-table td {
  padding: 10px 12px;
  border: 1px solid var(--color-border);
  color: var(--color-text-secondary);
}

.workers-table tbody tr:hover {
  background: var(--color-bg-page);
}

.operation-log-section {
  margin-top: 20px;
  padding-top: 20px;
  border-top: 1px solid var(--color-border);
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
  background: var(--color-border);
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
  background: var(--color-primary);
  border: 2px solid var(--color-bg-card);
  box-shadow: 0 0 0 2px var(--color-primary);
}

.timeline-content {
  display: flex;
  align-items: center;
  gap: 12px;
  flex-wrap: wrap;
}

.timeline-time {
  font-size: 14px;
  color: var(--color-text-secondary);
  font-family: monospace;
}

.timeline-operator {
  font-size: 14px;
  color: var(--color-text-primary);
  font-weight: 500;
}

.timeline-action {
  font-size: 13px;
  color: var(--color-primary);
  background: var(--color-primary-subtle);
  padding: 2px 8px;
  border-radius: 4px;
}

.no-logs {
  text-align: center;
  color: var(--color-text-placeholder);
  font-size: 14px;
  padding: 20px 0;
}

.status-section {
  margin-top: 16px;
  padding-top: 16px;
  border-top: 1px solid var(--color-border);
}

.status-tag {
  display: inline-block;
  padding: 4px 12px;
  border-radius: 4px;
  font-size: 14px;
  font-weight: 500;
}

.status-pending {
  background: var(--color-bg-card)3cd;
  color: #856404;
}

.status-waiting {
  background: var(--color-primary-subtle);
  color: var(--color-primary);
}

.status-confirmed {
  background: var(--color-success-subtle);
  color: var(--color-success);
}

.status-completed {
  background: #f3e5f5;
  color: #7b1fa2;
}

.status-returned {
  background: var(--color-danger-subtle);
  color: var(--color-danger);
}

.status-cancelled {
  background: var(--color-bg-page);
  color: #757575;
}

.photos-section {
  margin-top: 16px;
  padding-top: 16px;
  border-top: 1px solid var(--color-border);
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
  border: 1px solid var(--color-border);
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
  border-top: 1px solid var(--color-border);
}

.signature-container {
  margin-top: 8px;
  padding: 16px;
  background: var(--color-bg-page);
  border: 1px solid var(--color-border);
  border-radius: 8px;
  display: inline-block;
}

.signature-image {
  max-width: 300px;
  max-height: 150px;
  object-fit: contain;
}
</style>
