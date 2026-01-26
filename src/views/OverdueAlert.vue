<template>
  <div class="overdue-alert-page">
    <div class="main-wrapper">
      <div class="content-area">
        <div class="search-section">
          <div class="search-form">
            <div class="search-item">
              <label class="search-label">项目名称</label>
              <input type="text" class="search-input" placeholder="请输入" v-model="searchForm.projectName" />
            </div>
            <div class="search-item">
              <label class="search-label">客户名称</label>
              <input type="text" class="search-input" placeholder="请输入" v-model="searchForm.customerName" />
            </div>
            <div class="search-item">
              <label class="search-label">工单类型</label>
              <select class="search-select" v-model="searchForm.workOrderType">
                <option value="">请选择工单类型</option>
                <option value="定期巡检">定期巡检</option>
                <option value="临时维修">临时维修</option>
                <option value="零星用工">零星用工</option>
              </select>
            </div>
          </div>
          <div class="search-actions">
            <button class="btn btn-search" @click="handleSearch">搜索</button>
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
                <th>已超期（天）</th>
                <th>执行人员</th>
                <th>工单状态</th>
                <th>操作</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="(item, index) in filteredData" :key="item.id" class="table-row">
                <td>{{ index + 1 }}</td>
                <td>{{ item.workOrderNo }}</td>
                <td>{{ item.projectId }}</td>
                <td>{{ item.projectName }}</td>
                <td>{{ item.workOrderType }}</td>
                <td>{{ item.planEndDate }}</td>
                <td class="alert-type">已超期</td>
                <td class="overdue-days">
                  {{ item.overdueDays }}
                </td>
                <td>{{ item.executor }}</td>
                <td>{{ item.workOrderStatus }}</td>
                <td>
                  <button class="btn-action" @click="handleView(item)">查看</button>
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
            共 {{ filteredData.length }} 条记录
          </div>
          <div class="pagination-controls">
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
              <input type="number" class="page-input" v-model="jumpPage" min="1" :max="totalPages" />
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
                <div class="form-value">{{ viewData.workOrderNo || '-' }}</div>
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
                <label class="form-label">客户名称</label>
                <div class="form-value">{{ viewData.customerName || '-' }}</div>
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
                <div class="form-value">{{ viewData.planEndDate || '-' }}</div>
              </div>
              <div class="form-item">
                <label class="form-label">提醒类型</label>
                <div class="form-value alert-type">已超期</div>
              </div>
              <div class="form-item">
                <label class="form-label">已超期（天）</label>
                <div class="form-value overdue-days">{{ viewData.overdueDays }}</div>
              </div>
              <div class="form-item">
                <label class="form-label">工单状态</label>
                <div class="form-value">{{ viewData.workOrderStatus || '-' }}</div>
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
import { defineComponent, reactive, ref, computed } from 'vue'

export interface OverdueItem {
  id: string
  workOrderNo: string
  projectId: string
  projectName: string
  customerName: string
  workOrderType: string
  planEndDate: string
  workOrderStatus: string
  overdueDays: number
  executor: string
}

