<template>
  <div class="near-expiry-page">
    <LoadingSpinner :visible="loading" text="加载中..." />
    <Toast :visible="toast.visible" :message="toast.message" :type="toast.type" />

    <div class="search-section">
      <div class="search-form">
        <div class="search-item">
          <label class="search-label">项目名称：</label>
          <SearchInput
            v-model="searchForm.projectName"
            field-key="NearExpiryReminders_projectName"
            placeholder="请输入"
            @input="handleSearch"
          />
        </div>
        <div class="search-item">
          <label class="search-label">客户名称：</label>
          <SearchInput
            v-model="searchForm.clientName"
            field-key="NearExpiryReminders_clientName"
            placeholder="请输入"
            @input="handleSearch"
          />
        </div>
        <div class="search-item">
          <label class="search-label">工单类型：</label>
          <select class="search-select" v-model="searchForm.workOrderType">
            <option value="">全部</option>
            <option value="定期巡检">定期巡检工单</option>
            <option value="临时维修">临时维修工单</option>
            <option value="零星用工">零星用工工单</option>
          </select>
        </div>
      </div>
    </div>

    <div class="table-section">
      <table class="data-table">
        <thead>
          <tr>
            <th>序号</th>
            <th>工单编号</th>
            <th>项目编号</th>
            <th>项目名称</th>
            <th>工单类型</th>
            <th>计划开始日期</th>
            <th class="th-days-warning">距今日数</th>
            <th>运维人员</th>
            <th>操作</th>
          </tr>
        </thead>
        <tbody>
          <tr v-if="filteredData.length === 0">
            <td colspan="9" class="empty-cell">暂无数据</td>
          </tr>
          <tr v-for="(item, index) in paginatedData" :key="item.id + '-' + item.workOrderType" :class="{ 'even-row': index % 2 === 0 }">
            <td>{{ startIndex + index + 1 }}</td>
            <td>{{ item.workOrderId }}</td>
            <td>{{ item.projectId }}</td>
            <td>{{ item.projectName }}</td>
            <td>{{ item.workOrderType }}</td>
            <td>{{ formatDate(item.planStartDate) }}</td>
            <td :class="getDaysClass(item.daysFromToday)">{{ item.daysFromToday }} 天</td>
            <td>{{ item.executor || '-' }}</td>
            <td class="action-cell">
              <a href="#" class="action-link action-view" @click.prevent="handleView(item)">查看</a>
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
          v-for="page in displayedPages"
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
          <h3 class="modal-title">查看临期提醒</h3>
          <button class="modal-close" @click="closeViewModal">×</button>
        </div>
        <div class="modal-body">
          <div class="form-grid">
            <div class="form-column">
              <div class="form-item">
                <label class="form-label">工单编号</label>
                <div class="form-value">{{ viewData.workOrderId || '-' }}</div>
              </div>
              <div class="form-item">
                <label class="form-label">项目编号</label>
                <div class="form-value">{{ viewData.projectId || '-' }}</div>
              </div>
              <div class="form-item">
                <label class="form-label">项目名称</label>
                <div class="form-value">{{ viewData.projectName || '-' }}</div>
              </div>
              <div class="form-item">
                <label class="form-label">工单类型</label>
                <div class="form-value">{{ viewData.workOrderType || '-' }}</div>
              </div>
              <div class="form-item">
                <label class="form-label">客户单位</label>
                <div class="form-value">{{ viewData.clientName || '-' }}</div>
              </div>
              <div class="form-item">
                <label class="form-label">客户联系人</label>
                <div class="form-value">{{ viewData.clientContact || '-' }}</div>
              </div>
              <div class="form-item">
                <label class="form-label">联系人职位</label>
                <div class="form-value">{{ viewData.clientContactPosition || '-' }}</div>
              </div>
            </div>
            <div class="form-column">
              <div class="form-item">
                <label class="form-label">计划开始日期</label>
                <div class="form-value">{{ formatDate(viewData.planStartDate) || '-' }}</div>
              </div>
              <div class="form-item">
                <label class="form-label">运维人员</label>
                <div class="form-value">{{ viewData.executor || '-' }}</div>
              </div>
              <div class="form-item">
                <label class="form-label">客户联系方式</label>
                <div class="form-value">{{ viewData.clientContactInfo || '-' }}</div>
              </div>
              <div class="form-item">
                <label class="form-label">客户地址</label>
                <div class="form-value">{{ viewData.address || '-' }}</div>
              </div>
              <div class="form-item">
                <label class="form-label">距今日数</label>
                <div class="form-value days-warning">{{ viewData.daysFromToday }} 天</div>
              </div>
              <div class="form-item">
                <label class="form-label">合同剩余时间</label>
                <div class="form-value" :class="getRemainingTimeClass()">{{ viewData.remainingTime || '-' }}</div>
              </div>
              <div class="form-item">
                <label class="form-label">状态</label>
                <div class="form-value" :class="getStatusClass(viewData.status)">{{ viewData.status || '-' }}</div>
              </div>
            </div>
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
import { defineComponent, ref, reactive, computed, onMounted, onUnmounted } from 'vue'
import apiClient from '../utils/api'
import { projectInfoService, type ProjectInfo } from '../services/projectInfo'
import LoadingSpinner from '../components/LoadingSpinner.vue'
import Toast from '../components/Toast.vue'
import SearchInput from '../components/SearchInput.vue'
import { formatDate, USER_ROLES, WORK_STATUS } from '../config/constants'
import type { ApiResponse } from '../types/api'

