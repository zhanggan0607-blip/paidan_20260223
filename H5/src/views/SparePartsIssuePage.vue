<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { showLoadingToast, closeToast } from 'vant'
import api from '../utils/api'
import type { ApiResponse } from '../types'
import { formatDate } from '../config/constants'
import UserSelector from '../components/UserSelector.vue'
import { authService, type User } from '../services/auth'

interface SparePartsIssueItem {
  id: number
  project_id: string
  projectName: string
  productName: string
  brand: string
  model: string
  quantity: number
  userName: string
  issueTime: string
  unit: string
}

const router = useRouter()
const currentUser = ref<User | null>(null)
const loading = ref(false)
const issueList = ref<SparePartsIssueItem[]>([])

/**
 * 获取领用记录
 */
const fetchIssueList = async () => {
  loading.value = true
  showLoadingToast({ message: '加载中...', forbidClick: true })
  try {
    const response = await api.get<unknown, ApiResponse<{ items: SparePartsIssueItem[], total: number }>>('/spare-parts/usage', {
      params: { page: 0, pageSize: 100 }
    })
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

const handleBack = () => {
  router.push('/')
}

const handleUserChanged = () => {
  fetchIssueList()
}

onMounted(() => {
  currentUser.value = authService.getCurrentUser()
  fetchIssueList()
})
</script>

<template>
  <div class="spare-parts-issue-page">
    <van-nav-bar 
      title="备品备件领用" 
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
    
    <van-pull-refresh v-model="loading" @refresh="fetchIssueList">
      <van-list :loading="loading" :finished="true">
        <div class="issue-list">
          <div 
            v-for="item in issueList" 
            :key="item.id"
            class="issue-card"
          >
            <div class="card-header">
              <span class="product-name">{{ item.productName }}</span>
              <span class="issue-date">{{ formatDate(item.issueTime) }}</span>
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
                <span class="value">{{ item.userName }}</span>
              </div>
            </div>
          </div>
        </div>
        <van-empty v-if="!loading && issueList.length === 0" description="暂无领用记录" />
      </van-list>
    </van-pull-refresh>
  </div>
</template>

<style scoped>
.spare-parts-issue-page {
  min-height: 100vh;
  background-color: #f5f7fa;
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

:deep(.van-pull-refresh) {
  min-height: calc(100vh - 46px);
}
</style>
