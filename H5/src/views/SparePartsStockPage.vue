<script setup lang="ts">
import { ref, onMounted, computed, watch } from 'vue'
import { showLoadingToast, closeToast, showSuccessToast, showFailToast } from 'vant'
import { sparePartsService } from '../services'
import { useNavigation } from '../composables/useNavigation'
import { userStore } from '../stores/userStore'
import type { SparePartsStock } from '../types/models'

const { goBack } = useNavigation()

const loading = ref(false)
const stockList = ref<SparePartsStock[]>([])

const filterKeyword = ref('')

const currentUser = computed(() => userStore.getUser())

const existingProductNames = computed(() => {
  const names = new Set<string>()
  stockList.value.forEach((item) => {
    if (item.productName) {
      names.add(item.productName)
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
        item.productName?.toLowerCase().includes(keyword) ||
        item.brand?.toLowerCase().includes(keyword) ||
        item.model?.toLowerCase().includes(keyword)
    )
  }
  return result.sort((a, b) => {
    const aStock = a.stock || 0
    const bStock = b.stock || 0
    if (aStock === 0 && bStock !== 0) return -1
    if (aStock !== 0 && bStock === 0) return 1
    return 0
  })
})

const showInboundPopup = ref(false)
const inboundForm = ref({
  productName: '',
  brand: '',
  model: '',
  quantity: 1,
  supplier: '',
  unit: '件',
  remarks: '',
})

/**
 * 监听产品名称变化，自动填充已有产品的信息
 */
watch(
  () => inboundForm.value.productName,
  (newName) => {
    if (newName && existingProductNames.value.includes(newName)) {
      const existingProduct = stockList.value.find((item) => item.productName === newName)
      if (existingProduct) {
        inboundForm.value.brand = existingProduct.brand || ''
        inboundForm.value.model = existingProduct.model || ''
        inboundForm.value.unit = existingProduct.unit || '件'
      }
    }
  }
)

/**
 * 获取当前库存列表
 */
const fetchStockList = async () => {
  loading.value = true
  showLoadingToast({ message: '加载中...', forbidClick: true })
  try {
    const response = await sparePartsService.getStockList({ page: 0, pageSize: 100 })
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
 * 提交入库
 */
const handleSubmitInbound = async () => {
  if (!inboundForm.value.productName) {
    showFailToast('请输入产品名称')
    return
  }
  if (inboundForm.value.quantity <= 0) {
    showFailToast('请输入有效数量')
    return
  }

  loading.value = true
  showLoadingToast({ message: '提交中...', forbidClick: true })

  try {
    const response = await sparePartsService.inbound({
      product_name: inboundForm.value.productName,
      brand: inboundForm.value.brand || undefined,
      model: inboundForm.value.model || undefined,
      quantity: inboundForm.value.quantity,
      supplier: inboundForm.value.supplier || undefined,
      unit: inboundForm.value.unit,
      user_name: currentUser.value?.name || '',
      remarks: inboundForm.value.remarks || undefined,
    })

    if (response.code === 200) {
      showSuccessToast('入库成功')
      showInboundPopup.value = false
      inboundForm.value = {
        productName: '',
        brand: '',
        model: '',
        quantity: 1,
        supplier: '',
        unit: '件',
        remarks: '',
      }
      fetchStockList()
    } else {
      showFailToast(response.message || '入库失败')
    }
  } catch (error) {
    console.error('Failed to submit:', error)
    showFailToast('入库失败，请重试')
  } finally {
    loading.value = false
    closeToast()
  }
}

const handleBack = () => {
  goBack()
}

/**
 * 打开入库弹窗
 */
const openInboundPopup = () => {
  showInboundPopup.value = true
}

/**
 * 获取库存样式
 */
const getStockClass = (item: SparePartsStock) => {
  return (item.stock || 0) <= 0 ? 'stock-low' : 'stock-normal'
}

onMounted(() => {
  fetchStockList()
})
</script>

<template>
  <div class="spare-parts-stock-page">
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
        placeholder="搜索产品名称/品牌/型号"
        shape="round"
        class="search-input"
      />
      <van-button type="primary" size="small" @click="openInboundPopup"> 新增入库 </van-button>
    </div>

    <van-pull-refresh v-model="loading" @refresh="fetchStockList">
      <van-list :loading="loading" :finished="true">
        <div class="stock-list">
          <div v-for="item in filteredStockList" :key="item.id" class="stock-card">
            <div class="card-header">
              <span class="stock-name">{{ item.productName }}</span>
              <span :class="['stock-badge', getStockClass(item)]"
                >库存: {{ item.stock }} {{ item.unit }}</span
              >
            </div>
            <div class="card-body">
              <div class="info-row">
                <span class="label">品牌</span>
                <span class="value">{{ item.brand || '-' }}</span>
              </div>
              <div class="info-row">
                <span class="label">产品型号</span>
                <span class="value">{{ item.model || '-' }}</span>
              </div>
              <div class="info-row">
                <span class="label">状态</span>
                <span class="value">{{ item.status || '在库' }}</span>
              </div>
            </div>
          </div>
        </div>
        <van-empty v-if="!loading && filteredStockList.length === 0" description="暂无库存记录" />
      </van-list>
    </van-pull-refresh>

    <van-popup v-model:show="showInboundPopup" position="bottom" round :style="{ height: '80%' }">
      <div class="popup-content">
        <div class="popup-header">
          <span class="popup-title">新增备品备件库存</span>
          <van-icon name="cross" @click="showInboundPopup = false" />
        </div>
        <van-cell-group inset>
          <van-field
            v-model="inboundForm.productName"
            label="产品名称"
            placeholder="请输入或选择产品名称"
            required
          >
            <template #input>
              <input
                v-model="inboundForm.productName"
                list="productNames"
                placeholder="请输入或选择产品名称"
                class="datalist-input"
              />
              <datalist id="productNames">
                <option v-for="name in existingProductNames" :key="name" :value="name" />
              </datalist>
            </template>
          </van-field>
          <van-field v-model="inboundForm.brand" label="品牌" placeholder="请输入品牌" />
          <van-field v-model="inboundForm.model" label="产品型号" placeholder="请输入产品型号" />
          <van-field
            v-model="inboundForm.quantity"
            type="number"
            label="入库数量"
            placeholder="请输入入库数量"
            required
          />
          <van-field v-model="inboundForm.supplier" label="供应商" placeholder="请输入供应商" />
          <van-field v-model="inboundForm.unit" label="单位" placeholder="请输入单位">
            <template #input>
              <select v-model="inboundForm.unit" class="unit-select">
                <option value="件">件</option>
                <option value="个">个</option>
                <option value="套">套</option>
                <option value="箱">箱</option>
                <option value="台">台</option>
              </select>
            </template>
          </van-field>
          <van-field
            v-model="inboundForm.remarks"
            label="备注"
            placeholder="请输入备注"
            type="textarea"
            rows="2"
          />
        </van-cell-group>
        <div class="popup-footer">
          <van-button type="primary" block :loading="loading" @click="handleSubmitInbound">
            提交入库单
          </van-button>
        </div>
      </div>
    </van-popup>
  </div>
</template>

<style scoped>
.spare-parts-stock-page {
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

.stock-name {
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

.unit-select {
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
