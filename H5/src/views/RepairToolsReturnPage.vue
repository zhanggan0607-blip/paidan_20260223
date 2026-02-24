<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { showLoadingToast, closeToast, showSuccessToast, showFailToast, showConfirmDialog } from 'vant'
import api from '../utils/api'
import type { ApiResponse } from '../types'
import { formatDate } from '../config/constants'
import UserSelector from '../components/UserSelector.vue'
import { useNavigation } from '../composables/useNavigation'

interface RepairToolsIssueItem {
  id: number
  tool_id: string
  tool_name: string
  specification: string
  quantity: number
  return_quantity: number
  user_name: string
  issue_time: string
  project_name: string
  status: string
  stock_id: number | null
}

const { goBack } = useNavigation()
const loading = ref(false)
const issueList = ref<RepairToolsIssueItem[]>([])

const showReturnPopup = ref(false)
const selectedItem = ref<RepairToolsIssueItem | null>(null)
const returnForm = ref({
  returnQuantity: 1 as number
})

const maxReturnQuantity = computed(() => {
  if (!selectedItem.value) return 1
  return selectedItem.value.quantity - (selectedItem.value.return_quantity || 0)
})

/**
 * 获取待归还的领用记录
 */
const fetchIssueList = async () => {
  loading.value = true
  showLoadingToast({ message: '加载中...', forbidClick: true })
  try {
    const response = await api.get<unknown, ApiResponse<{ items: RepairToolsIssueItem[], total: number }>>('/repair-tools/issue', {
      params: { page: 0, size: 100, status: '待归还' }
    })
    if (response.code === 200) {
      issueList.value = response.data?.items || []
    }
  } catch (error) {
    console.error('Failed to fetch issue list:', error)
  } finally {
    loading.value = false
    closeToast()
  }
}

/**
 * 打开归还弹窗
 */
const handleOpenReturn = (item: RepairToolsIssueItem) => {
  selectedItem.value = item
  returnForm.value.returnQuantity = 1
  showReturnPopup.value = true
}

/**
 * 提交归还
 */
const handleSubmitReturn = async () => {
  if (!selectedItem.value) {
    showFailToast('请选择要归还的工具')
    return
  }
  if (returnForm.value.returnQuantity <= 0) {
    showFailToast('请输入归还数量')
    return
  }
  if (returnForm.value.returnQuantity > maxReturnQuantity.value) {
    showFailToast('归还数量不能超过待归还数量')
    return
  }

  try {
    await showConfirmDialog({
      title: '确认归还',
      message: `确认归还 ${selectedItem.value.tool_name} ${returnForm.value.returnQuantity}件?`
    })
  } catch {
    return
  }

  loading.value = true
  showLoadingToast({ message: '提交中...', forbidClick: true })
  
  try {
    const response = await api.put<unknown, ApiResponse<null>>(`/repair-tools/issue/${selectedItem.value.id}/return`, {
      return_quantity: returnForm.value.returnQuantity
    })
    
    if (response.code === 200) {
      showSuccessToast('归还成功')
      showReturnPopup.value = false
      selectedItem.value = null
      returnForm.value = {
        returnQuantity: 1
      }
      fetchIssueList()
    } else {
      showFailToast(response.message || '归还失败')
    }
  } catch (error) {
    console.error('Failed to submit:', error)
    showFailToast('归还失败，请重试')
  } finally {
    loading.value = false
    closeToast()
  }
}

/**
 * 获取待归还数量
 */
const getPendingReturn = (item: RepairToolsIssueItem | null) => {
  if (!item) return 0
  return item.quantity - (item.return_quantity || 0)
}

const handleBack = () => {
  goBack('/')
}

const handleUserChanged = () => {
  fetchIssueList()
}

onMounted(() => {
  fetchIssueList()
})
</script>

