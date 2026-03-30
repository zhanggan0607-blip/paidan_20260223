<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import {
  showLoadingToast,
  closeToast,
  showSuccessToast,
  showFailToast,
  showConfirmDialog,
} from 'vant'
import { sparePartsService, projectInfoService } from '../services'
import { formatDate } from '@sstcp/shared'
import { userStore } from '../stores/userStore'
import { useNavigation } from '../composables/useNavigation'
import type { SparePartsUsage, SparePartsStock, ProjectInfo } from '../types/models'

const { goBack } = useNavigation()
const loading = ref(false)
const issueList = ref<SparePartsUsage[]>([])
const stockList = ref<SparePartsStock[]>([])
const projectList = ref<ProjectInfo[]>([])

const showIssuePopup = ref(false)
const selectedStockId = ref<number | null>(null)
const issueForm = ref({
  projectId: '',
  projectName: '',
  quantity: 1 as number,
})

const filteredStockList = computed(() => {
  return stockList.value.filter((item) => (item.stock || 0) > 0)
})

const selectedStock = computed(() => {
  if (!selectedStockId.value) return null
  return stockList.value.find((item) => item.id === selectedStockId.value) || null
})

const maxQuantity = computed(() => {
  return selectedStock.value?.stock || 1
})

/**
 * 获取领用记录
 */
const fetchIssueList = async () => {
  loading.value = true
  showLoadingToast({ message: '加载中...', forbidClick: true })
  try {
    const response = await sparePartsService.getUsageList({ page: 0, pageSize: 100 })
    if (response && response.code === 200) {
      issueList.value = response.data?.items || []
    }
  } catch (error) {
    console.error('获取领用记录失败:', error)
  } finally {
    loading.value = false
    closeToast()
  }
}

/**
 * 获取库存列表
 */
const fetchStockList = async () => {
  try {
    const response = await sparePartsService.getStockList({ page: 0, pageSize: 500 })
    if (response.code === 200) {
      stockList.value = response.data?.items || []
    }
  } catch (error) {
    console.error('获取库存列表失败:', error)
  }
}

/**
 * 获取项目列表（根据用户权限自动过滤）
 */
const fetchProjectList = async () => {
  try {
    const response = await projectInfoService.getAll()
    if (response.code === 200) {
      projectList.value = response.data || []
    }
  } catch (error) {
    console.error('获取项目列表失败:', error)
  }
}

/**
 * 提交领用
 */
const handleSubmitIssue = async () => {
  if (!selectedStock.value) {
    showFailToast('请选择产品')
    return
  }
  if (!issueForm.value.projectId) {
    showFailToast('请选择项目')
    return
  }
  if (issueForm.value.quantity <= 0) {
    showFailToast('请选择领用数量')
    return
  }

  try {
    await showConfirmDialog({
      title: '确认领用',
      message: `确认领用 ${selectedStock.value.productName} ${issueForm.value.quantity}${selectedStock.value.unit}?`,
    })
  } catch {
    return
  }

  loading.value = true
  showLoadingToast({ message: '提交中...', forbidClick: true })

  try {
    const response = await sparePartsService.issue({
      product_name: selectedStock.value.productName,
      brand: selectedStock.value.brand || null,
      model: selectedStock.value.model || null,
      quantity: issueForm.value.quantity,
      user_name: userStore.getUser()?.name,
      issue_time: new Date().toISOString(),
      unit: selectedStock.value.unit,
      project_id: issueForm.value.projectId || null,
      project_name: issueForm.value.projectName || null,
    })

    if (response.code === 200) {
      showSuccessToast('领用成功')
      showIssuePopup.value = false
      selectedStockId.value = null
      issueForm.value = {
        projectId: '',
        projectName: '',
        quantity: 1,
      }
      fetchIssueList()
      fetchStockList()
    } else {
      showFailToast(response.message || '领用失败')
    }
  } catch (error) {
    console.error('Failed to submit:', error)
    showFailToast('领用失败，请重试')
  } finally {
    loading.value = false
    closeToast()
  }
}

const handleBack = () => {
  goBack()
}

onMounted(() => {
  fetchIssueList()
  fetchStockList()
  fetchProjectList()
})
</script>

