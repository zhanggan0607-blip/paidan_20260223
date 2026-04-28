<template>
  <div
    v-if="visible"
    class="pdf-preview-overlay"
    @click.self="handleClose"
  >
    <div class="pdf-preview-container">
      <div class="preview-header">
        <h3 class="preview-title">
          PDF预览 - {{ orderTitle }}
        </h3>
        <button
          class="preview-close"
          @click="handleClose"
        >
          ×
        </button>
      </div>
      <div class="preview-body">
        <div
          ref="a4Page"
          class="a4-page"
        >
          <div class="pdf-header">
            {{ orderTitle }}
          </div>

          <table class="pdf-info-table">
            <tr>
              <td class="pdf-label">
                {{ orderIdLabel }}
              </td>
              <td class="pdf-value">
                {{ orderId || '-' }}
              </td>
              <td class="pdf-label">
                项目编号
              </td>
              <td class="pdf-value">
                {{ data.project_id || '-' }}
              </td>
            </tr>
            <tr>
              <td class="pdf-label">
                项目名称
              </td>
              <td
                class="pdf-value"
                colspan="3"
              >
                {{ data.project_name || '-' }}
              </td>
            </tr>
            <tr>
              <td class="pdf-label">
                客户单位
              </td>
              <td class="pdf-value">
                {{ data.client_name || '-' }}
              </td>
              <td class="pdf-label">
                客户联系人
              </td>
              <td class="pdf-value">
                {{ data.client_contact || '-' }}
              </td>
            </tr>
            <tr>
              <td class="pdf-label">
                联系人职位
              </td>
              <td class="pdf-value">
                {{ data.client_contact_position || '-' }}
              </td>
              <td class="pdf-label">
                联系方式
              </td>
              <td class="pdf-value">
                {{ data.client_contact_info || '-' }}
              </td>
            </tr>
            <tr>
              <td class="pdf-label">
                客户地址
              </td>
              <td
                class="pdf-value"
                colspan="3"
              >
                {{ data.address || '-' }}
              </td>
            </tr>
            <tr>
              <td class="pdf-label">
                计划开始日期
              </td>
              <td class="pdf-value">
                {{ formatDate(data.plan_start_date) }}
              </td>
              <td class="pdf-label">
                计划结束日期
              </td>
              <td class="pdf-value">
                {{ formatDate(data.plan_end_date) }}
              </td>
            </tr>
            <tr>
              <td class="pdf-label">
                运维人员
              </td>
              <td class="pdf-value">
                {{ data.maintenance_personnel || '-' }}
              </td>
              <td class="pdf-label">
                状态
              </td>
              <td class="pdf-value">
                {{ data.status || '-' }}
              </td>
            </tr>
            <tr v-if="orderType === 'inspection'">
              <td class="pdf-label">
                合同剩余时间
              </td>
              <td
                class="pdf-value"
                colspan="3"
              >
                {{ data.remainingTime || '-' }}
              </td>
            </tr>
            <tr v-if="orderType === 'spotwork'">
              <td class="pdf-label">
                用工天数
              </td>
              <td class="pdf-value">
                {{ workDays }} 天
              </td>
              <td class="pdf-label">
                施工人数
              </td>
              <td class="pdf-value">
                {{ workers.length }} 人
              </td>
            </tr>
          </table>

          <div
            v-if="orderType === 'inspection' && inspectionRecords.length > 0"
            class="pdf-section-title"
          >
            巡检内容
          </div>
          <div
            v-if="orderType === 'inspection'"
            class="pdf-inspection-records"
          >
            <div
              v-for="(record, index) in inspectionRecords"
              :key="index"
              class="pdf-inspection-item"
            >
              <div class="pdf-inspection-header">
                <span class="pdf-inspection-num">{{ index + 1 }}.</span>
                <span class="pdf-inspection-name">{{ record.item_name || record.inspection_item || '巡检项' }}</span>
              </div>
              <div
                v-if="record.inspection_content"
                class="pdf-inspection-content"
              >
                {{ record.inspection_content }}
              </div>
              <div
                v-if="record.check_content"
                class="pdf-inspection-check"
              >
                <strong>检查要求：</strong> {{ record.check_content }}
              </div>
              <div
                v-if="record.equipment_name"
                class="pdf-inspection-equipment"
              >
                <strong>设备名称：</strong> {{ record.equipment_name }}
              </div>
              <div
                v-if="record.equipment_location"
                class="pdf-inspection-equipment"
              >
                <strong>设备位置：</strong> {{ record.equipment_location }}
              </div>
              <div
                v-if="record.inspection_result"
                class="pdf-inspection-result"
              >
                <strong>巡检结果：</strong> {{ record.inspection_result }}
              </div>
            </div>
          </div>

          <div class="pdf-section-title">
            {{ contentSectionTitle }}
          </div>
          <div class="pdf-content-box">
            {{ data.execution_result || data.work_content || '无' }}
          </div>

          <div class="pdf-section-title">
            {{ remarksSectionTitle }}
          </div>
          <div class="pdf-content-box">
            {{ data.remarks || '无' }}
          </div>

          <template v-if="orderType === 'spotwork'">
            <div class="pdf-section-title">
              施工人员名单
            </div>
            <table
              v-if="workers.length > 0"
              class="pdf-worker-table"
            >
              <thead>
                <tr>
                  <th style="width: 50px">
                    序号
                  </th>
                  <th style="width: 120px">
                    姓名
                  </th>
                  <th style="width: 60px">
                    性别
                  </th>
                  <th>身份证号</th>
                </tr>
              </thead>
              <tbody>
                <tr
                  v-for="(worker, index) in workers"
                  :key="index"
                >
                  <td style="text-align: center">
                    {{ index + 1 }}
                  </td>
                  <td>{{ worker.name }}</td>
                  <td style="text-align: center">
                    {{ worker.gender || '-' }}
                  </td>
                  <td>{{ maskIdCard(worker.id_card_number) }}</td>
                </tr>
              </tbody>
            </table>
            <div
              v-else
              class="pdf-no-content"
            >
              暂无施工人员
            </div>
          </template>

          <div class="pdf-section-title">
            现场照片
          </div>
          <div class="pdf-photo-grid">
            <template v-if="photos.length > 0">
              <div
                v-for="(photo, index) in photos"
                :key="index"
                class="pdf-photo-item"
              >
                <img
                  :src="photo"
                  alt="现场照片"
                >
              </div>
            </template>
            <div
              v-else
              class="pdf-no-content"
            >
              暂无现场照片
            </div>
          </div>

          <div class="pdf-section-title">
            {{ signatureTitle }}
          </div>
          <div class="pdf-signature-box">
            <img
              v-if="data.signature"
              :src="data.signature"
              :alt="signatureTitle"
              class="pdf-signature-img"
            >
            <span
              v-else
              class="pdf-no-content"
            >暂无{{ signatureTitle }}</span>
          </div>

          <div class="pdf-section-title">
            内部确认区
          </div>
          <table class="pdf-log-table">
            <thead>
              <tr>
                <th>操作时间</th>
                <th>操作人</th>
                <th>操作类型</th>
                <th>备注</th>
              </tr>
            </thead>
            <tbody>
              <template v-if="operationLogs.length > 0">
                <tr
                  v-for="log in operationLogs"
                  :key="log.id"
                >
                  <td>{{ formatOperationTime(log.created_at) }}</td>
                  <td>{{ log.operator_name }}</td>
                  <td>{{ log.operation_type_name }}</td>
                  <td>{{ log.operation_remark || '-' }}</td>
                </tr>
              </template>
              <tr v-else>
                <td
                  colspan="4"
                  class="pdf-no-content"
                >
                  暂无操作记录
                </td>
              </tr>
            </tbody>
          </table>

          <div class="pdf-footer">
            <p>打印时间：{{ currentDateTime }}</p>
          </div>
        </div>
      </div>
      <div class="preview-footer">
        <button
          class="btn btn-cancel"
          @click="handleClose"
        >
          关闭
        </button>
        <button
          class="btn btn-export"
          :disabled="exporting"
          @click="handleExport"
        >
          {{ exporting ? '导出中...' : '导出PDF' }}
        </button>
      </div>
    </div>
  </div>
