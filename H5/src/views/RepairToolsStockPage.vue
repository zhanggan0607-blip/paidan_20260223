<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { showLoadingToast, closeToast, showSuccessToast, showFailToast } from 'vant'
import api from '../utils/api'
import type { ApiResponse } from '../types'
import { formatDate } from '../config/constants'
import UserSelector from '../components/UserSelector.vue'
import { authService, type User } from '../services/auth'

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

const router = useRouter()
const currentUser = ref<User | null>(null)
const loading = ref(false)
const stockList = ref<RepairToolsStockItem[]>([])

const showAddPopup = ref(false)
const showRestockPopup = ref(false)
const isEdit = ref(false)

const addForm = ref({
  id: 0,
  tool_name: '',
  category: '',
  specification: '',
  unit: '',
  stock: 0,
  min_stock: 0,
  location: '',
  remark: ''
})

const restockForm = ref({
  id: 0,
  tool_name: '',
  current_stock: 0,
  quantity: 1,
  remark: ''
})

const categoryList = ['电动工具', '手动工具', '测量工具', '焊接工具', '起重工具', '其他']

/**
 * 获取库存列表
 */
const fetchStockList = async () => {
  loading.value = true
  showLoadingToast({ message: '加载中...', forbidClick: true })
  try {
    const response = await api.get<unknown, ApiResponse<{ items: RepairToolsStockItem[], total: number }>>('/repair-tools/stock', {
      params: { page: 0, size: 100 }
    })
    if (response.code === 200) {
      stockList.value = response.data?.items || []
    }
  } catch (error) {
    console.error('Failed to fetch stock list:', error)
  } finally {
    loading.value = false
    closeToast()
  }
}

/**
 * 新增工具
 */
const handleAdd = () => {
  isEdit.value = false
  addForm.value = {
    id: 0,
    tool_name: '',
    category: '',
    specification: '',
    unit: '',
    stock: 0,
    min_stock: 0,
    location: '',
    remark: ''
  }
  showAddPopup.value = true
}

/**
 * 编辑工具
 */
const handleEdit = (item: RepairToolsStockItem) => {
  isEdit.value = true
  addForm.value = {
    id: item.id,
    tool_name: item.tool_name,
    category: item.category,
    specification: item.specification,
    unit: item.unit,
    stock: item.stock,
    min_stock: item.min_stock,
    location: item.location,
    remark: ''
  }
  showAddPopup.value = true
}

/**
 * 提交新增/编辑
 */
const handleSubmitAdd = async () => {
  if (!addForm.value.tool_name || !addForm.value.category || !addForm.value.unit) {
    showFailToast('请填写必填项')
    return
  }

  loading.value = true
  showLoadingToast({ message: '提交中...', forbidClick: true })
  
  try {
    let response
    if (isEdit.value) {
      response = await api.put<unknown, ApiResponse<null>>(`/repair-tools/stock/${addForm.value.id}`, addForm.value)
    } else {
      response = await api.post<unknown, ApiResponse<null>>('/repair-tools/stock', addForm.value)
    }
    
    if (response.code === 200) {
      showSuccessToast(isEdit.value ? '编辑成功' : '新增成功')
      showAddPopup.value = false
      fetchStockList()
    } else {
      showFailToast(response.message || '操作失败')
    }
  } catch (error) {
    console.error('Failed to submit:', error)
    showFailToast('操作失败，请重试')
  } finally {
    loading.value = false
    closeToast()
  }
}

/**
 * 入库
 */
const handleRestock = (item: RepairToolsStockItem) => {
  restockForm.value = {
    id: item.id,
    tool_name: item.tool_name,
    current_stock: item.stock,
    quantity: 1,
    remark: ''
  }
  showRestockPopup.value = true
}

/**
 * 提交入库
 */
