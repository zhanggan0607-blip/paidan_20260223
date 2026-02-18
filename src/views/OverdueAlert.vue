<template>
  <div class="overdue-alert-page">
    <LoadingSpinner :visible="loading" text="加载中..." />
    <div class="main-wrapper">
      <div class="content-area">
        <div class="search-section">
          <div class="search-form">
            <div class="search-item">
              <label class="search-label">项目名称</label>
              <SearchInput
                v-model="searchForm.projectName"
                field-key="OverdueAlert_projectName"
                placeholder="请输入"
                @input="handleSearch"
              />
            </div>
            <div class="search-item">
              <label class="search-label">客户名称</label>
              <SearchInput
                v-model="searchForm.customerName"
                field-key="OverdueAlert_customerName"
                placeholder="请输入"
                @input="handleSearch"
              />
            </div>
            <div class="search-item">
              <label class="search-label">工单类型</label>
              <select class="search-select" v-model="searchForm.workOrderType">
                <option value="">请选择工单类型</option>
                <option value="定期巡检">定期巡检单</option>
                <option value="临时维修">临时维修单</option>
                <option value="零星用工">零星用工单</option>
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
                <th>计划结束日期</th>
                <th>提醒类型</th>
                <th class="th-overdue-days">已超期（天）</th>
                <th>运维人员</th>
                <th>工单状态</th>
                <th>操作</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="(item, index) in filteredData" :key="item.id" class="table-row">
                <td>{{ (currentPage - 1) * pageSize + index + 1 }}</td>
                <td>{{ item.workOrderNo }}</td>
                <td>{{ item.project_id }}</td>
                <td>{{ item.projectName }}</td>
                <td>{{ item.workOrderType }}</td>
                <td>{{ item.planEndDate }}</td>
                <td class="alert-type">已超期</td>
                <td class="overdue-days">{{ item.overdueDays }}</td>
                <td>{{ item.executor }}</td>
                <td>{{ item.workOrderStatus }}</td>
                <td class="action-cell">
                  <a href="#" class="action-link action-view" @click="handleView(item)">查看</a>
                </td>
              </tr>
            </tbody>
          </table>
          <div v-if="filteredData.length === 0" class="empty-state">
            <div class="empty-text">暂无超期数据</div>
          </div>
        </div>

        <div class="pagination-section">
          <div class="pagination-info">
            共 {{ filteredAllData.length }} 条记录
          </div>
          <div class="pagination-controls" v-if="totalPages > 0">
            <button class="page-btn" :disabled="currentPage === 1" @click="currentPage--">
              &lt;
            </button>
            <button
              v-for="page in totalPages"
              :key="page"
              class="page-btn"
              :class="{ active: page === currentPage }"
              @click="currentPage = page"
            >
              {{ page }}
            </button>
            <button class="page-btn" :disabled="currentPage === totalPages" @click="currentPage++">
              &gt;
            </button>
            <select class="page-select" v-model="pageSize">
              <option value="10">10 条 / 页</option>
              <option value="20">20 条 / 页</option>
              <option value="50">50 条 / 页</option>
            </select>
            <div class="page-jump">
              <span>跳至</span>
              <input type="number" class="page-input" v-model="jumpPage" min="1" :max="totalPages || 1" />
              <span>页</span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <div v-if="isViewModalOpen" class="modal-overlay" @click.self="closeViewModal">
      <div class="modal-container">
        <div class="modal-header">
          <h3 class="modal-title">查看工单详情</h3>
          <button class="modal-close" @click="closeViewModal">×</button>
        </div>
        <div class="modal-body">
          <div class="form-grid">
            <div class="form-column">
              <div class="form-item">
                <label class="form-label">工单编号</label>
                <div class="form-value">{{ viewData.work_order_no || '-' }}</div>
              </div>
              <div class="form-item">
                <label class="form-label">项目编号</label>
                <div class="form-value">{{ viewData.project_id || '-' }}</div>
              </div>
              <div class="form-item">
                <label class="form-label">工单类型</label>
                <div class="form-value">{{ viewData.work_order_type || '-' }}</div>
              </div>
              <div class="form-item">
                <label class="form-label">计划开始日期</label>
                <div class="form-value">{{ formatDate(viewData.plan_start_date) || '-' }}</div>
              </div>
              <div class="form-item">
                <label class="form-label">客户名称</label>
                <div class="form-value">{{ viewData.client_name || '-' }}</div>
              </div>
            </div>
            <div class="form-column">
              <div class="form-item">
                <label class="form-label">项目名称</label>
                <div class="form-value">{{ viewData.project_name || '-' }}</div>
              </div>
              <div class="form-item">
                <label class="form-label">工单状态</label>
                <div class="form-value">{{ viewData.status || '-' }}</div>
              </div>
              <div class="form-item">
                <label class="form-label">计划结束日期</label>
                <div class="form-value">{{ formatDate(viewData.plan_end_date) || '-' }}</div>
              </div>
              <div class="form-item">
                <label class="form-label">运维人员</label>
                <div class="form-value">{{ viewData.maintenance_personnel || '-' }}</div>
              </div>
            </div>
          </div>
          <div class="form-item-full">
            <label class="form-label">备注</label>
            <div class="form-value form-value-textarea">{{ viewData.remarks || '-' }}</div>
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
import { defineComponent, reactive, ref, computed, onMounted, onUnmounted } from 'vue'
import { overdueAlertService, type OverdueItem } from '../services/overdueAlert'
import { periodicInspectionService, type PeriodicInspection } from '../services/periodicInspection'
import { temporaryRepairService, type TemporaryRepair } from '../services/temporaryRepair'
import { spotWorkService, type SpotWork } from '../services/spotWork'
import { authService, type User } from '../services/auth'
import LoadingSpinner from '../components/LoadingSpinner.vue'
import SearchInput from '../components/SearchInput.vue'
import { USER_ROLES } from '../config/constants'

