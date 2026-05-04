<template>
  <div class="periodic-inspection-query">
    <LoadingSpinner
      :visible="loading"
      text="加载中..."
    />
    <Toast
      :visible="toast.visible"
      :message="toast.message"
      :type="toast.type"
    />

    <div class="search-section">
      <div class="search-form">
        <div class="search-row">
          <div class="search-item">
            <label
              for="search_projectName"
              class="search-label"
            >项目名称：</label>
            <SearchInput
              v-model="searchForm.projectName"
              input-id="search_projectName"
              field-key="PeriodicInspectionQuery_projectName"
              placeholder="请输入项目名称"
              @input="handleSearch"
            />
          </div>
          <div class="search-item">
            <label
              for="search_clientName"
              class="search-label"
            >客户名称：</label>
            <SearchInput
              v-model="searchForm.clientName"
              input-id="search_clientName"
              field-key="PeriodicInspectionQuery_clientName"
              placeholder="请输入客户名称"
              @input="handleSearch"
            />
          </div>
        </div>
      </div>
    </div>

    <div class="table-section">
      <table class="data-table">
        <thead>
          <tr>
            <th>序号</th>
            <th>项目编号</th>
            <th>项目名称</th>
            <th>巡检单编号</th>
            <th>开始日期</th>
            <th>结束日期</th>
            <th>客户单位</th>
            <th>运维人员</th>
            <th>状态</th>
            <th>操作</th>
          </tr>
        </thead>
        <tbody>
          <tr
            v-for="(item, index) in inspectionData"
            :key="item.id"
            :class="{ 'even-row': index % 2 === 0 }"
          >
            <td>{{ startIndex + index + 1 }}</td>
            <td>{{ item.project_id }}</td>
            <td>{{ item.project_name }}</td>
            <td>{{ item.inspection_id }}</td>
            <td>{{ formatDate(item.plan_start_date) }}</td>
            <td>{{ formatDate(item.plan_end_date) }}</td>
            <td>{{ item.client_name || '暂无数据' }}</td>
            <td>{{ item.maintenance_personnel || '暂无数据' }}</td>
            <td>
              <span
                :class="getStatusClass(item.status)"
                class="status-badge"
              >{{
                item.status
              }}</span>
            </td>
            <td class="action-cell">
              <a
                href="#"
                class="action-link action-view"
                @click.prevent="handleView(item)"
              >查看</a>
              <a
                v-if="canEditWork(item)"
                href="#"
                class="action-link action-edit"
                @click.prevent="handleEdit(item)"
              >编辑</a>
              <a
                v-if="isAdmin && item.status === WORK_STATUS.PENDING_CONFIRM"
                href="#"
                class="action-link action-reject"
                @click.prevent="handleReject(item)"
              >退回</a>
              <a
                v-if="canRecallWork(item)"
                href="#"
                class="action-link action-recall"
                @click.prevent="handleRecall(item)"
              >撤回</a>
              <a
                v-if="item.status === WORK_STATUS.COMPLETED"
                href="#"
                class="action-link action-export"
                @click.prevent="handleExport(item)"
              >导出</a>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <div class="pagination-section">
      <div class="pagination-info">
        共 {{ totalElements }} 条记录
      </div>
      <div class="pagination-controls">
        <button
          class="page-btn page-nav"
          :disabled="currentPage === 0"
          @click="currentPage--"
        >
          &lt;
        </button>
        <button
          v-for="page in totalPages"
          :key="page"
          class="page-btn page-num"
          :class="{ active: page === currentPage + 1 }"
          @click="currentPage = page - 1"
        >
          {{ page }}
        </button>
        <button
          class="page-btn page-nav"
          :disabled="currentPage >= totalPages - 1"
          @click="currentPage++"
        >
          &gt;
        </button>
        <select
          id="pageSize"
          v-model="pageSize"
          name="pageSize"
          class="page-select"
          @change="handlePageSizeChange"
        >
          <option value="10">
            10 条 / 页
          </option>
          <option value="20">
            20 条 / 页
          </option>
          <option value="50">
            50 条 / 页
          </option>
        </select>
        <div class="page-jump">
          <span>跳至</span>
          <input
            id="jumpPage"
            v-model="jumpPage"
            name="jumpPage"
            type="number"
            class="page-input"
            min="1"
            :max="totalPages"
          >
          <span>页</span>
          <button
            class="page-btn page-go"
            @click="handleJump"
          >
            Go
          </button>
        </div>
      </div>
    </div>

    <div
      v-if="isViewModalOpen"
      class="modal-overlay"
      @click.self="closeViewModal"
    >
      <div class="modal-container">
        <div class="modal-header">
          <h3 class="modal-title">
            查看巡检单
          </h3>
          <button
            class="modal-close"
            @click="closeViewModal"
          >
            ×
          </button>
        </div>
        <div class="modal-body">
          <div class="form-grid">
            <div class="form-column">
              <div class="form-item">
                <span class="form-label">巡检单编号</span>
                <div class="form-value">
                  {{ viewData.inspection_id || '暂无数据' }}
                </div>
              </div>
              <div class="form-item">
                <span class="form-label">项目编号</span>
                <div class="form-value">
                  {{ viewData.project_id || '暂无数据' }}
                </div>
              </div>
              <div class="form-item">
                <span class="form-label">项目名称</span>
                <div class="form-value">
                  {{ viewData.project_name || '暂无数据' }}
                </div>
              </div>
              <div class="form-item">
                <span class="form-label">客户单位</span>
                <div class="form-value">
                  {{ viewData.client_name || '暂无数据' }}
                </div>
              </div>
              <div class="form-item">
                <span class="form-label">客户联系人</span>
                <div class="form-value">
                  {{ viewData.client_contact || '暂无数据' }}
                </div>
              </div>
              <div class="form-item">
                <span class="form-label">联系人职位</span>
                <div class="form-value">
                  {{ viewData.client_contact_position || '暂无数据' }}
                </div>
              </div>
            </div>
            <div class="form-column">
              <div class="form-item">
                <span class="form-label">计划开始日期</span>
                <div class="form-value">
                  {{ formatDate(viewData.plan_start_date) || '暂无数据' }}
                </div>
              </div>
              <div class="form-item">
                <span class="form-label">计划结束日期</span>
                <div class="form-value">
                  {{ formatDate(viewData.plan_end_date) || '暂无数据' }}
                </div>
              </div>
              <div class="form-item">
                <span class="form-label">运维人员</span>
                <div class="form-value">
                  {{ viewData.maintenance_personnel || '暂无数据' }}
                </div>
              </div>
              <div class="form-item">
                <span class="form-label">客户联系方式</span>
                <div class="form-value">
                  {{ viewData.client_contact_info || '暂无数据' }}
                </div>
              </div>
              <div class="form-item">
                <span class="form-label">客户地址</span>
                <div class="form-value">
                  {{ viewData.address || '暂无数据' }}
                </div>
              </div>
              <div class="form-item">
                <span class="form-label">合同剩余时间</span>
                <div
                  class="form-value"
                  :class="getRemainingTimeClass()"
                >
                  {{ viewData.remainingTime || '暂无数据' }}
                </div>
              </div>
              <div class="form-item">
                <span class="form-label">状态</span>
                <div
                  class="form-value"
                  :class="getStatusClass(viewData.status)"
                >
                  {{ viewData.status || '暂无数据' }}
                </div>
              </div>
              <div class="form-item">
                <span class="form-label">创建时间</span>
                <div class="form-value">
                  {{ formatDateTime(viewData.created_at) || '暂无数据' }}
                </div>
              </div>
            </div>
          </div>
          <div class="form-item-full">
            <span class="form-label">发现问题</span>
            <div class="form-value form-value-textarea">
              {{ viewData.execution_result || '暂无数据' }}
            </div>
          </div>
          <div class="form-item-full">
            <span class="form-label">处理结果</span>
            <div class="form-value form-value-textarea">
              {{ viewData.remarks || '暂无数据' }}
            </div>
          </div>
          <div class="form-item-full">
            <span class="form-label">用户签字</span>
            <div
              v-if="viewData.signature"
              class="form-value signature-container"
            >
              <img
                :src="viewData.signature"
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
          <div class="form-item-full">
            <span class="form-label">现场照片</span>
            <div
              v-if="inspectionRecords.length > 0"
              class="photos-container"
            >
              <div
                v-for="record in inspectionRecords"
                :key="record.id"
                class="record-photos"
              >
                <div
                  v-for="(photo, photoIndex) in record.photos"
                  :key="photoIndex"
                  class="photo-item"
                  @click="previewPhoto(record.photos, photoIndex)"
                >
                  <img
                    :src="photo"
                    alt="现场照片"
                    loading="lazy"
                  >
                </div>
              </div>
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
            @click="closeViewModal"
          >
            关闭
          </button>
        </div>
      </div>
    </div>

    <div
      v-if="showRejectModal"
      class="modal-overlay"
      @click.self="closeRejectModal"
    >
      <div class="modal-container modal-small">
        <div class="modal-header">
          <h3 class="modal-title">
            退回确认
          </h3>
          <button
            class="modal-close"
            @click="closeRejectModal"
          >
            ×
          </button>
        </div>
        <div class="modal-body">
          <div class="form-item-full">
            <label
              for="rejectReason"
              class="form-label"
            >退回原因 <span class="required">*</span></label>
            <textarea
              id="rejectReason"
              v-model="rejectReason"
              name="rejectReason"
              class="form-input form-textarea"
              placeholder="请输入退回原因（10-500字符）"
              maxlength="500"
              rows="4"
            />
            <div class="char-count">
              {{ rejectReason.length }}/500
            </div>
          </div>
        </div>
        <div class="modal-footer">
          <button
            class="btn btn-cancel"
            @click="closeRejectModal"
          >
            取消
          </button>
          <button
            class="btn btn-reject"
            :disabled="saving"
            @click="confirmReject"
          >
            {{ saving ? '处理中...' : '确认退回' }}
          </button>
        </div>
      </div>
    </div>

    <PdfPreviewModal
      :visible="showPdfPreview"
      :data="pdfPreviewData"
      :operation-logs="pdfPreviewLogs"
      :photos="pdfPreviewPhotos"
      @close="closePdfPreview"
      @export="exportFromPreview"
    />
  </div>
