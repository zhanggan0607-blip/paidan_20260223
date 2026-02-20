<template>
  <div class="repair-tools-return-container">
    <div class="main-layout">
      <div class="content-area">
        <div class="content-wrapper">
          <div class="search-section">
            <div class="search-form">
              <div class="search-row">
                <div class="search-item">
                  <label class="search-label">运维人员：</label>
                  <SearchInput
                    v-model="filters.user"
                    field-key="RepairToolsReturn_user"
                    placeholder="请输入运维人员"
                    @input="handleSearch"
                  />
                </div>
                <div class="search-item">
                  <label class="search-label">工具名称：</label>
                  <SearchInput
                    v-model="filters.toolName"
                    field-key="RepairToolsReturn_toolName"
                    placeholder="请输入工具名称"
                    @input="handleSearch"
                  />
                </div>
              </div>
            </div>
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
                  <th>已归还</th>
                  <th>待归还</th>
                  <th>运维人员</th>
                  <th>领用时间</th>
                  <th>状态</th>
                  <th>操作</th>
                </tr>
              </thead>
              <tbody>
                <tr v-if="loading">
                  <td colspan="11" class="loading-cell">
                    <div class="loading-spinner"></div>
                    <span>加载中...</span>
                  </td>
                </tr>
                <tr v-else-if="dataList.length === 0">
                  <td colspan="11" class="empty-cell">暂无数据</td>
                </tr>
                <tr v-else v-for="(item, index) in dataList" :key="item.id">
                  <td>{{ (currentPage - 1) * pageSize + index + 1 }}</td>
                  <td>{{ item.tool_id || '-' }}</td>
                  <td>{{ item.tool_name }}</td>
                  <td>{{ item.specification || '-' }}</td>
                  <td>{{ item.quantity }}</td>
                  <td>{{ item.return_quantity || 0 }}</td>
                  <td>{{ getPendingReturn(item) }}</td>
                  <td>{{ item.user_name }}</td>
                  <td>{{ item.issue_time }}</td>
                  <td>
                    <span :class="['status-badge', item.status === '已领用' ? 'status-issued' : 'status-returned']">
                      {{ item.status }}
                    </span>
                  </td>
                  <td>
                    <button 
                      v-if="getPendingReturn(item) > 0"
                      @click="handleOpenReturn(item)" 
                      class="return-button"
                    >
                      归还
                    </button>
                    <span v-else class="no-action">-</span>
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

    <div v-if="showReturnModal" class="modal-overlay" @click.self="closeReturnModal">
      <div class="modal-content">
        <div class="modal-header">
          <h3>归还工具</h3>
          <button class="close-btn" @click="closeReturnModal">&times;</button>
        </div>
        <div class="modal-body">
          <div class="form-item">
            <label class="form-label">工具名称</label>
            <input :value="selectedItem?.tool_name" type="text" class="form-input" readonly disabled />
          </div>
          <div class="form-item">
            <label class="form-label">规格型号</label>
            <input :value="selectedItem?.specification || '-'" type="text" class="form-input" readonly disabled />
          </div>
          <div class="form-item">
            <label class="form-label">领用数量</label>
            <input :value="selectedItem?.quantity" type="number" class="form-input" readonly disabled />
          </div>
          <div class="form-item">
            <label class="form-label">已归还</label>
            <input :value="selectedItem?.return_quantity || 0" type="number" class="form-input" readonly disabled />
          </div>
          <div class="form-item">
            <label class="form-label">待归还</label>
            <input :value="getPendingReturn(selectedItem)" type="number" class="form-input" readonly disabled />
          </div>
          <div class="form-item">
            <label class="form-label">归还数量<span class="required">*</span></label>
            <input 
              v-model.number="returnQuantity" 
              type="number" 
              :min="1" 
              :max="maxReturnQuantity"
              class="form-input" 
              placeholder="请输入归还数量" 
            />
          </div>
        </div>
        <div class="modal-footer">
          <button class="cancel-btn" @click="closeReturnModal">取消</button>
          <button class="confirm-btn" @click="handleSubmitReturn" :disabled="submitting">
            {{ submitting ? '提交中...' : '确认归还' }}
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
import { USER_ROLES } from '@/config/constants'
import SearchInput from '@/components/SearchInput.vue'

interface RepairToolsIssueItem {
  id: number
  tool_id: string
  tool_name: string
  specification: string
  quantity: number
  return_quantity: number
  user_name: string
  issue_time: string
  project_name: string
  status: string
  stock_id: number | null
}

