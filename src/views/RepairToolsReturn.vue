<template>
  <div class="repair-tools-return-container">
    <div class="main-layout">
      <div class="content-area">
        <div class="content-wrapper">
          <div class="search-section">
            <div class="search-form">
              <div class="search-row">
                <div class="search-item">
                  <label
                    for="search_maintenancePersonnel"
                    class="search-label"
                  >运维人员：</label>
                  <SearchInput
                    v-model="filters.user"
                    input-id="search_maintenancePersonnel"
                    field-key="RepairToolsReturn_user"
                    placeholder="请输入运维人员"
                    @input="handleSearch"
                  />
                </div>
                <div class="search-item">
                  <label
                    for="search_toolName"
                    class="search-label"
                  >工具名称：</label>
                  <SearchInput
                    v-model="filters.toolName"
                    input-id="search_toolName"
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
                  <td
                    colspan="11"
                    class="loading-cell"
                  >
                    <div class="loading-spinner" />
                    <span>加载中...</span>
                  </td>
                </tr>
                <tr v-else-if="dataList.length === 0">
                  <td
                    colspan="11"
                    class="empty-cell"
                  >
                    暂无数据
                  </td>
                </tr>
                <tr
                  v-for="(item, index) in dataList"
                  v-else
                  :key="item.id"
                >
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
                    <span
                      :class="[
                        'status-badge',
                        item.status === '已领用' ? 'status-issued' : 'status-returned',
                      ]"
                    >
                      {{ item.status }}
                    </span>
                  </td>
                  <td>
                    <button
                      v-if="getPendingReturn(item) > 0"
                      class="return-button"
                      @click="handleOpenReturn(item)"
                    >
                      归还
                    </button>
                    <span
                      v-else
                      class="no-action"
                    >-</span>
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
                  :disabled="currentPage === 1"
                  class="pagination-button"
                  @click="handlePageChange(currentPage - 1)"
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
                  >
                  <span class="pagination-slash">/</span>
                  <span>{{ totalPages }}</span>
                </span>
                <button
                  :disabled="currentPage === totalPages"
                  class="pagination-button"
                  @click="handlePageChange(currentPage + 1)"
                >
                  下一页
                </button>
              </div>
              <div class="page-size-selector">
                <span>每页</span>
                <select
                  id="pageSize"
                  v-model="pageSize"
                  name="pageSize"
                  class="page-size-select"
                  @change="handlePageSizeChange"
                >
                  <option :value="10">
                    10
                  </option>
                  <option :value="20">
                    20
                  </option>
                  <option :value="50">
                    50
                  </option>
                  <option :value="100">
                    100
                  </option>
                </select>
                <span>条</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <div
      v-if="showReturnModal"
      class="modal-overlay"
      @click.self="closeReturnModal"
    >
      <div class="modal-content">
        <div class="modal-header">
          <h3>归还工具</h3>
          <button
            class="close-btn"
            @click="closeReturnModal"
          >
            &times;
          </button>
        </div>
        <div class="modal-body">
          <div class="form-item">
            <label
              for="toolName"
              class="form-label"
            >工具名称</label>
            <input
              id="toolName"
              name="toolName"
              :value="selectedItem?.tool_name"
              type="text"
              class="form-input"
              readonly
              disabled
            >
          </div>
          <div class="form-item">
            <label
              for="specification"
              class="form-label"
            >规格型号</label>
            <input
              id="specification"
              name="specification"
              :value="selectedItem?.specification || '-'"
              type="text"
              class="form-input"
              readonly
              disabled
            >
          </div>
          <div class="form-item">
            <label
              for="issueQuantity"
              class="form-label"
            >领用数量</label>
            <input
              id="issueQuantity"
              name="issueQuantity"
              :value="selectedItem?.quantity"
              type="number"
              class="form-input"
              readonly
              disabled
            >
          </div>
          <div class="form-item">
            <label
              for="returnedQuantity"
              class="form-label"
            >已归还</label>
            <input
              id="returnedQuantity"
              name="returnedQuantity"
              :value="selectedItem?.return_quantity || 0"
              type="number"
              class="form-input"
              readonly
              disabled
            >
          </div>
          <div class="form-item">
            <label
              for="pendingReturn"
              class="form-label"
            >待归还</label>
            <input
              id="pendingReturn"
              name="pendingReturn"
              :value="getPendingReturn(selectedItem)"
              type="number"
              class="form-input"
              readonly
              disabled
            >
          </div>
          <div class="form-item">
            <label
              for="returnQuantity"
              class="form-label"
            >归还数量<span class="required">*</span></label>
            <input
              id="returnQuantity"
              v-model.number="returnQuantity"
              name="returnQuantity"
              type="number"
              :min="1"
              :max="maxReturnQuantity"
              class="form-input"
              placeholder="请输入归还数量"
            >
          </div>
        </div>
        <div class="modal-footer">
          <button
            class="cancel-btn"
            @click="closeReturnModal"
          >
            取消
          </button>
          <button
            class="confirm-btn"
            :disabled="submitting"
            @click="handleSubmitReturn"
          >
            {{ submitting ? '提交中...' : '确认归还' }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script lang="ts">
import { defineComponent, ref, onMounted, computed, onUnmounted } from 'vue'
import { request } from '@/api/request'
import type { ApiResponse, PaginatedResponse } from '@/types/api'
import { USER_ROLES } from '@/config/constants'
import { SearchInput } from '@sstcp/shared'
import { ElMessage, ElMessageBox } from 'element-plus'

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
    SearchInput,
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
      toolName: '',
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
          size: pageSize.value,
        }
        if (filters.value.user) params.user_name = filters.value.user
        if (filters.value.toolName) params.tool_name = filters.value.toolName

        const response = (await request.get('/repair-tools/issue', {
          params,
          signal: abortController.signal,
        })) as unknown as PaginatedResponse<RepairToolsIssueItem>

        if (response && response.code === 200 && response.data) {
          dataList.value = response.data.items || []
          total.value = response.data.total || 0
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
        const response = (await request.get('/personnel/all/list')) as unknown as ApiResponse<
          User[]
        >
        if (response && response.code === 200 && response.data) {
          userList.value = (Array.isArray(response.data) ? response.data : []).filter(
            (user: User) => user && user.name && user.role === USER_ROLES.EMPLOYEE
          )
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
        ElMessage.warning('请选择要归还的工具')
        return
      }
      if (!returnQuantity.value || returnQuantity.value <= 0) {
        ElMessage.warning('请输入归还数量')
        return
      }
      if (returnQuantity.value > maxReturnQuantity.value) {
        ElMessage.warning('归还数量不能超过待归还数量')
        return
      }

      try {
        await ElMessageBox.confirm(`确认归还 ${selectedItem.value.tool_name} ${returnQuantity.value}件?`, '提示', {
          confirmButtonText: '确定',
          cancelButtonText: '取消',
          type: 'warning',
        })
      } catch {
        return
      }

      submitting.value = true
      try {
        const response = (await request.put(
          `/repair-tools/issue/${selectedItem.value.id}/return`,
          {
            return_quantity: returnQuantity.value,
          }
        )) as unknown as ApiResponse<any>

        if (response && response.code === 200) {
          ElMessage.success('归还成功')
          closeReturnModal()
          loadData()
        } else {
          ElMessage.error(response?.message || '归还失败')
        }
      } catch (error) {
        console.error('归还失败:', error)
        ElMessage.error('归还失败')
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
      handlePageSizeChange,
    }
  },
})
</script>