interface NearExpiryItem {
  id: number
  workOrderId: string
  projectId: string
  projectName: string
  workOrderType: string
  planStartDate: string
  daysFromToday: number
  executor: string
}

export default defineComponent({
  name: 'NearExpiryReminders',
  components: {
    LoadingSpinner,
    Toast,
    SearchInput
  },
  setup() {
    const loading = ref(false)
    const currentUser = ref<any>(null)
    const isViewModalOpen = ref(false)
    const searchForm = reactive({
      projectName: '',
      clientName: '',
      workOrderType: ''
    })

    const currentPage = ref(0)
    const pageSize = ref(10)
    const jumpPage = ref(1)
    const allData = ref<NearExpiryItem[]>([])

    const toast = reactive({
      visible: false,
      message: '',
      type: 'success' as 'success' | 'error' | 'warning' | 'info'
    })

    const viewData = reactive({
      id: 0,
      workOrderId: '',
      projectId: '',
      projectName: '',
      workOrderType: '',
      planStartDate: '',
      planEndDate: '',
      clientName: '',
      clientContact: '',
      clientContactInfo: '',
      clientContactPosition: '',
      address: '',
      executor: '',
      status: '',
      daysFromToday: 0,
      remainingTime: ''
    })

    const showToast = (message: string, type: 'success' | 'error' | 'warning' | 'info' = 'success') => {
      toast.message = message
      toast.type = type
      toast.visible = true
    }

    const formatDate = (dateStr: string) => {
      if (!dateStr) return '-'
      const date = new Date(dateStr)
      return date.toLocaleDateString('zh-CN', {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit'
      })
    }

    const getDaysClass = (days: number): string => {
      return 'days-warning'
    }

    const loadData = async () => {
      loading.value = true
      try {
        const response = await apiClient.get<unknown, ApiResponse<{ items: any[], total: number }>>('/expiring-soon', { params: { page: 0, size: 1000 } })
        
        const items: NearExpiryItem[] = []

        if (response.code === 200 && response.data?.items) {
          response.data.items.forEach((item: any) => {
            items.push({
              id: parseInt(item.id),
              workOrderId: item.workOrderNo,
              projectId: item.project_id,
              projectName: item.projectName,
              workOrderType: item.workOrderType,
              planStartDate: item.planStartDate,
              daysFromToday: item.daysRemaining,
              executor: item.executor
            })
          })
        }

        allData.value = items.sort((a, b) => a.daysFromToday - b.daysFromToday)
      } catch (error: any) {
        console.error('加载数据失败:', error)
        showToast(error.message || '加载数据失败，请检查网络连接', 'error')
      } finally {
        loading.value = false
      }
    }

    const filteredData = computed(() => {
      let result = allData.value

      const user = currentUser.value
      if (user && user.role === USER_ROLES.EMPLOYEE) {
        result = result.filter(item => item.executor === user.name)
      }

      if (searchForm.projectName) {
        result = result.filter(item => 
          item.projectName.toLowerCase().includes(searchForm.projectName.toLowerCase())
        )
      }

      if (searchForm.clientName) {
        result = result.filter(item => 
          item.projectId.toLowerCase().includes(searchForm.clientName.toLowerCase())
        )
      }

      if (searchForm.workOrderType) {
        result = result.filter(item => item.workOrderType === searchForm.workOrderType)
      }

      return result
    })

    const totalElements = computed(() => filteredData.value.length)

    const totalPages = computed(() => Math.ceil(totalElements.value / pageSize.value) || 1)

    const startIndex = computed(() => currentPage.value * pageSize.value)

    const paginatedData = computed(() => {
      const start = startIndex.value
      const end = start + pageSize.value
      return filteredData.value.slice(start, end)
    })

    const displayedPages = computed(() => {
      const pages: number[] = []
      const start = Math.max(1, currentPage.value - 1)
      const end = Math.min(totalPages.value, currentPage.value + 3)
      for (let i = start; i <= end; i++) {
        pages.push(i)
      }
      return pages
    })

    const handleSearch = () => {
      currentPage.value = 0
    }

    const handleReset = () => {
      searchForm.projectName = ''
      searchForm.clientName = ''
      searchForm.workOrderType = ''
      currentPage.value = 0
    }

    const handlePageSizeChange = () => {
      currentPage.value = 0
    }

    const handleJump = () => {
      const page = jumpPage.value
      if (page >= 1 && page <= totalPages.value) {
        currentPage.value = page - 1
      }
    }

    const handleView = async (item: NearExpiryItem) => {
      viewData.id = item.id
      viewData.workOrderId = item.workOrderId
      viewData.projectId = item.projectId
      viewData.projectName = item.projectName
      viewData.workOrderType = item.workOrderType
      viewData.planStartDate = item.planStartDate
      viewData.planEndDate = ''
      viewData.clientName = ''
      viewData.clientContact = ''
      viewData.clientContactInfo = ''
      viewData.clientContactPosition = ''
      viewData.address = ''
      viewData.executor = item.executor || ''
      viewData.status = WORK_STATUS.NOT_STARTED
      viewData.daysFromToday = item.daysFromToday
      viewData.remainingTime = '-'

      try {
        const projectResponse = await projectInfoService.getAll()
        if (projectResponse.code === 200 && projectResponse.data) {
          const project = projectResponse.data.find((p: ProjectInfo) => p.project_id === item.projectId)
          if (project) {
            viewData.projectName = project.project_name || viewData.projectName
            viewData.clientName = project.client_name || ''
            viewData.clientContact = project.client_contact || ''
            viewData.clientContactInfo = project.client_contact_info || ''
            viewData.clientContactPosition = project.client_contact_position || ''
            viewData.address = project.address || ''
            viewData.remainingTime = calculateRemainingTime(project.maintenance_end_date)
          }
        }
      } catch (error) {
        console.error('获取项目信息失败:', error)
      }

      isViewModalOpen.value = true
    }

    const closeViewModal = () => {
      isViewModalOpen.value = false
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
          return 'status-pending'
        case WORK_STATUS.PENDING_CONFIRM:
        case '待确认':
          return 'status-confirmed'
        case WORK_STATUS.IN_PROGRESS:
          return 'status-in-progress'
        case WORK_STATUS.COMPLETED:
        case '已完成':
          return 'status-completed'
        case WORK_STATUS.CANCELLED:
          return 'status-cancelled'
        default:
          return ''
      }
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

    const handleUserChanged = ((event: Event) => {
      const customEvent = event as CustomEvent
      currentUser.value = customEvent.detail
      loadData()
    }) as EventListener

    onMounted(() => {
      loadData()
      window.addEventListener('user-changed', handleUserChanged)
    })

    onUnmounted(() => {
      window.removeEventListener('user-changed', handleUserChanged)
    })

    return {
      loading,
      currentUser,
      searchForm,
      currentPage,
      pageSize,
      jumpPage,
      filteredData,
      paginatedData,
      totalElements,
      totalPages,
      startIndex,
      displayedPages,
      toast,
      isViewModalOpen,
      viewData,
      formatDate,
      formatDateTime,
      getDaysClass,
      getRemainingTimeClass,
      getStatusClass,
      handleSearch,
      handleReset,
      handlePageSizeChange,
      handleJump,
      handleView,
      closeViewModal
    }
  }
})
</script>