</template>

<script lang="ts">
import { defineComponent, ref, computed, PropType } from 'vue'

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

interface InspectionRecordItem {
  id: number
  item_id: string
  item_name: string
  inspection_item: string
  inspection_content: string
  check_content: string
  equipment_name: string
  equipment_location: string
  inspection_result: string
  photos: string
}

interface WorkerItem {
  id?: number
  name: string
  gender: string
  id_card_number?: string
}

interface PreviewData {
  id: number
  inspection_id?: string
  repair_id?: string
  work_id?: string
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
  execution_result: string
  remarks: string
  signature: string
  remainingTime: string
  work_content?: string
}

type OrderType = 'inspection' | 'repair' | 'spotwork'

export default defineComponent({
  name: 'PdfPreviewModal',
  props: {
    visible: {
      type: Boolean,
      default: false,
    },
    data: {
      type: Object as PropType<PreviewData>,
      required: true,
    },
    operationLogs: {
      type: Array as PropType<OperationLogItem[]>,
      default: (): any[] => [],
    },
    photos: {
      type: Array as PropType<string[]>,
      default: (): any[] => [],
    },
    orderType: {
      type: String as PropType<OrderType>,
      default: 'inspection',
    },
    inspectionRecords: {
      type: Array as PropType<InspectionRecordItem[]>,
      default: (): any[] => [],
    },
    workers: {
      type: Array as PropType<WorkerItem[]>,
      default: (): any[] => [],
    },
  },
  emits: ['close', 'export'],
  setup(props, { emit }) {
    const a4Page = ref<HTMLElement | null>(null)
    const exporting = ref(false)

    const orderTitle = computed(() => {
      switch (props.orderType) {
        case 'inspection':
          return '定期巡检单'
        case 'repair':
          return '临时维修单'
        case 'spotwork':
          return '零星用工单'
        default:
          return '工单'
      }
    })

    const orderIdLabel = computed(() => {
      switch (props.orderType) {
        case 'inspection':
          return '巡检单编号'
        case 'repair':
          return '维修单编号'
        case 'spotwork':
          return '用工单编号'
        default:
          return '工单编号'
      }
    })

    const orderId = computed(() => {
      switch (props.orderType) {
        case 'inspection':
          return props.data.inspection_id
        case 'repair':
          return props.data.repair_id
        case 'spotwork':
          return props.data.work_id
        default:
          return props.data.inspection_id
      }
    })

    const contentSectionTitle = computed(() => {
      switch (props.orderType) {
        case 'inspection':
          return '发现问题'
        case 'repair':
          return '故障情况'
        case 'spotwork':
          return '工作内容'
        default:
          return '内容'
      }
    })

    const remarksSectionTitle = computed(() => {
      switch (props.orderType) {
        case 'inspection':
          return '处理结果'
        case 'repair':
          return '维修结果'
        case 'spotwork':
          return '工作备注'
        default:
          return '备注'
      }
    })

    const signatureTitle = computed(() => {
      if (props.orderType === 'spotwork') {
        return '班组签字'
      }
      return '用户签字'
    })

    const workDays = computed(() => {
      if (!props.data.plan_start_date || !props.data.plan_end_date) {
        return '-'
      }
      const startDate = new Date(props.data.plan_start_date)
      const endDate = new Date(props.data.plan_end_date)
      const diffTime = endDate.getTime() - startDate.getTime()
      const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24)) + 1
      return diffDays > 0 ? diffDays : '-'
    })

    const maskIdCard = (idCard?: string) => {
      if (!idCard) return '-'
      if (idCard.length >= 10) {
        return `${idCard.slice(0, 6)}****${idCard.slice(-4)}`
      }
      return idCard
    }

    const currentDateTime = computed(() => {
      const now = new Date()
      const year = now.getFullYear()
      const month = String(now.getMonth() + 1).padStart(2, '0')
      const day = String(now.getDate()).padStart(2, '0')
      const hours = String(now.getHours()).padStart(2, '0')
      const minutes = String(now.getMinutes()).padStart(2, '0')
      const seconds = String(now.getSeconds()).padStart(2, '0')
      return `${year}-${month}-${day} ${hours}:${minutes}:${seconds}`
    })

    const formatDate = (dateStr: string) => {
      if (!dateStr) return '-'
      if (dateStr.includes('T')) {
        return dateStr.split('T')[0]
      }
      return dateStr
    }

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

    const handleClose = () => {
      emit('close')
    }

    const handleExport = async () => {
      exporting.value = true
      try {
        emit('export')
      } finally {
        setTimeout(() => {
          exporting.value = false
        }, 1000)
      }
    }

    return {
      a4Page,
      exporting,
      currentDateTime,
      formatDate,
      formatOperationTime,
      handleClose,
      handleExport,
      orderTitle,
      orderIdLabel,
      orderId,
      contentSectionTitle,
      remarksSectionTitle,
      signatureTitle,
      workDays,
      maskIdCard,
    }
  },
})
</script>