interface User {
  id: number
  name: string
  role: string
}

export default defineComponent({
  name: 'RepairToolsReturn',
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
    const showReturnModal = ref(false)
    const selectedItem = ref<RepairToolsIssueItem | null>(null)
    const returnQuantity = ref(1)

    const filters = ref({
      user: '',
      toolName: ''
    })

    const userList = ref<User[]>([])

    let abortController: AbortController | null = null

    const totalPages = computed(() => {
      return Math.ceil(total.value / pageSize.value) || 1
    })

    const maxReturnQuantity = computed(() => {
      if (!selectedItem.value) return 1
      return getPendingReturn(selectedItem.value)
    })

    const getPendingReturn = (item: RepairToolsIssueItem | null) => {
      if (!item) return 0
      return item.quantity - (item.return_quantity || 0)
    }

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
        console.error('加载维修工具归还数据失败:', error)
      } finally {
        loading.value = false
      }
    }

    const loadUsers = async () => {
      try {
        const response = await apiClient.get('/personnel/all/list') as unknown as ApiResponse<User[]>
        if (response && response.code === 200 && response.data) {
          userList.value = (Array.isArray(response.data) ? response.data : []).filter((user: User) => user && user.name && user.role === USER_ROLES.EMPLOYEE)
        }
      } catch (error) {
        console.error('加载人员列表失败:', error)
      }
    }

    const handleSearch = () => {
      currentPage.value = 1
      loadData()
    }

    const handleOpenReturn = (item: RepairToolsIssueItem) => {
      selectedItem.value = item
      returnQuantity.value = 1
      showReturnModal.value = true
    }

    const closeReturnModal = () => {
      showReturnModal.value = false
      selectedItem.value = null
      returnQuantity.value = 1
    }

    const handleSubmitReturn = async () => {
      if (!selectedItem.value) {
        alert('请选择要归还的工具')
        return
      }
      if (!returnQuantity.value || returnQuantity.value <= 0) {
        alert('请输入归还数量')
        return
      }
      if (returnQuantity.value > maxReturnQuantity.value) {
        alert('归还数量不能超过待归还数量')
        return
      }

      if (!confirm(`确认归还 ${selectedItem.value.tool_name} ${returnQuantity.value}件?`)) {
        return
      }

      submitting.value = true
      try {
        const response = await apiClient.put(`/repair-tools/issue/${selectedItem.value.id}/return`, {
          return_quantity: returnQuantity.value
        }) as unknown as ApiResponse<any>
        
        if (response && response.code === 200) {
          alert('归还成功')
          closeReturnModal()
          loadData()
        } else {
          alert(response?.message || '归还失败')
        }
      } catch (error) {
        console.error('归还失败:', error)
        alert('归还失败')
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

    const handleUserChanged = () => {
      loadData()
    }

    onMounted(() => {
      loadUsers()
      loadData()
      window.addEventListener('user-changed', handleUserChanged)
    })

    onUnmounted(() => {
      if (abortController) abortController.abort()
      window.removeEventListener('user-changed', handleUserChanged)
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
      userList,
      showReturnModal,
      selectedItem,
      returnQuantity,
      maxReturnQuantity,
      getPendingReturn,
      handleSearch,
      handleOpenReturn,
      closeReturnModal,
      handleSubmitReturn,
      handlePageChange,
      handlePageSizeChange
    }
  }
})
</script>

<style scoped>
.repair-tools-return-container {
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

.search-section {
  display: flex;
  gap: 16px;
  margin-bottom: 20px;
  align-items: flex-start;
  padding: 16px;
  background: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
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

.return-button {
  padding: 6px 16px;
  border: none;
  border-radius: 4px;
  font-size: 13px;
  font-weight: 500;
  cursor: pointer;
  background: linear-gradient(135deg, #388e3c 0%, #66bb6a 100%);
  color: #fff;
  transition: transform 0.2s, box-shadow 0.2s;
}

.return-button:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(56, 142, 60, 0.3);
}

.no-action {
  color: #999;
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

.form-input {
  width: 100%;
  padding: 10px 12px;
  border: 1px solid #e0e0e0;
  border-radius: 4px;
  font-size: 14px;
  box-sizing: border-box;
}

.form-input:focus {
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
  background: linear-gradient(135deg, #388e3c 0%, #66bb6a 100%);
  color: #fff;
}

.confirm-btn:hover:not(:disabled) {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(56, 142, 60, 0.3);
}

.confirm-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}
</style>
