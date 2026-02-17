<template>
  <div class="inventory-container">
    <div class="main-layout">
      <div class="content-area">
        <div class="content-wrapper">
          <div class="header-section">
            <h2 class="page-title">备品备件库存</h2>
          </div>

          <div class="filter-section">
            <div class="filter-fields">
              <div class="filter-group">
                <label class="filter-label">产品名称</label>
                <SearchInput
                  v-model="filters.product_name"
                  field-key="SparePartsInventory_product_name"
                  placeholder="请输入产品名称"
                  @input="handleSearch"
                />
              </div>
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
                </tr>
              </thead>
              <tbody>
                <tr v-if="loading">
                  <td colspan="8" class="loading-cell">
                    <div class="loading-spinner"></div>
                    <span>加载中...</span>
                  </td>
                </tr>
                <tr v-else-if="stockList.length === 0">
                  <td colspan="8" class="empty-cell">暂无库存数据</td>
                </tr>
                <tr v-else v-for="(item, index) in stockList" :key="item.id">
                  <td>{{ index + 1 }}</td>
                  <td>{{ item.productName }}</td>
                  <td>{{ item.brand || '-' }}</td>
                  <td>{{ item.model || '-' }}</td>
                  <td>{{ item.unit }}</td>
                  <td>
                    <span :class="getStockClass(item.quantity)">{{ item.quantity }}</span>
                  </td>
                  <td>
                    <span :class="getStatusClass(item.status)">{{ item.status || '在库' }}</span>
                  </td>
                  <td>{{ formatDateTime(item.updatedAt) }}</td>
                </tr>
              </tbody>
            </table>

            <div class="summary-section">
              <div class="summary-item">
                <span class="summary-label">产品种类：</span>
                <span class="summary-value">{{ stockList.length }} 种</span>
              </div>
              <div class="summary-item">
                <span class="summary-label">库存总量：</span>
                <span class="summary-value">{{ totalQuantity }} 件</span>
              </div>
            </div>
          </div>
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
import { defineComponent, ref, onMounted, computed } from 'vue'
import apiClient from '@/utils/api'
import Toast from '@/components/Toast.vue'
import SearchInput from '@/components/SearchInput.vue'

interface StockItem {
  id: number
  productName: string
  brand: string
  model: string
  unit: string
  quantity: number
  status: string
  createdAt: string
  updatedAt: string
}

interface ApiResponse {
  code: number
  message: string
  data: {
    items: StockItem[]
    total: number
  }
}

export default defineComponent({
  name: 'SparePartsInventory',
  components: {
    Toast,
    SearchInput
  },
  setup() {
    const loading = ref(false)
    const stockList = ref<StockItem[]>([])
    const filters = ref({
      product_name: ''
    })

    const toast = ref({
      visible: false,
      message: '',
      type: 'info' as 'success' | 'error' | 'warning' | 'info'
    })

    const totalQuantity = computed(() => {
      return stockList.value.reduce((sum, item) => sum + item.quantity, 0)
    })

    const showToast = (message: string, type: 'success' | 'error' | 'warning' | 'info' = 'info') => {
      toast.value = { visible: true, message, type }
    }

    const formatDateTime = (dateStr: string) => {
      if (!dateStr) return '-'
      const date = new Date(dateStr)
      return `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}-${String(date.getDate()).padStart(2, '0')} ${String(date.getHours()).padStart(2, '0')}:${String(date.getMinutes()).padStart(2, '0')}`
    }

    const getStockClass = (quantity: number) => {
      if (quantity <= 0) return 'stock-zero'
      if (quantity < 10) return 'stock-low'
      return 'stock-normal'
    }

    const getStatusClass = (status: string) => {
      switch (status) {
        case '在库':
          return 'status-in-stock'
        case '已使用':
          return 'status-used'
        case '缺货':
          return 'status-out-of-stock'
        default:
          return 'status-in-stock'
      }
    }

    const loadStock = async () => {
      loading.value = true
      try {
        const params: Record<string, string> = {}
        if (filters.value.product_name) {
          params.product_name = filters.value.product_name
        }
        const response = await apiClient.get<ApiResponse>('/spare-parts/stock', { params }) as unknown as ApiResponse
        if (response && response.code === 200 && response.data) {
          stockList.value = response.data.items || []
        }
      } catch (error) {
        console.error('加载库存数据失败:', error)
        showToast('加载库存数据失败', 'error')
      } finally {
        loading.value = false
      }
    }

    const handleSearch = () => {
      loadStock()
    }

    const handleReset = () => {
      filters.value.product_name = ''
      loadStock()
    }

    onMounted(() => {
      loadStock()
      window.addEventListener('user-changed', handleUserChanged)
    })

    const handleUserChanged = () => {
      loadStock()
    }

    return {
      loading,
      stockList,
      filters,
      toast,
      totalQuantity,
      formatDateTime,
      getStockClass,
      getStatusClass,
      handleSearch,
      handleReset
    }
  }
})
</script>

<style scoped>
.inventory-container {
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
  margin-bottom: 10px;
}

.page-title {
  font-size: 24px;
  font-weight: 600;
  color: #333;
  margin: 0;
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

.filter-fields {
  display: flex;
  gap: 16px;
  align-items: flex-end;
  flex: 1;
}

.filter-group {
  display: flex;
  flex-direction: column;
  gap: 6px;
  flex: 1;
  max-width: 300px;
}

.filter-label {
  font-size: 14px;
  color: #333;
  font-weight: 500;
}

.filter-input {
  padding: 8px 12px;
  border: 1px solid #e0e0e0;
  border-radius: 4px;
  font-size: 14px;
  transition: border-color 0.2s;
}

.filter-input:focus {
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
}

.search-button:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(25, 118, 210, 0.3);
}

.reset-button {
  padding: 8px 24px;
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
  background: #f5f5f5;
  border-color: #ccc;
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

.stock-zero {
  color: #f44336;
  font-weight: 600;
}

.stock-low {
  color: #ff9800;
  font-weight: 600;
}

.stock-normal {
  color: #4caf50;
  font-weight: 600;
}

.status-in-stock {
  color: #4caf50;
  font-weight: 500;
}

.status-used {
  color: #ff9800;
  font-weight: 500;
}

.status-out-of-stock {
  color: #f44336;
  font-weight: 500;
}

.summary-section {
  display: flex;
  gap: 32px;
  padding: 16px;
  background: #f5f7fa;
  border-top: 1px solid #e0e0e0;
}

.summary-item {
  display: flex;
  align-items: center;
  gap: 8px;
}

.summary-label {
  font-size: 14px;
  color: #666;
}

.summary-value {
  font-size: 16px;
  font-weight: 600;
  color: #1976d2;
}
</style>
