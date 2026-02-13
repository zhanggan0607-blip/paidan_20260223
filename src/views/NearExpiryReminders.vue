<template>
  <div class="expiry-page">
    <div class="content-area">
      <div class="filters">
        <label>项目名称
          <input type="text" placeholder="请输入" v-model="filters.projectName" />
        </label>
        <label>客户名称
          <input type="text" placeholder="请输入" v-model="filters.customerName" />
        </label>
        <label>工单类型
          <select v-model="filters.type">
            <option value="">请选择工单类型</option>
            <option value="临时维修">临时维修工单</option>
            <option value="定期巡检">定期巡检工单</option>
            <option value="零星用工">零星用工工单</option>
          </select>
        </label>
        <button class="btn btn-search" @click="handleSearch">搜索</button>
        <button class="btn btn-reset" @click="handleReset">重置</button>
      </div>
      <div class="table-section">
        <div v-if="loading" class="loading-container">
          <div class="loading-spinner"></div>
          <span>加载中...</span>
        </div>
        <table v-else class="data-table">
          <thead>
            <tr>
              <th>序号</th>
              <th>工单编号</th>
              <th>项目编号</th>
              <th>项目名称</th>
              <th>工单类型</th>
              <th>计划结束日期</th>
              <th>提醒类型</th>
              <th>执行人员</th>
              <th>操作</th>
            </tr>
          </thead>
          <tbody>
            <tr v-if="rows.length === 0">
              <td colspan="9" class="empty-cell">暂无数据</td>
            </tr>
            <tr v-for="(row, idx) in rows" :key="row.id">
              <td>{{ (currentPage - 1) * pageSize + idx + 1 }}</td>
              <td>{{ row.workOrderNo }}</td>
              <td>{{ row.project_id }}</td>
              <td>{{ row.projectName }}</td>
              <td>{{ row.workOrderType }}</td>
              <td>{{ formatDate(row.planEndDate) }}</td>
              <td class="alert-type">超期</td>
              <td>{{ row.executor || '-' }}</td>
              <td class="action-cell">
                <a href="#" class="action-link action-view" @click.prevent="viewDetail(row)">查看</a>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
      <div class="pagination-area" v-if="total > 0">
        <button class="page-btn" :disabled="currentPage === 1" @click="goToPage(currentPage - 1)">上一页</button>
        <span 
          v-for="page in displayedPages" 
          :key="page" 
          class="page-num" 
          :class="{ active: page === currentPage }"
          @click="goToPage(page)"
        >{{ page }}</span>
        <button class="page-btn" :disabled="currentPage === totalPages" @click="goToPage(currentPage + 1)">下一页</button>
        <select class="page-select" v-model.number="pageSize" @change="handlePageSizeChange">
          <option :value="10">10 条 / 页</option>
          <option :value="20">20 条 / 页</option>
          <option :value="50">50 条 / 页</option>
        </select>
        <div class="page-jump">
          <span>跳至</span>
          <input type="number" class="page-input" v-model.number="jumpPage" :min="1" :max="totalPages" />
          <span>页</span>
          <button class="btn-jump" @click="handleJump">跳转</button>
        </div>
        <span class="total-info">共 {{ total }} 条</span>
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
                <div class="form-value">{{ viewData.workOrderNo || '-' }}</div>
              </div>
              <div class="form-item">
                <label class="form-label">项目编号</label>
                <div class="form-value">{{ viewData.project_id || '-' }}</div>
              </div>
              <div class="form-item">
                <label class="form-label">项目名称</label>
                <div class="form-value">{{ viewData.projectName || '-' }}</div>
              </div>
              <div class="form-item">
                <label class="form-label">执行人员</label>
                <div class="form-value">{{ viewData.executor || '-' }}</div>
              </div>
            </div>
            <div class="form-column">
              <div class="form-item">
                <label class="form-label">工单类型</label>
                <div class="form-value">{{ viewData.workOrderType || '-' }}</div>
              </div>
              <div class="form-item">
                <label class="form-label">计划结束日期</label>
                <div class="form-value">{{ formatDate(viewData.planEndDate) || '-' }}</div>
              </div>
              <div class="form-item">
                <label class="form-label">提醒类型</label>
                <div class="form-value alert-type">超期</div>
              </div>
              <div class="form-item">
                <label class="form-label">超期天数</label>
                <div class="form-value alert-type">{{ viewData.overdueDays || 0 }} 天</div>
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
import { defineComponent, ref, reactive, computed, onMounted } from 'vue'
import { overdueAlertService, type OverdueItem } from '@/services/overdueAlert'

