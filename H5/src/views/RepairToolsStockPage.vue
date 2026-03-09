<script setup lang="ts">
import { ref, onMounted, computed, watch } from 'vue'
import { showLoadingToast, closeToast, showSuccessToast, showFailToast } from 'vant'
import { repairToolsService } from '../services'
import { formatDate } from '@sstcp/shared'
import { useNavigation } from '../composables/useNavigation'
import type { RepairToolsStock } from '../types/models'

const { goBack } = useNavigation()
const loading = ref(false)
const stockList = ref<RepairToolsStock[]>([])

const filterKeyword = ref('')
const filterCategory = ref('')

const existingToolNames = computed(() => {
  const names = new Set<string>()
  stockList.value.forEach((item) => {
    if (item.tool_name) {
      names.add(item.tool_name)
    }
  })
  return Array.from(names).sort()
})

const filteredStockList = computed(() => {
  let result = stockList.value
  if (filterKeyword.value) {
    const keyword = filterKeyword.value.toLowerCase()
    result = result.filter(
      (item) =>
        item.tool_name?.toLowerCase().includes(keyword) ||
        item.tool_id?.toLowerCase().includes(keyword) ||
        item.specification?.toLowerCase().includes(keyword)
    )
  }
  if (filterCategory.value) {
    result = result.filter((item) => item.category === filterCategory.value)
  }
  return result.sort((a, b) => {
    const aStock = a.stock || 0
    const bStock = b.stock || 0
    if (aStock === 0 && bStock !== 0) return -1
    if (aStock !== 0 && bStock === 0) return 1
    return 0
  })
})

const showAddPopup = ref(false)

const addForm = ref({
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

/**
 * 监听工具名称变化，自动填充已有工具的信息
 */
watch(
  () => addForm.value.tool_name,
  (newName) => {
    if (newName && existingToolNames.value.includes(newName)) {
      const existingTool = stockList.value.find((item) => item.tool_name === newName)
      if (existingTool) {
        addForm.value.category = existingTool.category || ''
        addForm.value.specification = existingTool.specification || ''
        addForm.value.unit = existingTool.unit || ''
        addForm.value.min_stock = existingTool.min_stock || 0
        addForm.value.location = existingTool.location || ''
      }
    }
  }
)

const categoryList = ['电动工具', '手动工具', '测量工具', '焊接工具', '起重工具', '其他']

/**
 * 获取库存列表
 */
const fetchStockList = async () => {
  loading.value = true
  showLoadingToast({ message: '加载中...', forbidClick: true })
  try {
    const response = await repairToolsService.getStockList({ page: 0, size: 100 })
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
  addForm.value = {
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
  showAddPopup.value = true
}

/**
 * 提交新增
 */
const handleSubmitAdd = async () => {
  if (!addForm.value.tool_name || !addForm.value.category || !addForm.value.unit) {
    showFailToast('请填写必填项')
    return
  }

  loading.value = true
  showLoadingToast({ message: '提交中...', forbidClick: true })

  try {
    const response = await repairToolsService.createStock(addForm.value)

    if (response.code === 200) {
      showSuccessToast('新增成功')
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
 * 获取库存样式
 */
const getStockClass = (item: RepairToolsStock) => {
  return (item.stock || 0) <= (item.min_stock || 0) ? 'stock-low' : 'stock-normal'
}

const handleBack = () => {
  goBack()
}

onMounted(() => {
  fetchStockList()
})
</script>

<template>
  <div class="repair-tools-stock-page">
    <van-nav-bar fixed placeholder @click-left="handleBack">
      <template #left>
        <div class="nav-left">
          <van-icon name="arrow-left" />
          <span>返回</span>
        </div>
      </template>
    </van-nav-bar>

    <div class="action-bar">
      <van-search
        v-model="filterKeyword"
        placeholder="搜索工具名称/编号/规格"
        shape="round"
        class="search-input"
      />
      <van-field v-model="filterCategory" label="" placeholder="分类筛选" class="category-filter">
        <template #input>
          <select v-model="filterCategory" class="category-select-filter">
            <option value="">全部分类</option>
            <option v-for="cat in categoryList" :key="cat" :value="cat">{{ cat }}</option>
          </select>
        </template>
      </van-field>
      <van-button type="primary" size="small" @click="handleAdd"> 新增入库 </van-button>
    </div>

    <van-pull-refresh v-model="loading" @refresh="fetchStockList">
      <van-list :loading="loading" :finished="true">
        <div class="stock-list">
          <div v-for="item in filteredStockList" :key="item.id" class="stock-card">
            <div class="card-header">
              <span class="tool-name">{{ item.tool_name }}</span>
              <span :class="['stock-badge', getStockClass(item)]"> 库存: {{ item.stock }} </span>
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
          </div>
        </div>
        <van-empty v-if="!loading && filteredStockList.length === 0" description="暂无工具库存" />
      </van-list>
    </van-pull-refresh>

    <van-popup v-model:show="showAddPopup" position="bottom" round :style="{ height: '80%' }">
      <div class="popup-content">
        <div class="popup-header">
          <span class="popup-title">新增工具入库</span>
          <van-icon name="cross" @click="showAddPopup = false" />
        </div>
        <van-cell-group inset>
          <van-field
            v-model="addForm.tool_name"
            label="工具名称"
            placeholder="请输入或选择工具名称"
            required
          >
            <template #input>
              <input
                v-model="addForm.tool_name"
                list="toolNames"
                placeholder="请输入或选择工具名称"
                class="datalist-input"
              />
              <datalist id="toolNames">
                <option v-for="name in existingToolNames" :key="name" :value="name" />
              </datalist>
            </template>
          </van-field>
          <van-field v-model="addForm.category" label="工具分类" placeholder="请选择分类" required>
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
          <van-field v-model="addForm.unit" label="单位" placeholder="如：个、把、台" required />
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
          <van-field v-model="addForm.location" label="存放位置" placeholder="如：A区1号柜" />
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
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.search-input {
  padding: 0 !important;
}

.category-filter {
  padding: 0 !important;
}

.category-select-filter {
  width: 100%;
  padding: 8px 0;
  border: none;
  font-size: 14px;
  background: transparent;
}

.action-buttons {
  display: flex;
  justify-content: flex-end;
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

.datalist-input {
  width: 100%;
  padding: 8px 0;
  border: none;
  font-size: 14px;
  background: transparent;
  outline: none;
}

:deep(.van-cell-group--inset) {
  margin: 12px;
}
</style>
