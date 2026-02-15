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
      <div class="search-actions">
        <button class="btn btn-search" @click="handleSearch">搜索</button>
        <button class="btn btn-reset" @click="handleReset">重置</button>
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
            <th>执行人员</th>
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
  </div>
</template>

<script lang="ts">
import { defineComponent, ref, reactive, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { workPlanService, type WorkPlan } from '../services/workPlan'
import { temporaryRepairService, type TemporaryRepair } from '../services/temporaryRepair'
import { spotWorkService, type SpotWork } from '../services/spotWork'
import LoadingSpinner from '../components/LoadingSpinner.vue'
import Toast from '../components/Toast.vue'
import SearchInput from '../components/SearchInput.vue'
import { PLAN_TYPES, formatDate } from '../config/constants'

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
    const router = useRouter()
    const loading = ref(false)
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

    const getDaysFromToday = (dateStr: string): number => {
      if (!dateStr) return 999
      const today = new Date()
      today.setHours(0, 0, 0, 0)
      const targetDate = new Date(dateStr)
      targetDate.setHours(0, 0, 0, 0)
      const diffTime = targetDate.getTime() - today.getTime()
      const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24))
      return diffDays
    }

    const getDaysClass = (days: number): string => {
      return 'days-warning'
    }

    const loadData = async () => {
      loading.value = true
      try {
        const [workPlansRes, tempRepairsRes, spotWorksRes] = await Promise.all([
          workPlanService.getAll({ plan_type: PLAN_TYPES.PERIODIC_INSPECTION }),
          temporaryRepairService.getAll(),
          spotWorkService.getAll()
        ])

        const items: NearExpiryItem[] = []

        if (workPlansRes.code === 200 && workPlansRes.data) {
          workPlansRes.data.forEach((item: WorkPlan) => {
            const days = getDaysFromToday(item.plan_start_date)
            if (days <= 3 && days >= 0) {
              items.push({
                id: item.id,
                workOrderId: item.plan_id,
                projectId: item.project_id,
                projectName: item.project_name,
                workOrderType: PLAN_TYPES.PERIODIC_INSPECTION,
                planStartDate: item.plan_start_date,
                daysFromToday: days,
                executor: item.maintenance_personnel
              })
            }
          })
        }

        if (tempRepairsRes.code === 200 && tempRepairsRes.data) {
          tempRepairsRes.data.forEach((item: TemporaryRepair) => {
            const days = getDaysFromToday(item.plan_start_date)
            if (days <= 3 && days >= 0) {
              items.push({
                id: item.id,
                workOrderId: item.repair_id,
                projectId: item.project_id,
                projectName: item.project_name,
                workOrderType: PLAN_TYPES.TEMPORARY_REPAIR,
                planStartDate: item.plan_start_date,
                daysFromToday: days,
                executor: item.maintenance_personnel
              })
            }
          })
        }

        if (spotWorksRes.code === 200 && spotWorksRes.data) {
          spotWorksRes.data.forEach((item: SpotWork) => {
            const days = getDaysFromToday(item.plan_start_date)
            if (days <= 3 && days >= 0) {
              items.push({
                id: item.id,
                workOrderId: item.work_id,
                projectId: item.project_id,
                projectName: item.project_name,
                workOrderType: '零星用工',
                planStartDate: item.plan_start_date,
                daysFromToday: days,
                executor: item.maintenance_personnel
              })
            }
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
      switch (item.workOrderType) {
        case PLAN_TYPES.PERIODIC_INSPECTION:
          router.push({
            path: '/work-order/periodic-inspection',
            query: { id: item.id }
          })
          break
        case PLAN_TYPES.TEMPORARY_REPAIR:
          router.push({
            path: '/work-order/temporary-repair/detail',
            query: { id: item.id }
          })
          break
        case PLAN_TYPES.SPOT_WORK:
          router.push({
            path: '/work-order/spot-work',
            query: { id: item.id }
          })
          break
      }
    }

    onMounted(() => {
      loadData()
    })

    return {
      loading,
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
      formatDate,
      getDaysClass,
      handleSearch,
      handleReset,
      handlePageSizeChange,
      handleJump,
      handleView
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
</style>