<style scoped>
.pdf-preview-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.6);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 2000;
}

.pdf-preview-container {
  background: var(--color-bg-page);
  border-radius: 8px;
  width: 900px;
  max-width: 95vw;
  max-height: 95vh;
  display: flex;
  flex-direction: column;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.2);
}

.preview-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 24px;
  background: var(--color-bg-card);
  border-bottom: 1px solid var(--color-border);
  border-radius: 8px 8px 0 0;
}

.preview-title {
  font-size: 18px;
  font-weight: 600;
  color: var(--color-text-primary);
  margin: 0;
}

.preview-close {
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

.preview-close:hover {
  color: var(--color-text-primary);
}

.preview-body {
  flex: 1;
  overflow-y: auto;
  padding: 20px;
  display: flex;
  justify-content: center;
}

.a4-page {
  width: 210mm;
  min-height: 297mm;
  background: var(--color-bg-card);
  padding: 15mm;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  font-family: "SimSun", "Microsoft YaHei", sans-serif;
  font-size: 12px;
  line-height: 1.6;
  color: var(--color-text-primary);
}

.pdf-header {
  text-align: center;
  font-size: 20px;
  font-weight: bold;
  margin-bottom: 20px;
  padding-bottom: 10px;
  border-bottom: 2px solid var(--color-text-primary);
}

.pdf-info-table {
  width: 100%;
  border-collapse: collapse;
  margin-bottom: 15px;
}

.pdf-info-table td {
  border: 1px solid var(--color-text-primary);
  padding: 6px 10px;
  vertical-align: middle;
}

.pdf-label {
  background-color: var(--color-bg-page);
  font-weight: bold;
  width: 80px;
  text-align: center;
}

.pdf-value {
  min-width: 100px;
}

.pdf-section-title {
  font-size: 14px;
  font-weight: bold;
  margin: 12px 0 8px 0;
  padding-left: 8px;
  border-left: 3px solid var(--color-primary);
}

.pdf-content-box {
  border: 1px solid var(--color-text-primary);
  padding: 8px 10px;
  min-height: 50px;
  margin-bottom: 10px;
  white-space: pre-wrap;
}

.pdf-photo-grid {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-bottom: 10px;
}

.pdf-photo-item {
  width: 80px;
  height: 80px;
  border: 1px solid #ddd;
  overflow: hidden;
}

.pdf-photo-item img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.pdf-no-content {
  color: var(--color-text-placeholder);
  text-align: center;
  padding: 10px;
}

.pdf-signature-box {
  border: 1px solid var(--color-text-primary);
  padding: 10px;
  min-height: 60px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 10px;
}

.pdf-signature-img {
  max-width: 200px;
  max-height: 80px;
  object-fit: contain;
}

.pdf-log-table {
  width: 100%;
  border-collapse: collapse;
  margin-bottom: 10px;
}

.pdf-log-table th,
.pdf-log-table td {
  border: 1px solid var(--color-text-primary);
  padding: 6px 8px;
  text-align: left;
}

.pdf-log-table th {
  background-color: var(--color-bg-page);
  font-weight: bold;
  text-align: center;
}

.pdf-log-table td {
  font-size: 11px;
}

.pdf-worker-table {
  width: 100%;
  border-collapse: collapse;
  margin-bottom: 10px;
}

.pdf-worker-table th,
.pdf-worker-table td {
  border: 1px solid var(--color-text-primary);
  padding: 6px 8px;
  text-align: left;
}

.pdf-worker-table th {
  background-color: var(--color-bg-page);
  font-weight: bold;
  text-align: center;
}

.pdf-worker-table td {
  font-size: 11px;
}

.pdf-footer {
  text-align: center;
  margin-top: 20px;
  padding-top: 10px;
  border-top: 1px solid #ddd;
  font-size: 10px;
  color: var(--color-text-secondary);
}

.pdf-inspection-records {
  margin-bottom: 10px;
}

.pdf-inspection-item {
  border: 1px solid #ddd;
  padding: 10px;
  margin-bottom: 8px;
  background: var(--color-bg-page);
}

.pdf-inspection-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 8px;
  padding-bottom: 8px;
  border-bottom: 1px solid var(--color-border-light);
}

