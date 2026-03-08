<template>
  <div class="spare-parts-stock-container">
    <div class="main-layout">
      <div class="content-area">
        <div class="content-wrapper">
          <div class="search-section">
            <div class="search-form">
              <div class="search-row">
                <div class="search-item">
                  <label class="search-label">产品名称：</label>
                  <SearchInput
                    v-model="filters.productName"
                    field-key="SparePartsStock_productName"
                    placeholder="请输入产品名称"
                    @input="handleSearch"
                  />
                </div>
              </div>
            </div>
            <div class="action-buttons">
              <button v-if="isMaterialManager" class="btn btn-add" @click="handleAdd">
                新增入库
              </button>
            </div>
          </div>

          <div class="table-section">
            <table class="data-table">
              <thead>
                <tr>
                  <th>序号</th>
                  <th>产品名称</th>
                  <th>品牌</th>
                  <th>产品型号</th>
                  <th>单位</th>
                  <th>库存数量</th>
                  <th>状态</th>
                  <th>更新时间</th>
                  <th>操作</th>
                </tr>
              </thead>
              <tbody>
                <tr v-if="loading">
                  <td colspan="9" class="loading-cell">
                    <div class="loading-spinner"></div>
                    <span>加载中...</span>
                  </td>
                </tr>
                <tr v-else-if="stockList.length === 0">
                  <td colspan="9" class="empty-cell">暂无数据</td>
                </tr>
                <tr v-for="(item, index) in stockList" v-else :key="item.id">
                  <td>{{ (currentPage - 1) * pageSize + index + 1 }}</td>
                  <td>{{ item.productName }}</td>
                  <td>{{ item.brand || '-' }}</td>
                  <td>{{ item.model || '-' }}</td>
                  <td>{{ item.unit }}</td>
                  <td>
                    <span :class="['stock-badge', item.stock <= 0 ? 'stock-low' : 'stock-normal']">
                      {{ item.stock }}
                    </span>
                  </td>
                  <td>{{ item.status || '在库' }}</td>
                  <td>{{ formatTime(item.updatedAt) }}</td>
                  <td>
                    <button class="action-btn restock-btn" @click="handleRestock(item)">
                      入库
                    </button>
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
                  />
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
                <select v-model="pageSize" class="page-size-select" @change="handlePageSizeChange">
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
          <h3>新增备品备件入库</h3>
          <button class="close-btn" @click="closeAddModal">&times;</button>
        </div>
        <div class="modal-body">
          <div class="form-item">
            <label class="form-label">产品名称<span class="required">*</span></label>
            <input
              v-model="formData.productName"
              type="text"
              class="form-input"
              placeholder="请输入产品名称"
            />
          </div>
          <div class="form-row">
            <div class="form-item half">
              <label class="form-label">品牌</label>
              <input
                v-model="formData.brand"
                type="text"
                class="form-input"
                placeholder="请输入品牌"
              />
            </div>
            <div class="form-item half">
              <label class="form-label">产品型号</label>
              <input
                v-model="formData.model"
                type="text"
                class="form-input"
                placeholder="请输入产品型号"
              />
            </div>
          </div>
          <div class="form-row">
            <div class="form-item half">
              <label class="form-label">入库数量<span class="required">*</span></label>
              <input
                v-model.number="formData.quantity"
                type="number"
                class="form-input"
                placeholder="请输入入库数量"
                min="1"
              />
            </div>
            <div class="form-item half">
              <label class="form-label">单位</label>
              <select v-model="formData.unit" class="form-select">
                <option value="件">件</option>
                <option value="个">个</option>
                <option value="套">套</option>
                <option value="箱">箱</option>
                <option value="台">台</option>
              </select>
            </div>
          </div>
          <div class="form-item">
            <label class="form-label">供应商</label>
            <input
              v-model="formData.supplier"
              type="text"
              class="form-input"
              placeholder="请输入供应商"
            />
          </div>
          <div class="form-item">
            <label class="form-label">入库人<span class="required">*</span></label>
            <select v-model="formData.userName" class="form-select">
              <option value="">请选择入库人</option>
              <option v-for="user in userList" :key="user.id" :value="user.name">
                {{ user.name }}
              </option>
            </select>
          </div>
          <div class="form-item">
            <label class="form-label">备注</label>
            <textarea
              v-model="formData.remarks"
              class="form-textarea"
              placeholder="请输入备注（可选）"
            ></textarea>
          </div>
        </div>
        <div class="modal-footer">
          <button class="cancel-btn" @click="closeAddModal">取消</button>
          <button class="confirm-btn" :disabled="submitting" @click="handleSubmit">
            {{ submitting ? '提交中...' : '确认' }}
          </button>
        </div>
      </div>
    </div>

    <div v-if="showRestockModal" class="modal-overlay" @click.self="closeRestockModal">
      <div class="modal-content">
        <div class="modal-header">
          <h3>备品备件入库</h3>
          <button class="close-btn" @click="closeRestockModal">&times;</button>
        </div>
        <div class="modal-body">
          <div class="form-item">
            <label class="form-label">产品名称</label>
            <input :value="restockData.productName" class="form-input" disabled />
          </div>
          <div class="form-row">
            <div class="form-item half">
              <label class="form-label">品牌</label>
              <input :value="restockData.brand || '-'" class="form-input" disabled />
            </div>
            <div class="form-item half">
              <label class="form-label">产品型号</label>
              <input :value="restockData.model || '-'" class="form-input" disabled />
            </div>
          </div>
          <div class="form-item">
            <label class="form-label">当前库存</label>
            <input :value="restockData.currentStock" class="form-input" disabled />
          </div>
          <div class="form-item">
            <label class="form-label">入库数量<span class="required">*</span></label>
            <input
              v-model.number="restockData.quantity"
              type="number"
              :min="1"
              class="form-input"
              placeholder="请输入入库数量"
            />
          </div>
          <div class="form-item">
            <label class="form-label">入库人<span class="required">*</span></label>
            <select v-model="restockData.userName" class="form-select">
              <option value="">请选择入库人</option>
              <option v-for="user in userList" :key="user.id" :value="user.name">
                {{ user.name }}
              </option>
            </select>
          </div>
          <div class="form-item">
            <label class="form-label">备注</label>
            <textarea
              v-model="restockData.remarks"
              class="form-textarea"
              placeholder="请输入备注"
            ></textarea>
          </div>
        </div>
        <div class="modal-footer">
          <button class="cancel-btn" @click="closeRestockModal">取消</button>
          <button class="confirm-btn" :disabled="submitting" @click="handleRestockSubmit">
            {{ submitting ? '提交中...' : '确认入库' }}
          </button>
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
import type { ApiResponse, PaginatedResponse } from '@/types/api'
import Toast from '@/components/Toast.vue'
import SearchInput from '@/components/SearchInput.vue'
import { USER_ROLES } from '@/config/constants'
import { userStore } from '@/stores/userStore'