<template>
  <div class="repair-tools-return-page">
    <van-nav-bar 
      title="维修工具归还" 
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
    
    <div class="tips-bar">
      <van-notice-bar 
        left-icon="info-o" 
        background="#fff7cc" 
        color="#ed6a0c"
      >
        以下为待归还的工具，点击"归还"按钮进行归还操作
      </van-notice-bar>
    </div>
    
    <van-pull-refresh v-model="loading" @refresh="fetchIssueList">
      <van-list :loading="loading" :finished="true">
        <div class="issue-list">
          <div 
            v-for="item in issueList" 
            :key="item.id"
            class="issue-card"
          >
            <div class="card-header">
              <span class="tool-name">{{ item.tool_name }}</span>
              <span class="status-badge status-pending">
                待归还 {{ getPendingReturn(item) }} 件
              </span>
            </div>
            <div class="card-body">
              <div class="info-row">
                <span class="label">工具编号</span>
                <span class="value">{{ item.tool_id || '-' }}</span>
              </div>
              <div class="info-row">
                <span class="label">规格型号</span>
                <span class="value">{{ item.specification || '-' }}</span>
              </div>
              <div class="info-row">
                <span class="label">领用数量</span>
                <span class="value">{{ item.quantity }} 件</span>
              </div>
              <div class="info-row">
                <span class="label">已归还</span>
                <span class="value returned">{{ item.return_quantity || 0 }} 件</span>
              </div>
              <div class="info-row">
                <span class="label">运维人员</span>
                <span class="value">{{ item.user_name }}</span>
              </div>
              <div class="info-row">
                <span class="label">领用时间</span>
                <span class="value">{{ formatDate(item.issue_time) }}</span>
              </div>
              <div class="info-row">
                <span class="label">所属项目</span>
                <span class="value">{{ item.project_name || '-' }}</span>
              </div>
            </div>
            <div class="card-footer">
              <van-button 
                type="primary" 
                size="small"
                @click="handleOpenReturn(item)"
              >
                归还
              </van-button>
            </div>
          </div>
        </div>
        <van-empty v-if="!loading && issueList.length === 0" description="暂无待归还工具" />
      </van-list>
    </van-pull-refresh>

    <van-popup v-model:show="showReturnPopup" position="bottom" round :style="{ height: '50%' }">
      <div class="popup-content">
        <div class="popup-header">
          <span class="popup-title">归还工具</span>
          <van-icon name="cross" @click="showReturnPopup = false" />
        </div>
        
        <div class="popup-body">
          <van-cell-group inset>
            <van-field 
              :model-value="selectedItem?.tool_name || ''"
              label="工具名称"
              readonly
            />
            <van-field 
              :model-value="selectedItem?.specification || '-'"
              label="规格型号"
              readonly
            />
            <van-field 
              :model-value="selectedItem?.quantity || 0"
              label="领用数量"
              readonly
            />
            <van-field 
              :model-value="selectedItem?.return_quantity || 0"
              label="已归还"
              readonly
            />
            <van-field 
              :model-value="getPendingReturn(selectedItem)"
              label="待归还"
              readonly
            />
            <van-field label="归还数量" required>
              <template #input>
                <van-stepper 
                  v-model="returnForm.returnQuantity" 
                  :min="1" 
                  :max="maxReturnQuantity"
                  theme="round"
                  button-size="22"
                />
              </template>
            </van-field>
          </van-cell-group>
        </div>
        
        <div class="popup-footer">
          <van-button type="primary" block :loading="loading" @click="handleSubmitReturn">
            确认归还
          </van-button>
        </div>
      </div>
    </van-popup>
  </div>
</template>

<style scoped>
.repair-tools-return-page {
  min-height: 100vh;
  background-color: #f5f7fa;
}

.tips-bar {
  background: #fff;
}

.issue-list {
  padding: 12px;
}

.issue-card {
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

.status-badge {
  padding: 4px 12px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 500;
}

.status-pending {
  background: #fff3e0;
  color: #e65100;
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

.info-row .value.returned {
  color: #07c160;
  font-weight: 500;
}

.card-footer {
  display: flex;
  justify-content: flex-end;
  gap: 8px;
  padding: 12px 16px;
  border-top: 1px solid #ebedf0;
}

.card-footer .van-button {
  min-width: 80px;
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
  flex-shrink: 0;
}

.popup-title {
  font-size: 16px;
  font-weight: 500;
}

.popup-body {
  flex: 1;
  overflow-y: auto;
  padding-top: 12px;
}

.popup-footer {
  padding: 16px;
  flex-shrink: 0;
  border-top: 1px solid #ebedf0;
}

:deep(.van-pull-refresh) {
  min-height: calc(100vh - 46px - 40px);
}

:deep(.van-cell-group--inset) {
  margin: 12px;
}
</style>