.pdf-inspection-num {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 24px;
  height: 24px;
  background: var(--color-primary);
  color: var(--color-bg-card);
  border-radius: 50%;
  font-size: 12px;
  font-weight: bold;
}

.pdf-inspection-name {
  font-size: 14px;
  font-weight: bold;
  color: var(--color-text-primary);
}

.pdf-inspection-content,
.pdf-inspection-check,
.pdf-inspection-equipment,
.pdf-inspection-result {
  font-size: 12px;
  color: #555;
  margin: 4px 0;
  line-height: 1.5;
}

.pdf-inspection-check strong,
.pdf-inspection-equipment strong,
.pdf-inspection-result strong {
  color: var(--color-text-primary);
}

.preview-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  padding: 16px 24px;
  background: var(--color-bg-card);
  border-top: 1px solid var(--color-border);
  border-radius: 0 0 8px 8px;
}

.btn {
  padding: 8px 20px;
  border: none;
  border-radius: 4px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.15s;
}

.btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.btn-cancel {
  background: var(--color-bg-card);
  color: var(--color-text-secondary);
  border: 1px solid var(--color-border);
}

.btn-cancel:hover:not(:disabled) {
  background: var(--color-bg-page);
}

.btn-export {
  background: var(--color-primary);
  color: var(--color-bg-card);
}

.btn-export:hover:not(:disabled) {
  background: var(--color-primary-dark);
}

@media print {
  .pdf-preview-overlay {
    background: none;
  }

  .pdf-preview-container {
    width: 100%;
    max-width: none;
    max-height: none;
    box-shadow: none;
  }

  .preview-header,
  .preview-footer {
    display: none;
  }

  .preview-body {
    padding: 0;
    overflow: visible;
  }

  .a4-page {
    width: 100%;
    box-shadow: none;
    padding: 0;
  }
}
</style>
