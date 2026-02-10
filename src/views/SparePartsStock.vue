<template>
  <div class="spare-parts-stock-container">
    <div class="main-layout">
      <div class="content-area">
        <div class="content-wrapper">
          <div class="header-section">
            <h2 class="page-title">备品备件入库</h2>
            <button @click="showAddModal = true" class="add-button">
              <span class="add-icon">+</span>
              新增备品备件
            </button>
          </div>

          <div class="filter-section">
            <div class="filter-group">
              <label class="filter-label">产品名称</label>
              <input 
                v-model="filters.product" 
                type="text" 
                class="filter-input" 
                placeholder="请输入产品名称"
              />
            </div>
            <div class="filter-group">
              <label class="filter-label">入库人</label>
              <select v-model="filters.user" class="filter-select">
                <option value="">全部</option>
                <option v-for="user in userList" :key="user.id" :value="user.name">
                  {{ user.name }}
                </option>
              </select>
            </div>
            <button @click="handleSearch" class="search-button">
              <span class="search-icon">🔍</span>
              搜索
            </button>
          </div>

          <div class="table-section">
            <table class="data-table">
              <thead>
                <tr>
                  <th>序号</th>
                  <th>入库单号</th>
                  <th>产品名称</th>
                  <th>品牌</th>
                  <th>产品型号</th>
                  <th>入库数量</th>
                  <th>供应商</th>
                  <th>入库人</th>
                  <th>入库时间</th>
                  <th>备注</th>
                </tr>
              </thead>
              <tbody>
                <tr v-if="loading">
                  <td colspan="10" class="loading-cell">
                    <div class="loading-spinner"></div>
                    <span>加载中...</span>
                  </td>
                </tr>
                <tr v-else-if="recordList.length === 0">
                  <td colspan="10" class="empty-cell">暂无数据</td>
                </tr>
                <tr v-else v-for="(item, index) in recordList" :key="item.id">
                  <td>{{ (currentPage - 1) * pageSize + index + 1 }}</td>
                  <td>{{ item.inboundNo }}</td>
                  <td>{{ item.productName }}</td>
                  <td>{{ item.brand }}</td>
                  <td>{{ item.model }}</td>
                  <td>{{ item.quantity }} {{ item.unit }}</td>
                  <td>{{ item.supplier }}</td>
                  <td>{{ item.userName }}</td>
                  <td>{{ item.inboundTime }}</td>
                  <td>{{ item.remarks || '-' }}</td>
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

    <div v-if="showAddModal" class="modal-overlay" @click.self="showAddModal = false">
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <h3>新增备品备件入库</h3>
          <button @click="showAddModal = false" class="modal-close">&times;</button>
        </div>
        <div class="modal-body">
          <div class="form-grid">
            <div class="form-item">
              <label class="form-label">产品名称 <span class="required">*</span></label>
              <input 
                v-model="inboundForm.productName" 
                type="text" 
                class="form-input" 
                placeholder="请输入产品名称"
              />
            </div>
            <div class="form-item">
              <label class="form-label">品牌</label>
              <input 
                v-model="inboundForm.brand" 
                type="text" 
                class="form-input" 
                placeholder="请输入品牌"
              />
            </div>
            <div class="form-item">
              <label class="form-label">产品型号</label>
              <input 
                v-model="inboundForm.model" 
                type="text" 
                class="form-input" 
                placeholder="请输入产品型号"
              />
            </div>
            <div class="form-item">
              <label class="form-label">入库数量 <span class="required">*</span></label>
              <input 
                v-model.number="inboundForm.quantity" 
                type="number" 
                class="form-input" 
                placeholder="请输入入库数量"
                min="1"
              />
            </div>
            <div class="form-item">
              <label class="form-label">供应商</label>
              <input 
                v-model="inboundForm.supplier" 
                type="text" 
                class="form-input" 
                placeholder="请输入供应商"
              />
            </div>
            <div class="form-item">
              <label class="form-label">单位</label>
              <select v-model="inboundForm.unit" class="form-select">
                <option value="件">件</option>
                <option value="个">个</option>
                <option value="套">套</option>
                <option value="箱">箱</option>
                <option value="台">台</option>
              </select>
            </div>
            <div class="form-item">
              <label class="form-label">入库人 <span class="required">*</span></label>
              <select v-model="inboundForm.userName" class="form-select">
                <option value="">请选择入库人</option>
                <option v-for="user in userList" :key="user.id" :value="user.name">
                  {{ user.name }}
                </option>
              </select>
            </div>
            <div class="form-item full-width">
              <label class="form-label">备注</label>
              <textarea 
                v-model="inboundForm.remarks" 
                class="form-textarea" 
                placeholder="请输入备注（可选）"
                rows="3"
              ></textarea>
            </div>
          </div>
        </div>
        <div class="modal-footer">
          <button @click="handleInboundSubmit" class="submit-button" :disabled="submitting">
            {{ submitting ? '提交中...' : '提交入库单' }}
          </button>
          <button @click="handleResetForm" class="reset-button">重置</button>
        </div>
      </div>
    </div>

    <Toast
      :visible="toast.visible"
      :message="toast.message"
      :type="toast.type"
      @update:visible="toast.visible = $event"
    />
  </div>
