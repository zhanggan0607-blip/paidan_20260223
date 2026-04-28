<template>
  <div class="repair-tools-inbound-container">
    <div class="main-layout">
      <div class="content-area">
        <div class="content-wrapper">
          <div class="search-section">
            <div class="search-form">
              <div class="search-row">
                <div class="search-item">
                  <label for="search_toolName" class="search-label">工具名称：</label>
                  <SearchInput
              input-id="search_toolName"
                    v-model="filters.toolName"
                    field-key="RepairToolsInbound_toolName"
                    placeholder="请输入工具名称"
                    @input="handleSearch"
                  />
                </div>
              </div>
            </div>
            <div class="action-buttons">
              <button
                v-if="canInbound"
                class="btn btn-add"
                @click="handleAdd"
              >
                新增入库
              </button>
            </div>
          </div>

          <div class="table-section">
            <table class="data-table">
              <thead>
                <tr>
                  <th>序号</th>
                  <th>工具编号</th>
                  <th>工具名称</th>
                  <th>工具分类</th>
                  <th>规格型号</th>
                  <th>单位</th>
                  <th>库存数量</th>
                  <th>存放位置</th>
                  <th>最后入库时间</th>
                  <th>操作</th>
                </tr>
              </thead>
              <tbody>
                <tr v-if="loading">
                  <td
                    colspan="10"
                    class="loading-cell"
                  >
                    <div class="loading-spinner" />
                    <span>加载中...</span>
                  </td>
                </tr>
                <tr v-else-if="dataList.length === 0">
                  <td
                    colspan="10"
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
                  <td>{{ item.tool_id }}</td>
                  <td>{{ item.tool_name }}</td>
                  <td>{{ item.category }}</td>
                  <td>{{ item.specification }}</td>
                  <td>{{ item.unit }}</td>
                  <td>
                    <span
                      :class="[
                        'stock-badge',
                        item.stock <= item.min_stock ? 'stock-low' : 'stock-normal',
                      ]"
                    >
                      {{ item.stock }}
                    </span>
                  </td>
                  <td>{{ item.location }}</td>
                  <td>{{ item.last_stock_time }}</td>
                  <td>
                    <button
                      class="action-btn edit-btn"
                      @click="handleEdit(item)"
                    >
                      编辑
                    </button>
                    <button
                      class="action-btn restock-btn"
                      @click="handleRestock(item)"
                    >
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
                  name="pageSize"
                  v-model="pageSize"
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
      v-if="showAddModal"
      class="modal-overlay"
      @click.self="closeAddModal"
    >
      <div class="modal-content">
        <div class="modal-header">
          <h3>{{ isEdit ? '编辑工具' : '新增工具入库' }}</h3>
          <button
            class="close-btn"
            @click="closeAddModal"
          >
            &times;
          </button>
        </div>
        <div class="modal-body">
          <div class="form-item">
            <label for="toolName" class="form-label">工具名称<span class="required">*</span></label>
            <input id="toolName" name="toolName"
              v-model="formData.tool_name"
              type="text"
              class="form-input"
              placeholder="请输入工具名称"
            >
          </div>
          <div class="form-item">
            <label for="toolCategory" class="form-label">工具分类<span class="required">*</span></label>
            <select id="toolCategory" name="toolCategory"
              v-model="formData.category"
              class="form-select"
            >
              <option value="">
                请选择分类
              </option>
              <option value="电动工具">
                电动工具
              </option>
              <option value="手动工具">
                手动工具
              </option>
              <option value="测量工具">
                测量工具
              </option>
              <option value="焊接工具">
                焊接工具
              </option>
              <option value="起重工具">
                起重工具
              </option>
              <option value="其他">
                其他
              </option>
            </select>
          </div>
          <div class="form-item">
            <label for="specification" class="form-label">规格型号</label>
            <input id="specification" name="specification"
              v-model="formData.specification"
              type="text"
              class="form-input"
              placeholder="请输入规格型号"
            >
          </div>
          <div class="form-row">
            <div class="form-item half">
              <label for="unit" class="form-label">单位<span class="required">*</span></label>
              <input id="unit" name="unit"
                v-model="formData.unit"
                type="text"
                class="form-input"
                placeholder="如：个、把、台"
              >
            </div>
            <div class="form-item half">
              <label for="stockQuantity" class="form-label">库存数量<span class="required">*</span></label>
              <input id="stockQuantity" name="stockQuantity"
                v-model.number="formData.stock"
                type="number"
                :min="0"
                class="form-input"
                placeholder="请输入数量"
              >
            </div>
          </div>
          <div class="form-row">
            <div class="form-item half">
              <label for="minStock" class="form-label">最低库存</label>
              <input id="minStock" name="minStock"
                v-model.number="formData.min_stock"
                type="number"
                :min="0"
                class="form-input"
                placeholder="预警阈值"
              >
            </div>
            <div class="form-item half">
              <label for="location" class="form-label">存放位置</label>
              <input id="location" name="location"
                v-model="formData.location"
                type="text"
                class="form-input"
                placeholder="如：A区1号柜"
              >
            </div>
          </div>
          <div class="form-item">
            <label for="remarks" class="form-label">备注</label>
            <textarea id="remarks" name="remarks"
              v-model="formData.remark"
              class="form-textarea"
              placeholder="请输入备注"
            />
          </div>
        </div>
        <div class="modal-footer">
          <button
            class="cancel-btn"
            @click="closeAddModal"
          >
            取消
          </button>
          <button
            class="confirm-btn"
            :disabled="submitting"
            @click="handleSubmit"
          >
            {{ submitting ? '提交中...' : '确认' }}
          </button>
        </div>
      </div>
    </div>

    <div
      v-if="showRestockModal"
      class="modal-overlay"
      @click.self="closeRestockModal"
    >
      <div class="modal-content">
        <div class="modal-header">
          <h3>工具入库</h3>
          <button
            class="close-btn"
            @click="closeRestockModal"
          >
            &times;
          </button>
        </div>
        <div class="modal-body">
          <div class="form-item">
            <label for="toolName" class="form-label">工具名称</label>
            <input id="toolName" name="toolName"
              :value="restockData.tool_name"
              class="form-input"
              disabled
            >
          </div>
          <div class="form-item">
            <label for="currentStock" class="form-label">当前库存</label>
            <input id="currentStock" name="currentStock"
              :value="restockData.current_stock"
              class="form-input"
              disabled
            >
          </div>
          <div class="form-item">
            <label for="inboundQuantity" class="form-label">入库数量<span class="required">*</span></label>
            <input id="inboundQuantity" name="inboundQuantity"
              v-model.number="restockData.quantity"
              type="number"
              :min="1"
              class="form-input"
              placeholder="请输入入库数量"
            >
          </div>
          <div class="form-item">
            <label for="remarks" class="form-label">备注</label>
            <textarea id="remarks" name="remarks"
              v-model="restockData.remark"
              class="form-textarea"
              placeholder="请输入备注"
            />
          </div>
        </div>
        <div class="modal-footer">
          <button
            class="cancel-btn"
            @click="closeRestockModal"
          >
            取消
          </button>
          <button
            class="confirm-btn"
            :disabled="submitting"
            @click="handleRestockSubmit"
          >
            {{ submitting ? '提交中...' : '确认入库' }}
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
import SearchInput from '@/components/SearchInput.vue'
import { userStore } from '@/stores/userStore'
import { ElMessage } from 'element-plus'

