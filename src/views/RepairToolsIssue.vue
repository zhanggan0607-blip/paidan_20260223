<template>
  <div class="repair-tools-issue-container">
    <div class="main-layout">
      <div class="content-area">
        <div class="content-wrapper">
          <div class="filter-section">
            <div class="filter-item">
              <label class="filter-label">领用人员</label>
              <select v-model="filters.user" class="filter-select">
                <option value="">全部</option>
                <option v-for="user in userList" :key="user.id" :value="user.name">
                  {{ user.name }}
                </option>
              </select>
            </div>

            <div class="filter-item">
              <label class="filter-label">工具名称</label>
              <SearchInput
                v-model="filters.toolName"
                field-key="RepairToolsIssue_toolName"
                placeholder="请输入工具名称"
                @input="handleSearch"
              />
            </div>

            <div class="filter-item">
              <label class="filter-label">项目名称</label>
              <select v-model="filters.project" class="filter-select">
                <option value="">全部</option>
                <option v-for="project in projectList" :key="project.id" :value="project.project_name">
                  {{ project.project_name }}
                </option>
              </select>
            </div>

            <button @click="handleSearch" class="search-button">搜索</button>
            <button @click="handleAdd" class="add-button">新增领用</button>
          </div>

          <div class="table-section">
            <table class="data-table">
              <thead>
                <tr>
                  <th>序号</th>
                  <th>工具编号</th>
                  <th>工具名称</th>
                  <th>规格型号</th>
                  <th>领用数量</th>
                  <th>领用人</th>
                  <th>领用时间</th>
                  <th>所属项目</th>
                  <th>状态</th>
                </tr>
              </thead>
              <tbody>
                <tr v-if="loading">
                  <td colspan="9" class="loading-cell">
                    <div class="loading-spinner"></div>
                    <span>加载中...</span>
                  </td>
                </tr>
                <tr v-else-if="dataList.length === 0">
                  <td colspan="9" class="empty-cell">暂无数据</td>
                </tr>
                <tr v-else v-for="(item, index) in dataList" :key="item.id">
                  <td>{{ (currentPage - 1) * pageSize + index + 1 }}</td>
                  <td>{{ item.tool_id }}</td>
                  <td>{{ item.tool_name }}</td>
                  <td>{{ item.specification }}</td>
                  <td>{{ item.quantity }}</td>
                  <td>{{ item.user_name }}</td>
                  <td>{{ item.issue_time }}</td>
                  <td>{{ item.project_name }}</td>
                  <td>
                    <span :class="['status-badge', item.status === '已领用' ? 'status-issued' : 'status-returned']">
                      {{ item.status }}
                    </span>
                  </td>
                </tr>
              </tbody>
            </table>

            <div class="pagination-section">
              <div class="pagination-info">
                共 {{ total }} 条记录，第 {{ currentPage }} / {{ totalPages }} 页
              </div>
              <div class="pagination-controls">
                <button 
                  @click="handlePageChange(currentPage - 1)" 
                  :disabled="currentPage === 1"
                  class="pagination-button"
                >
                  上一页
                </button>
                <span class="pagination-pages">
                  <input 
                    v-model.number="currentPage" 
                    type="number" 
                    :min="1" 
                    :max="totalPages"
                    class="pagination-input"
                  />
                  <span class="pagination-slash">/</span>
                  <span>{{ totalPages }}</span>
                </span>
                <button 
                  @click="handlePageChange(currentPage + 1)" 
                  :disabled="currentPage === totalPages"
                  class="pagination-button"
                >
                  下一页
                </button>
              </div>
              <div class="page-size-selector">
                <span>每页</span>
                <select v-model="pageSize" @change="handlePageSizeChange" class="page-size-select">
                  <option :value="10">10</option>
                  <option :value="20">20</option>
                  <option :value="50">50</option>
                  <option :value="100">100</option>
                </select>
                <span>条</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <div v-if="showAddModal" class="modal-overlay" @click.self="closeAddModal">
      <div class="modal-content">
        <div class="modal-header">
          <h3>新增工具领用</h3>
          <button class="close-btn" @click="closeAddModal">&times;</button>
        </div>
        <div class="modal-body">
          <div class="form-item">
            <label class="form-label">工具名称<span class="required">*</span></label>
            <select v-model="formData.tool_id" class="form-select" @change="handleToolChange">
              <option value="">请选择工具</option>
              <option v-for="tool in toolList" :key="tool.id" :value="tool.id">
                {{ tool.tool_name }} (库存: {{ tool.stock }})
              </option>
            </select>
          </div>
          <div class="form-item">
            <label class="form-label">领用数量<span class="required">*</span></label>
            <input v-model.number="formData.quantity" type="number" :min="1" class="form-input" placeholder="请输入领用数量" />
          </div>
          <div class="form-item">
            <label class="form-label">领用人<span class="required">*</span></label>
            <select v-model="formData.user_id" class="form-select">
              <option value="">请选择领用人</option>
              <option v-for="user in userList" :key="user.id" :value="user.id">
                {{ user.name }}
              </option>
            </select>
          </div>
          <div class="form-item">
            <label class="form-label">所属项目</label>
            <select v-model="formData.project_id" class="form-select">
              <option value="">请选择项目</option>
              <option v-for="project in projectList" :key="project.id" :value="project.id">
                {{ project.project_name }}
              </option>
            </select>
          </div>
          <div class="form-item">
            <label class="form-label">备注</label>
            <textarea v-model="formData.remark" class="form-textarea" placeholder="请输入备注"></textarea>
          </div>
        </div>
        <div class="modal-footer">
          <button class="cancel-btn" @click="closeAddModal">取消</button>
          <button class="confirm-btn" @click="handleSubmit" :disabled="submitting">
            {{ submitting ? '提交中...' : '确认' }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script lang="ts">
import { defineComponent, ref, onMounted, computed, onUnmounted } from 'vue'
import apiClient from '@/utils/api'
import type { ApiResponse, PaginatedResponse } from '@/types/api'
import SearchInput from '@/components/SearchInput.vue'

interface RepairToolsIssueItem {
  id: number
  tool_id: string
  tool_name: string
  specification: string
  quantity: number
  user_name: string
  issue_time: string
  project_name: string
  status: string
}

interface Tool {
  id: number
  tool_name: string
  specification: string
  stock: number
}

interface User {
  id: number
  name: string
  role: string
}

interface Project {
  id: number
  project_name: string
}

export default defineComponent({
  name: 'RepairToolsIssue',
  components: {
    SearchInput
  },
  setup() {
    const loading = ref(false)
    const submitting = ref(false)
    const dataList = ref<RepairToolsIssueItem[]>([])
    const total = ref(0)
    const currentPage = ref(1)
    const pageSize = ref(10)
    const showAddModal = ref(false)

    const filters = ref({
      user: '',
      toolName: '',
      project: ''
    })

    const formData = ref({
      tool_id: '',
      quantity: 1,
      user_id: '',
      project_id: '',
      remark: ''
    })

    const toolList = ref<Tool[]>([])
    const userList = ref<User[]>([])
    const projectList = ref<Project[]>([])

    let abortController: AbortController | null = null

    const totalPages = computed(() => {
      return Math.ceil(total.value / pageSize.value) || 1
    })

    const loadData = async () => {
      if (abortController) {
        abortController.abort()
      }
      abortController = new AbortController()

      loading.value = true
      try {
        const params: Record<string, any> = {
          page: currentPage.value - 1,
          size: pageSize.value
        }
        if (filters.value.user) params.user_name = filters.value.user
        if (filters.value.toolName) params.tool_name = filters.value.toolName
        if (filters.value.project) params.project_name = filters.value.project

        const response = await apiClient.get('/repair-tools/issue', { 
          params, 
          signal: abortController.signal 
        }) as unknown as ApiResponse<PaginatedResponse<RepairToolsIssueItem>>
        
        if (response && response.code === 200 && response.data) {
          dataList.value = response.data.items || response.data.content || []
          total.value = response.data.total || response.data.totalElements || 0
        }
      } catch (error) {
        if (error instanceof Error && error.name === 'AbortError') return
        console.error('加载维修工具领用数据失败:', error)
      } finally {
        loading.value = false
      }
    }

    const loadTools = async () => {
      try {
        const response = await apiClient.get('/repair-tools/stock', { 
          params: { page: 0, size: 100 } 
        }) as unknown as ApiResponse<PaginatedResponse<Tool>>
        if (response && response.code === 200 && response.data) {
          toolList.value = response.data.items || response.data.content || []
        }
      } catch (error) {
        console.error('加载工具列表失败:', error)
      }
    }

    const loadUsers = async () => {
      try {
        const response = await apiClient.get('/personnel/all/list') as unknown as ApiResponse<User[]>
        if (response && response.code === 200 && response.data) {
          userList.value = Array.isArray(response.data) ? response.data : []
        }
      } catch (error) {
        console.error('加载人员列表失败:', error)
      }
    }

    const loadProjects = async () => {
      try {
        const response = await apiClient.get('/project-info', { 
          params: { page: 0, size: 100 } 
        }) as unknown as ApiResponse<{ content: Project[] }>
        if (response && response.code === 200 && response.data) {
          projectList.value = response.data.content || []
        }
      } catch (error) {
        console.error('加载项目列表失败:', error)
      }
    }

    const handleSearch = () => {
      currentPage.value = 1
      loadData()
    }

    const handleAdd = () => {
      formData.value = {
        tool_id: '',
        quantity: 1,
        user_id: '',
        project_id: '',
        remark: ''
      }
      showAddModal.value = true
    }

    const closeAddModal = () => {
      showAddModal.value = false
    }

    const handleToolChange = () => {
      const tool = toolList.value.find(t => t.id === Number(formData.value.tool_id))
      if (tool && formData.value.quantity > tool.stock) {
        formData.value.quantity = tool.stock
      }
    }

    const handleSubmit = async () => {
      if (!formData.value.tool_id || !formData.value.quantity || !formData.value.user_id) {
        alert('请填写必填项')
        return
      }

      submitting.value = true
      try {
        const response = await apiClient.post('/repair-tools/issue', formData.value) as unknown as ApiResponse<any>
        if (response && response.code === 200) {
          alert('领用成功')
          closeAddModal()
          loadData()
          loadTools()
        } else {
          alert(response?.message || '领用失败')
        }
      } catch (error) {
        console.error('提交失败:', error)
        alert('提交失败')
      } finally {
        submitting.value = false
      }
    }

    const handlePageChange = (page: number) => {
      if (page < 1 || page > totalPages.value) return
      currentPage.value = page
      loadData()
    }

    const handlePageSizeChange = () => {
      currentPage.value = 1
      loadData()
    }

    onMounted(() => {
      loadTools()
      loadUsers()
      loadProjects()
      loadData()
    })

    onUnmounted(() => {
      if (abortController) abortController.abort()
    })

    return {
      loading,
      submitting,
      dataList,
      total,
      currentPage,
      pageSize,
      totalPages,
      filters,
      formData,
      toolList,
      userList,
      projectList,
      showAddModal,
      handleSearch,
      handleAdd,
      closeAddModal,
      handleToolChange,
      handleSubmit,
      handlePageChange,
      handlePageSizeChange
    }
  }
})
</script>

<style scoped>
.repair-tools-issue-container {
  min-height: 100vh;
  background: #f8f9fa;
}

.main-layout {
  display: flex;
  min-height: 100vh;
}

.content-area {
  flex: 1;
  display: flex;
  flex-direction: column;
  background: #f8f9fa;
}

.content-wrapper {
  display: flex;
  flex-direction: column;
  gap: 20px;
  padding: 20px;
  flex: 1;
  overflow-y: auto;
}

.filter-section {
  display: flex;
  gap: 16px;
  align-items: flex-end;
  padding: 16px;
  background: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
  flex-wrap: wrap;
}

.filter-item {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.filter-label {
  font-size: 14px;
  color: #333;
  font-weight: 500;
}

.filter-select,
.filter-input {
  padding: 8px 12px;
  border: 1px solid #e0e0e0;
  border-radius: 4px;
  font-size: 14px;
  min-width: 180px;
  transition: border-color 0.2s;
}

.filter-select:focus,
.filter-input:focus {
  outline: none;
  border-color: #1976d2;
  box-shadow: 0 0 0 3px rgba(25, 118, 210, 0.1);
}

.search-button,
.add-button {
  padding: 8px 24px;
  border: none;
  border-radius: 4px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: transform 0.2s, box-shadow 0.2s;
  height: 38px;
}

.search-button {
  background: linear-gradient(135deg, #1976d2 0%, #42a5f5 100%);
  color: #fff;
}

.add-button {
  background: linear-gradient(135deg, #388e3c 0%, #66bb6a 100%);
  color: #fff;
}

.search-button:hover,
.add-button:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(25, 118, 210, 0.3);
}

.table-section {
  background: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
  overflow: hidden;
}

.data-table {
  width: 100%;
  border-collapse: collapse;
}

.data-table thead {
  background: #f5f7fa;
}

.data-table th {
  padding: 12px 16px;
  text-align: left;
  font-weight: 600;
  color: #333;
  border-bottom: 2px solid #e0e0e0;
  white-space: nowrap;
}

.data-table tbody tr {
  border-bottom: 1px solid #e0e0e0;
  transition: background 0.2s;
}

.data-table tbody tr:hover {
  background: #f8f9fa;
}

.data-table td {
  padding: 12px 16px;
  text-align: left;
  color: #555;
  white-space: nowrap;
}

.loading-cell,
.empty-cell {
  padding: 40px 16px;
  text-align: center;
  color: #999;
  font-size: 14px;
}

.loading-spinner {
  width: 24px;
  height: 24px;
  border: 3px solid #f3f3f3;
  border-top: 3px solid #1976d2;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin: 0 auto 12px;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.status-badge {
  padding: 4px 12px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 500;
}

.status-issued {
  background: #fff3e0;
  color: #e65100;
}

.status-returned {
  background: #e8f5e9;
  color: #2e7d32;
}

.pagination-section {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px;
  background: #f5f7fa;
  border-top: 1px solid #e0e0e0;
  flex-wrap: wrap;
  gap: 12px;
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

.pagination-button {
  padding: 6px 16px;
  background: #fff;
  border: 1px solid #e0e0e0;
  border-radius: 4px;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.2s;
}

.pagination-button:hover:not(:disabled) {
  background: #1976d2;
  color: #fff;
}

.pagination-button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.pagination-pages {
  display: flex;
  align-items: center;
  gap: 4px;
}

.pagination-input {
  width: 60px;
  padding: 6px 8px;
  border: 1px solid #e0e0e0;
  border-radius: 4px;
  text-align: center;
  font-size: 14px;
}

.pagination-slash {
  color: #666;
}

.page-size-selector {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
  color: #666;
}

.page-size-select {
  padding: 6px 8px;
  border: 1px solid #e0e0e0;
  border-radius: 4px;
  font-size: 14px;
  cursor: pointer;
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

.modal-content {
  background: #fff;
  border-radius: 8px;
  width: 500px;
  max-width: 90%;
  max-height: 90vh;
  overflow-y: auto;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 20px;
  border-bottom: 1px solid #e0e0e0;
}

.modal-header h3 {
  margin: 0;
  font-size: 18px;
  color: #333;
}

.close-btn {
  background: none;
  border: none;
  font-size: 24px;
  cursor: pointer;
  color: #999;
}

.modal-body {
  padding: 20px;
}

.form-item {
  margin-bottom: 16px;
}

.form-label {
  display: block;
  margin-bottom: 6px;
  font-size: 14px;
  color: #333;
  font-weight: 500;
}

.required {
  color: #f44336;
  margin-left: 2px;
}

.form-select,
.form-input,
.form-textarea {
  width: 100%;
  padding: 10px 12px;
  border: 1px solid #e0e0e0;
  border-radius: 4px;
  font-size: 14px;
  box-sizing: border-box;
}

.form-textarea {
  min-height: 80px;
  resize: vertical;
}

.form-select:focus,
.form-input:focus,
.form-textarea:focus {
  outline: none;
  border-color: #1976d2;
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  padding: 16px 20px;
  border-top: 1px solid #e0e0e0;
}

.cancel-btn,
.confirm-btn {
  padding: 10px 24px;
  border: none;
  border-radius: 4px;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.2s;
}

.cancel-btn {
  background: #f5f5f5;
  color: #666;
}

.cancel-btn:hover {
  background: #e0e0e0;
}

.confirm-btn {
  background: linear-gradient(135deg, #1976d2 0%, #42a5f5 100%);
  color: #fff;
}

.confirm-btn:hover:not(:disabled) {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(25, 118, 210, 0.3);
}

.confirm-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}
</style>
