<template>
  <div class="periodic-inspection-query">
    <LoadingSpinner :visible="loading" text="加载中..." />
    <Toast :visible="toast.visible" :message="toast.message" :type="toast.type" />

    <div class="search-section">
      <div class="search-form">
        <div class="search-row">
          <div class="search-item">
            <label class="search-label">项目名称：</label>
            <SearchInput
              v-model="searchForm.projectName"
              field-key="PeriodicInspectionQuery_projectName"
              placeholder="请输入项目名称"
              @input="handleSearch"
            />
          </div>
          <div class="search-item">
            <label class="search-label">客户名称：</label>
            <SearchInput
              v-model="searchForm.clientName"
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
          <tr v-for="(item, index) in inspectionData" :key="item.id" :class="{ 'even-row': index % 2 === 0 }">
            <td>{{ startIndex + index + 1 }}</td>
            <td>{{ item.project_id }}</td>
            <td>{{ item.project_name }}</td>
            <td>{{ item.inspection_id }}</td>
            <td>{{ formatDate(item.plan_start_date) }}</td>
            <td>{{ formatDate(item.plan_end_date) }}</td>
            <td>{{ item.client_name || '-' }}</td>
            <td>{{ item.maintenance_personnel || '-' }}</td>
            <td>
              <span :class="getStatusClass(item.status)" class="status-badge">{{ item.status }}</span>
            </td>
            <td class="action-cell">
              <a href="#" class="action-link action-view" @click.prevent="handleView(item)">查看</a>
              <a href="#" class="action-link action-export" @click.prevent="handleExport(item)" v-if="item.status === WORK_STATUS.COMPLETED">导出</a>
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
        <button class="page-btn page-nav" :disabled="currentPage === 0" @click="currentPage--">
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
        <button class="page-btn page-nav" :disabled="currentPage >= totalPages - 1" @click="currentPage++">
          &gt;
        </button>
        <select class="page-select" v-model="pageSize" @change="handlePageSizeChange">
          <option value="10">10 条 / 页</option>
          <option value="20">20 条 / 页</option>
          <option value="50">50 条 / 页</option>
        </select>
        <div class="page-jump">
          <span>跳至</span>
          <input type="number" class="page-input" v-model="jumpPage" min="1" :max="totalPages" />
          <span>页</span>
          <button class="page-btn page-go" @click="handleJump">Go</button>
        </div>
      </div>
    </div>

    <div v-if="isViewModalOpen" class="modal-overlay" @click.self="closeViewModal">
      <div class="modal-container">
        <div class="modal-header">
          <h3 class="modal-title">查看巡检单</h3>
          <button class="modal-close" @click="closeViewModal">×</button>
        </div>
        <div class="modal-body">
          <div class="form-grid">
            <div class="form-column">
              <div class="form-item">
                <label class="form-label">巡检单编号</label>
                <div class="form-value">{{ viewData.inspection_id || '-' }}</div>
              </div>
              <div class="form-item">
                <label class="form-label">项目编号</label>
                <div class="form-value">{{ viewData.project_id || '-' }}</div>
              </div>
              <div class="form-item">
                <label class="form-label">项目名称</label>
                <div class="form-value">{{ viewData.project_name || '-' }}</div>
              </div>
              <div class="form-item">
                <label class="form-label">客户单位</label>
                <div class="form-value">{{ viewData.client_name || '-' }}</div>
              </div>
              <div class="form-item">
                <label class="form-label">客户联系人</label>
                <div class="form-value">{{ viewData.client_contact || '-' }}</div>
              </div>
              <div class="form-item">
                <label class="form-label">联系人职位</label>
                <div class="form-value">{{ viewData.client_contact_position || '-' }}</div>
              </div>
            </div>
            <div class="form-column">
              <div class="form-item">
                <label class="form-label">计划开始日期</label>
                <div class="form-value">{{ formatDate(viewData.plan_start_date) || '-' }}</div>
              </div>
              <div class="form-item">
                <label class="form-label">计划结束日期</label>
                <div class="form-value">{{ formatDate(viewData.plan_end_date) || '-' }}</div>
              </div>
              <div class="form-item">
                <label class="form-label">运维人员</label>
                <div class="form-value">{{ viewData.maintenance_personnel || '-' }}</div>
              </div>
              <div class="form-item">
                <label class="form-label">客户联系方式</label>
                <div class="form-value">{{ viewData.client_contact_info || '-' }}</div>
              </div>
              <div class="form-item">
                <label class="form-label">客户地址</label>
                <div class="form-value">{{ viewData.address || '-' }}</div>
              </div>
              <div class="form-item">
                <label class="form-label">合同剩余时间</label>
                <div class="form-value" :class="getRemainingTimeClass()">{{ viewData.remainingTime || '-' }}</div>
              </div>
              <div class="form-item">
                <label class="form-label">状态</label>
                <div class="form-value" :class="getStatusClass(viewData.status)">{{ viewData.status || '-' }}</div>
              </div>
              <div class="form-item">
                <label class="form-label">创建时间</label>
                <div class="form-value">{{ formatDateTime(viewData.created_at) || '-' }}</div>
              </div>
            </div>
          </div>
          <div class="form-item-full">
            <label class="form-label">发现问题</label>
            <div class="form-value form-value-textarea">{{ viewData.execution_result || '-' }}</div>
          </div>
          <div class="form-item-full">
            <label class="form-label">处理结果</label>
            <div class="form-value form-value-textarea">{{ viewData.remarks || '-' }}</div>
          </div>
          <div class="form-item-full">
            <label class="form-label">用户签字</label>
            <div class="form-value signature-container" v-if="viewData.signature">
              <img :src="viewData.signature" alt="用户签字" class="signature-image" />
            </div>
            <div class="form-value" v-else>暂无用户签字</div>
          </div>
          <div class="form-item-full">
            <label class="form-label">现场照片</label>
            <div class="photos-container" v-if="inspectionRecords.length > 0">
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
                  <img :src="photo" alt="现场照片" loading="lazy" />
                </div>
              </div>
            </div>
            <div class="form-value" v-else>暂无现场照片</div>
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
          <button class="btn btn-cancel" @click="closeViewModal">关闭</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script lang="ts">
