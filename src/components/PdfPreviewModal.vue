<template>
  <div v-if="visible" class="pdf-preview-overlay" @click.self="handleClose">
    <div class="pdf-preview-container">
      <div class="preview-header">
        <h3 class="preview-title">PDF预览 - 定期巡检单</h3>
        <button class="preview-close" @click="handleClose">×</button>
      </div>
      <div class="preview-body">
        <div class="a4-page" ref="a4Page">
          <div class="pdf-header">定期巡检单</div>

          <table class="pdf-info-table">
            <tr>
              <td class="pdf-label">巡检单编号</td>
              <td class="pdf-value">{{ data.inspection_id || '-' }}</td>
              <td class="pdf-label">项目编号</td>
              <td class="pdf-value">{{ data.project_id || '-' }}</td>
            </tr>
            <tr>
              <td class="pdf-label">项目名称</td>
              <td class="pdf-value" colspan="3">{{ data.project_name || '-' }}</td>
            </tr>
            <tr>
              <td class="pdf-label">客户单位</td>
              <td class="pdf-value">{{ data.client_name || '-' }}</td>
              <td class="pdf-label">客户联系人</td>
              <td class="pdf-value">{{ data.client_contact || '-' }}</td>
            </tr>
            <tr>
              <td class="pdf-label">联系人职位</td>
              <td class="pdf-value">{{ data.client_contact_position || '-' }}</td>
              <td class="pdf-label">联系方式</td>
              <td class="pdf-value">{{ data.client_contact_info || '-' }}</td>
            </tr>
            <tr>
              <td class="pdf-label">客户地址</td>
              <td class="pdf-value" colspan="3">{{ data.address || '-' }}</td>
            </tr>
            <tr>
              <td class="pdf-label">计划开始日期</td>
              <td class="pdf-value">{{ formatDate(data.plan_start_date) }}</td>
              <td class="pdf-label">计划结束日期</td>
              <td class="pdf-value">{{ formatDate(data.plan_end_date) }}</td>
            </tr>
            <tr>
              <td class="pdf-label">运维人员</td>
              <td class="pdf-value">{{ data.maintenance_personnel || '-' }}</td>
              <td class="pdf-label">状态</td>
              <td class="pdf-value">{{ data.status || '-' }}</td>
            </tr>
            <tr>
              <td class="pdf-label">合同剩余时间</td>
              <td class="pdf-value" colspan="3">{{ data.remainingTime || '-' }}</td>
            </tr>
          </table>

          <div class="pdf-section-title">发现问题</div>
          <div class="pdf-content-box">{{ data.execution_result || '无' }}</div>

          <div class="pdf-section-title">处理结果</div>
          <div class="pdf-content-box">{{ data.remarks || '无' }}</div>

          <div class="pdf-section-title">现场照片</div>
          <div class="pdf-photo-grid">
            <template v-if="photos.length > 0">
              <div v-for="(photo, index) in photos" :key="index" class="pdf-photo-item">
                <img :src="photo" alt="现场照片" />
              </div>
            </template>
            <div v-else class="pdf-no-content">暂无现场照片</div>
          </div>

          <div class="pdf-section-title">用户签字</div>
          <div class="pdf-signature-box">
            <img v-if="data.signature" :src="data.signature" alt="用户签字" class="pdf-signature-img" />
            <span v-else class="pdf-no-content">暂无用户签字</span>
          </div>

          <div class="pdf-section-title">内部确认区</div>
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
                <tr v-for="log in operationLogs" :key="log.id">
                  <td>{{ formatOperationTime(log.created_at) }}</td>
                  <td>{{ log.operator_name }}</td>
                  <td>{{ log.operation_type_name }}</td>
                  <td>{{ log.operation_remark || '-' }}</td>
                </tr>
              </template>
              <tr v-else>
                <td colspan="4" class="pdf-no-content">暂无操作记录</td>
              </tr>
            </tbody>
          </table>

          <div class="pdf-footer">
            <p>打印时间：{{ currentDateTime }}</p>
          </div>
        </div>
      </div>
      <div class="preview-footer">
        <button class="btn btn-cancel" @click="handleClose">关闭</button>
        <button class="btn btn-export" :disabled="exporting" @click="handleExport">
          {{ exporting ? '导出中...' : '导出PDF' }}
        </button>
      </div>
    </div>
  </div>
</template>

<script lang="ts">
import { defineComponent, ref, computed } from 'vue'

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

interface PreviewData {
  id: number
  inspection_id: string
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
}

export default defineComponent({
  name: 'PdfPreviewModal',
  props: {
    visible: {
      type: Boolean,
      default: false,
    },
    data: {
      type: Object as () => PreviewData,
      required: true,
    },
    operationLogs: {
      type: Array as () => OperationLogItem[],
      default: () => [],
    },
    photos: {
      type: Array as () => string[],
      default: () => [],
    },
  },
  emits: ['close', 'export'],
  setup(_props, { emit }) {
    const a4Page = ref<HTMLElement | null>(null)
    const exporting = ref(false)

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
  background: #f5f5f5;
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
  background: #fff;
  border-bottom: 1px solid #e0e0e0;
  border-radius: 8px 8px 0 0;
}

.preview-title {
  font-size: 18px;
  font-weight: 600;
  color: #333;
  margin: 0;
}

.preview-close {
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

.preview-close:hover {
  color: #333;
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
  background: #fff;
  padding: 15mm;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  font-family: "SimSun", "Microsoft YaHei", sans-serif;
  font-size: 12px;
  line-height: 1.6;
  color: #333;
}

.pdf-header {
  text-align: center;
  font-size: 20px;
  font-weight: bold;
  margin-bottom: 20px;
  padding-bottom: 10px;
  border-bottom: 2px solid #333;
}

.pdf-info-table {
  width: 100%;
  border-collapse: collapse;
  margin-bottom: 15px;
}

.pdf-info-table td {
  border: 1px solid #333;
  padding: 6px 10px;
  vertical-align: middle;
}

.pdf-label {
  background-color: #f5f5f5;
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
  border-left: 3px solid #1976d2;
}

.pdf-content-box {
  border: 1px solid #333;
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
  color: #999;
  text-align: center;
  padding: 10px;
}

.pdf-signature-box {
  border: 1px solid #333;
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
  border: 1px solid #333;
  padding: 6px 8px;
  text-align: left;
}

.pdf-log-table th {
  background-color: #f5f5f5;
  font-weight: bold;
  text-align: center;
}

.pdf-log-table td {
  font-size: 11px;
}

.pdf-footer {
  text-align: center;
  margin-top: 20px;
  padding-top: 10px;
  border-top: 1px solid #ddd;
  font-size: 10px;
  color: #666;
}

.preview-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  padding: 16px 24px;
  background: #fff;
  border-top: 1px solid #e0e0e0;
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
  background: #fff;
  color: #666;
  border: 1px solid #e0e0e0;
}

.btn-cancel:hover:not(:disabled) {
  background: #f5f5f5;
}

.btn-export {
  background: #1976d2;
  color: #fff;
}

.btn-export:hover:not(:disabled) {
  background: #1565c0;
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