interface ViewData {
  id: number
  work_order_no: string
  project_id: string
  project_name: string
  work_order_type: string
  plan_start_date: string
  plan_end_date: string
  client_name: string
  maintenance_personnel: string
  status: string
  remarks: string
}

export default defineComponent({
  name: 'OverdueAlert',
  components: {
    LoadingSpinner,
    SearchInput
  },
  setup() {
    const currentUser = ref<User | null>(authService.getCurrentUser())
    const searchForm = reactive({
      projectName: '',
      customerName: '',
      workOrderType: ''
    })

    const currentPage = ref(1)
    const pageSize = ref(10)
    const jumpPage = ref(1)
    const loading = ref(false)

    const allData = ref<OverdueItem[]>([])

    const isViewModalOpen = ref(false)
    const currentWorkOrderType = ref('')

    const viewData = reactive<ViewData>({
      id: 0,
      work_order_no: '',
      project_id: '',
      project_name: '',
      work_order_type: '',
      plan_start_date: '',
      plan_end_date: '',
      client_name: '',
      maintenance_personnel: '',
      status: '',
      remarks: ''
    })

    const formatDate = (dateStr: string) => {
      if (!dateStr) return ''
      try {
        const date = new Date(dateStr)
        const year = date.getFullYear()
        const month = String(date.getMonth() + 1).padStart(2, '0')
        const day = String(date.getDate()).padStart(2, '0')
        return `${year}-${month}-${day}`
      } catch {
        return dateStr
      }
    }

    const updateViewDataFromInspection = (data: PeriodicInspection) => {
      viewData.id = data.id
      viewData.work_order_no = data.inspection_id
      viewData.project_id = data.project_id
      viewData.project_name = data.project_name
      viewData.work_order_type = '定期巡检单'
      viewData.plan_start_date = data.plan_start_date
      viewData.plan_end_date = data.plan_end_date
      viewData.client_name = data.client_name || ''
      viewData.maintenance_personnel = data.maintenance_personnel || ''
      viewData.status = data.status
      viewData.remarks = data.remarks || ''
    }

    const updateViewDataFromRepair = (data: TemporaryRepair) => {
      viewData.id = data.id
      viewData.work_order_no = data.repair_id
      viewData.project_id = data.project_id
      viewData.project_name = data.project_name
      viewData.work_order_type = '临时维修单'
      viewData.plan_start_date = data.plan_start_date
      viewData.plan_end_date = data.plan_end_date
      viewData.client_name = data.client_name
      viewData.maintenance_personnel = data.maintenance_personnel
      viewData.status = data.status
      viewData.remarks = data.remarks || ''
    }

    const updateViewDataFromSpotWork = (data: SpotWork) => {
      viewData.id = data.id
      viewData.work_order_no = data.work_id
      viewData.project_id = data.project_id
      viewData.project_name = data.project_name
      viewData.work_order_type = '零星用工单'
      viewData.plan_start_date = data.plan_start_date
      viewData.plan_end_date = data.plan_end_date
      viewData.client_name = data.client_name
      viewData.maintenance_personnel = data.maintenance_personnel
      viewData.status = data.status
      viewData.remarks = data.remarks || ''
    }

    const closeViewModal = () => {
      isViewModalOpen.value = false
      currentWorkOrderType.value = ''
    }

    const loadData = async () => {
      loading.value = true
      try {
        const params: any = {}
        if (searchForm.projectName.trim()) {
          params.project_name = searchForm.projectName.trim()
        }
        if (searchForm.customerName.trim()) {
          params.client_name = searchForm.customerName.trim()
        }
        if (searchForm.workOrderType) {
          params.work_order_type = searchForm.workOrderType
        }

        const response = await overdueAlertService.getOverdueAlerts(params)
        if (response.code === 200 && response.data) {
          allData.value = response.data.items
        }
      } catch (error) {
        console.error('加载超期提醒数据失败:', error)
      } finally {
        loading.value = false
      }
    }

    const filteredAllData = computed(() => {
      let result = allData.value
      const user = currentUser.value
      if (user && user.role === USER_ROLES.EMPLOYEE) {
        result = result.filter(item => item.executor === user.name)
      }
      return result
    })

    const filteredData = computed(() => {
      const result = filteredAllData.value
      const start = (currentPage.value - 1) * pageSize.value
      const end = start + pageSize.value
      return result.slice(start, end)
    })

    const totalPages = computed(() => {
      return Math.ceil(filteredAllData.value.length / pageSize.value)
    })

    const handleSearch = () => {
      currentPage.value = 1
      loadData()
    }

    const handleView = async (item: OverdueItem) => {
      loading.value = true
      try {
        const itemId = parseInt(item.id)
        if (isNaN(itemId)) {
          console.error('无效的工单ID:', item.id)
          return
        }
        
        if (item.workOrderType === '定期巡检') {
          currentWorkOrderType.value = '定期巡检'
          const response = await periodicInspectionService.getById(itemId)
          if (response.code === 200 && response.data) {
            updateViewDataFromInspection(response.data)
            isViewModalOpen.value = true
          }
        } else if (item.workOrderType === '临时维修') {
          currentWorkOrderType.value = '临时维修'
          const response = await temporaryRepairService.getById(itemId)
          if (response.code === 200 && response.data) {
            updateViewDataFromRepair(response.data)
            isViewModalOpen.value = true
          }
        } else if (item.workOrderType === '零星用工') {
          currentWorkOrderType.value = '零星用工'
          const response = await spotWorkService.getById(itemId)
          if (response.code === 200 && response.data) {
            updateViewDataFromSpotWork(response.data)
            isViewModalOpen.value = true
          }
        }
      } catch (error) {
        console.error('加载工单详情失败:', error)
      } finally {
        loading.value = false
      }
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
      currentUser,
      searchForm,
      filteredData,
      filteredAllData,
      allData,
      currentPage,
      pageSize,
      totalPages,
      jumpPage,
      loading,
      handleSearch,
      handleView,
      isViewModalOpen,
      currentWorkOrderType,
      viewData,
      closeViewModal,
      formatDate
    }
  }
})
</script>

