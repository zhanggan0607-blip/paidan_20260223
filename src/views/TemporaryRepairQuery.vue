<template>
  <div class="temporary-repair-page">
    <div class="content">
      <div class="search-section">
        <div class="search-form">
          <div class="search-item">
            <label class="search-label">项目名称：</label>
            <input type="text" class="search-input" placeholder="请输入项目名称" v-model="searchForm.projectName" />
          </div>
          <div class="search-item">
            <label class="search-label">客户名称：</label>
            <input type="text" class="search-input" placeholder="请输入客户名称" v-model="searchForm.clientName" />
          </div>
        </div>
        <button class="btn btn-search" @click="handleSearch">
          搜索
        </button>
      </div>

      <div class="table-section">
        <table class="data-table">
          <thead>
            <tr>
              <th>序号</th>
              <th>项目编号</th>
              <th>项目名称</th>
              <th>维修单编号</th>
              <th>开始日期</th>
              <th>结束日期</th>
              <th>客户单位</th>
              <th>运维人员</th>
              <th>状态</th>
              <th>操作</th>
            </tr>
          </thead>
          <tbody>
            <tr v-if="loading">
              <td colspan="9" style="text-align: center; padding: 20px;">加载中...</td>
            </tr>
            <tr v-else-if="repairData.length === 0">
              <td colspan="9" style="text-align: center; padding: 20px;">暂无数据</td>
            </tr>
            <tr v-else v-for="(item, index) in repairData" :key="item.id" :class="{ 'even-row': index % 2 === 0 }">
              <td>{{ (currentPage - 1) * pageSize + index + 1 }}</td>
              <td>{{ item.projectId }}</td>
              <td>{{ item.projectName }}</td>
              <td>{{ item.repairId }}</td>
              <td>{{ formatDate(item.startDate) }}</td>
              <td>{{ formatDate(item.endDate) }}</td>
              <td>{{ item.clientName || '-' }}</td>
              <td>{{ item.maintenancePerson || '-' }}</td>
              <td>
                <span v-if="item.status === '未进行'" class="status-tag status-pending">未进行</span>
                <span v-else-if="item.status === '待确认'" class="status-tag status-waiting">待确认</span>
                <span v-else-if="item.status === '进行中'" class="status-tag status-in-progress">进行中</span>
                <span v-else-if="item.status === '已完成'" class="status-tag status-completed">已完成</span>
                <span v-else class="status-tag">{{ item.status }}</span>
              </td>
              <td class="action-cell">
                <a href="#" class="action-link action-view" @click.prevent="handleView(item)">查看</a>
                <a href="#" v-if="item.status === '已完成'" class="action-link action-export" @click.prevent="handleExport(item)">导出</a>
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

interface RepairItem {
  id: number
  projectId: string
  projectName: string
  repairId: string
  startDate: string
  endDate: string
  clientName: string
  maintenancePerson: string
  status: string
}

export default defineComponent({
  name: 'TemporaryRepairQuery',
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

    const repairData = ref<RepairItem[]>([
      {
        id: 1,
        projectId: 'P001',
        projectName: '天齐大厦维保项目',
        repairId: 'WX20260129001',
        startDate: '2026-01-15',
        endDate: '2026-01-20',
        clientName: '天齐物业',
        maintenancePerson: '晋海龙',
        status: '已完成'
      },
      {
        id: 2,
        projectId: 'P002',
        projectName: '天齐大厦维保项目',
        repairId: 'WX20260129002',
        startDate: '2026-01-18',
        endDate: '2026-01-22',
        clientName: '天齐物业',
        maintenancePerson: '王五',
        status: '进行中'
      },
      {
        id: 3,
        projectId: 'P003',
        projectName: '天齐大厦维保项目',
        repairId: 'WX20260129003',
        startDate: '2026-01-20',
        endDate: '2026-01-25',
        clientName: '天齐物业',
        maintenancePerson: '李四',
        status: '待确认'
      },
      {
        id: 4,
        projectId: 'P004',
        projectName: '天齐大厦维保项目',
        repairId: 'WX20260129004',
        startDate: '2026-01-22',
        endDate: '2026-01-28',
        clientName: '天齐物业',
        maintenancePerson: '张三',
        status: '未进行'
      },
      {
        id: 5,
        projectId: 'P005',
        projectName: '天齐大厦维保项目',
        repairId: 'WX20260129005',
        startDate: '2026-01-25',
        endDate: '2026-01-30',
        clientName: '天齐物业',
        maintenancePerson: '刘启智',
        status: '已完成'
      }
    ])

    totalElements.value = repairData.value.length
    totalPages.value = Math.ceil(totalElements.value / pageSize.value)

    const formatDate = (dateStr: string) => {
      if (!dateStr) return '-'
      const date = new Date(dateStr)
      return `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}-${String(date.getDate()).padStart(2, '0')}`
    }

    const handleSearch = () => {
      console.log('Search:', searchForm.value)
    }

    const handleView = (item: RepairItem) => {
      console.log('View:', item)
    }

    const handleExport = (item: RepairItem) => {
      console.log('Export:', item)
    }

    const handleJump = () => {
      const page = parseInt(String(jumpPage.value))
      if (page >= 1 && page <= totalPages.value) {
        currentPage.value = page
      }
    }

    const toggleSidebar = () => {
      console.log('Toggle sidebar')
    }

    return {
      currentPage,
      pageSize,
      jumpPage,
      loading,
      totalElements,
      totalPages,
      searchForm,
      repairData,
      formatDate,
      handleSearch,
      handleView,
      handleExport,
      handleJump,
      toggleSidebar
    }
  }
})
</script>

<style scoped>
.temporary-repair-page {
  background: #fff;
  min-height: 100vh;
}

.top-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 20px;
  background: #F5F7FA;
  border-bottom: 1px solid #e0e0e0;
}

.menu-toggle {
  cursor: pointer;
  padding: 8px;
  border-radius: 4px;
  transition: background 0.2s;
}

.menu-toggle:hover {
  background: rgba(0, 0, 0, 0.05);
}

.breadcrumb {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
  color: #666;
  font-weight: 500;
}

.breadcrumb-level1 {
  color: #1976d2;
  font-weight: 500;
}

.breadcrumb-separator {
  color: #999;
}

.breadcrumb-level2 {
  color: #333;
  font-weight: 600;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 6px 12px;
  background: #fff;
  border-radius: 20px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.user-avatar {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background: linear-gradient(135deg, #1976d2 0%, #42a5f5 100%);
  color: #fff;
  font-size: 12px;
  font-weight: 600;
  display: flex;
  align-items: center;
  justify-content: center;
}

.user-name {
  font-size: 14px;
  color: #333;
  font-weight: 500;
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

.btn {
  padding: 8px 16px;
  border: none;
  border-radius: 4px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
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

.action-export {
  color: #1976d2;
}

.action-export:hover {
  color: #1565c0;
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
  background: #4caf50;
  color: #fff;
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

.page-btn.page-nav {
  background: #f5f5f5;
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