const handleSubmitRestock = async () => {
  if (!restockForm.value.quantity || restockForm.value.quantity < 1) {
    showFailToast('请输入有效的入库数量')
    return
  }

  loading.value = true
  showLoadingToast({ message: '提交中...', forbidClick: true })
  
  try {
    const response = await api.post<unknown, ApiResponse<null>>(`/repair-tools/stock/${restockForm.value.id}/restock`, {
      quantity: restockForm.value.quantity,
      remark: restockForm.value.remark
    })
    
    if (response.code === 200) {
      showSuccessToast('入库成功')
      showRestockPopup.value = false
      fetchStockList()
    } else {
      showFailToast(response.message || '入库失败')
    }
  } catch (error) {
    console.error('Failed to restock:', error)
    showFailToast('入库失败，请重试')
  } finally {
    loading.value = false
    closeToast()
  }
}

/**
 * 获取库存样式
 */
const getStockClass = (item: RepairToolsStockItem) => {
  return item.stock <= item.min_stock ? 'stock-low' : 'stock-normal'
}

const handleBack = () => {
  router.push('/')
}

const handleUserChanged = () => {
  fetchStockList()
}

onMounted(() => {
  currentUser.value = authService.getCurrentUser()
  fetchStockList()
})
</script>

<template>
  <div class="repair-tools-stock-page">
    <van-nav-bar 
      title="维修工具库存" 
      fixed 
      placeholder 
      @click-left="handleBack" 
    >
      <template #left>
        <div class="nav-left" @click="handleBack">
          <van-icon name="arrow-left" />
          <span>返回</span>
        </div>
      </template>
      <template #right>
        <UserSelector @userChanged="handleUserChanged" />
      </template>
    </van-nav-bar>
    
    <div class="action-bar">
      <van-button type="primary" size="small" @click="handleAdd">
        新增入库
      </van-button>
    </div>
    
    <van-pull-refresh v-model="loading" @refresh="fetchStockList">
      <van-list :loading="loading" :finished="true">
        <div class="stock-list">
          <div 
            v-for="item in stockList" 
            :key="item.id"
            class="stock-card"
          >
            <div class="card-header">
              <span class="tool-name">{{ item.tool_name }}</span>
              <span :class="['stock-badge', getStockClass(item)]">
                库存: {{ item.stock }}
              </span>
            </div>
            <div class="card-body">
              <div class="info-row">
                <span class="label">工具编号</span>
                <span class="value">{{ item.tool_id }}</span>
              </div>
              <div class="info-row">
                <span class="label">工具分类</span>
                <span class="value">{{ item.category }}</span>
              </div>
              <div class="info-row">
                <span class="label">规格型号</span>
                <span class="value">{{ item.specification || '-' }}</span>
              </div>
              <div class="info-row">
                <span class="label">单位</span>
                <span class="value">{{ item.unit }}</span>
              </div>
              <div class="info-row">
                <span class="label">最低库存</span>
                <span class="value">{{ item.min_stock }}</span>
              </div>
              <div class="info-row">
                <span class="label">存放位置</span>
                <span class="value">{{ item.location || '-' }}</span>
              </div>
              <div class="info-row">
                <span class="label">最后入库</span>
                <span class="value">{{ formatDate(item.last_stock_time) }}</span>
              </div>
            </div>
            <div class="card-footer">
              <van-button size="small" @click="handleEdit(item)">编辑</van-button>
              <van-button type="primary" size="small" @click="handleRestock(item)">入库</van-button>
            </div>
          </div>
        </div>
        <van-empty v-if="!loading && stockList.length === 0" description="暂无工具库存" />
      </van-list>
    </van-pull-refresh>

    <van-popup v-model:show="showAddPopup" position="bottom" round :style="{ height: '80%' }">
      <div class="popup-content">
        <div class="popup-header">
          <span class="popup-title">{{ isEdit ? '编辑工具' : '新增工具入库' }}</span>
          <van-icon name="cross" @click="showAddPopup = false" />
        </div>
        <van-cell-group inset>
          <van-field 
            v-model="addForm.tool_name"
            label="工具名称"
            placeholder="请输入工具名称"
            required
          />
          <van-field 
            v-model="addForm.category"
            label="工具分类"
            placeholder="请选择分类"
            required
          >
            <template #input>
              <select v-model="addForm.category" class="category-select">
                <option value="">请选择分类</option>
                <option v-for="cat in categoryList" :key="cat" :value="cat">{{ cat }}</option>
              </select>
            </template>
          </van-field>
          <van-field 
            v-model="addForm.specification"
            label="规格型号"
            placeholder="请输入规格型号"
          />
          <van-field 
            v-model="addForm.unit"
            label="单位"
            placeholder="如：个、把、台"
            required
          />
          <van-field 
            v-model="addForm.stock"
            type="number"
            label="库存数量"
            placeholder="请输入数量"
            required
          />
          <van-field 
            v-model="addForm.min_stock"
            type="number"
            label="最低库存"
            placeholder="预警阈值"
          />
          <van-field 
            v-model="addForm.location"
            label="存放位置"
            placeholder="如：A区1号柜"
          />
          <van-field 
            v-model="addForm.remark"
            label="备注"
            placeholder="请输入备注"
            type="textarea"
            rows="2"
          />
        </van-cell-group>
        <div class="popup-footer">
          <van-button type="primary" block :loading="loading" @click="handleSubmitAdd">
            确认
          </van-button>
        </div>
      </div>
    </van-popup>

    <van-popup v-model:show="showRestockPopup" position="bottom" round :style="{ height: '50%' }">
      <div class="popup-content">
        <div class="popup-header">
          <span class="popup-title">工具入库</span>
          <van-icon name="cross" @click="showRestockPopup = false" />
        </div>
        <van-cell-group inset>
          <van-field 
            :model-value="restockForm.tool_name"
            label="工具名称"
            disabled
          />
          <van-field 
            :model-value="restockForm.current_stock"
            label="当前库存"
            disabled
          />
          <van-field 
            v-model="restockForm.quantity"
            type="number"
            label="入库数量"
            placeholder="请输入入库数量"
            required
          />
          <van-field 
            v-model="restockForm.remark"
            label="备注"
            placeholder="请输入备注"
            type="textarea"
            rows="2"
          />
        </van-cell-group>
        <div class="popup-footer">
          <van-button type="primary" block :loading="loading" @click="handleSubmitRestock">
            确认入库
          </van-button>
        </div>
      </div>
    </van-popup>
  </div>