<style scoped>
.overdue-alert-page {
  min-height: 100vh;
  background: #f8f9fa;
}

.main-wrapper {
  display: flex;
  gap: 20px;
  padding: 20px;
}

.content-area {
  flex: 1;
  min-width: 0;
}

.search-section {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding: 20px;
  background: #fff;
  border-radius: 4px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.search-form {
  display: flex;
  gap: 24px;
  align-items: center;
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
  border: 1px solid #D9D9D9;
  border-radius: 3px;
  font-size: 14px;
  color: #333;
  background: #fff;
  transition: border-color 0.15s;
}

.search-input:focus {
  outline: none;
  border-color: #1890FF;
  box-shadow: 0 0 0 2px rgba(24, 144, 255, 0.1);
}

.search-input::placeholder {
  color: #999;
}

.search-select {
  width: 150px;
  padding: 8px 12px;
  border: 1px solid #D9D9D9;
  border-radius: 3px;
  font-size: 14px;
  color: #333;
  background: #fff;
  transition: border-color 0.15s;
}

.search-select:focus {
  outline: none;
  border-color: #1890FF;
  box-shadow: 0 0 0 2px rgba(24, 144, 255, 0.1);
}

.search-actions {
  display: flex;
  gap: 10px;
}

.btn-search {
  padding: 8px 16px;
  border: none;
  border-radius: 3px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.15s;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.1);
  background: #2196F3;
  color: #fff;
}

.btn-search:hover {
  background: #1976D2;
}

.table-section {
  margin-bottom: 20px;
  background: #fff;
  border-radius: 4px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  overflow: hidden;
}

.data-table {
  width: 100%;
  border-collapse: collapse;
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
}

.th-overdue-days {
  color: #F5222D !important;
}

.data-table td {
  padding: 12px 16px;
  text-align: left;
  font-size: 14px;
  color: #333;
  border-bottom: 1px solid #f0f0f0;
}

.table-row:hover {
  background: #F5F7FA;
}

.alert-type {
  color: #F5222D;
  font-weight: 500;
}

.overdue-days {
  background: #FFF1F0;
  color: #F5222D;
  font-weight: 500;
  padding: 4px 8px;
  border-radius: 2px;
  display: inline-block;
}

td.overdue-days {
  color: #F5222D;
  font-weight: 500;
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

.empty-state {
  padding: 60px 20px;
  text-align: center;
}

.empty-text {
  font-size: 14px;
  color: #999;
}

.pagination-section {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 20px;
  background: #fff;
  border-radius: 4px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
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
  border: 1px solid #D9D9D9;
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

.page-select {
  padding: 6px 12px;
  border: 1px solid #D9D9D9;
  border-radius: 3px;
  font-size: 14px;
  color: #333;
  background: #fff;
  cursor: pointer;
}

@media (max-width: 1400px) {
  .main-wrapper {
    flex-direction: column;
  }
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
  min-height: 70px;
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
  white-space: pre-wrap;
  word-break: break-all;
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
