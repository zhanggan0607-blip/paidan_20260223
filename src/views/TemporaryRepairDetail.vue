<template>
  <div
    class="modal-overlay"
    @click.self="goBack"
  >
    <div class="modal-container">
      <div class="modal-header">
        <h3 class="modal-title">
          {{ isEditMode ? '编辑临时维修工单' : '临时维修工单详情' }}
        </h3>
        <button
          class="modal-close"
          @click="goBack"
        >
          ×
        </button>
      </div>
      <div class="modal-body">
        <div class="form-grid">
          <div class="form-column">
            <div class="form-item">
              <span class="form-label">项目名称</span>
              <div class="form-value">
                {{ repairData.project_name || '暂无数据' }}
              </div>
            </div>
            <div class="form-item">
              <label
                for="planStartDate"
                class="form-label"
              >计划开始日期</label>
              <input
                v-if="isEditMode"
                id="planStartDate"
                v-model="planStartDate"
                name="planStartDate"
                type="date"
                class="form-input"
              >
              <div
                v-else
                class="form-value"
              >
                {{ formatDate(repairData.plan_start_date) }}
              </div>
            </div>
            <div class="form-item">
              <span class="form-label">运维人员</span>
              <div class="form-value">
                {{ repairData.maintenance_personnel || '暂无数据' }}
              </div>
            </div>
            <div class="form-item">
              <span class="form-label">客户单位</span>
              <div class="form-value">
                {{ repairData.client_name || '暂无数据' }}
              </div>
            </div>
            <div class="form-item">
              <label
                for="clientContact"
                class="form-label"
              >客户联系人</label>
              <input
                v-if="isEditMode"
                id="clientContact"
                v-model="repairData.client_contact"
                name="clientContact"
                type="text"
                class="form-input"
                placeholder="请输入客户联系人"
              >
              <div
                v-else
                class="form-value"
              >
                {{ repairData.client_contact || '暂无数据' }}
              </div>
            </div>
          </div>
          <div class="form-column">
            <div class="form-item">
              <span class="form-label">项目编号</span>
              <div class="form-value">
                {{ repairData.project_id || '暂无数据' }}
              </div>
            </div>
            <div class="form-item">
              <label
                for="planEndDate"
                class="form-label"
              >计划结束日期</label>
              <input
                v-if="isEditMode"
                id="planEndDate"
                v-model="planEndDate"
                name="planEndDate"
                type="date"
                class="form-input"
              >
              <div
                v-else
                class="form-value"
              >
                {{ formatDate(repairData.plan_end_date) }}
              </div>
            </div>
            <div class="form-item">
              <span class="form-label">工单编号</span>
              <div class="form-value">
                {{ repairData.repair_id || '暂无数据' }}
              </div>
            </div>
            <div class="form-item">
              <span class="form-label">客户地址</span>
              <div class="form-value">
                {{ repairData.address || '暂无数据' }}
              </div>
            </div>
            <div class="form-item">
              <label
                for="clientContactInfo"
                class="form-label"
              >客户联系方式</label>
              <input
                v-if="isEditMode"
                id="clientContactInfo"
                v-model="repairData.client_contact_info"
                name="clientContactInfo"
                type="text"
                class="form-input"
                placeholder="请输入客户联系方式"
              >
              <div
                v-else
                class="form-value"
              >
                {{ repairData.client_contact_info || '暂无数据' }}
              </div>
            </div>
          </div>
        </div>
        <div class="form-item-full">
          <label
            for="repairContent"
            class="form-label"
          >报修内容</label>
          <textarea
            id="repairContent"
            v-model="repairData.remarks"
            name="repairContent"
            class="form-textarea"
            placeholder="请输入报修内容"
            maxlength="500"
          />
        </div>

        <div class="section-divider">
          <span class="section-divider-text">维修详情</span>
        </div>

        <div class="form-item-full">
          <span class="form-label">故障描述</span>
          <div class="form-value form-value-large">
            {{ repairData.fault_description || '暂无数据' }}
          </div>
        </div>

        <div class="form-item-full">
          <span class="form-label">解决方案</span>
          <div class="form-value form-value-large">
            {{ repairData.solution || '暂无数据' }}
          </div>
        </div>

        <div class="form-item-full">
          <span class="form-label">现场图片</span>
          <div
            v-if="repairData.photos && repairData.photos.length > 0"
            class="photo-grid"
          >
            <div
              v-for="(photo, index) in repairData.photos"
              :key="index"
              class="photo-item"
              @click="previewPhoto(photo)"
            >
              <img
                :src="photo"
                alt="现场图片"
                loading="lazy"
              >
            </div>
          </div>
          <div
            v-else
            class="form-value"
          >
            暂无数据
          </div>
        </div>

        <div class="form-item-full">
          <span class="form-label">用户签字</span>
          <div
            v-if="repairData.signature"
            class="signature-container"
          >
            <img
              :src="repairData.signature"
              alt="用户签字"
              class="signature-image"
            >
          </div>
          <div
            v-else
            class="form-value"
          >
            暂无数据
          </div>
        </div>

        <div class="operation-log-section">
          <div class="section-title">
            内部确认区
          </div>
          <div
            v-if="operationLogs.length > 0"
            class="timeline"
          >
            <div
              v-for="(log, index) in operationLogs"
              :key="log.id"
              class="timeline-item"
              :class="{ last: index === operationLogs.length - 1 }"
            >
              <div class="timeline-dot" />
              <div class="timeline-content">
                <span class="timeline-time">{{ formatOperationTime(log.created_at) }}</span>
                <span class="timeline-operator">{{ log.operator_name }}</span>
                <span class="timeline-action">{{ log.operation_type_name }}</span>
              </div>
            </div>
          </div>
          <div
            v-else
            class="no-logs"
          >
            暂无数据
          </div>
        </div>
      </div>
      <div class="modal-footer">
        <button
          class="btn btn-cancel"
          @click="goBack"
        >
          关闭
        </button>
        <button
          v-if="isEditMode"
          class="btn btn-save"
          :disabled="saving"
          @click="handleSave"
        >
          {{ saving ? '保存中...' : '保存' }}
        </button>
      </div>
    </div>
  </div>