import { defineComponent, reactive, ref, computed, watch, onMounted, onUnmounted, watchEffect } from 'vue'
import { useRoute } from 'vue-router'
import { periodicInspectionService, type PeriodicInspection } from '../services/periodicInspection'
import { workPlanService, type WorkPlan } from '../services/workPlan'
import { projectInfoService, type ProjectInfo } from '../services/projectInfo'
import apiClient from '../utils/api'
import type { ApiResponse } from '../types/api'
import LoadingSpinner from '../components/LoadingSpinner.vue'
import Toast from '../components/Toast.vue'
import SearchInput from '../components/SearchInput.vue'
import { WORK_STATUS, formatDate as formatDateUtil } from '../config/constants'

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
    SearchInput
  },
  setup() {
    const route = useRoute()
    const searchForm = reactive({
      projectName: '',
      clientName: ''
    })

    const currentPage = ref(0)
    const pageSize = ref(10)
    const jumpPage = ref(1)
    const loading = ref(false)
    const isViewModalOpen = ref(false)
    
    const inspectionData = ref<InspectionItem[]>([])
    const totalElements = ref(0)
    const totalPages = ref(0)

    const toast = reactive({
      visible: false,
      message: '',
      type: 'success' as 'success' | 'error' | 'warning' | 'info'
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
      remainingTime: ''
    })

    const inspectionRecords = ref<InspectionRecord[]>([])
    const loadingRecords = ref(false)

    const operationLogs = ref<OperationLogItem[]>([])
    const loadingLogs = ref(false)

    const startIndex = computed(() => currentPage.value * pageSize.value)

    let abortController: AbortController | null = null

    const showToast = (message: string, type: 'success' | 'error' | 'warning' | 'info' = 'success') => {
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
        minute: '2-digit'
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
        const response = await apiClient.get(`/work-order-operation-log?work_order_type=periodic_inspection&work_order_id=${workOrderId}`) as unknown as ApiResponse<OperationLogItem[]>
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
        const response = await apiClient.get(`/periodic-inspection-record/inspection/${inspectionId}`) as unknown as ApiResponse<InspectionRecord[]>
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
      switch (status) {
        case WORK_STATUS.NOT_STARTED:
        case '待执行':
        case '未进行':
          return 'status-pending'
        case WORK_STATUS.PENDING_CONFIRM:
        case '待确认':
          return 'status-confirmed'
        case WORK_STATUS.CONFIRMED:
        case '已确认':
          return 'status-confirmed'
        case WORK_STATUS.IN_PROGRESS:
        case '执行中':
          return 'status-in-progress'
        case WORK_STATUS.COMPLETED:
        case '已完成':
          return 'status-completed'
        case WORK_STATUS.CANCELLED:
        case '已取消':
          return 'status-cancelled'
        case WORK_STATUS.RETURNED:
        case '已退回':
          return 'status-returned'
        default:
          return ''
      }
    }

    /**
     * 预览照片
     */
    const previewPhoto = (photos: string[], startIndex: number) => {
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
        const response = await periodicInspectionService.getList({
          page: currentPage.value,
          size: pageSize.value,
          project_name: searchForm.projectName || undefined,
          client_name: searchForm.clientName || undefined
        })
        
        if (response.code === 200) {
          inspectionData.value = response.data.content.map((item: PeriodicInspection) => ({
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
            status: item.status || '未进行',
            execution_result: item.execution_result || '',
            remarks: item.remarks || '',
            signature: item.signature || '',
            created_at: item.created_at,
            updated_at: item.updated_at
          }))
          totalElements.value = response.data.totalElements
          totalPages.value = response.data.totalPages
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
          const project = projectResponse.data.find((p: ProjectInfo) => p.project_id === item.project_id)
          if (project) {
            viewData.remainingTime = calculateRemainingTime(project.maintenance_end_date)
          }
        }
      } catch (error) {
        console.error('获取项目信息失败:', error)
      }

      fetchOperationLogs(item.id)
      fetchInspectionRecords(item.inspection_id)
      isViewModalOpen.value = true
    }

    const closeViewModal = () => {
      isViewModalOpen.value = false
      operationLogs.value = []
      inspectionRecords.value = []
    }

    const handleExport = (item: InspectionItem) => {
      showToast('导出功能开发中', 'info')
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
              const project = projectResponse.data.find((p: ProjectInfo) => p.project_id === item.project_id)
              if (project) {
                viewData.remainingTime = calculateRemainingTime(project.maintenance_end_date)
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
      viewData,
      toast,
      operationLogs,
      loadingLogs,
      inspectionRecords,
      loadingRecords,
      openModal: () => {},
      closeModal: () => {},
      handleView,
      closeViewModal,
      handleExport,
      handleSearch,
      handleJump,
      handlePageSizeChange,
      formatDate,
      formatDateTime,
      formatOperationTime,
      getStatusClass,
      getRemainingTimeClass,
      previewPhoto,
      WORK_STATUS
    }
  }
})
</script>