interface RepairToolsStockItem {
  id: number
  tool_id: string
  tool_name: string
  category: string
  specification: string
  unit: string
  stock: number
  min_stock: number
  location: string
  last_stock_time: string
}

export default defineComponent({
  name: 'RepairToolsInbound',
  components: {
    SearchInput,
  },
  setup() {
    const loading = ref(false)
    const submitting = ref(false)
    const dataList = ref<RepairToolsStockItem[]>([])
    const total = ref(0)
    const currentPage = ref(1)
    const pageSize = ref(10)
    const showAddModal = ref(false)
    const showRestockModal = ref(false)
    const isEdit = ref(false)

    const filters = ref({
      toolName: '',
    })

    const formData = ref({
      id: 0,
      tool_name: '',
      category: '',
      specification: '',
      unit: '',
      stock: 0,
      min_stock: 0,
      location: '',
      remark: '',
    })

    const restockData = ref({
      id: 0,
      tool_name: '',
      current_stock: 0,
      quantity: 1,
      remark: '',
    })

    const categoryList = ref(['电动工具', '手动工具', '测量工具', '焊接工具', '起重工具', '其他'])

    const canInbound = ref(false)

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
          size: pageSize.value,
        }
        if (filters.value.toolName) params.tool_name = filters.value.toolName

        const response = (await request.get('/repair-tools/stock', {
          params,
          signal: abortController.signal,
        })) as unknown as PaginatedResponse<RepairToolsStockItem>

        if (response && response.code === 200 && response.data) {
          const items = response.data.items || response.data.content || []
          dataList.value = items.sort((a, b) => {
            if (a.stock === 0 && b.stock !== 0) return -1
            if (a.stock !== 0 && b.stock === 0) return 1
            return 0
          })
          total.value = response.data.total || response.data.totalElements || 0
        }
      } catch (error) {
        if (error instanceof Error && error.name === 'AbortError') return
        console.error('加载维修工具库存数据失败:', error)
      } finally {
        loading.value = false
      }
    }

    const handleSearch = () => {
      currentPage.value = 1
      loadData()
    }

    const handleAdd = () => {
      isEdit.value = false
      formData.value = {
        id: 0,
        tool_name: '',
        category: '',
        specification: '',
        unit: '',
        stock: 0,
        min_stock: 0,
        location: '',
        remark: '',
      }
      showAddModal.value = true
    }

    const handleEdit = (item: RepairToolsStockItem) => {
      isEdit.value = true
      formData.value = {
        id: item.id,
        tool_name: item.tool_name,
        category: item.category,
        specification: item.specification,
        unit: item.unit,
        stock: item.stock,
        min_stock: item.min_stock,
        location: item.location,
        remark: '',
      }
      showAddModal.value = true
    }

    const closeAddModal = () => {
      showAddModal.value = false
    }

    const handleSubmit = async () => {
      if (!formData.value.tool_name || !formData.value.category || !formData.value.unit) {
        ElMessage.warning('请填写必填项')
        return
      }

      submitting.value = true
      try {
        let response
        if (isEdit.value) {
          response = (await request.put(
            `/repair-tools/stock/${formData.value.id}`,
            formData.value
          )) as unknown as ApiResponse<any>
        } else {
          response = (await request.post(
            '/repair-tools/stock',
            formData.value
          )) as unknown as ApiResponse<any>
        }

        if (response && response.code === 200) {
          ElMessage.success(isEdit.value ? '编辑成功' : '新增成功')
          closeAddModal()
          loadData()
        } else {
          ElMessage.error(response?.message || '操作失败')
        }
      } catch (error) {
        console.error('提交失败:', error)
        ElMessage.error('提交失败')
      } finally {
        submitting.value = false
      }
    }

    const handleRestock = (item: RepairToolsStockItem) => {
      restockData.value = {
        id: item.id,
        tool_name: item.tool_name,
        current_stock: item.stock,
        quantity: 1,
        remark: '',
      }
      showRestockModal.value = true
    }

    const closeRestockModal = () => {
      showRestockModal.value = false
    }

    const handleRestockSubmit = async () => {
      if (!restockData.value.quantity || restockData.value.quantity < 1) {
        ElMessage.warning('请输入有效的入库数量')
        return
      }

      submitting.value = true
      try {
        const response = (await request.post(
          `/repair-tools/stock/${restockData.value.id}/restock`,
          {
            quantity: restockData.value.quantity,
            remark: restockData.value.remark,
          }
        )) as unknown as ApiResponse<any>

        if (response && response.code === 200) {
          ElMessage.success('入库成功')
          closeRestockModal()
          loadData()
        } else {
          ElMessage.error(response?.message || '入库失败')
        }
      } catch (error) {
        console.error('入库失败:', error)
        ElMessage.error('入库失败')
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
      canInbound.value = userStore.isManager() || userStore.isDepartmentManager()
      loadData()
      window.addEventListener('user-changed', handleUserChanged)
    })

    onUnmounted(() => {
      if (abortController) abortController.abort()
      window.removeEventListener('user-changed', handleUserChanged)
    })

    const handleUserChanged = () => {
      loadData()
    }

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
      restockData,
      categoryList,
      showAddModal,
      showRestockModal,
      isEdit,
      canInbound,
      handleSearch,
      handleAdd,
      handleEdit,
      closeAddModal,
      handleSubmit,
      handleRestock,
      closeRestockModal,
      handleRestockSubmit,
      handlePageChange,
      handlePageSizeChange,
    }
  },
})
</script>

