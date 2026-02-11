<template>
  <div class="temporary-repair-page">
    <Toast :visible="toast.visible" :message="toast.message" :type="toast.type" />
    <div class="content">
      <div class="search-section">
        <div class="search-form">
          <div class="search-row">
            <div class="search-item">
              <label class="search-label">项目名称：</label>
              <input type="text" class="search-input" placeholder="请输入项目名称" v-model="searchForm.project_name" />
            </div>
            <div class="search-item">
              <label class="search-label">客户名称：</label>
              <input type="text" class="search-input" placeholder="请输入客户名称" v-model="searchForm.client_name" />
            </div>
          </div>
          <div class="search-row">
            <div class="search-item">
              <label class="search-label">开始日期：</label>
              <input type="date" class="search-input" v-model="searchForm.plan_start_date" />
            </div>
            <div class="search-item">
              <label class="search-label">结束日期：</label>
              <input type="date" class="search-input" v-model="searchForm.plan_end_date" />
            </div>
          </div>
        </div>
        <div class="action-buttons">
          <button class="btn btn-reset" @click="handleReset">
            重置
          </button>
          <button class="btn btn-add" @click="handleAdd">
            新增临时工单
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
              <th>维修单编号</th>
              <th>计划开始日期</th>
              <th>计划结束日期</th>
              <th>客户单位</th>
              <th>运维人员</th>
              <th>维修内容</th>
              <th>操作</th>
            </tr>
          </thead>
          <tbody>
            <tr v-if="loading">
              <td colspan="10" style="text-align: center; padding: 20px;">加载中...</td>
            </tr>
            <tr v-else-if="repairData.length === 0">
              <td colspan="10" style="text-align: center; padding: 20px;">暂无数据</td>
            </tr>
            <tr v-else v-for="(item, index) in repairData" :key="item.id" :class="{ 'even-row': index % 2 === 0 }">
              <td>{{ (currentPage - 1) * pageSize + index + 1 }}</td>
              <td>{{ item.project_id }}</td>
              <td>{{ item.project_name }}</td>
              <td>{{ item.repair_id }}</td>
              <td>{{ formatDate(item.plan_start_date) }}</td>
              <td>{{ formatDate(item.plan_end_date) }}</td>
              <td>{{ item.client_name || '-' }}</td>
              <td>{{ item.maintenance_personnel || '-' }}</td>
              <td>{{ item.remarks || '-' }}</td>
              <td class="action-cell">
                <a href="#" class="action-link action-view" @click.prevent="handleView(item)">查看</a>
                <a href="#" class="action-link action-export" @click.prevent="handleExport(item)">导出</a>
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

    <div v-if="isAddModalOpen" class="modal-overlay" @click.self="closeAddModal">
      <div class="modal-container">
        <div class="modal-header">
          <h3 class="modal-title">新增临时工单</h3>
          <button class="modal-close" @click="closeAddModal">×</button>
        </div>
        <div class="modal-body">
          <div class="form-grid">
            <div class="form-column">
              <div class="form-item">
                <label class="form-label">
                  <span class="required">*</span> 项目名称
                </label>
                <select class="form-input" v-model="formData.project_name" @change="handleProjectChange">
                  <option value="">请选择项目</option>
                  <option v-for="project in projectList" :key="project.id" :value="project.project_name">
                    {{ project.project_name }}
                  </option>
                </select>
              </div>
              <div class="form-item">
                <label class="form-label">
                  <span class="required">*</span> 项目编号
                </label>
                <input type="text" class="form-input form-input-readonly" placeholder="请输入项目编号" v-model="formData.project_id" readonly />
              </div>
              <div class="form-item">
                <label class="form-label">
                  <span class="required">*</span> 维修单编号
                </label>
                <input type="text" class="form-input" placeholder="请输入维修单编号" v-model="formData.repair_id" maxlength="50" />
              </div>
              <div class="form-item">
                <label class="form-label">
                  <span class="required">*</span> 客户单位
                </label>
                <input type="text" class="form-input form-input-readonly" placeholder="请输入客户单位" v-model="formData.client_name" readonly />
              </div>
            </div>
            <div class="form-column">
              <div class="form-item">
                <label class="form-label">
                  <span class="required">*</span> 计划开始日期
                </label>
                <input type="date" class="form-input" v-model="formData.plan_start_date" />
              </div>
              <div class="form-item">
                <label class="form-label">
                  <span class="required">*</span> 计划结束日期
                </label>
                <input type="date" class="form-input" v-model="formData.plan_end_date" />
              </div>
              <div class="form-item">
                <label class="form-label">
                  <span class="required">*</span> 运维人员
                </label>
                <select class="form-input" v-model="formData.maintenance_personnel">
                  <option value="">请选择</option>
                  <option v-for="person in personnelList" :key="person.id" :value="person.name">
                    {{ person.name }}
                  </option>
                </select>
              </div>
              <div class="form-item">
                <label class="form-label">维修内容</label>
                <input type="text" class="form-input" placeholder="请输入维修内容" v-model="formData.remarks" maxlength="500" />
              </div>
            </div>
          </div>
        </div>
        <div class="modal-footer">
          <button class="btn btn-cancel" @click="closeAddModal">取消</button>
          <button class="btn btn-save" @click="handleSave" :disabled="saving">
            {{ saving ? '保存中...' : '保存' }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script lang="ts">
import { defineComponent, ref, onMounted, reactive, watch } from 'vue'
import { useRouter } from 'vue-router'
import { projectInfoService, type ProjectInfo } from '@/services/projectInfo'
import { personnelService, type Personnel } from '@/services/personnel'
import { temporaryRepairService, type TemporaryRepair } from '@/services/temporaryRepair'
import Toast from '@/components/Toast.vue'

interface RepairItem {
  id: number
  repair_id: string
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
  name: 'TemporaryRepairQuery',
  setup() {
    const router = useRouter()
    const currentPage = ref(1)
    const pageSize = ref(10)
    const jumpPage = ref(1)
    const loading = ref(false)
    const saving = ref(false)
    const totalElements = ref(0)
    const totalPages = ref(1)
    const isAddModalOpen = ref(false)

    const toast = reactive({
      visible: false,
      message: '',
      type: 'success' as 'success' | 'error' | 'warning' | 'info'
    })

    const searchForm = ref({
      project_name: '',
      client_name: '',
      plan_start_date: '',
      plan_end_date: ''
    })

    const projectList = ref<ProjectInfo[]>([])
    const personnelList = ref<Personnel[]>([])

    const formData = ref({
      project_name: '',
      project_id: '',
      repair_id: '',
      client_name: '',
      plan_start_date: '',
      plan_end_date: '',
      maintenance_personnel: '',
      status: '未进行',
      remarks: ''
    })

    const repairData = ref<RepairItem[]>([])

    const showToast = (message: string, type: 'success' | 'error' | 'warning' | 'info' = 'success') => {
      toast.message = message
      toast.type = type
      toast.visible = true
    }

    const loadData = async () => {
      loading.value = true
      try {
        console.log('📤 [前端] 请求参数:', {
          page: currentPage.value - 1,
          size: pageSize.value,
          project_name: searchForm.value.project_name || undefined,
          client_name: searchForm.value.client_name || undefined
        })
        
        const response = await temporaryRepairService.getList({
          page: currentPage.value - 1,
          size: pageSize.value,
          project_name: searchForm.value.project_name || undefined,
          client_name: searchForm.value.client_name || undefined
        })
        
        console.log('📥 [前端] 响应数据:', response)
        
        if (response.code === 200) {
          console.log('✅ [前端] 数据加载成功，记录数:', response.data.content.length)
          repairData.value = response.data.content
          totalElements.value = response.data.totalElements
          totalPages.value = response.data.totalPages
          console.log('📋 [前端] 当前列表:', repairData.value)
        } else {
          console.error('❌ [前端] 数据加载失败:', response.message)
          showToast(response.message || '加载数据失败', 'error')
        }
      } catch (error: any) {
        console.error('❌ [前端] 加载数据异常:', error)
        showToast(error.message || '加载数据失败，请检查网络连接', 'error')
      } finally {
        loading.value = false
      }
    }

    const formatDate = (dateStr: string) => {
      if (!dateStr) return '-'
      const date = new Date(dateStr)
      return `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}-${String(date.getDate()).padStart(2, '0')}`
    }

    const handleSearch = () => {
      console.log('Search:', searchForm.value)
      currentPage.value = 1
      loadData()
    }

    const handleReset = () => {
      searchForm.value = {
        project_name: '',
        client_name: '',
        plan_start_date: '',
        plan_end_date: ''
      }
      currentPage.value = 1
      loadData()
    }

    const loadProjects = async () => {
      try {
        const response = await projectInfoService.getAll()
        if (response.code === 200 && response.data) {
          projectList.value = response.data
        }
      } catch (error) {
        console.error('加载项目列表失败:', error)
      }
    }

    const loadPersonnel = async () => {
      try {
        const response = await personnelService.getAll()
        if (response.code === 200 && response.data) {
          personnelList.value = response.data
        }
      } catch (error) {
        console.error('加载人员列表失败:', error)
      }
    }

    const handleProjectChange = () => {
      const selectedProject = projectList.value.find(p => p.project_name === formData.value.project_name)
      if (selectedProject) {
        formData.value.project_id = selectedProject.project_id
        formData.value.client_name = selectedProject.client_name
      }
    }

    onMounted(() => {
      loadProjects()
      loadPersonnel()
      loadData()
    })

    watch([currentPage, pageSize], () => {
      loadData()
    })

    const handleAdd = () => {
      isAddModalOpen.value = true
    }

    const closeAddModal = () => {
      isAddModalOpen.value = false
      resetForm()
    }

    const resetForm = () => {
      formData.value = {
        project_name: '',
        project_id: '',
        repair_id: '',
        client_name: '',
        plan_start_date: '',
        plan_end_date: '',
        maintenance_personnel: '',
        status: '未进行',
        remarks: ''
      }
    }

    const handleSave = async () => {
      console.log('Save:', formData.value)
      saving.value = true
      
      try {
        const response = await temporaryRepairService.create({
          repair_id: formData.value.repair_id,
          project_id: formData.value.project_id,
          project_name: formData.value.project_name,
          plan_start_date: formData.value.plan_start_date,
          plan_end_date: formData.value.plan_end_date,
          client_name: formData.value.client_name,
          maintenance_personnel: formData.value.maintenance_personnel,
          status: formData.value.status,
          remarks: formData.value.remarks
        })
        
        if (response.code === 200) {
          showToast('保存成功', 'success')
          await loadData()
          closeAddModal()
        } else {
          showToast(response.message || '保存失败', 'error')
        }
      } catch (error: any) {
        console.error('保存失败:', error)
        showToast('保存失败，请检查网络连接', 'error')
      } finally {
        saving.value = false
      }
    }

    const handleView = (item: RepairItem) => {
      router.push({
        name: 'TemporaryRepairDetail',
        query: { id: item.id }
      })
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
      saving,
      totalElements,
      totalPages,
      isAddModalOpen,
      toast,
      searchForm,
      formData,
      projectList,
      personnelList,
      repairData,
      formatDate,
      handleSearch,
      handleReset,
      handleProjectChange,
      handleAdd,
      closeAddModal,
      handleSave,
      handleView,
      handleExport,
      handleJump,
      toggleSidebar,
      Toast
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

.action-buttons {
  display: flex;
  gap: 12px;
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

.btn-add {
  background: #4caf50;
  color: #fff;
}

.btn-add:hover {
  background: #45a049;
}

.btn-reset {
  background: #f5f5f5;
  color: #666;
  border: 1px solid #d0d7de;
}

.btn-reset:hover {
  background: #e0e0e0;
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
  min-height: 90px;
  padding: 4px 0;
}

.form-label {
  font-size: 14px;
  font-weight: 500;
  color: #424242;
}

.required {
  color: #D32F2F;
  margin-right: 4px;
}

.form-input {
  padding: 8px 12px;
  border: 1px solid #e0e0e0;
  border-radius: 3px;
  font-size: 14px;
  color: #333;
  background: #fff;
  transition: border-color 0.15s;
}

.form-input:focus {
  outline: none;
  border-color: #1976d2;
  box-shadow: 0 0 0 2px rgba(25, 118, 210, 0.1);
}

.form-input::placeholder {
  color: #999;
}

.form-input-readonly {
  background: #f5f5f5;
  color: #666;
  cursor: not-allowed;
}

.form-input-readonly:focus {
  outline: none;
  border-color: #e0e0e0;
  box-shadow: none;
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

.btn-save {
  background: #1976d2;
  color: #fff;
}

.btn-save:hover:not(:disabled) {
  background: #1565c0;
}

.btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}
</style>