<style scoped>
.periodic-inspection-query {
  background: #fff;
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
  background: #f8f9fa;
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
  color: #424242;
  white-space: nowrap;
}

.search-input {
  width: 200px;
  padding: 8px 12px;
  border: 1px solid #e0e0e0;
  border-radius: 3px;
  font-size: 14px;
  color: #333;
  background: #fff;
  transition: border-color 0.15s;
}

.search-input:focus {
  outline: none;
  border-color: #1976d2;
  box-shadow: 0 0 0 2px rgba(25, 118, 210, 0.1);
}

.search-input::placeholder {
  color: #999;
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
  background: #2196F3;
  color: #fff;
}

.btn-search:hover {
  background: #1976D2;
}

.table-section {
  margin-bottom: 20px;
  border: 1px solid #e0e0e0;
  border-radius: 4px;
  overflow-x: auto;
}

.data-table {
  width: 100%;
  border-collapse: collapse;
  min-width: 1400px;
}

.data-table thead {
  background: #E0E0E0;
}

.data-table th {
  padding: 12px 16px;
  text-align: left;
  font-size: 14px;
  font-weight: 600;
  color: #333;
  border-bottom: 1px solid #d0d0d0;
  white-space: nowrap;
}

.data-table td {
  padding: 12px 16px;
  text-align: left;
  font-size: 14px;
  color: #616161;
  border-bottom: 1px solid #f0f0f0;
}