</template>

<script lang="ts">
import { defineComponent, ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { temporaryRepairService } from '@/services/temporaryRepair'
import request from '@/api/request'
import type { ApiResponse } from '@/types/api'

interface RepairData {
  id: number
  repair_id: string
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
  fault_description?: string
  solution?: string
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
  name: 'TemporaryRepairDetail',
  setup() {
    const route = useRoute()
    const router = useRouter()
    const isEditMode = ref(false)
    const repairData = ref<RepairData>({
      id: 0,
      repair_id: '',
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
      fault_description: '',
      solution: '',
      photos: [],
      signature: '',
    })

    const operationLogs = ref<OperationLogItem[]>([])
    const loadingLogs = ref(false)
    const saving = ref(false)

    const formatDate = (dateStr: string) => {
      if (!dateStr) return '-'
      const date = new Date(dateStr)
      return `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}-${String(date.getDate()).padStart(2, '0')}`
    }

    const toDateString = (value: any): string => {
      if (!value) return ''
      return String(value).split('T')[0]
    }

    const planStartDate = computed({
      get: () => toDateString(repairData.value.plan_start_date),
      set: (val: string) => { repairData.value.plan_start_date = val }
    })

    const planEndDate = computed({
      get: () => toDateString(repairData.value.plan_end_date),
      set: (val: string) => { repairData.value.plan_end_date = val }
    })

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
     * 获取操作日志
     */
    const fetchOperationLogs = async (workOrderId: number) => {
      if (!workOrderId) return
      loadingLogs.value = true
      try {
        const response = (await request.get(
          `/work-order-operation-log?work_order_type=temporary_repair&work_order_id=${workOrderId}`
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

    /**
     * 预览图片
     */
    const previewPhoto = (photo: string) => {
      window.open(photo, '_blank')
    }

    /**
     * 保存报修内容
     */
    const handleSave = async () => {
      if (!repairData.value.id) return

      saving.value = true
      try {
        const response = await temporaryRepairService.patch(repairData.value.id, {
          plan_start_date: repairData.value.plan_start_date || undefined,
          plan_end_date: repairData.value.plan_end_date || undefined,
          client_contact: repairData.value.client_contact || undefined,
          client_contact_info: repairData.value.client_contact_info || undefined,
          remarks: repairData.value.remarks || undefined,
        })
        if (response.code === 200) {
          if (repairData.value.status === '执行中' || repairData.value.status === '已退回') {
            try {
              const submitResponse = await temporaryRepairService.submit(repairData.value.id)
              if (submitResponse.code === 200) {
                repairData.value.status = '待确认'
                alert('保存成功，已自动提交审核')
              } else {
                alert('保存成功，但提交审核失败：' + (submitResponse.message || '未知错误'))
              }
            } catch (submitError) {
              console.error('提交审核失败:', submitError)
              alert('保存成功，但提交审核失败')
            }
          } else {
            alert('保存成功')
          }
        } else {
          alert(response.message || '保存失败')
        }
      } catch (error) {
        console.error('保存失败:', error)
        alert('保存失败')
      } finally {
        saving.value = false
      }
    }

    const loadData = async () => {
      const id = route.query.id as string
      const type = route.query.type as string
      isEditMode.value = type === 'edit'
      if (id) {
        try {
          const response = await temporaryRepairService.getById(parseInt(id))
          if (response.code === 200) {
            const item = response.data
            repairData.value = {
              id: item.id,
              repair_id: item.repair_id,
              project_id: item.project_id,
              project_name: item.project_name,
              plan_start_date: item.plan_start_date ? String(item.plan_start_date).split('T')[0] : '',
              plan_end_date: item.plan_end_date ? String(item.plan_end_date).split('T')[0] : '',
              client_name: item.client_name || '',
              client_contact: item.client_contact || '',
              client_contact_info: item.client_contact_info || '',
              client_contact_position: item.client_contact_position || '',
              address: item.address || '',
              maintenance_personnel: item.maintenance_personnel || '',
              status: item.status,
              remarks: item.remarks || '',
              fault_description: item.fault_description || '',
              solution: item.solution || '',
              photos: item.photos || [],
              signature: item.signature || '',
            }
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
      repairData,
      operationLogs,
      loadingLogs,
      saving,
      isEditMode,
      formatDate,
      formatOperationTime,
      goBack,
      previewPhoto,
      handleSave,
      planStartDate,
      planEndDate,
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
  min-height: 90px;
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

.form-item-full {
  margin-top: 24px;
}

.form-item-full .form-label {
  font-size: 14px;
  font-weight: 500;
  color: var(--color-text-regular);
  margin-bottom: 8px;
  display: block;
}

.form-value-large {
  min-height: 108px;
  align-items: flex-start;
  padding-top: 12px;
  white-space: pre-wrap;
  word-break: break-word;
}

.section-divider {
  margin-top: 24px;
  margin-bottom: 16px;
  border-bottom: 1px solid var(--color-border);
  position: relative;
}

.section-divider-text {
  position: absolute;
  top: -10px;
  left: 0;
  background: var(--color-bg-card);
  padding-right: 12px;
  font-size: 15px;
  font-weight: 600;
  color: var(--color-primary);
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
  border-radius: 4px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-cancel {
  background: var(--color-bg-card);
  color: var(--color-text-secondary);
  border: 1px solid var(--color-border);
}

.btn-cancel:hover:not(:disabled) {
  background: var(--color-bg-page);
}

.btn-save {
  background: var(--color-primary);
  color: var(--color-bg-card);
}

.btn-save:hover:not(:disabled) {
  background: var(--color-primary-dark);
}

.btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.form-input {
  width: 100%;
  padding: 8px 12px;
  border: 1px solid var(--color-border);
  border-radius: 4px;
  font-size: 14px;
  color: var(--color-text-primary);
  box-sizing: border-box;
}

.form-input:focus {
  outline: none;
  border-color: var(--color-primary);
  box-shadow: 0 0 0 2px rgba(25, 118, 210, 0.1);
}

.form-textarea {
  width: 100%;
  min-height: 108px;
  padding: 12px;
  border: 1px solid var(--color-border);
  border-radius: 4px;
  font-size: 14px;
  color: var(--color-text-primary);
  resize: vertical;
  font-family: inherit;
  line-height: 1.5;
  box-sizing: border-box;
}

.form-textarea:focus {
  outline: none;
  border-color: var(--color-primary);
  box-shadow: 0 0 0 2px rgba(25, 118, 210, 0.1);
}

.form-textarea::placeholder {
  color: var(--color-text-placeholder);
}

.operation-log-section {
  margin-top: 20px;
  padding-top: 20px;
  border-top: 1px solid var(--color-border);
}

.section-title {
  font-size: 16px;
  font-weight: 600;
  color: var(--color-text-primary);
  margin-bottom: 16px;
  padding-left: 12px;
  border-left: 3px solid var(--color-primary);
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

.photo-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 12px;
  margin-top: 8px;
}

.photo-item {
  position: relative;
  aspect-ratio: 1;
  border-radius: 8px;
  overflow: hidden;
  cursor: pointer;
  border: 1px solid var(--color-border);
  transition:
    transform 0.2s,
    box-shadow 0.2s;
}

.photo-item:hover {
  transform: scale(1.02);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.photo-item img {
  width: 100%;
  height: 100%;
  object-fit: cover;
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
