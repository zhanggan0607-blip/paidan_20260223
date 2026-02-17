<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { showLoadingToast, closeToast } from 'vant'
import api from '../utils/api'
import type { ApiResponse } from '../types'
import { formatDate } from '../config/constants'
import UserSelector from '../components/UserSelector.vue'

const router = useRouter()

const activeTab = ref(0)
const loading = ref(false)
const workList = ref<any[]>([])
const userReady = ref(false)

const tabs = [
  { key: '待处理', title: '待处理', statuses: ['未进行', '已退回'], color: '#ee0a24' },
  { key: '待确认', title: '待确认', statuses: ['待确认'], color: '#ff976a' },
  { key: '已完成', title: '已完成', statuses: ['已确认', '已完成'], color: '#07c160' }
]

const currentTab = computed(() => tabs[activeTab.value])
const currentTabColor = computed(() => tabs[activeTab.value]?.color || '#1989fa')

const getStatusType = (status: string) => {
  switch (status) {
    case '已完成':
    case '已确认':
      return 'success'
    case '未进行':
    case '已退回':
      return 'danger'
    case '待确认':
      return 'warning'
    default:
      return 'default'
  }
}

const getDisplayStatus = (status: string) => {
  if (status === '已确认' || status === '已完成') return '已完成'
  if (status === '待确认') return '待确认'
  if (status === '未进行' || status === '已退回') return '待处理'
  return status
}

const getWorkIdFontSize = (workId: string) => {
  if (!workId) return 14
  const len = workId.length
  if (len <= 20) return 14
  if (len <= 25) return 12
  if (len <= 30) return 11
  if (len <= 35) return 10
  return 9
}

const fetchWorkList = async () => {
  if (!userReady.value) return
  loading.value = true
  showLoadingToast({ message: '加载中...', forbidClick: true })
  try {
    const response = await api.get<unknown, ApiResponse<any>>('/spot-work', { 
      params: { 
        page: 0,
        size: 100
      } 
    })
    if (response.code === 200) {
      const allItems = response.data?.content || []
      workList.value = allItems.filter((item: any) => 
        currentTab.value?.statuses.includes(item.status)
      )
    }
  } catch (error) {
    console.error('Failed to fetch work list:', error)
  } finally {
    loading.value = false
    closeToast()
  }
}

const handleView = (item: any) => {
  router.push(`/spot-work/${item.id}`)
}

const handleBack = () => {
  router.push('/')
}

const handleUserReady = () => {
  userReady.value = true
  fetchWorkList()
}

const handleUserChanged = () => {
  fetchWorkList()
}

onMounted(() => {
})
</script>

<template>
  <div class="spot-work-page">
    <van-nav-bar 
      title="零星用工" 
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
        <UserSelector @userChanged="handleUserChanged" @ready="handleUserReady" />
      </template>
    </van-nav-bar>
    
    <van-tabs v-model:active="activeTab" sticky @change="fetchWorkList" :color="currentTabColor">
      <van-tab v-for="tab in tabs" :key="tab.key" :title="tab.title">
        <van-pull-refresh v-model="loading" @refresh="fetchWorkList">
          <van-list :loading="loading" :finished="true">
            <div class="work-list">
              <div 
                v-for="item in workList" 
                :key="item.id"
                class="work-card"
              >
                <div class="card-header">
                  <span class="work-id" :style="{ fontSize: getWorkIdFontSize(item.work_id) + 'px' }">{{ item.work_id }}</span>
                  <van-tag :type="getStatusType(item.status)" size="medium">
                    {{ getDisplayStatus(item.status) }}
                  </van-tag>
                </div>
                <div class="card-body">
                  <div class="info-row">
                    <span class="label">项目名称</span>
                    <span class="value">{{ item.project_name }}</span>
                  </div>
                  <div class="info-row">
                    <span class="label">客户单位</span>
                    <span class="value">{{ item.client_name || '-' }}</span>
                  </div>
                  <div class="info-row">
                    <span class="label">运维时间</span>
                    <span class="value">{{ formatDate(item.plan_start_date) }} -- {{ formatDate(item.plan_end_date) }}</span>
                  </div>
                  <div class="info-row">
                    <span class="label">备注</span>
                    <span class="value">{{ item.remarks || '-' }}</span>
                  </div>
                </div>
                <div class="card-footer">
                  <van-button 
                    type="primary" 
                    size="small"
                    @click="handleView(item)"
                  >
                    查看
                  </van-button>
                </div>
              </div>
            </div>
            <van-empty v-if="!loading && workList.length === 0" description="暂无数据" />
          </van-list>
        </van-pull-refresh>
      </van-tab>
    </van-tabs>
  </div>
</template>

<style scoped>
.spot-work-page {
  min-height: 100vh;
  background-color: #f5f7fa;
}

.work-list {
  padding: 12px;
}

.work-card {
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
  flex-wrap: nowrap;
}

.work-id {
  font-weight: 600;
  color: #323233;
  white-space: nowrap;
  flex: 1;
  margin-right: 8px;
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

.card-footer .van-button {
  min-width: 60px;
}

:deep(.van-tabs__nav) {
  padding-left: 0;
  padding-right: 0;
}

:deep(.van-tab) {
  flex: 1;
}

:deep(.van-pull-refresh) {
  min-height: calc(100vh - 46px - 44px);
}

:deep(.van-tabs__line) {
  transition: background-color 0.3s;
}
</style>