export default defineComponent({
  name: 'OverdueAlert',
  setup() {
    const searchForm = reactive({
      projectName: '',
      customerName: '',
      workOrderType: ''
    })

    const currentPage = ref(1)
    const pageSize = ref(10)
    const jumpPage = ref(1)
    const isViewModalOpen = ref(false)
    const viewData = reactive({
      workOrderNo: '',
      projectId: '',
      projectName: '',
      customerName: '',
      workOrderType: '',
      planEndDate: '',
      workOrderStatus: '',
      overdueDays: 0,
      executor: ''
    })

    const calculateOverdueDays = (planEndDate: string): number => {
      const today = new Date()
      const endDate = new Date(planEndDate)
      const diffTime = today.getTime() - endDate.getTime()
      const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24))
      return diffDays > 0 ? diffDays : 0
    }

    const allData = ref<OverdueItem[]>([
      {
        id: '1',
        workOrderNo: 'GD-2025-001',
        projectId: 'PRJ-2025-001',
        projectName: '上海中心大厦维保项目',
        customerName: '上海城投（集团）有限公司',
        workOrderType: '定期巡检',
        planEndDate: '2025-01-15',
        workOrderStatus: '未确认',
        overdueDays: 0,
        executor: '刘园智'
      },
      {
        id: '2',
        workOrderNo: 'GD-2025-002',
        projectId: 'PRJ-2025-002',
        projectName: '环球金融中心维保项目',
        customerName: '上海建工集团股份有限公司',
        workOrderType: '临时维修',
        planEndDate: '2025-01-14',
        workOrderStatus: '进行中',
        overdueDays: 0,
        executor: '晋海龙'
      },
      {
        id: '3',
        workOrderNo: 'GD-2025-003',
        projectId: 'PRJ-2025-003',
        projectName: '金茂大厦维保项目',
        customerName: '中国金茂控股集团有限公司',
        workOrderType: '定期巡检',
        planEndDate: '2025-01-09',
        workOrderStatus: '未进行',
        overdueDays: 0,
        executor: '张伟'
      },
      {
        id: '4',
        workOrderNo: 'GD-2025-004',
        projectId: 'PRJ-2025-004',
        projectName: '东方明珠塔维保项目',
        customerName: '上海文化广播影视集团有限公司',
        workOrderType: '零星用工',
        planEndDate: '2025-01-09',
        workOrderStatus: '未确认',
        overdueDays: 0,
        executor: '李明'
      }
    ])

    allData.value = allData.value.map(item => ({
      ...item,
      overdueDays: calculateOverdueDays(item.planEndDate)
    }))

    const validStatuses = ['未确认', '未下发', '未进行', '进行中', '待确认', '已退回']

    const filteredData = computed(() => {
      let result = allData.value

      if (searchForm.projectName.trim()) {
        result = result.filter(item =>
          item.projectName.toLowerCase().includes(searchForm.projectName.toLowerCase().trim())
        )
      }

      if (searchForm.customerName.trim()) {
        result = result.filter(item =>
          item.customerName.toLowerCase().includes(searchForm.customerName.toLowerCase().trim())
        )
      }

      if (searchForm.workOrderType) {
        result = result.filter(item => item.workOrderType === searchForm.workOrderType)
      }

      result = result.filter(item => validStatuses.includes(item.workOrderStatus))

      result = result.filter(item => {
        const today = new Date()
        const endDate = new Date(item.planEndDate)
        return endDate < today
      })

      result = result.filter(item => item.overdueDays > 0)

      const start = (currentPage.value - 1) * pageSize.value
      const end = start + pageSize.value
      return result.slice(start, end)
    })

    const totalPages = computed(() => {
      let result = allData.value

      if (searchForm.projectName.trim()) {
        result = result.filter(item =>
          item.projectName.toLowerCase().includes(searchForm.projectName.toLowerCase().trim())
        )
      }

      if (searchForm.customerName.trim()) {
        result = result.filter(item =>
          item.customerName.toLowerCase().includes(searchForm.customerName.toLowerCase().trim())
        )
      }

      if (searchForm.workOrderType) {
        result = result.filter(item => item.workOrderType === searchForm.workOrderType)
      }

      result = result.filter(item => validStatuses.includes(item.workOrderStatus))
      result = result.filter(item => {
        const today = new Date()
        const endDate = new Date(item.planEndDate)
        return endDate < today
      })
      result = result.filter(item => item.overdueDays > 0)

      return Math.ceil(result.length / pageSize.value)
    })

    const handleSearch = () => {
      currentPage.value = 1
    }

    const handleView = (item: OverdueItem) => {
      viewData.workOrderNo = item.workOrderNo
      viewData.projectId = item.projectId
      viewData.projectName = item.projectName
      viewData.customerName = item.customerName
      viewData.workOrderType = item.workOrderType
      viewData.planEndDate = item.planEndDate
      viewData.workOrderStatus = item.workOrderStatus
      viewData.overdueDays = item.overdueDays
      viewData.executor = item.executor
      isViewModalOpen.value = true
    }

    const closeViewModal = () => {
      isViewModalOpen.value = false
    }

    return {
      searchForm,
      filteredData,
      currentPage,
      pageSize,
      totalPages,
      jumpPage,
      handleSearch,
      handleView,
      closeViewModal,
      isViewModalOpen,
      viewData
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

.btn-action {
  padding: 6px 12px;
  background: #2E7D32;
  color: #fff;
  border: none;
  border-radius: 3px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: background 0.15s;
}

.btn-action:hover {
  background: #1B5E20;
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
  align-items: center;
  gap: 8px;
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

.form-value.overdue-days {
  background: #FFF1F0;
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
}

.btn-cancel:hover {
  background: #f5f5f5;
}

</style>