</template>

<style scoped>
.repair-tools-stock-page {
  min-height: 100vh;
  background-color: #f5f7fa;
}

.action-bar {
  padding: 12px 16px;
  background: #fff;
  border-bottom: 1px solid #ebedf0;
}

.stock-list {
  padding: 12px;
}

.stock-card {
  background: #fff;
  border-radius: 8px;
  margin-bottom: 12px;
  overflow: hidden;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.08);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 16px;
  background: #f7f8fa;
  border-bottom: 1px solid #ebedf0;
}

.tool-name {
  font-weight: 600;
  color: #323233;
}

.stock-badge {
  padding: 4px 12px;
  border-radius: 12px;
  font-size: 12px;
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

.card-body {
  padding: 12px 16px;
}

.info-row {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  padding: 6px 0;
  font-size: 13px;
}

.info-row .label {
  color: #969799;
  flex-shrink: 0;
  width: 70px;
}

.info-row .value {
  color: #323233;
  text-align: right;
  flex: 1;
  margin-left: 12px;
  word-break: break-all;
}

.card-footer {
  display: flex;
  justify-content: flex-end;
  gap: 8px;
  padding: 12px 16px;
  border-top: 1px solid #ebedf0;
}

.nav-left {
  display: flex;
  align-items: center;
  gap: 4px;
  color: #323233;
}

.popup-content {
  height: 100%;
  display: flex;
  flex-direction: column;
}

.popup-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px;
  border-bottom: 1px solid #ebedf0;
}

.popup-title {
  font-size: 16px;
  font-weight: 500;
}

.popup-footer {
  padding: 16px;
  margin-top: auto;
}

.category-select {
  width: 100%;
  padding: 8px 0;
  border: none;
  font-size: 14px;
  background: transparent;
}

:deep(.van-cell-group--inset) {
  margin: 12px;
}
</style>