</template>

<script lang="ts">
import { defineComponent, ref, onMounted, computed, onUnmounted } from 'vue'
import apiClient from '@/utils/api'
import type { ApiResponse, PaginatedResponse, SparePartsStockQueryParams } from '@/types/api'
import Toast from '@/components/Toast.vue'

interface InboundRecord {
  id: number
  inboundNo: string
  productName: string
  brand: string
  model: string
  quantity: number
  supplier: string
  userName: string
  inboundTime: string
  unit: string
  remarks: string
}

interface User {
  id: number
  name: string
  role: string
}

export default defineComponent({
  name: 'SparePartsStock',
  setup() {
    const loading = ref(false)
    const submitting = ref(false)
    const recordList = ref<InboundRecord[]>([])
    const total = ref(0)
    const currentPage = ref(1)
    const pageSize = ref(10)
    const showAddModal = ref(false)
    const inboundForm = ref({
      productName: '',
      brand: '',
      model: '',
      quantity: 1,
      supplier: '',
      unit: '件',
      userName: '',
      remarks: ''
    })
    const filters = ref({
      product: '',
      user: ''
    })
    const userList = ref<User[]>([])

    // Toast state
    const toast = ref({
      visible: false,
      message: '',
      type: 'info' as 'success' | 'error' | 'warning' | 'info'
    })

    // AbortController for request cancellation
    let abortController: AbortController | null = null

    const totalPages = computed(() => {
      return Math.ceil(total.value / pageSize.value)
    })

    const showToast = (message: string, type: 'success' | 'error' | 'warning' | 'info' = 'info') => {
      toast.value = { visible: true, message, type }
    }

    const loadRecords = async () => {
      // Cancel previous request if exists
      if (abortController) {
        abortController.abort()
      }

      // Create new AbortController for this request
      abortController = new AbortController()

      loading.value = true
      try {
        const params: SparePartsStockQueryParams = {
          page: currentPage.value - 1,
          pageSize: pageSize.value
        }
        if (filters.value.product) {
          params.product = filters.value.product
        }
        if (filters.value.user) {
          params.user = filters.value.user
        }
        const response = await apiClient.get<ApiResponse<PaginatedResponse<InboundRecord>>>(
          '/spare-parts/inbound-records',
          { params, signal: abortController.signal }
        ) as unknown as ApiResponse<PaginatedResponse<InboundRecord>>
        if (response && response.code === 200 && response.data) {
          recordList.value = response.data.items || []
          total.value = response.data.total || 0
        }
      } catch (error) {
        // Ignore error if request was aborted
        if (error instanceof Error && error.name === 'AbortError') {
          return
        }
        console.error('加载入库记录失败:', error)
        showToast('加载入库记录失败', 'error')
      } finally {
        loading.value = false
      }
    }

    const loadUsers = async () => {
      try {
        const response = await apiClient.get('/personnel/all/list') as ApiResponse<User[]>
        if (response && response.code === 200 && response.data) {
          userList.value = (response.data || []).filter((user: User) => user && user.role === '材料员')
        }
      } catch (error) {
        console.error('加载人员列表失败:', error)
      }
    }

    const handleInboundSubmit = async () => {
      if (!inboundForm.value.productName) {
        showToast('请输入产品名称', 'warning')
        return
      }
      if (!inboundForm.value.quantity || inboundForm.value.quantity <= 0) {
        showToast('请输入有效的入库数量', 'warning')
        return
      }
      if (!inboundForm.value.userName) {
        showToast('请选择入库人', 'warning')
        return
      }
      submitting.value = true
      try {
        const response = await apiClient.post('/spare-parts/inbound', inboundForm.value) as ApiResponse<any>
        if (response && response.code === 200) {
          showToast('入库单提交成功！', 'success')
          handleResetForm()
          showAddModal.value = false
          loadRecords()
        } else {
          showToast('入库单提交失败：' + (response?.message || '未知错误'), 'error')
        }
      } catch (error) {
        console.error('提交入库单失败:', error)
        showToast('入库单提交失败，请稍后重试', 'error')
      } finally {
        submitting.value = false
      }
    }

    const handleResetForm = () => {
      inboundForm.value = {
        productName: '',
        brand: '',
        model: '',
        quantity: 1,
        supplier: '',
        unit: '件',
        userName: '',
        remarks: ''
      }
    }

    const handleSearch = () => {
      currentPage.value = 1
      loadRecords()
    }

    const handlePageChange = (page: number) => {
      if (page < 1 || page > totalPages.value) {
        return
      }
      currentPage.value = page
      loadRecords()
    }

    const handlePageSizeChange = () => {
      currentPage.value = 1
      loadRecords()
    }

    onMounted(() => {
      loadUsers()
      loadRecords()
    })

    onUnmounted(() => {
      // Clean up pending requests when component unmounts
      if (abortController) {
        abortController.abort()
      }
    })

    return {
      loading,
      submitting,
      recordList,
      total,
      currentPage,
      pageSize,
      totalPages,
      showAddModal,
      inboundForm,
      filters,
      userList,
      toast,
      handleInboundSubmit,
      handleResetForm,
      handleSearch,
      handlePageChange,
      handlePageSizeChange
    }
  }
})
</script>

