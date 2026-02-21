<template>
  <div class="spare-parts-issue-container">
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
                    field-key="SparePartsIssue_user"
                    placeholder="请输入运维人员"
                    @input="handleSearch"
                  />
                </div>
                <div class="search-item">
                  <label class="search-label">产品名称：</label>
                  <SearchInput
                    v-model="filters.product"
                    field-key="SparePartsIssue_product"
                    placeholder="请输入产品名称"
                    @input="handleSearch"
                  />
                </div>
                <div class="search-item">
                  <label class="search-label">项目名称：</label>
                  <SearchInput
                    v-model="filters.project"
                    field-key="SparePartsIssue_project"
                    placeholder="请输入项目名称"
                    @input="handleSearch"
                  />
                </div>
              </div>
            </div>
            <div class="action-buttons">
              <button @click="handleAdd" class="btn btn-add">新增领用</button>
            </div>
          </div>

          <div class="table-section">
            <table class="data-table">
              <thead>
                <tr>
                  <th>序号</th>
                  <th>项目编号</th>
                  <th>项目名称</th>
                  <th>产品名称</th>
                  <th>品牌</th>
                  <th>产品型号</th>
                  <th>领用数量</th>
                  <th>运维人员</th>
                  <th>领用时间</th>
                  <th>单位</th>
                </tr>
              </thead>
              <tbody>
                <tr v-if="loading">
                  <td colspan="10" class="loading-cell">
                    <div class="loading-spinner"></div>
                    <span>加载中...</span>
                  </td>
                </tr>
                <tr v-else-if="dataList.length === 0">
                  <td colspan="10" class="empty-cell">暂无数据</td>
                </tr>
                <tr v-else v-for="(item, index) in dataList" :key="item.id" :class="{ 'even-row': index % 2 === 0 }">
                  <td>{{ (currentPage - 1) * pageSize + index + 1 }}</td>
                  <td>{{ item.project_id }}</td>
                  <td>{{ item.project_name }}</td>
                  <td>{{ item.product_name }}</td>
                  <td>{{ item.brand }}</td>
                  <td>{{ item.model }}</td>
                  <td>{{ item.quantity }}</td>
                  <td>{{ item.user_name }}</td>
                  <td>{{ item.issue_time }}</td>
                  <td>{{ item.unit }}</td>
                </tr>
              </tbody>
            </table>

            <div class="pagination-section">
              <div class="pagination-info">
                共 {{ total }} 条记录
              </div>
              <div class="pagination-controls">
                <button class="page-btn page-nav" :disabled="currentPage === 1" @click="handlePageChange(currentPage - 1)">
                  &lt;
                </button>
                <button
                  v-for="page in displayedPages"
                  :key="page"
                  class="page-btn page-num"
                  :class="{ active: page === currentPage }"
                  @click="handlePageChange(page)"
                >
                  {{ page }}
                </button>
                <button class="page-btn page-nav" :disabled="currentPage >= totalPages" @click="handlePageChange(currentPage + 1)">
                  &gt;
                </button>
                <select class="page-select" v-model="pageSize" @change="handlePageSizeChange">
                  <option value="10">10 条 / 页</option>
                  <option value="20">20 条 / 页</option>
                  <option value="50">50 条 / 页</option>
                  <option value="100">100 条 / 页</option>
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
      </div>
    </div>

    <div v-if="showAddModal" class="modal-overlay" @click.self="closeAddModal">
      <div class="modal-content modal-content-large">
        <div class="modal-header">
          <h3>新增备品备件领用</h3>
          <button class="close-btn" @click="closeAddModal">&times;</button>
        </div>
        <div class="modal-body">
          <div class="form-item">
            <label class="form-label">产品名称<span class="required">*</span></label>
            <div class="product-search-wrapper">
              <input
                v-model="productSearchKeyword"
                type="text"
                class="form-input"
                placeholder="输入关键词搜索产品..."
                @input="handleProductSearch"
                @focus="showProductDropdown = true"
              />
              <div v-if="showProductDropdown && filteredStockList.length > 0" class="product-dropdown">
                <div
                  v-for="stock in filteredStockList"
                  :key="stock.id"
                  class="product-option"
                  @click="selectProduct(stock)"
                >
                  <span class="product-name">{{ stock.product_name }}</span>
                  <span class="product-spec">{{ stock.brand || '-' }} / {{ stock.model || '-' }}</span>
                  <span class="product-stock">库存: {{ stock.quantity }}</span>
                </div>
              </div>
              <div v-if="showProductDropdown && productSearchKeyword && filteredStockList.length === 0" class="product-dropdown">
                <div class="product-empty">未找到匹配的产品</div>
              </div>
            </div>
            <div v-if="selectedProduct" class="selected-product-info">
              已选择: {{ selectedProduct.product_name }} ({{ selectedProduct.brand || '无品牌' }} / {{ selectedProduct.model || '无型号' }}) - 库存: {{ selectedProduct.quantity }}
            </div>
          </div>
          <div class="form-item">
            <label class="form-label">领用数量<span class="required">*</span></label>
            <input v-model.number="formData.quantity" type="number" :min="1" class="form-input" placeholder="请输入领用数量" />
          </div>
          <div class="form-item">
            <label class="form-label">运维人员</label>
            <input
              :value="currentUser?.name || ''"
              type="text"
              class="form-input"
              readonly
              disabled
            />
          </div>
          <div class="form-item">
            <label class="form-label">所属项目</label>
            <select v-model="formData.project_id" class="form-select" @change="handleProjectChange">
              <option value="">请选择项目</option>
              <option v-for="project in filteredProjectList" :key="project.project_id" :value="project.project_id">
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
import { defineComponent, ref, onMounted, computed, onUnmounted, watch } from 'vue'
import apiClient from '@/utils/api'
import type { ApiResponse, PaginatedResponse } from '@/types/api'
import { USER_ROLES } from '@/config/constants'
import SearchInput from '@/components/SearchInput.vue'
import { userStore } from '@/stores/userStore'

