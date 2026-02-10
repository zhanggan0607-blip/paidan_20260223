<template>
  <div class="spot-work-page">
    <div class="content">
      <div class="search-section">
        <div class="search-form">
          <div class="search-item">
            <label class="search-label">项目名称：</label>
            <input type="text" class="search-input" placeholder="请输入" v-model="searchForm.projectName" />
          </div>
          <div class="search-item">
            <label class="search-label">客户名称：</label>
            <input type="text" class="search-input" placeholder="请输入" v-model="searchForm.clientName" />
          </div>
        </div>
        <div class="action-buttons">
          <button class="btn btn-add" @click="handleAdd">
            新增零星用工单
          </button>
          <button class="btn btn-search" @click="handleSearch">
            搜索
          </button>
        </div>
      </div>

      <div class="table-section">
        <table class="data-table">
          <thead>
            <tr>
              <th>序号</th>
              <th>自动编号</th>
              <th>项目名称</th>
              <th>零星用工编号</th>
              <th>计划开始日期</th>
              <th>计划结束日期</th>
              <th>客户单位</th>
              <th>实际人员</th>
              <th>状态</th>
              <th>说明</th>
              <th>操作</th>
            </tr>
          </thead>
          <tbody>
            <tr v-if="loading">
              <td colspan="10" style="text-align: center; padding: 20px;">加载中...</td>
            </tr>
            <tr v-else-if="workData.length === 0">
              <td colspan="10" style="text-align: center; padding: 20px;">暂无数据</td>
            </tr>
            <tr v-else v-for="(item, index) in workData" :key="item.id" :class="{ 'even-row': index % 2 === 0 }">
              <td>{{ (currentPage - 1) * pageSize + index + 1 }}</td>
              <td>{{ item.autoId }}</td>
              <td>{{ item.projectName }}</td>
              <td>{{ item.workId }}</td>
              <td>{{ formatDate(item.startDate) }}</td>
              <td>{{ formatDate(item.endDate) }}</td>
              <td>{{ item.clientName || '-' }}</td>
              <td>{{ item.actualPerson || '-' }}</td>
              <td>
                <span v-if="item.status === '未进行'" class="status-tag status-pending">未进行</span>
                <span v-else-if="item.status === '待确认'" class="status-tag status-waiting">待确认</span>
                <span v-else-if="item.status === '进行中'" class="status-tag status-in-progress">进行中</span>
                <span v-else-if="item.status === '已完成'" class="status-tag status-completed">已完成</span>
                <span v-else class="status-tag">{{ item.status }}</span>
              </td>
              <td>{{ item.remark || '-' }}</td>
              <td class="action-cell">
                <a href="#" class="action-link action-view" @click.prevent="handleView(item)">查看</a>
                <a href="#" v-if="item.status === '未进行'" class="action-link action-edit" @click.prevent="handleEdit(item)">编辑</a>
                <a href="#" v-if="item.status === '未进行'" class="action-link action-delete" @click.prevent="handleDelete(item)">删除</a>
                <a href="#" v-if="item.status === '待确认'" class="action-link action-confirm" @click.prevent="handleConfirm(item)">确认</a>
                <a href="#" v-if="item.status === '待确认'" class="action-link action-delete" @click.prevent="handleDelete(item)">删除</a>
                <a href="#" v-if="item.status === '进行中'" class="action-link action-view" @click.prevent="handleView(item)">查看</a>
                <a href="#" v-if="item.status === '进行中'" class="action-link action-edit" @click.prevent="handleEdit(item)">编辑</a>
                <a href="#" v-if="item.status === '进行中'" class="action-link action-delete" @click.prevent="handleDelete(item)">删除</a>
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
          <button class="page-btn page-nav" :disabled="currentPage === 1" @click="currentPage--">
            &lt;
          </button>
          <button
            v-for="page in totalPages"
            :key="page"
            class="page-btn page-num"
            :class="{ active: page === currentPage }"
            @click="currentPage = page"
          >
            {{ page }}
          </button>
          <button class="page-btn page-nav" :disabled="currentPage === totalPages" @click="currentPage++">
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
            <button class="page-btn page-go" @click="handleJump">Go</button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script lang="ts">