interface SparePartsStockItem {
  id: number
  productName: string
  brand: string
  model: string
  unit: string
  stock: number
  status: string
  createdAt: string
  updatedAt: string
}

interface User {
  id: number
  name: string
  role: string
}

export default defineComponent({
  name: 'SparePartsStock',
  components: {
    Toast,
    SearchInput,
  },
  setup() {
    const loading = ref(false)
    const submitting = ref(false)
    const stockList = ref<SparePartsStockItem[]>([])
    const total = ref(0)
    const currentPage = ref(1)
    const pageSize = ref(10)
    const showAddModal = ref(false)
    const showRestockModal = ref(false)
    const userList = ref<User[]>([])
    const isMaterialManager = ref(false)

    const filters = ref({
      productName: '',
    })

    const formData = ref({
      productName: '',
      brand: '',
      model: '',
      quantity: 1,
      supplier: '',
      unit: '件',
      userName: '',
      remarks: '',
    })

    const restockData = ref({
      id: 0,
      productName: '',
      brand: '',
      model: '',
      unit: '',
      currentStock: 0,
      quantity: 1,
      userName: '',
      remarks: '',
    })

    const toast = ref({
      visible: false,
      message: '',
      type: 'info' as 'success' | 'error' | 'warning' | 'info',
    })

    let abortController: AbortController | null = null

    const totalPages = computed(() => {
      return Math.ceil(total.value / pageSize.value) || 1
    })

    const showToast = (
      message: string,
      type: 'success' | 'error' | 'warning' | 'info' = 'info'
    ) => {
      toast.value = { visible: true, message, type }
    }

    const formatTime = (time: string | null) => {
      if (!time) return '-'
      try {
        const date = new Date(time)
        return date.toLocaleString('zh-CN', {
          year: 'numeric',
          month: '2-digit',
          day: '2-digit',
          hour: '2-digit',
          minute: '2-digit',
        })
      } catch {
        return time
      }
    }

    const loadStockList = async () => {
      if (abortController) {
        abortController.abort()
      }
      abortController = new AbortController()

      loading.value = true
      try {
        const params: Record<string, any> = {}
        if (filters.value.productName) {
          params.product_name = filters.value.productName
        }
        const response = (await apiClient.get('/spare-parts-stock/stock', {
          params,
          signal: abortController.signal,
        })) as unknown as PaginatedResponse<SparePartsStockItem>

        if (response && response.code === 200 && response.data) {
          stockList.value = response.data.items || []
          total.value = response.data.total || 0
        }
      } catch (error) {
        if (error instanceof Error && error.name === 'AbortError') {
          return
        }
        console.error('加载库存列表失败:', error)
        showToast('加载库存列表失败', 'error')
      } finally {
        loading.value = false
      }
    }

    const loadUsers = async () => {
      try {
        const response = (await apiClient.get('/personnel/all/list')) as ApiResponse<User[]>
        if (response && response.code === 200 && response.data) {
          userList.value = (Array.isArray(response.data) ? response.data : []).filter(
            (user: User) => user && user.role === USER_ROLES.MATERIAL_MANAGER
          )
        }
      } catch (error) {
        console.error('加载人员列表失败:', error)
      }
    }

    const handleAdd = () => {
      formData.value = {
        productName: '',
        brand: '',
        model: '',
        quantity: 1,
        supplier: '',
        unit: '件',
        userName: '',
        remarks: '',
      }
      showAddModal.value = true
    }

    const closeAddModal = () => {
      showAddModal.value = false
    }

    const handleSubmit = async () => {
      if (!formData.value.productName) {
        showToast('请输入产品名称', 'warning')
        return
      }
      if (!formData.value.quantity || formData.value.quantity <= 0) {
        showToast('请输入有效的入库数量', 'warning')
        return
      }
      if (!formData.value.userName) {
        showToast('请选择入库人', 'warning')
        return
      }
      submitting.value = true
      try {
        const requestData = {
          product_name: formData.value.productName,
          brand: formData.value.brand || null,
          model: formData.value.model || null,
          quantity: formData.value.quantity,
          supplier: formData.value.supplier || null,
          unit: formData.value.unit,
          user_name: formData.value.userName || null,
          remarks: formData.value.remarks || null,
        }
        const response = (await apiClient.post(
          '/spare-parts-stock/inbound',
          requestData
        )) as ApiResponse<any>
        if (response && response.code === 200) {
          showToast('入库成功！', 'success')
          closeAddModal()
          loadStockList()
        } else {
          showToast('入库失败：' + (response?.message || '未知错误'), 'error')
        }
      } catch (error) {
        console.error('入库失败:', error)
        showToast('入库失败，请稍后重试', 'error')
      } finally {
        submitting.value = false
      }
    }

    const handleRestock = (item: SparePartsStockItem) => {
      restockData.value = {
        id: item.id,
        productName: item.productName,
        brand: item.brand || '',
        model: item.model || '',
        unit: item.unit || '件',
        currentStock: item.stock,
        quantity: 1,
        userName: '',
        remarks: '',
      }
      showRestockModal.value = true
    }

    const closeRestockModal = () => {
      showRestockModal.value = false
    }

    const handleRestockSubmit = async () => {
      if (!restockData.value.quantity || restockData.value.quantity < 1) {
        showToast('请输入有效的入库数量', 'warning')
        return
      }
      if (!restockData.value.userName) {
        showToast('请选择入库人', 'warning')
        return
      }
      submitting.value = true
      try {
        const requestData = {
          product_name: restockData.value.productName,
          brand: restockData.value.brand || null,
          model: restockData.value.model || null,
          quantity: restockData.value.quantity,
          unit: restockData.value.unit,
          user_name: restockData.value.userName,
          remarks: restockData.value.remarks || null,
        }
        const response = (await apiClient.post(
          '/spare-parts-stock/inbound',
          requestData
        )) as ApiResponse<any>
        if (response && response.code === 200) {
          showToast('入库成功！', 'success')
          closeRestockModal()
          loadStockList()
        } else {
          showToast('入库失败：' + (response?.message || '未知错误'), 'error')
        }
      } catch (error) {
        console.error('入库失败:', error)
        showToast('入库失败', 'error')
      } finally {
        submitting.value = false
      }
    }

    const handleSearch = () => {
      currentPage.value = 1
      loadStockList()
    }

    const handlePageChange = (page: number) => {
      if (page < 1 || page > totalPages.value) {
        return
      }
      currentPage.value = page
      loadStockList()
    }

    const handlePageSizeChange = () => {
      currentPage.value = 1
      loadStockList()
    }

    onMounted(() => {
      isMaterialManager.value = userStore.isMaterialManagerOnly()
      loadUsers()
      loadStockList()
      window.addEventListener('user-changed', handleUserChanged)
    })

    onUnmounted(() => {
      if (abortController) {
        abortController.abort()
      }
      window.removeEventListener('user-changed', handleUserChanged)
    })

    const handleUserChanged = () => {
      loadStockList()
    }

    return {
      loading,
      submitting,
      stockList,
      total,
      currentPage,
      pageSize,
      totalPages,
      showAddModal,
      showRestockModal,
      formData,
      restockData,
      filters,
      userList,
      isMaterialManager,
      toast,
      formatTime,
      handleAdd,
      closeAddModal,
      handleSubmit,
      handleRestock,
      closeRestockModal,
      handleRestockSubmit,
      handleSearch,
      handlePageChange,
      handlePageSizeChange,
    }
  },
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
  0% {
    transform: rotate(0deg);
  }
  100% {
    transform: rotate(360deg);
  }
}

.stock-badge {
  padding: 4px 12px;
  border-radius: 12px;
  font-size: 13px;
  font-weight: 600;
}

.stock-normal {
  background: #e8f5e9;
  color: #2e7d32;
}

.stock-low {
  background: #ffebee;
  color: #c62828;
}

.action-btn {
  padding: 5px 12px;
  border: none;
  border-radius: 4px;
  font-size: 12px;
  cursor: pointer;
  transition: all 0.2s;
  margin-right: 6px;
}

.restock-btn {
  background: #e8f5e9;
  color: #388e3c;
}

.restock-btn:hover {
  background: #388e3c;
  color: #fff;
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
  width: 550px;
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

.form-row {
  display: flex;
  gap: 16px;
}

.form-item.half {
  flex: 1;
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

.form-input:disabled {
  background: #f5f5f5;
  color: #666;
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
