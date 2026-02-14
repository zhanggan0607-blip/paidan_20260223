<template>
  <div class="spot-work-page">
    <Toast :visible="toast.visible" :message="toast.message" :type="toast.type" />
    <div class="content">
      <div class="search-section">
        <div class="search-form">
          <div class="search-item">
            <label class="search-label">项目名称：</label>
            <input type="text" class="search-input" placeholder="请输入" v-model="searchForm.project_name" />
          </div>
          <div class="search-item">
            <label class="search-label">客户名称：</label>
            <input type="text" class="search-input" placeholder="请输入" v-model="searchForm.client_name" />
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
              <th>项目编号</th>
              <th>项目名称</th>
              <th>零星用工编号</th>
              <th>计划开始日期</th>
              <th>计划结束日期</th>
              <th>客户单位</th>
              <th>运维人员</th>
              <th>状态</th>
              <th>备注</th>
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
              <td>{{ item.project_id }}</td>
              <td>{{ item.project_name }}</td>
              <td>{{ item.work_id }}</td>
              <td>{{ formatDate(item.plan_start_date) }}</td>
              <td>{{ formatDate(item.plan_end_date) }}</td>
              <td>{{ item.client_name || '-' }}</td>
              <td>{{ item.maintenance_personnel || '-' }}</td>
              <td>
                <span v-if="item.status === WORK_STATUS.NOT_STARTED" class="status-tag status-pending">未进行</span>
                <span v-else-if="item.status === WORK_STATUS.PENDING_CONFIRM" class="status-tag status-waiting">待确认</span>
                <span v-else-if="item.status === WORK_STATUS.IN_PROGRESS" class="status-tag status-in-progress">进行中</span>
                <span v-else-if="item.status === WORK_STATUS.COMPLETED" class="status-tag status-completed">已完成</span>
                <span v-else class="status-tag">{{ item.status }}</span>
              </td>
              <td>{{ item.remarks || '-' }}</td>
              <td class="action-cell">
                <a href="#" class="action-link action-view" @click.prevent="handleView(item)">查看</a>
                <a href="#" v-if="item.status === WORK_STATUS.NOT_STARTED" class="action-link action-edit" @click.prevent="handleEdit(item)">编辑</a>
                <a href="#" v-if="item.status === WORK_STATUS.NOT_STARTED" class="action-link action-delete" @click.prevent="handleDelete(item)">删除</a>
                <a href="#" v-if="item.status === WORK_STATUS.PENDING_CONFIRM" class="action-link action-confirm" @click.prevent="handleConfirm(item)">确认</a>
                <a href="#" v-if="item.status === WORK_STATUS.PENDING_CONFIRM" class="action-link action-delete" @click.prevent="handleDelete(item)">删除</a>
                <a href="#" v-if="item.status === WORK_STATUS.IN_PROGRESS" class="action-link action-view" @click.prevent="handleView(item)">查看</a>
                <a href="#" v-if="item.status === WORK_STATUS.IN_PROGRESS" class="action-link action-edit" @click.prevent="handleEdit(item)">编辑</a>
                <a href="#" v-if="item.status === WORK_STATUS.IN_PROGRESS" class="action-link action-delete" @click.prevent="handleDelete(item)">删除</a>
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
import { defineComponent, ref, onMounted, watch, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessageBox } from 'element-plus'
import { maintenancePlanService, type MaintenancePlan } from '@/services/maintenancePlan'
import Toast from '@/components/Toast.vue'
import { WORK_STATUS, formatDate } from '@/config/constants'

interface WorkItem {
  id: number
  work_id: string
  project_id: string
  project_name: string
  plan_start_date: string
  plan_end_date: string
  client_name: string
  maintenance_personnel: string
  status: string
  remarks?: string
}

export default defineComponent({
  name: 'SpotWorkManagement',
  components: {
    Toast
  },
  setup() {
    const router = useRouter()
    const currentPage = ref(1)
    const pageSize = ref(10)
    const jumpPage = ref(1)
    const loading = ref(false)
    const totalElements = ref(0)
    const totalPages = ref(1)

    const toast = reactive({
      visible: false,
      message: '',
      type: 'success' as 'success' | 'error' | 'warning' | 'info'
    })

    const showToast = (message: string, type: 'success' | 'error' | 'warning' | 'info' = 'success') => {
      toast.message = message
      toast.type = type
      toast.visible = true
      setTimeout(() => {
        toast.visible = false
      }, 3000)
    }

    const searchForm = ref({
      project_name: '',
      client_name: ''
    })

    const workData = ref<WorkItem[]>([])

    const loadData = async () => {
      loading.value = true
      try {
        const response = await maintenancePlanService.getList({
          page: currentPage.value - 1,
          size: pageSize.value,
          plan_name: searchForm.value.project_name || undefined,
          client_name: searchForm.value.client_name || undefined,
          plan_type: '零星用工'
        })
        
        if (response.code === 200) {
          workData.value = response.data.content.map((item: MaintenancePlan) => ({
            id: item.id,
            work_id: item.plan_id,
            project_id: item.project_id,
            project_name: item.plan_name,
            plan_start_date: item.plan_start_date,
            plan_end_date: item.plan_end_date,
            client_name: item.responsible_department || '',
            maintenance_personnel: item.responsible_person || '',
            status: item.plan_status || '待执行',
            remarks: item.remarks || ''
          }))
          totalElements.value = response.data.totalElements
          totalPages.value = response.data.totalPages || 1
        }
      } catch (error: any) {
        console.error('加载数据失败:', error)
      } finally {
        loading.value = false
      }
    }

    const handleSearch = () => {
      currentPage.value = 1
      loadData()
    }

    const handleAdd = () => {
    }

    const handleView = (item: WorkItem) => {
      router.push({
        name: 'SpotWorkDetail',
        query: { id: item.id }
      })
    }

    const handleEdit = (item: WorkItem) => {
    }

    const handleDelete = async (item: WorkItem) => {
      try {
        await ElMessageBox.confirm(`确定要删除用工单 ${item.work_id} 吗？`, '提示', {
          confirmButtonText: '确定',
          cancelButtonText: '取消',
          type: 'warning'
        })
        
        await maintenancePlanService.delete(item.id)
        showToast('删除成功', 'success')
        loadData()
      } catch (error: any) {
        if (error !== 'cancel') {
          console.error('删除失败:', error)
          showToast('删除失败', 'error')
        }
      }
    }

    const handleConfirm = async (item: WorkItem) => {
      try {
        await maintenancePlanService.update(item.id, {
          plan_id: item.work_id,
          plan_name: item.project_name,
          project_id: item.project_id,
          plan_type: '零星用工',
          equipment_id: 'N/A',
          equipment_name: '零星用工',
          plan_start_date: item.plan_start_date,
          plan_end_date: item.plan_end_date,
          responsible_person: item.maintenance_personnel,
          responsible_department: item.client_name,
          maintenance_content: item.remarks || '',
          plan_status: '进行中',
          execution_status: '进行中'
        })
        showToast('确认成功', 'success')
        loadData()
      } catch (error) {
        console.error('确认失败:', error)
        showToast('确认失败', 'error')
      }
    }

    const handleJump = () => {
      const page = parseInt(String(jumpPage.value))
      if (page >= 1 && page <= totalPages.value) {
        currentPage.value = page
      }
    }

    watch([currentPage, pageSize], () => {
      loadData()
    })

    onMounted(() => {
      loadData()
    })

    return {
      currentPage,
      pageSize,
      jumpPage,
      loading,
      totalElements,
      totalPages,
      searchForm,
      workData,
      toast,
      formatDate,
      WORK_STATUS,
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