import { defineComponent, ref } from 'vue'

interface WorkItem {
  id: number
  autoId: string
  projectName: string
  workId: string
  startDate: string
  endDate: string
  clientName: string
  actualPerson: string
  status: string
  remark: string
}

export default defineComponent({
  name: 'SpotWorkManagement',
  setup() {
    const currentPage = ref(1)
    const pageSize = ref(10)
    const jumpPage = ref(1)
    const loading = ref(false)
    const totalElements = ref(0)
    const totalPages = ref(1)

    const searchForm = ref({
      projectName: '',
      clientName: ''
    })

    const workData = ref<WorkItem[]>([
      {
        id: 1,
        autoId: 'ZD-2023-116A-SH',
        projectName: '曹杨项目维保',
        workId: 'LX-CYDP-20251101',
        startDate: '2025-01-15',
        endDate: '2025-01-20',
        clientName: '曹杨街道',
        actualPerson: '张三',
        status: '未进行',
        remark: '待安排人员'
      },
      {
        id: 2,
        autoId: 'ZD-2023-117B-SH',
        projectName: '曹杨项目维保',
        workId: 'LX-CYDP-20251102',
        startDate: '2025-01-18',
        endDate: '2025-01-25',
        clientName: '曹杨街道',
        actualPerson: '李四',
        status: '待确认',
        remark: '待确认'
      },
      {
        id: 3,
        autoId: 'ZD-2023-118C-SH',
        projectName: '曹杨项目维保',
        workId: 'LX-CYDP-20251103',
        startDate: '2025-01-20',
        endDate: '2025-01-28',
        clientName: '曹杨街道',
        actualPerson: '王五',
        status: '已完成',
        remark: '已完成'
      },
      {
        id: 4,
        autoId: 'ZD-2023-119D-SH',
        projectName: '曹杨项目维保',
        workId: 'LX-CYDP-20251104',
        startDate: '2025-01-22',
        endDate: '2025-01-30',
        clientName: '曹杨街道',
        actualPerson: '赵六',
        status: '进行中',
        remark: '进行中'
      }
    ])

    totalElements.value = workData.value.length
    totalPages.value = Math.ceil(totalElements.value / pageSize.value)

    const formatDate = (dateStr: string) => {
      if (!dateStr) return '-'
      const date = new Date(dateStr)
      return `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}-${String(date.getDate()).padStart(2, '0')}`
    }

    const handleSearch = () => {
      console.log('Search:', searchForm.value)
    }

    const handleAdd = () => {
      console.log('Add new work order')
    }

    const handleView = (item: WorkItem) => {
      console.log('View:', item)
    }

    const handleEdit = (item: WorkItem) => {
      console.log('Edit:', item)
    }

    const handleDelete = (item: WorkItem) => {
      console.log('Delete:', item)
    }

    const handleConfirm = (item: WorkItem) => {
      console.log('Confirm:', item)
    }

    const handleJump = () => {
      const page = parseInt(String(jumpPage.value))
      if (page >= 1 && page <= totalPages.value) {
        currentPage.value = page
      }
    }

    return {
      currentPage,
      pageSize,
      jumpPage,
      loading,
      totalElements,
      totalPages,
      searchForm,
      workData,
      formatDate,
      handleSearch,
      handleAdd,
      handleView,
      handleEdit,
      handleDelete,
      handleConfirm,
      handleJump
    }
  }
})
</script>

<style scoped>
.spot-work-page {
  background: #fff;
  min-height: 100vh;
}

.content {
  padding: 20px;
}

.search-section {
  display: flex;
  gap: 16px;
  margin-bottom: 20px;
  align-items: center;
}

.search-form {
  display: flex;
  gap: 16px;
  align-items: center;
  flex: 1;
}

.search-item {
  display: flex;
  align-items: center;
  gap: 8px;
}