<template>
  <div class="spare-parts-issue-page">
    <van-nav-bar fixed placeholder @click-left="handleBack">
      <template #left>
        <div class="nav-left">
          <van-icon name="arrow-left" />
          <span>返回</span>
        </div>
      </template>
    </van-nav-bar>

    <div class="action-bar">
      <van-button type="primary" size="small" @click="showIssuePopup = true"> 新增领用 </van-button>
    </div>

    <van-pull-refresh v-model="loading" @refresh="fetchIssueList">
      <van-list :loading="loading" :finished="true">
        <div class="issue-list">
          <div v-for="item in issueList" :key="item.id" class="issue-card">
            <div class="card-header">
              <span class="product-name">{{ item.productName || item.product_name }}</span>
              <span class="issue-date">{{ formatDate(item.issueTime || item.issue_time) }}</span>
            </div>
            <div class="card-body">
              <div class="info-row">
                <span class="label">项目编号</span>
                <span class="value">{{ item.project_id }}</span>
              </div>
              <div class="info-row">
                <span class="label">项目名称</span>
                <span class="value">{{ item.projectName }}</span>
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
                <span class="label">领用数量</span>
                <span class="value">{{ item.quantity }} {{ item.unit }}</span>
              </div>
              <div class="info-row">
                <span class="label">运维人员</span>
                <span class="value">{{ item.userName || item.user_name || '-' }}</span>
              </div>
            </div>
          </div>
        </div>
        <van-empty v-if="!loading && issueList.length === 0" description="暂无领用记录" />
      </van-list>
    </van-pull-refresh>

    <van-popup v-model:show="showIssuePopup" position="bottom" round :style="{ height: '85%' }">
      <div class="popup-content">
        <div class="popup-header">
          <span class="popup-title">新增备品备件领用</span>
          <van-icon name="cross" @click="showIssuePopup = false" />
        </div>

        <div class="popup-body">
          <van-cell-group inset>
            <van-field label="选择产品" placeholder="请选择产品" required>
              <template #input>
                <select
                  v-model="selectedStockId"
                  class="stock-select"
                  @change="issueForm.quantity = 1"
                >
                  <option :value="null">请选择产品</option>
                  <option v-for="item in filteredStockList" :key="item.id" :value="item.id">
                    {{ item.productName }} {{ item.brand ? `(${item.brand})` : '' }} - 库存:
                    {{ item.stock }}{{ item.unit }}
                  </option>
                </select>
              </template>
            </van-field>
            <van-field
              :model-value="selectedStock?.productName || ''"
              label="产品名称"
              placeholder="请选择产品"
              readonly
            />
            <van-field :model-value="selectedStock?.brand || ''" label="品牌" readonly />
            <van-field :model-value="selectedStock?.model || ''" label="产品型号" readonly />
            <van-field :model-value="selectedStock?.unit || ''" label="单位" readonly />
            <van-field :model-value="selectedStock?.stock || 0" label="库存数量" readonly />
            <van-field label="领用数量" required>
              <template #input>
                <van-stepper
                  v-model="issueForm.quantity"
                  :min="1"
                  :max="maxQuantity"
                  theme="round"
                  button-size="22"
                />
              </template>
            </van-field>
            <van-field
              v-model="issueForm.projectName"
              label="所属项目"
              placeholder="请选择项目"
              required
            >
              <template #input>
                <select
                  v-model="issueForm.projectId"
                  class="project-select"
                  @change="
                    () => {
                      const project = projectList.find((p) => p.project_id === issueForm.projectId)
                      issueForm.projectName = project ? project.project_name : ''
                    }
                  "
                >
                  <option value="">请选择项目</option>
                  <option
                    v-for="project in projectList"
                    :key="project.project_id"
                    :value="project.project_id"
                  >
                    {{ project.project_name }}
                  </option>
                </select>
              </template>
            </van-field>
          </van-cell-group>
        </div>

        <div class="popup-footer">
          <van-button type="primary" block :loading="loading" @click="handleSubmitIssue">
            确认领用
          </van-button>
        </div>
      </div>
    </van-popup>
  </div>
</template>

<style scoped>
.spare-parts-issue-page {
  min-height: 100vh;
  background-color: #f5f7fa;
}

.action-bar {
  padding: 12px 16px;
  background: #fff;
  border-bottom: 1px solid #ebedf0;
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

.product-name {
  font-weight: 600;
  color: #323233;
}

.issue-date {
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
  flex-shrink: 0;
}

.popup-title {
  font-size: 16px;
  font-weight: 500;
}

.popup-body {
  flex: 1;
  overflow-y: auto;
}

.popup-footer {
  padding: 16px;
  flex-shrink: 0;
  border-top: 1px solid #ebedf0;
}

.project-select,
.stock-select {
  width: 100%;
  padding: 8px 0;
  border: none;
  font-size: 14px;
  background: transparent;
}

:deep(.van-pull-refresh) {
  min-height: calc(100vh - 92px);
}

:deep(.van-cell-group--inset) {
  margin: 12px;
}
</style>