export default defineComponent({
  name: 'NearExpiryReminders',
  setup() {
    const filters = ref({ projectName: '', customerName: '', type: '' as string })
    const rows = ref<OverdueItem[]>([])
    const loading = ref(false)
    const currentPage = ref(1)
    const pageSize = ref(10)
    const total = ref(0)
    const jumpPage = ref(1)
    const isViewModalOpen = ref(false)
    const viewData = reactive({
      workOrderNo: '',
      project_id: '',
      projectName: '',
      workOrderType: '',
      planEndDate: '',
      executor: '',
      overdueDays: 0
    })

    const totalPages = computed(() => Math.ceil(total.value / pageSize.value) || 1)
    
    const displayedPages = computed(() => {
      const pages: number[] = []
      const start = Math.max(1, currentPage.value - 2)
      const end = Math.min(totalPages.value, currentPage.value + 2)
      for (let i = start; i <= end; i++) {
        pages.push(i)
      }
      return pages
    })

    const formatDate = (dateStr: string | undefined): string => {
      if (!dateStr) return '-'
      try {
        const date = new Date(dateStr)
        return date.toLocaleDateString('zh-CN')
      } catch {
        return dateStr
      }
    }

    const loadData = async () => {
      loading.value = true
      try {
        const response = await overdueAlertService.getOverdueAlerts({
          project_name: filters.value.projectName || undefined,
          client_name: filters.value.customerName || undefined,
          work_order_type: filters.value.type || undefined
        })
        
        if (response.code === 200 && response.data) {
          rows.value = response.data.items || []
          total.value = response.data.total || 0
        }
      } catch (error) {
        console.error('加载超期提醒数据失败:', error)
        rows.value = []
        total.value = 0
      } finally {
        loading.value = false
      }
    }

    const handleSearch = () => {
      currentPage.value = 1
      loadData()
    }

    const handleReset = () => {
      filters.value = { projectName: '', customerName: '', type: '' }
      currentPage.value = 1
      loadData()
    }

    const goToPage = (page: number) => {
      if (page >= 1 && page <= totalPages.value) {
        currentPage.value = page
        loadData()
      }
    }

    const handlePageSizeChange = () => {
      currentPage.value = 1
      loadData()
    }

    const handleJump = () => {
      if (jumpPage.value >= 1 && jumpPage.value <= totalPages.value) {
        goToPage(jumpPage.value)
      }
    }

    const viewDetail = (row: OverdueItem) => {
      viewData.workOrderNo = row.workOrderNo
      viewData.project_id = row.project_id
      viewData.projectName = row.projectName
      viewData.workOrderType = row.workOrderType
      viewData.planEndDate = row.planEndDate
      viewData.executor = row.executor
      viewData.overdueDays = row.overdueDays
      isViewModalOpen.value = true
    }

    const closeViewModal = () => {
      isViewModalOpen.value = false
    }

    onMounted(() => {
      loadData()
    })

    return { 
      filters, 
      rows, 
      loading,
      currentPage,
      pageSize, 
      total,
      totalPages,
      displayedPages,
      jumpPage, 
      formatDate,
      handleSearch, 
      handleReset,
      goToPage,
      handlePageSizeChange,
      handleJump,
      viewDetail, 
      closeViewModal, 
      isViewModalOpen, 
      viewData 
    }
  }
})
</script>

<style scoped>
.expiry-page {
  padding: 0;
}