.search-label {
  font-size: 14px;
  color: #666;
  font-weight: 500;
  white-space: nowrap;
}

.search-input {
  padding: 8px 12px;
  border: 1px solid #d0d7de;
  border-radius: 4px;
  font-size: 14px;
  outline: none;
  min-width: 200px;
}

.search-input:focus {
  border-color: #1976d2;
  box-shadow: 0 0 0 2px rgba(25, 118, 210, 0.1);
}

.action-buttons {
  display: flex;
  gap: 12px;
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

.btn-add {
  background: #4caf50;
  color: #fff;
}

.btn-add:hover {
  background: #45a049;
}

.btn-search {
  background: #1976d2;
  color: #fff;
}

.btn-search:hover {
  background: #1565c0;
}

.table-section {
  background: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
}

.data-table {
  width: 100%;
  border-collapse: collapse;
}

.data-table thead {
  background: #f5f5f5;
}

.data-table th {
  padding: 12px 8px;
  text-align: left;
  font-size: 14px;
  font-weight: 600;
  color: #333;
  border-bottom: 2px solid #e0e0e0;
}

.data-table tbody tr {
  transition: background 0.15s;
}

.data-table tbody tr:hover {
  background: #f9f9f9;
}

.data-table tbody tr.even-row {
  background: #fafafa;
}

.data-table td {
  padding: 12px 8px;
  border-bottom: 1px solid #e0e0e0;
  font-size: 14px;
  color: #666;
}

.action-cell {
  display: flex;
  gap: 8px;
}

.action-link {
  font-size: 14px;
  font-weight: 500;
  text-decoration: none;
  transition: color 0.2s;
}

.action-view {
  color: #1976d2;
}

.action-view:hover {
  color: #1565c0;
}

.action-edit {
  color: #1976d2;
}

.action-edit:hover {
  color: #1565c0;
}

.action-confirm {
  color: #4caf50;
}

.action-confirm:hover {
  color: #45a049;
}

.action-delete {
  color: #f44336;
}

.action-delete:hover {
  color: #d32f2f;
}

.status-tag {
  display: inline-block;
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 12px;
  font-weight: 500;
}

.status-pending {
  background: #fff3cd;
  color: #856404;
}

.status-waiting {
  background: #fff7e0;
  color: #f57c00;
}

.status-in-progress {
  background: #e3f2fd;
  color: #fff;
}

.status-completed {
  background: #9e9e9e;
  color: #666;
}

.pagination-section {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 0;
  border-top: 1px solid #e0e0e0;
}

.pagination-info {
  font-size: 14px;
  color: #666;
}

.pagination-controls {
  display: flex;
  gap: 8px;
  align-items: center;
}

.page-btn {
  min-width: 32px;
  padding: 6px 12px;
  border: 1px solid #d0d7de;
  border-radius: 4px;
  background: #fff;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.2s;
}

.page-btn:hover:not(:disabled) {
  background: #f5f5f5;
  border-color: #1976d2;
}

.page-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.page-btn.page-num {
  min-width: 36px;
}

.page-btn.active {
  background: #1976d2;
  color: #fff;
  border-color: #1976d2;
}

.page-select {
  padding: 6px 8px;
  border: 1px solid #d0d7de;
  border-radius: 4px;
  font-size: 14px;
  background: #fff;
  cursor: pointer;
  outline: none;
}

.page-select:focus {
  border-color: #1976d2;
  box-shadow: 0 0 0 2px rgba(25, 118, 210, 0.1);
}

.page-jump {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
  color: #666;
}

.page-input {
  width: 60px;
  padding: 6px 8px;
  border: 1px solid #d0d7de;
  border-radius: 4px;
  font-size: 14px;
  text-align: center;
  outline: none;
}

.page-input:focus {
  border-color: #1976d2;
  box-shadow: 0 0 0 2px rgba(25, 118, 210, 0.1);
}

.page-btn.page-go {
  background: #1976d2;
  color: #fff;
}

.page-btn.page-go:hover {
  background: #1565c0;
}
</style>