</template>

<script lang="ts">
import {
  defineComponent,
  reactive,
  ref,
  computed,
  watch,
  onMounted,
  onUnmounted,
  watchEffect,
} from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { periodicInspectionService, type PeriodicInspection } from '../services/periodicInspection'
import { workPlanService } from '../services/workPlan'
import { projectInfoService, type ProjectInfo } from '../services/projectInfo'
import request from '@/api/request'
import type { ApiResponse } from '../types/api'
import { LoadingSpinner, Toast, SearchInput } from '@sstcp/shared'
import PdfPreviewModal from '../components/PdfPreviewModal.vue'
import { WORK_STATUS, formatDate as formatDateUtil } from '../config/constants'
import { useUserStore } from '../stores/userStore'

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

interface InspectionItem {
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
  created_at: string
  updated_at: string
}

interface InspectionRecord {
  id: number
  item_id: string
  item_name: string
  inspection_item: string
  inspection_content: string
  inspection_result: string
  photos: string[]
  inspected: boolean
}

export default defineComponent({
  name: 'PeriodicInspectionQuery',
  components: {
    LoadingSpinner,
    Toast,
    SearchInput,
    PdfPreviewModal,
  },
  setup() {
    const userStore = useUserStore()
    const route = useRoute()
    const router = useRouter()
    const searchForm = reactive({
      projectName: '',
      clientName: '',
    })

    const currentPage = ref(0)
    const pageSize = ref(10)
    const jumpPage = ref(1)
    const loading = ref(false)
    const saving = ref(false)
    const isViewModalOpen = ref(false)

    const isAdmin = ref(userStore.isAdmin())
    const isDepartmentManager = ref(userStore.isDepartmentManager?.() || false)
    const currentUserName = ref(userStore.currentUser?.name || '')

    const canEditWork = (item: InspectionItem): boolean => {
      if (isAdmin.value) return true
      if (item.status === WORK_STATUS.COMPLETED) return false
      const isOwner = item.maintenance_personnel === currentUserName.value
      const isEditableStatus = item.status === WORK_STATUS.PENDING_CONFIRM ||
                               item.status === WORK_STATUS.IN_PROGRESS ||
                               item.status === WORK_STATUS.RETURNED
      return isOwner && isEditableStatus
    }

    const canRecallWork = (item: InspectionItem): boolean => {
      if (item.status !== WORK_STATUS.PENDING_CONFIRM) return false
      if (isAdmin.value) return true
      return item.maintenance_personnel === currentUserName.value
    }

    const inspectionData = ref<InspectionItem[]>([])
    const totalElements = ref(0)
    const totalPages = ref(0)

    const toast = reactive({
      visible: false,
      message: '',
      type: 'success' as 'success' | 'error' | 'warning' | 'info',
    })

    const viewData = reactive({
      id: 0,
      inspection_id: '',
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
      execution_result: '',
      remarks: '',
      signature: '',
      created_at: '',
      updated_at: '',
      remainingTime: '',
    })

    const inspectionRecords = ref<InspectionRecord[]>([])
    const loadingRecords = ref(false)

    const operationLogs = ref<OperationLogItem[]>([])
    const loadingLogs = ref(false)

    const showPdfPreview = ref(false)
    const pdfPreviewData = ref<any>({})
    const pdfPreviewLogs = ref<OperationLogItem[]>([])
    const pdfPreviewPhotos = ref<string[]>([])
    const pendingExportItem = ref<InspectionItem | null>(null)

    const startIndex = computed(() => currentPage.value * pageSize.value)

    let abortController: AbortController | null = null

    const showToast = (
      message: string,
      type: 'success' | 'error' | 'warning' | 'info' = 'success'
    ) => {
      toast.message = message
      toast.type = type
      toast.visible = true
    }

    const formatDate = (dateStr: string) => {
      return formatDateUtil(dateStr)
    }

    const formatDateTime = (dateStr: string) => {
      if (!dateStr) return '-'
      const date = new Date(dateStr)
      return date.toLocaleString('zh-CN', {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit',
      })
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
     * 获取操作日志
     */
    const fetchOperationLogs = async (workOrderId: number) => {
      if (!workOrderId) return
      loadingLogs.value = true
      try {
        const response = (await request.get(
          `/work-order-operation-log?work_order_type=periodic_inspection&work_order_id=${workOrderId}`
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

    /**
     * 获取巡检记录
     */
    const fetchInspectionRecords = async (inspectionId: string) => {
      if (!inspectionId) return
      loadingRecords.value = true
      try {
        const response = (await request.get(
          `/periodic-inspection-record/inspection/${inspectionId}`
        )) as unknown as ApiResponse<InspectionRecord[]>
        if (response.code === 200) {
          inspectionRecords.value = response.data || []
        }
      } catch (error) {
        console.error('获取巡检记录失败:', error)
        inspectionRecords.value = []
      } finally {
        loadingRecords.value = false
      }
    }

    const calculateRemainingTime = (endDate: string): string => {
      if (!endDate) return '-'

      const today = new Date()
      today.setHours(0, 0, 0, 0)

      const end = new Date(endDate)
      end.setHours(0, 0, 0, 0)

      const diffTime = end.getTime() - today.getTime()

      if (diffTime < 0) {
        return '已过期'
      }

      const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24))

      const years = Math.floor(diffDays / 365)
      const months = Math.floor((diffDays % 365) / 30)
      const days = diffDays % 30

      const parts: string[] = []
      if (years > 0) parts.push(`${years}年`)
      if (months > 0) parts.push(`${months}月`)
      if (days > 0 || parts.length === 0) parts.push(`${days}日`)

      return parts.join('')
    }

    const getRemainingTimeClass = () => {
      if (!viewData.remainingTime) return ''
      if (viewData.remainingTime === '已过期') return 'remaining-expired'
      return 'remaining-normal'
    }

    const getStatusClass = (status: string) => {
      if (status === '执行中') {
        return 'status-in-progress'
      }
      if (status === '待确认') {
        return 'status-confirmed'
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
     * 预览照片
     */
    const previewPhoto = (photos: string[], _startIndex: number) => {
      if (!photos || photos.length === 0) return
      const previewWindow = window.open('', '_blank')
      if (previewWindow) {
        previewWindow.document.write(`
          <!DOCTYPE html>
          <html>
          <head>
            <title>照片预览</title>
            <style>
              body { margin: 0; padding: 20px; background: #f5f5f5; display: flex; flex-wrap: wrap; gap: 10px; justify-content: center; }
              img { max-width: 300px; max-height: 300px; object-fit: cover; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); cursor: pointer; }
              img:hover { transform: scale(1.02); }
            </style>
          </head>
          <body>
            ${photos.map((p, i) => `<img src="${p}" alt="照片${i + 1}" onclick="window.open('${p}', '_blank')" />`).join('')}
          </body>
          </html>
        `)
        previewWindow.document.close()
      }
    }

    const loadData = async () => {
      if (abortController) {
        abortController.abort()
      }
      abortController = new AbortController()

      loading.value = true
      try {
        const response = await periodicInspectionService.getList(
          {
            page: currentPage.value,
            size: pageSize.value,
            project_name: searchForm.projectName || undefined,
            client_name: searchForm.clientName || undefined,
          },
          abortController.signal
        )

        if (response.code === 200 && response.data) {
          inspectionData.value = (response.data.items || []).map((item: PeriodicInspection) => ({
            id: item.id,
            inspection_id: item.inspection_id,
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
            execution_result: item.execution_result || '',
            remarks: item.remarks || '',
            signature: item.signature || '',
            created_at: item.created_at,
            updated_at: item.updated_at,
          }))
          totalElements.value = response.data.total ?? 0
          totalPages.value = response.data.totalPages ?? 0
        } else {
          showToast(response.message || '加载数据失败', 'error')
        }
      } catch (error: any) {
        if (error instanceof Error && error.name === 'AbortError') {
          return
        }
        console.error('加载数据异常:', error)
        showToast(error.message || '加载数据失败，请检查网络连接', 'error')
      } finally {
        loading.value = false
      }
    }

    const handleSearch = () => {
      currentPage.value = 0
      loadData()
    }

    const handleView = async (item: InspectionItem) => {
      viewData.id = item.id
      viewData.inspection_id = item.inspection_id
      viewData.project_id = item.project_id
      viewData.project_name = item.project_name
      viewData.plan_start_date = item.plan_start_date
      viewData.plan_end_date = item.plan_end_date
      viewData.client_name = item.client_name || ''
      viewData.client_contact = item.client_contact || ''
      viewData.client_contact_info = item.client_contact_info || ''
      viewData.client_contact_position = item.client_contact_position || ''
      viewData.address = item.address || ''
      viewData.maintenance_personnel = item.maintenance_personnel || ''
      viewData.status = item.status
      viewData.execution_result = item.execution_result || ''
      viewData.remarks = item.remarks || ''
      viewData.signature = item.signature || ''
      viewData.created_at = item.created_at
      viewData.updated_at = item.updated_at
      viewData.remainingTime = '-'

      try {
        const projectResponse = await projectInfoService.getAll()
        if (projectResponse.code === 200 && projectResponse.data) {
          const project = projectResponse.data.find(
            (p: ProjectInfo) => p.project_id === item.project_id
          )
          if (project) {
            viewData.remainingTime = calculateRemainingTime(project.maintenance_end_date ?? '')
          }
        }
      } catch (error) {
        console.error('获取项目信息失败:', error)
      }

      fetchOperationLogs(item.id)
      fetchInspectionRecords(item.inspection_id)
      isViewModalOpen.value = true
    }

    const handleEdit = (item: InspectionItem) => {
      router.push({
        name: 'PeriodicInspection',
        query: { id: item.id.toString(), type: 'edit' },
      })
    }

    const closeViewModal = () => {
      isViewModalOpen.value = false
      operationLogs.value = []
      inspectionRecords.value = []
    }

    const handleExport = async (item: InspectionItem) => {
      pendingExportItem.value = item
      loading.value = true
      try {
        const logsResponse = (await request.get(
          `/work-order-operation-log?work_order_type=periodic_inspection&work_order_id=${item.id}`
        )) as unknown as ApiResponse<OperationLogItem[]>
        if (logsResponse.code === 200) {
          pdfPreviewLogs.value = logsResponse.data || []
        }

        const recordsResponse = (await request.get(
          `/periodic-inspection-record/inspection/${item.inspection_id}`
        )) as unknown as ApiResponse<InspectionRecord[]>
        if (recordsResponse.code === 200) {
          const records = recordsResponse.data || []
          const allPhotos: string[] = []
          records.forEach((record) => {
            if (record.photos && record.photos.length > 0) {
              allPhotos.push(...record.photos)
            }
          })
          pdfPreviewPhotos.value = allPhotos
        }

        let remainingTime = '-'
        try {
          const projectResponse = await projectInfoService.getAll()
          if (projectResponse.code === 200 && projectResponse.data) {
            const project = projectResponse.data.find(
              (p: ProjectInfo) => p.project_id === item.project_id
            )
            if (project) {
              remainingTime = calculateRemainingTime(project.maintenance_end_date ?? '')
            }
          }
        } catch (error) {
          console.error('获取项目信息失败:', error)
        }

        pdfPreviewData.value = {
          id: item.id,
          inspection_id: item.inspection_id,
          project_id: item.project_id,
          project_name: item.project_name,
          plan_start_date: item.plan_start_date,
          plan_end_date: item.plan_end_date,
          client_name: item.client_name,
          client_contact: item.client_contact,
          client_contact_info: item.client_contact_info,
          client_contact_position: item.client_contact_position,
          address: item.address,
          maintenance_personnel: item.maintenance_personnel,
          status: item.status,
          execution_result: item.execution_result,
          remarks: item.remarks,
          signature: item.signature,
          remainingTime: remainingTime,
        }

        showPdfPreview.value = true
      } catch (error) {
        console.error('加载预览数据失败:', error)
        showToast('加载预览数据失败', 'error')
      } finally {
        loading.value = false
      }
    }

    const closePdfPreview = () => {
      showPdfPreview.value = false
      pdfPreviewData.value = {}
      pdfPreviewLogs.value = []
      pdfPreviewPhotos.value = []
    }

    const exportFromPreview = async () => {
      if (!pendingExportItem.value) return
      const item = pendingExportItem.value
      const defaultFilename = `定期巡检单_${item.inspection_id}.pdf`

      let fileHandle: any = null

      if ('showSaveFilePicker' in window && window.isSecureContext) {
        try {
          fileHandle = await (window as any).showSaveFilePicker({
            suggestedName: defaultFilename,
            types: [{
              description: 'PDF文件',
              accept: { 'application/pdf': ['.pdf'] },
            }],
          })
        } catch (err: any) {
          if (err.name === 'AbortError') {
            return
          }
        }
      }

      try {
        const token = localStorage.getItem('token')
        const response = await fetch(`/api/v1/export/periodic-inspection/${item.id}`, {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        })

        if (!response.ok) {
          const error = await response.json()
          showToast(error.message || '导出失败', 'error')
          return
        }

        const blob = await response.blob()

        if (fileHandle) {
          const writable = await fileHandle.createWritable()
          await writable.write(blob)
          await writable.close()
          showToast('导出成功', 'success')
          closePdfPreview()
        } else {
          const url = window.URL.createObjectURL(blob)
          const a = document.createElement('a')
          a.href = url
          a.download = defaultFilename
          document.body.appendChild(a)
          a.click()
          document.body.removeChild(a)
          setTimeout(() => window.URL.revokeObjectURL(url), 100)
          showToast('导出成功', 'success')
          closePdfPreview()
        }
      } catch (error) {
        console.error('导出失败:', error)
        showToast('导出失败，请检查网络连接', 'error')
      }
    }

    const showRejectModal = ref(false)
    const rejectReason = ref('')
    const pendingRejectItem = ref<InspectionItem | null>(null)

    const handleReject = (item: InspectionItem) => {
      pendingRejectItem.value = item
      rejectReason.value = ''
      showRejectModal.value = true
    }

    const handleRecall = async (item: InspectionItem) => {
      if (!confirm('确认撤回此工单？撤回后可继续编辑。')) return
      try {
        const response = await periodicInspectionService.recall(item.id)
        if (response.code === 200) {
          showToast('撤回成功', 'success')
          await loadData()
        } else {
          showToast(response.message || '撤回失败', 'error')
        }
      } catch (error) {
        console.error('撤回失败:', error)
        showToast('撤回失败', 'error')
      }
    }

    const closeRejectModal = () => {
      showRejectModal.value = false
      pendingRejectItem.value = null
      rejectReason.value = ''
    }

    const confirmReject = async () => {
      if (!pendingRejectItem.value) return

      const reason = rejectReason.value.trim()
      if (!reason) {
        showToast('请输入退回原因', 'error')
        return
      }
      if (reason.length < 10) {
        showToast('退回原因至少需要10个字符', 'error')
        return
      }
      if (reason.length > 500) {
        showToast('退回原因不能超过500个字符', 'error')
        return
      }

      saving.value = true
      try {
        const response = await periodicInspectionService.patch(pendingRejectItem.value.id, {
          status: '已退回',
          reject_reason: reason,
        })

        if (response.code === 200) {
          showToast('已退回', 'success')
          closeRejectModal()
          await loadData()
        } else {
          showToast(response.message || '退回失败', 'error')
        }
      } catch (error: any) {
        console.error('退回失败:', error)
        showToast(error.response?.data?.detail || '退回失败，请检查网络连接', 'error')
      } finally {
        saving.value = false
      }
    }

    const handleJump = () => {
      const page = parseInt(jumpPage.value.toString())
      if (page >= 1 && page <= totalPages.value) {
        currentPage.value = page - 1
      }
    }

    const handlePageSizeChange = () => {
      currentPage.value = 0
      loadData()
    }

    watchEffect((onCleanup) => {
      const unwatch = watch(currentPage, () => {
        loadData()
      })
      onCleanup(() => {
        unwatch()
      })
    })

    const handleViewFromUrl = async (id: number) => {
      try {
        loading.value = true
        const response = await workPlanService.getById(id)
        if (response.code === 200 && response.data) {
          const item = response.data
          viewData.id = item.id
          viewData.inspection_id = item.plan_id
          viewData.project_id = item.project_id
          viewData.project_name = item.project_name
          viewData.plan_start_date = item.plan_start_date
          viewData.plan_end_date = item.plan_end_date
          viewData.client_name = item.client_name || ''
          viewData.maintenance_personnel = item.maintenance_personnel || ''
          viewData.status = item.status
          viewData.remarks = item.remarks || ''
          viewData.created_at = item.created_at
          viewData.updated_at = item.updated_at
          viewData.remainingTime = '-'

          try {
            const projectResponse = await projectInfoService.getAll()
            if (projectResponse.code === 200 && projectResponse.data) {
              const project = projectResponse.data.find(
                (p: ProjectInfo) => p.project_id === item.project_id
              )
              if (project) {
                viewData.remainingTime = calculateRemainingTime(project.maintenance_end_date ?? '')
              }
            }
          } catch (error) {
            console.error('获取项目信息失败:', error)
          }

          isViewModalOpen.value = true
        } else {
          showToast(response.message || '获取工单信息失败', 'error')
        }
      } catch (error: any) {
        console.error('获取工单信息失败:', error)
        showToast(error.message || '获取工单信息失败', 'error')
      } finally {
        loading.value = false
      }
    }

    onMounted(async () => {
      await loadData()
      const urlId = route.query.id
      if (urlId) {
        const id = parseInt(urlId as string)
        if (!isNaN(id)) {
          await handleViewFromUrl(id)
        }
      }
    })

    onUnmounted(() => {
      if (abortController) {
        abortController.abort()
      }
    })

    return {
      searchForm,
      inspectionData,
      currentPage,
      pageSize,
      totalPages,
      jumpPage,
      totalElements,
      startIndex,
      isViewModalOpen,
      loading,
      saving,
      viewData,
      toast,
      operationLogs,
      loadingLogs,
      inspectionRecords,
      loadingRecords,
      showRejectModal,
      rejectReason,
      pendingRejectItem,
      openModal: () => {},
      closeModal: () => {},
      handleView,
      closeViewModal,
      handleExport,
      handleEdit,
      handleReject,
      handleRecall,
      canEditWork,
      canRecallWork,
      closeRejectModal,
      confirmReject,
      handleSearch,
      handleJump,
      handlePageSizeChange,
      formatDate,
      formatDateTime,
      formatOperationTime,
      getStatusClass,
      getRemainingTimeClass,
      previewPhoto,
      WORK_STATUS,
      isAdmin,
      isDepartmentManager,
      showPdfPreview,
      pdfPreviewData,
      pdfPreviewLogs,
      pdfPreviewPhotos,
      closePdfPreview,
      exportFromPreview,
    }
  },
})
</script>

<style scoped>
.periodic-inspection-query {
  background: var(--color-bg-card);
  border-radius: 4px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  padding: 20px;
  position: relative;
}

.search-section {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding: 20px;
  background: var(--color-bg-page);
  border-radius: 4px;
}

.search-form {
  display: flex;
  flex-direction: column;
  gap: 16px;
  align-items: flex-start;
  flex: 1;
}

.search-row {
  display: flex;
  gap: 16px;
  align-items: center;
  flex-wrap: wrap;
}

.search-item {
  display: flex;
  align-items: center;
  gap: 8px;
}

.search-label {
  font-size: 14px;
  font-weight: 500;
  color: var(--color-text-regular);
  white-space: nowrap;
}

.search-input {
  width: 200px;
  padding: 8px 12px;
  border: 1px solid var(--color-border);
  border-radius: 3px;
  font-size: 14px;
  color: var(--color-text-primary);
  background: var(--color-bg-card);
  transition: border-color 0.15s;
}

.search-input:focus {
  outline: none;
  border-color: var(--color-primary);
  box-shadow: 0 0 0 2px rgba(25, 118, 210, 0.1);
}

.search-input::placeholder {
  color: var(--color-text-placeholder);
}

.search-actions {
  display: flex;
  flex-wrap: nowrap;
  gap: 10px;
  overflow-x: auto;
  white-space: nowrap;
  min-width: max-content;
  align-items: center;
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

.btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.btn-search {
  background: var(--color-primary);
  color: var(--color-bg-card);
}

.btn-search:hover {
  background: var(--color-primary);
}

.table-section {
  margin-bottom: 20px;
  border: 1px solid var(--color-border);
  border-radius: 4px;
  overflow-x: auto;
}

.data-table {
  width: 100%;
  border-collapse: collapse;
  min-width: 1400px;
}

.data-table thead {
  background: var(--color-border);
}

.data-table th {
  padding: 12px 16px;
  text-align: left;
  font-size: 14px;
  font-weight: 600;
  color: var(--color-text-primary);
  border-bottom: 1px solid var(--color-border);
  white-space: nowrap;
}

.data-table td {
  padding: 12px 16px;
  text-align: left;
  font-size: 14px;
  color: var(--color-text-regular);
  border-bottom: 1px solid var(--color-border-light);
}

.data-table tbody tr:hover {
  background: var(--color-bg-page);
}

.even-row {
  background: var(--color-bg-page);
}

.action-cell {
  display: flex;
  flex-wrap: nowrap;
  gap: 16px;
  overflow-x: auto;
  white-space: nowrap;
  min-width: max-content;
  align-items: center;
}

.action-link {
  font-size: 14px;
  text-decoration: none;
  transition: opacity 0.15s;
}

.action-link:hover {
  opacity: 0.8;
}

.action-view {
  color: var(--color-success);
}

.action-export {
  color: var(--color-primary);
}

.status-badge {
  padding: 4px 12px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 500;
  display: inline-block;
}

.status-pending {
  background: var(--color-warning-subtle);
  color: var(--color-warning);
}

.status-confirmed {
  background: var(--color-success-subtle);
  color: var(--color-success);
}

.status-in-progress {
  background: var(--color-success-subtle);
  color: var(--color-success);
}

.status-completed {
  background: var(--color-success-subtle);
  color: var(--color-success);
}

.status-cancelled {
  background: var(--color-danger-subtle);
  color: var(--color-danger);
}

.status-returned {
  background: var(--color-bg-card)8e1;
  color: var(--color-warning);
}

.remaining-normal {
  color: var(--color-success);
  font-weight: 500;
}

.remaining-expired {
  color: var(--color-danger);
  font-weight: 600;
}

.pagination-section {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 0;
}

.pagination-info {
  font-size: 14px;
  color: var(--color-text-secondary);
}

.pagination-controls {
  display: flex;
  flex-wrap: nowrap;
  align-items: center;
  gap: 8px;
  overflow-x: auto;
  white-space: nowrap;
  min-width: max-content;
}

.page-btn {
  min-width: 32px;
  height: 32px;
  padding: 0 8px;
  border: 1px solid var(--color-border);
  border-radius: 3px;
  background: var(--color-bg-card);
  font-size: 14px;
  color: var(--color-text-primary);
  cursor: pointer;
  transition: all 0.15s;
  display: flex;
  align-items: center;
  justify-content: center;
}

.page-btn:hover:not(:disabled) {
  border-color: var(--color-primary);
  color: var(--color-primary);
}

.page-btn:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}

.page-btn.active {
  background: var(--color-primary);
  color: var(--color-bg-card);
  border-color: var(--color-primary);
}

.page-nav {
  font-size: 16px;
}

.page-select {
  padding: 6px 12px;
  border: 1px solid var(--color-border);
  border-radius: 3px;
  font-size: 14px;
  color: var(--color-text-primary);
  background: var(--color-bg-card);
  cursor: pointer;
}

.page-jump {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
  color: var(--color-text-secondary);
}

.page-input {
  width: 48px;
  padding: 6px 8px;
  border: 1px solid var(--color-border);
  border-radius: 3px;
  font-size: 14px;
  color: var(--color-text-primary);
  text-align: center;
  background: var(--color-bg-card);
}

.page-input:focus {
  outline: none;
  border-color: var(--color-primary);
}

.page-go {
  min-width: 40px;
  height: 28px;
  padding: 0 8px;
  background: var(--color-primary);
  color: var(--color-bg-card);
  border: none;
  border-radius: 3px;
  font-size: 12px;
  cursor: pointer;
  transition: background 0.15s;
}

.page-go:hover {
  background: var(--color-primary);
}

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
  width: 1000px;
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

.form-item-full {
  display: flex;
  flex-direction: column;
  gap: 8px;
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

.form-value-textarea {
  min-height: 60px;
  align-items: flex-start;
  padding-top: 12px;
  padding-bottom: 12px;
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  padding: 20px 24px;
  border-top: 1px solid var(--color-border);
}

.btn-cancel {
  background: var(--color-bg-card);
  color: var(--color-text-secondary);
  border: 1px solid var(--color-border);
}

.btn-cancel:hover:not(:disabled) {
  background: var(--color-bg-page);
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

.signature-container {
  padding: 12px;
  background: var(--color-bg-card);
}

.signature-image {
  max-width: 200px;
  max-height: 100px;
  object-fit: contain;
}

.photos-container {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
}

.record-photos {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.photo-item {
  width: 100px;
  height: 100px;
  border-radius: 8px;
  overflow: hidden;
  cursor: pointer;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
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
</style>
