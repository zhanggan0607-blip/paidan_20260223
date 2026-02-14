<template>
  <div class="overdue-alert-page">
    <LoadingSpinner :visible="loading" text="加载中..." />
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
                <option value="维保计划">维保计划</option>
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
                <th class="th-overdue-days">已超期（天）</th>
                <th>执行人员</th>
                <th>工单状态</th>
                <th>操作</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="(item, index) in filteredData" :key="item.id" class="table-row">
                <td>{{ index + 1 }}</td>
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
            共 {{ filteredData.length }} 条记录
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
  </div>
</template>

<script lang="ts">
import { defineComponent, reactive, ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { overdueAlertService, type OverdueItem } from '../services/overdueAlert'
import LoadingSpinner from '../components/LoadingSpinner.vue'

export default defineComponent({
  name: 'OverdueAlert',
  components: {
    LoadingSpinner
  },
  setup() {
    const router = useRouter()
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

    const filteredData = computed(() => {
      const start = (currentPage.value - 1) * pageSize.value
      const end = start + pageSize.value
      return allData.value.slice(start, end)
    })

    const totalPages = computed(() => {
      return Math.ceil(allData.value.length / pageSize.value)
    })

    const handleSearch = () => {
      currentPage.value = 1
      loadData()
    }

    const handleView = (item: OverdueItem) => {
      switch (item.workOrderType) {
        case '定期巡检':
          router.push({
            path: '/work-order/periodic-inspection',
            query: { id: item.id }
          })
          break
        case '临时维修':
          router.push({
            path: '/work-order/temporary-repair/detail',
            query: { id: item.id }
          })
          break
        case '零星用工':
          router.push({
            path: '/work-order/spot-work',
            query: { id: item.id }
          })
          break
        case '维保计划':
          router.push({
            path: '/maintenance-plan',
            query: { id: item.id }
          })
          break
      }
    }

    onMounted(() => {
      loadData()
    })

    return {
      searchForm,
      filteredData,
      currentPage,
      pageSize,
      totalPages,
      jumpPage,
      loading,
      handleSearch,
      handleView
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
</style>