<style scoped>
.repair-tools-return-container {
  min-height: 100vh;
  background: var(--color-bg-page);
}

.main-layout {
  display: flex;
  min-height: 100vh;
}

.content-area {
  flex: 1;
  display: flex;
  flex-direction: column;
  background: var(--color-bg-page);
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
  background: var(--color-bg-card);
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
  color: var(--color-text-secondary);
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
  color: var(--color-text-primary);
  font-weight: 500;
}

.filter-select,
.filter-input {
  padding: 8px 12px;
  border: 1px solid var(--color-border);
  border-radius: 4px;
  font-size: 14px;
  min-width: 180px;
  transition: border-color 0.2s;
}

.filter-select:focus,
.filter-input:focus {
  outline: none;
  border-color: var(--color-primary);
  box-shadow: 0 0 0 3px rgba(25, 118, 210, 0.1);
}

.return-button {
  padding: 6px 16px;
  border: none;
  border-radius: 4px;
  font-size: 13px;
  font-weight: 500;
  cursor: pointer;
  background: linear-gradient(135deg, var(--color-success) 0%, #66bb6a 100%);
  color: var(--color-bg-card);
  transition:
    transform 0.2s,
    box-shadow 0.2s;
}

.return-button:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(56, 142, 60, 0.3);
}