.content-area {
  padding: 0;
  display: block;
}

.filters {
  display: flex;
  flex-wrap: nowrap;
  gap: 16px;
  align-items: center;
  margin-bottom: 16px;
  overflow-x: auto;
  white-space: nowrap;
  min-width: max-content;
}

.filters label {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
  color: #333;
}

.filters input,
.filters select {
  height: 36px;
  padding: 6px 12px;
  border: 1px solid #D9D9D9;
  border-radius: 4px;
  font-size: 14px;
  min-width: 180px;
}

.btn-search {
  background: #1890FF;
  color: #fff;
  height: 36px;
  border: none;
  border-radius: 4px;
  padding: 0 20px;
  cursor: pointer;
  font-size: 14px;
}

.btn-search:hover {
  background: #40a9ff;
}

.btn-reset {
  background: #fff;
  color: #666;
  height: 36px;
  border: 1px solid #d9d9d9;
  border-radius: 4px;
  padding: 0 20px;
  cursor: pointer;
  font-size: 14px;
}

.btn-reset:hover {
  border-color: #1890ff;
  color: #1890ff;
}

.table-section {
  margin-top: 0;
}

.loading-container {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 40px;
  gap: 12px;
  color: #666;
}

.loading-spinner {
  width: 24px;
  height: 24px;
  border: 3px solid #f0f0f0;
  border-top-color: #1890ff;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.data-table {
  width: 100%;
  border-collapse: collapse;
  background: #fff;
}

.data-table thead {
  background: #E0E0E0;
}

.data-table th {
  padding: 12px 16px;
  text-align: left;
  font-weight: 600;
  color: #333;
  font-size: 14px;
  border: 1px solid #e0e0e0;
}

.data-table td {
  padding: 12px 16px;
  border: 1px solid #e0e0e0;
  font-size: 14px;
  color: #333;
}

.data-table tbody tr {
  background: #fff;
}

.data-table tbody tr:hover {
  background: #f5f5f5;
}

.empty-cell {
  text-align: center;
  color: #999;
  padding: 40px !important;
}

.alert-type {
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

.pagination-area {
  display: flex;
  flex-wrap: nowrap;
  align-items: center;
  gap: 8px;
  margin-top: 16px;
  padding: 16px 0;
  overflow-x: auto;
  white-space: nowrap;
  min-width: max-content;
}

.page-btn {
  border: 1px solid #e0e0e0;
  background: #fff;
  border-radius: 4px;
  padding: 6px 12px;
  cursor: pointer;
  font-size: 14px;
  color: #666;
}

.page-btn:hover:not(:disabled) {
  background: #f5f5f5;
}

.page-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.page-num {
  padding: 6px 12px;
  border: 1px solid #e0e0e0;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
  color: #666;
  background: #fff;
}

.page-num:hover {
  background: #f5f5f5;
}

.page-num.active {
  background: #1890FF;
  color: #fff;
  border-color: #1890FF;
}

.page-select {
  margin-left: 12px;
  height: 32px;
  padding: 4px 8px;
  border: 1px solid #e0e0e0;
  border-radius: 4px;
  font-size: 14px;
}

.page-jump {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  margin-left: 12px;
  font-size: 14px;
  color: #666;
}

.page-input {
  width: 60px;
  height: 32px;
  border: 1px solid #e0e0e0;
  border-radius: 4px;
  padding: 0 8px;
  font-size: 14px;
  text-align: center;
}

.btn-jump {
  background: #1890FF;
  color: #fff;
  border: none;
  border-radius: 4px;
  padding: 4px 12px;
  cursor: pointer;
  font-size: 14px;
}

.btn-jump:hover {
  background: #40a9ff;
}

.total-info {
  margin-left: 12px;
  color: #666;
  font-size: 14px;
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
  min-height: 60px;
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

.form-value.alert-type {
  color: #F5222D;
  font-weight: 500;
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
  padding: 8px 20px;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
}

.btn-cancel:hover {
  background: #f5f5f5;
}

</style>
