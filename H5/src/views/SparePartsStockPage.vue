<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { showLoadingToast, closeToast, showSuccessToast, showFailToast } from 'vant'
import api from '../utils/api'
import type { ApiResponse } from '../types'
import { formatDate } from '../config/constants'
import UserSelector from '../components/UserSelector.vue'
import type { User } from '../stores/userStore'

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

interface SimpleUser {
  id: number
  name: string
  role: string
}

const router = useRouter()
const loading = ref(false)
const stockList = ref<InboundRecord[]>([])
const userList = ref<SimpleUser[]>([])

const showInboundPopup = ref(false)
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

/**
 * 获取入库记录
 */
const fetchStockList = async () => {
  loading.value = true
  showLoadingToast({ message: '加载中...', forbidClick: true })
  try {
    const response = await api.get<unknown, ApiResponse<{ items: InboundRecord[], total: number }>>('/spare-parts/inbound-records', {
      params: { page: 0, pageSize: 100 }
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
 * 获取人员列表
 */
const fetchUserList = async () => {
  try {
    const response = await api.get<unknown, ApiResponse<User[]>>('/personnel/all/list')
    if (response.code === 200) {
      userList.value = (response.data || []).filter((user: User) => user.role === 'material_manager')
    }
  } catch (error) {
    console.error('Failed to fetch user list:', error)
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
  if (!inboundForm.value.userName) {
    showFailToast('请选择入库人')
    return
  }

  loading.value = true
  showLoadingToast({ message: '提交中...', forbidClick: true })
  
  try {
    const response = await api.post<unknown, ApiResponse<null>>('/spare-parts/inbound', {
      product_name: inboundForm.value.productName,
      brand: inboundForm.value.brand || null,
      model: inboundForm.value.model || null,
      quantity: inboundForm.value.quantity,
      supplier: inboundForm.value.supplier || null,
      unit: inboundForm.value.unit,
      user_name: inboundForm.value.userName,
      remarks: inboundForm.value.remarks || null
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
        userName: '',
        remarks: ''
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
  router.push('/')
}

const handleUserChanged = () => {
  fetchStockList()
}

onMounted(() => {
  fetchUserList()
  fetchStockList()
})
</script>

<template>
  <div class="spare-parts-stock-page">
    <van-nav-bar 
      title="配品备件入库" 
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
      <van-button type="primary" size="small" @click="showInboundPopup = true">
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
              <span class="stock-name">{{ item.productName }}</span>
              <span class="stock-date">{{ formatDate(item.inboundTime) }}</span>
            </div>
            <div class="card-body">
              <div class="info-row">
                <span class="label">入库单号</span>
                <span class="value">{{ item.inboundNo }}</span>
              </div>
              <div class="info-row">
                <span class="label">品牌</span>
                <span class="value">{{ item.brand || '-' }}</span>
              </div>
              <div class="info-row">
                <span class="label">产品型号</span>
                <span class="value">{{ item.model || '-' }}</span>
              </div>
              <div class="info-row">
                <span class="label">入库数量</span>
                <span class="value">{{ item.quantity }} {{ item.unit }}</span>
              </div>
              <div class="info-row">
                <span class="label">供应商</span>
                <span class="value">{{ item.supplier || '-' }}</span>
              </div>
              <div class="info-row">
                <span class="label">入库人</span>
                <span class="value">{{ item.userName }}</span>
              </div>
              <div class="info-row" v-if="item.remarks">
                <span class="label">备注</span>
                <span class="value">{{ item.remarks }}</span>
              </div>
            </div>
          </div>
        </div>
        <van-empty v-if="!loading && stockList.length === 0" description="暂无入库记录" />
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
            placeholder="请输入产品名称"
            required
          />
          <van-field 
            v-model="inboundForm.brand"
            label="品牌"
            placeholder="请输入品牌"
          />
          <van-field 
            v-model="inboundForm.model"
            label="产品型号"
            placeholder="请输入产品型号"
          />
          <van-field 
            v-model="inboundForm.quantity"
            type="number"
            label="入库数量"
            placeholder="请输入入库数量"
            required
          />
          <van-field 
            v-model="inboundForm.supplier"
            label="供应商"
            placeholder="请输入供应商"
          />
          <van-field 
            v-model="inboundForm.unit"
            label="单位"
            placeholder="请输入单位"
          >
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
            v-model="inboundForm.userName"
            label="入库人"
            placeholder="请选择入库人"
            required
          >
            <template #input>
              <select v-model="inboundForm.userName" class="user-select">
                <option value="">请选择入库人</option>
                <option v-for="user in userList" :key="user.id" :value="user.name">
                  {{ user.name }}
                </option>
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

.stock-date {
  font-size: 12px;
  color: #969799;
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

.unit-select,
.user-select {
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