<style scoped>
.near-expiry-page {
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
  gap: 24px;
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

.search-input,
.search-select {
  width: 200px;
  padding: 8px 12px;
  border: 1px solid #e0e0e0;
  border-radius: 3px;
  font-size: 14px;
  color: #333;
  background: #fff;
  transition: border-color 0.15s;
}

.search-input:focus,
.search-select:focus {
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

.btn-search {
  background: #2196F3;
  color: #fff;
}

.btn-search:hover {
  background: #1976D2;
}

.btn-reset {
  background: #fff;
  color: #666;
  border: 1px solid #e0e0e0;
}

.btn-reset:hover {
  background: #f5f5f5;
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
  min-width: 1200px;
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

.th-days-warning {
  color: #F57C00 !important;
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

.empty-cell {
  text-align: center;
  color: #999;
  padding: 40px !important;
}

.days-critical {
  color: #D32F2F;
  font-weight: 600;
}

.days-warning {
  color: #F57C00 !important;
  font-weight: 600;
}

.days-normal {
  color: #388E3C;
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
  min-height: 70px;
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

.btn-cancel {
  background: #fff;
  color: #666;
  border: 1px solid #e0e0e0;
}

.btn-cancel:hover {
  background: #f5f5f5;
}

.remaining-normal {
  color: #388E3C;
  font-weight: 500;
}

.remaining-expired {
  color: #D32F2F;
  font-weight: 600;
}

.status-pending {
  color: #FF9800;
}

.status-confirmed {
  color: #2E7D32;
}

.status-in-progress {
  color: #2E7D32;
}

.status-completed {
  color: #2E7D32;
}

.status-cancelled {
  color: #D32F2F;
}
</style>