<style scoped>
.spare-parts-stock-container {
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

.header-section {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.page-title {
  font-size: 24px;
  font-weight: 600;
  color: #333;
  margin: 0;
}

.add-button {
  padding: 12px 24px;
  background: linear-gradient(135deg, #1976d2 0%, #42a5f5 100%);
  color: #fff;
  border: none;
  border-radius: 4px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: transform 0.2s, box-shadow 0.2s;
  display: flex;
  align-items: center;
  gap: 8px;
}

.add-button:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(25, 118, 210, 0.3);
}

.add-icon {
  font-size: 20px;
  font-weight: bold;
}

.filter-section {
  display: flex;
  gap: 16px;
  align-items: flex-end;
  background: #fff;
  padding: 16px;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
}

.filter-group {
  display: flex;
  flex-direction: column;
  gap: 6px;
  flex: 1;
}

.filter-label {
  font-size: 14px;
  color: #333;
  font-weight: 500;
}

.filter-input,
.filter-select {
  padding: 8px 12px;
  border: 1px solid #e0e0e0;
  border-radius: 4px;
  font-size: 14px;
  transition: border-color 0.2s;
}

.filter-input:focus,
.filter-select:focus {
  outline: none;
  border-color: #1976d2;
  box-shadow: 0 0 3px rgba(25, 118, 210, 0.1);
}

.search-button {
  padding: 8px 24px;
  background: linear-gradient(135deg, #1976d2 0%, #42a5f5 100%);
  color: #fff;
  border: none;
  border-radius: 4px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: transform 0.2s, box-shadow 0.2s;
  display: flex;
  align-items: center;
  gap: 8px;
}

.search-button:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(25, 118, 210, 0.3);
}

.search-icon {
  font-size: 16px;
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

.pagination-input:focus {
  outline: none;
  border-color: #1976d2;
}

.pagination-slash {
  color: #666;
}

.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.modal-content {
  background: #fff;
  border-radius: 8px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.2);
  max-width: 800px;
  width: 90%;
  max-height: 90vh;
  overflow-y: auto;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px;
  border-bottom: 1px solid #e0e0e0;
}

.modal-header h3 {
  font-size: 18px;
  font-weight: 600;
  color: #333;
  margin: 0;
}

.modal-close {
  background: none;
  border: none;
  font-size: 24px;
  color: #999;
  cursor: pointer;
  padding: 0;
  transition: color 0.2s;
}

.modal-close:hover {
  color: #333;
}

.modal-body {
  padding: 20px;
}

.form-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
  gap: 16px;
}

.form-item {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.form-item.full-width {
  grid-column: 1 / -1;
}

.form-label {
  font-size: 14px;
  color: #333;
  font-weight: 500;
}

.required {
  color: #f56c6c;
  margin-left: 4px;
}

.form-input,
.form-select,
.form-textarea {
  padding: 8px 12px;
  border: 1px solid #e0e0e0;
  border-radius: 4px;
  font-size: 14px;
  transition: border-color 0.2s;
}

.form-input:focus,
.form-select:focus,
.form-textarea:focus {
  outline: none;
  border-color: #1976d2;
  box-shadow: 0 0 3px rgba(25, 118, 210, 0.1);
}

.form-textarea {
  resize: vertical;
  font-family: inherit;
}

.modal-footer {
  display: flex;
  gap: 12px;
  justify-content: flex-end;
  padding: 20px;
  border-top: 1px solid #e0e0e0;
}

.submit-button {
  padding: 10px 32px;
  background: linear-gradient(135deg, #1976d2 0%, #42a5f5 100%);
  color: #fff;
  border: none;
  border-radius: 4px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: transform 0.2s, box-shadow 0.2s;
}

.submit-button:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(25, 118, 210, 0.3);
}

.submit-button:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.reset-button {
  padding: 10px 32px;
  background: #fff;
  color: #666;
  border: 1px solid #e0e0e0;
  border-radius: 4px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
}

.reset-button:hover {
  background: #f5f7f5;
  border-color: #ccc;
}
</style>