/**
 * 备品备件领用记录接口
 */
interface SparePartsIssueItem {
  id: number
  project_id: string
  project_name: string
  product_name: string
  brand: string
  model: string
  quantity: number
  user_name: string
  issue_time: string
  unit: string
}

/**
 * 备品备件库存接口
 */
interface SparePartsStock {
  id: number
  product_name: string
  brand: string
  model: string
  quantity: number
  unit: string
}

/**
 * 用户接口
 */
interface User {
  id: number
  name: string
  role: string
}

/**
 * 项目接口
 */
interface Project {
  project_id: string
  project_name: string
}

/**
 * 人员项目关联接口
 */
interface PersonnelProject {
  personnel_id: number
  personnel_name: string
  projects: Project[]
}

export default defineComponent({
  name: 'SparePartsIssue',
  components: {
    SearchInput
  },
  setup() {
    const loading = ref(false)
    const submitting = ref(false)
    const dataList = ref<SparePartsIssueItem[]>([])
    const total = ref(0)
    const currentPage = ref(1)
    const pageSize = ref(10)
    const jumpPage = ref(1)
    const showAddModal = ref(false)

    const filters = ref({
      user: '',
      product: '',
      project: ''
    })

    const formData = ref({
      product_id: '',
      quantity: 1,
      project_id: '',
      remark: '',
      user_id: ''
    })

    const stockList = ref<SparePartsStock[]>([])
    const projectList = ref<Project[]>([])
    const personnelProjects = ref<PersonnelProject[]>([])

    const productSearchKeyword = ref('')
    const showProductDropdown = ref(false)
    const selectedProduct = ref<SparePartsStock | null>(null)

    let abortController: AbortController | null = null
    let productSearchTimer: ReturnType<typeof setTimeout> | null = null

    /**
     * 计算总页数
     */
    const totalPages = computed(() => {
      return Math.ceil(total.value / pageSize.value) || 1
    })

    /**
     * 计算显示的页码列表
     */
    const displayedPages = computed(() => {
      const pages: number[] = []
      const start = Math.max(1, currentPage.value - 2)
      const end = Math.min(totalPages.value, start + 4)
      for (let i = start; i <= end; i++) {
        pages.push(i)
      }
      return pages
    })

    /**
     * 过滤库存列表
     */
    const filteredStockList = computed(() => {
      if (!productSearchKeyword.value) {
        return stockList.value.filter(s => s.quantity > 0)
      }
      const keyword = productSearchKeyword.value.toLowerCase()
      return stockList.value.filter(s =>
        s.quantity > 0 && (
          s.product_name.toLowerCase().includes(keyword) ||
          (s.brand && s.brand.toLowerCase().includes(keyword)) ||
          (s.model && s.model.toLowerCase().includes(keyword))
        )
      )
    })

    /**
     * 过滤项目列表
     */
    const filteredProjectList = computed(() => {
      if (formData.value.user_id) {
        const userProjects = personnelProjects.value.find(
          pp => pp.personnel_id === Number(formData.value.user_id)
        )
        if (userProjects) {
          return userProjects.projects
        }
      }
      return projectList.value
    })

    /**
     * 加载备品备件领用数据
     */
    const loadData = async () => {
      if (abortController) {
        abortController.abort()
      }
      abortController = new AbortController()

      loading.value = true
      try {
        const params: Record<string, any> = {
          page: currentPage.value - 1,
          pageSize: pageSize.value
        }
        if (filters.value.user) params.user = filters.value.user
        if (filters.value.product) params.product = filters.value.product
        if (filters.value.project) params.project = filters.value.project

        const response = await apiClient.get('/spare-parts/usage', {
          params,
          signal: abortController.signal
        }) as unknown as ApiResponse<PaginatedResponse<SparePartsIssueItem>>

        if (response && response.code === 200 && response.data) {
          dataList.value = response.data.items || response.data.content || []
          total.value = response.data.total || response.data.totalElements || 0
        }
      } catch (error) {
        if (error instanceof Error && error.name === 'AbortError') return
        console.error('加载备品备件领用数据失败:', error)
      } finally {
        loading.value = false
      }
    }

    /**
     * 加载库存列表
     */
    const loadStock = async () => {
      try {
        const response = await apiClient.get('/spare-parts/stock', {
          params: { page: 0, pageSize: 500 }
        }) as unknown as ApiResponse<PaginatedResponse<SparePartsStock>>
        if (response && response.code === 200 && response.data) {
          stockList.value = response.data.items || response.data.content || []
        }
      } catch (error) {
        console.error('加载库存列表失败:', error)
      }
    }

    /**
     * 加载项目列表
     */
    const loadProjects = async () => {
      try {
        const response = await apiClient.get('/project-info/all/list') as unknown as ApiResponse<Project[]>
        if (response && response.code === 200 && response.data) {
          projectList.value = response.data || []
        }
      } catch (error) {
        console.error('加载项目列表失败:', error)
      }
    }

    /**
     * 加载人员项目关联
     */
    const loadPersonnelProjects = async () => {
      try {
        const response = await apiClient.get('/repair-tools/personnel-projects') as unknown as ApiResponse<PersonnelProject[]>
        if (response && response.code === 200 && response.data) {
          personnelProjects.value = response.data || []
        }
      } catch (error) {
        console.error('加载人员项目关联失败:', error)
      }
    }

    /**
     * 处理产品搜索
     */
    const handleProductSearch = () => {
      if (productSearchTimer) {
        clearTimeout(productSearchTimer)
      }
      productSearchTimer = setTimeout(() => {
        showProductDropdown.value = true
      }, 300)
    }

    /**
     * 选择产品
     * @param stock 选中的库存项
     */
    const selectProduct = (stock: SparePartsStock) => {
      selectedProduct.value = stock
      formData.value.product_id = String(stock.id)
      if (formData.value.quantity > stock.quantity) {
        formData.value.quantity = stock.quantity
      }
      showProductDropdown.value = false
      productSearchKeyword.value = stock.product_name
    }

    /**
     * 处理项目变更
     */
    const handleProjectChange = async () => {
      if (formData.value.project_id) {
        try {
          const response = await apiClient.get('/repair-tools/personnel-projects', {
            params: { project_id: formData.value.project_id }
          }) as unknown as ApiResponse<User[]>
          if (response && response.code === 200 && response.data && response.data.length > 0) {
            const projectUserIds = response.data.map((u: User) => u.id)
            if (formData.value.user_id && !projectUserIds.includes(Number(formData.value.user_id))) {
              formData.value.user_id = ''
            }
          }
        } catch (error) {
          console.error('加载项目关联人员失败:', error)
        }
      }
    }

    /**
     * 处理搜索
     */
    const handleSearch = () => {
      currentPage.value = 1
      loadData()
    }

    /**
     * 处理新增领用
     */
    const handleAdd = () => {
      formData.value = {
        product_id: '',
        quantity: 1,
        project_id: '',
        remark: '',
        user_id: ''
      }
      productSearchKeyword.value = ''
      selectedProduct.value = null
      showProductDropdown.value = false
      showAddModal.value = true
    }

    /**
     * 关闭新增弹窗
     */
    const closeAddModal = () => {
      showAddModal.value = false
      showProductDropdown.value = false
    }

    /**
     * 处理提交
     */
    const handleSubmit = async () => {
      if (!formData.value.product_id || !formData.value.quantity) {
        alert('请填写必填项')
        return
      }

      submitting.value = true
      try {
        const project = projectList.value.find(p => p.project_id === formData.value.project_id)

        const response = await apiClient.post('/spare-parts/usage', {
          product_name: selectedProduct.value?.product_name,
          brand: selectedProduct.value?.brand,
          model: selectedProduct.value?.model,
          quantity: formData.value.quantity,
          unit: selectedProduct.value?.unit,
          user_name: userStore.getUser()?.name,
          project_id: formData.value.project_id || null,
          project_name: project?.project_name || null,
          remark: formData.value.remark
        }) as unknown as ApiResponse<any>

        if (response && response.code === 200) {
          alert('领用成功')
          closeAddModal()
          loadData()
          loadStock()
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

    /**
     * 处理页码变更
     * @param page 目标页码
     */
    const handlePageChange = (page: number) => {
      if (page < 1 || page > totalPages.value) return
      currentPage.value = page
      loadData()
    }

    /**
     * 处理每页条数变更
     */
    const handlePageSizeChange = () => {
      currentPage.value = 1
      loadData()
    }

    /**
     * 处理跳转页码
     */
    const handleJump = () => {
      const page = parseInt(String(jumpPage.value))
      if (page >= 1 && page <= totalPages.value) {
        handlePageChange(page)
      }
    }

    /**
     * 处理点击外部区域
     * @param event 鼠标事件
     */
    const handleClickOutside = (event: MouseEvent) => {
      const target = event.target as HTMLElement
      if (!target.closest('.product-search-wrapper')) {
        showProductDropdown.value = false
      }
    }

    /**
     * 处理项目信息变更
     */
    const handleProjectInfoChanged = () => {
      loadProjects()
      loadPersonnelProjects()
    }

    /**
     * 处理用户变更
     */
    const handleUserChanged = () => {
      loadData()
    }

    onMounted(() => {
      loadStock()
      loadProjects()
      loadPersonnelProjects()
      loadData()
      window.addEventListener('user-changed', handleUserChanged)
      window.addEventListener('project-info-changed', handleProjectInfoChanged)
      document.addEventListener('click', handleClickOutside)
    })

    onUnmounted(() => {
      if (abortController) abortController.abort()
      if (productSearchTimer) clearTimeout(productSearchTimer)
      window.removeEventListener('user-changed', handleUserChanged)
      window.removeEventListener('project-info-changed', handleProjectInfoChanged)
      document.removeEventListener('click', handleClickOutside)
    })

    return {
      loading,
      submitting,
      dataList,
      total,
      currentPage,
      pageSize,
      totalPages,
      jumpPage,
      displayedPages,
      filters,
      formData,
      stockList,
      projectList,
      personnelProjects,
      showAddModal,
      productSearchKeyword,
      showProductDropdown,
      selectedProduct,
      filteredStockList,
      filteredProjectList,
      currentUser: userStore.readonlyCurrentUser,
      handleSearch,
      handleAdd,
      closeAddModal,
      handleProductSearch,
      selectProduct,
      handleProjectChange,
      handleSubmit,
      handlePageChange,
      handlePageSizeChange,
      handleJump
    }
  }
})
</script>

<style scoped>
.spare-parts-issue-container {
  min-height: 100vh;
  background: #fff;
}

.main-layout {
  display: flex;
  min-height: 100vh;
}

.content-area {
  flex: 1;
  display: flex;
  flex-direction: column;
  background: #fff;
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
  overflow-x: auto;
}

.data-table {
  width: 100%;
  border-collapse: collapse;
  min-width: 1200px;
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
  white-space: nowrap;
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

.modal-content {
  background: #fff;
  border-radius: 8px;
  width: 500px;
  max-width: 90%;
  max-height: 90vh;
  overflow-y: auto;
}

.modal-content-large {
  width: 600px;
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

.product-search-wrapper {
  position: relative;
}

.product-dropdown {
  position: absolute;
  top: 100%;
  left: 0;
  right: 0;
  background: #fff;
  border: 1px solid #e0e0e0;
  border-radius: 4px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  max-height: 200px;
  overflow-y: auto;
  z-index: 100;
}

.product-option {
  padding: 10px 12px;
  cursor: pointer;
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-bottom: 1px solid #f0f0f0;
}

.product-option:last-child {
  border-bottom: none;
}

.product-option:hover {
  background: #f5f7fa;
}

.product-name {
  font-weight: 500;
  color: #333;
}

.product-spec {
  color: #666;
  font-size: 12px;
}

.product-stock {
  color: #1976d2;
  font-size: 12px;
  font-weight: 500;
}

.product-empty {
  padding: 20px;
  text-align: center;
  color: #999;
}

.selected-product-info {
  margin-top: 8px;
  padding: 8px 12px;
  background: #e3f2fd;
  border-radius: 4px;
  font-size: 13px;
  color: #1976d2;
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
  background: #1976d2;
  color: #fff;
}

.confirm-btn:hover:not(:disabled) {
  background: #1565c0;
}

.confirm-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
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

.action-delete {
  color: #f44336;
}

.action-delete:hover {
  color: #d32f2f;
}
</style>