.no-action {
  color: var(--color-text-placeholder);
}

.table-section {
  background: var(--color-bg-card);
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
  overflow: hidden;
}

.data-table {
  width: 100%;
  border-collapse: collapse;
}

.data-table thead {
  background: var(--color-bg-page);
}

.data-table th {
  padding: 12px 16px;
  text-align: left;
  font-weight: 600;
  color: var(--color-text-primary);
  border-bottom: 2px solid var(--color-border);
  white-space: nowrap;
}

.data-table tbody tr {
  border-bottom: 1px solid var(--color-border);
  transition: background 0.2s;
}

.data-table tbody tr:hover {
  background: var(--color-bg-page);
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
  color: var(--color-text-placeholder);
  font-size: 14px;
}

.loading-spinner {
  width: 24px;
  height: 24px;
  border: 3px solid #f3f3f3;
  border-top: 3px solid var(--color-primary);
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin: 0 auto 12px;
}

@keyframes spin {
  0% {
    transform: rotate(0deg);
  }
  100% {
    transform: rotate(360deg);
  }
}

.status-badge {
  padding: 4px 12px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 500;
}

.status-issued {
  background: var(--color-warning-subtle);
  color: var(--color-warning-dark);
}

.status-returned {
  background: var(--color-success-subtle);
  color: var(--color-success);
}

.pagination-section {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px;
  background: var(--color-bg-page);
  border-top: 1px solid var(--color-border);
  flex-wrap: wrap;
  gap: 12px;
}

.pagination-info {
  font-size: 14px;
  color: var(--color-text-secondary);
}

.pagination-controls {
  display: flex;
  align-items: center;
  gap: 8px;
}

.pagination-button {
  padding: 6px 16px;
  background: var(--color-bg-card);
  border: 1px solid var(--color-border);
  border-radius: 4px;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.2s;
}

.pagination-button:hover:not(:disabled) {
  background: var(--color-primary);
  color: var(--color-bg-card);
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
  border: 1px solid var(--color-border);
  border-radius: 4px;
  text-align: center;
  font-size: 14px;
}

.pagination-slash {
  color: var(--color-text-secondary);
}

.page-size-selector {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
  color: var(--color-text-secondary);
}

.page-size-select {
  padding: 6px 8px;
  border: 1px solid var(--color-border);
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
  background: var(--color-bg-card);
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
  border-bottom: 1px solid var(--color-border);
}

.modal-header h3 {
  margin: 0;
  font-size: 18px;
  color: var(--color-text-primary);
}

.close-btn {
  background: none;
  border: none;
  font-size: 24px;
  cursor: pointer;
  color: var(--color-text-placeholder);
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
  color: var(--color-text-primary);
  font-weight: 500;
}

.required {
  color: var(--color-danger);
  margin-left: 2px;
}

.form-input {
  width: 100%;
  padding: 10px 12px;
  border: 1px solid var(--color-border);
  border-radius: 4px;
  font-size: 14px;
  box-sizing: border-box;
}

.form-input:focus {
  outline: none;
  border-color: var(--color-primary);
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  padding: 16px 20px;
  border-top: 1px solid var(--color-border);
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
  background: var(--color-bg-page);
  color: var(--color-text-secondary);
}

.cancel-btn:hover {
  background: var(--color-border);
}

.confirm-btn {
  background: linear-gradient(135deg, var(--color-success) 0%, #66bb6a 100%);
  color: var(--color-bg-card);
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