<style scoped>
.repair-tools-inbound-container {
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
  background: var(--color-success);
  color: var(--color-bg-card);
}

.btn-add:hover {
  background: #45a049;
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

.stock-badge {
  padding: 4px 12px;
  border-radius: 12px;
  font-size: 13px;
  font-weight: 600;
}

.stock-normal {
  background: var(--color-success-subtle);
  color: var(--color-success);
}

.stock-low {
  background: var(--color-danger-subtle);
  color: var(--color-danger);
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

.edit-btn {
  background: var(--color-primary-subtle);
  color: var(--color-primary);
}

.edit-btn:hover {
  background: var(--color-primary);
  color: var(--color-bg-card);
}

.restock-btn {
  background: var(--color-success-subtle);
  color: var(--color-success);
}

.restock-btn:hover {
  background: var(--color-success);
  color: var(--color-bg-card);
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
  color: var(--color-text-primary);
  font-weight: 500;
}

.required {
  color: var(--color-danger);
  margin-left: 2px;
}

.form-select,
.form-input,
.form-textarea {
  width: 100%;
  padding: 10px 12px;
  border: 1px solid var(--color-border);
  border-radius: 4px;
  font-size: 14px;
  box-sizing: border-box;
}

.form-input:disabled {
  background: var(--color-bg-page);
  color: var(--color-text-secondary);
}

.form-textarea {
  min-height: 80px;
  resize: vertical;
}

.form-select:focus,
.form-input:focus,
.form-textarea:focus {
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
  background: linear-gradient(135deg, var(--color-primary) 0%, #42a5f5 100%);
  color: var(--color-bg-card);
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
