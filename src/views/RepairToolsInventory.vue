<template>
  <div class="repair-tools-inventory-container">
    <div class="main-layout">
      <div class="content-area">
        <div class="content-wrapper">
          <div class="filter-section">
            <div class="filter-item">
              <label class="filter-label">工具名称</label>
              <SearchInput
                v-model="filters.toolName"
                field-key="RepairToolsInventory_toolName"
                placeholder="请输入工具名称"
                @input="handleSearch"
              />
            </div>

            <div class="filter-item">
              <label class="filter-label">工具分类</label>
              <select v-model="filters.category" class="filter-select">
                <option value="">全部</option>
                <option v-for="cat in categoryList" :key="cat" :value="cat">
                  {{ cat }}
                </option>
              </select>
            </div>

            <button @click="handleSearch" class="search-button">搜索</button>
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
                  <th>最后更新时间</th>
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
                  <td>{{ item.category }}</td>
                  <td>{{ item.specification }}</td>
                  <td>{{ item.unit }}</td>
                  <td>
                    <span :class="['stock-badge', item.stock <= item.min_stock ? 'stock-low' : 'stock-normal']">
                      {{ item.stock }}
                    </span>
                  </td>
                  <td>{{ item.location }}</td>
                  <td>{{ item.last_stock_time }}</td>
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
  </div>
</template>

<script lang="ts">
import { defineComponent, ref, onMounted, computed, onUnmounted } from 'vue'
import apiClient from '@/utils/api'
import type { ApiResponse } from '@/types/api'
import SearchInput from '@/components/SearchInput.vue'

interface RepairToolsInventoryItem {
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
  name: 'RepairToolsInventory',
  components: {
    SearchInput
  },
  setup() {
    const loading = ref(false)
    const dataList = ref<RepairToolsInventoryItem[]>([])
    const total = ref(0)
    const currentPage = ref(1)
    const pageSize = ref(10)

    const filters = ref({
      toolName: '',
      category: ''
    })

    const categoryList = ref(['电动工具', '手动工具', '测量工具', '焊接工具', '起重工具', '其他'])

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
        if (filters.value.toolName) params.tool_name = filters.value.toolName
        if (filters.value.category) params.category = filters.value.category

        const response = await apiClient.get('/repair-tools/stock', { 
          params, 
          signal: abortController.signal 
        }) as unknown as ApiResponse<{ items: RepairToolsInventoryItem[], total: number, page: number, size: number }>
        
        if (response && response.code === 200 && response.data) {
          dataList.value = response.data.items || []
          total.value = response.data.total || 0
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
      loadData()
    })

    onUnmounted(() => {
      if (abortController) abortController.abort()
    })

    return {
      loading,
      dataList,
      total,
      currentPage,
      pageSize,
      totalPages,
      filters,
      categoryList,
      handleSearch,
      handlePageChange,
      handlePageSizeChange
    }
  }
})
</script>

<style scoped>
.repair-tools-inventory-container {
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
  height: 38px;
}

.search-button:hover {
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
</style>