.data-table tbody tr:hover {
  background: #f5f5f5;
}

.even-row {
  background: #fafafa;
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
  color: #2E7D32;
}

.action-export {
  color: #2196F3;
}

.status-badge {
  padding: 4px 12px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 500;
  display: inline-block;
}

.status-pending {
  background: #FFF3E0;
  color: #FF9800;
}

.status-confirmed {
  background: #E8F5E9;
  color: #2E7D32;
}

.status-in-progress {
  background: #E8F5E9;
  color: #2E7D32;
}

.status-completed {
  background: #E8F5E9;
  color: #2E7D32;
}

.status-cancelled {
  background: #FFEBEE;
  color: #D32F2F;
}

.status-returned {
  background: #FFF8E1;
  color: #F57C00;
}

.remaining-normal {
  color: #388E3C;
  font-weight: 500;
}

.remaining-expired {
  color: #D32F2F;
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
  color: #666;
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
  border: 1px solid #e0e0e0;
  border-radius: 3px;
  background: #fff;
  font-size: 14px;
  color: #333;
  cursor: pointer;
  transition: all 0.15s;
  display: flex;
  align-items: center;
  justify-content: center;
}

.page-btn:hover:not(:disabled) {
  border-color: #2196F3;
  color: #2196F3;
}

.page-btn:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}

.page-btn.active {
  background: #2196F3;
  color: #fff;
  border-color: #2196F3;
}

.page-nav {
  font-size: 16px;
}

.page-select {
  padding: 6px 12px;
  border: 1px solid #e0e0e0;
  border-radius: 3px;
  font-size: 14px;
  color: #333;
  background: #fff;
  cursor: pointer;
}

.page-jump {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
  color: #666;
}

.page-input {
  width: 48px;
  padding: 6px 8px;
  border: 1px solid #e0e0e0;
  border-radius: 3px;
  font-size: 14px;
  color: #333;
  text-align: center;
  background: #fff;
}

.page-input:focus {
  outline: none;
  border-color: #2196F3;
}

.page-go {
  min-width: 40px;
  height: 28px;
  padding: 0 8px;
  background: #2196F3;
  color: #fff;
  border: none;
  border-radius: 3px;
  font-size: 12px;
  cursor: pointer;
  transition: background 0.15s;
}

.page-go:hover {
  background: #1976D2;
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
  background: #fff;
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

.form-item-full {
  display: flex;
  flex-direction: column;
  gap: 8px;
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
  border-top: 1px solid #e0e0e0;
}

.btn-cancel {
  background: #fff;
  color: #666;
  border: 1px solid #e0e0e0;
}

.btn-cancel:hover:not(:disabled) {
  background: #f5f5f5;
}

.operation-log-section {
  margin-top: 20px;
  padding-top: 20px;
  border-top: 1px solid #e0e0e0;
}

.section-title {
  font-size: 16px;
  font-weight: 600;
  color: #333;
  margin-bottom: 16px;
  padding-left: 12px;
  border-left: 3px solid #1976d2;
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

.signature-container {
  padding: 12px;
  background: #fff;
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
