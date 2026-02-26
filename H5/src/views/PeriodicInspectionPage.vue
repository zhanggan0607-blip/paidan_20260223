<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { showLoadingToast, closeToast } from 'vant'
import api from '../utils/api'
import type { ApiResponse } from '../types'
import { formatDate, formatDateTime } from '../config/constants'
import { getStatusType, getDisplayStatus, BASE_WORK_TABS, APPROVAL_TAB } from '../utils/status'
import { getWorkIdFontSize } from '../utils/format'
import { copyOrderId } from '../utils/clipboard'
import UserSelector from '../components/UserSelector.vue'
import { userStore, type User } from '../stores/userStore'
import { useNavigation } from '../composables/useNavigation'

const router = useRouter()
const route = useRoute()
const { goBack } = useNavigation()

const activeTab = ref(0)
const loading = ref(false)
const workList = ref<any[]>([])
const userReady = ref(false)

const canApprove = computed(() => userStore.canApprovePeriodicInspection())

const tabs = computed(() => {
  if (canApprove.value) {
    return [APPROVAL_TAB, ...BASE_WORK_TABS]
  }
  return BASE_WORK_TABS
})

const currentTab = computed(() => tabs.value[activeTab.value])
const currentTabColor = computed(() => tabs.value[activeTab.value]?.color || '#1989fa')

/**
 * 获取工单列表
 * 排序规则：
 * 1. 待确认tab中，部门经理登录时，自己负责的工单排最上面
 * 2. 时间最近的排最上面
 */
const fetchWorkList = async () => {
  if (!userReady.value) return
  loading.value = true
  showLoadingToast({ message: '加载中...', forbidClick: true })
  try {
    const response = await api.get<unknown, ApiResponse<any>>('/periodic-inspection', { 
      params: { 
        page: 0,
        size: 100
      } 
    })
    if (response.code === 200) {
      const allItems = response.data?.content || []
      const filteredItems = allItems.filter((item: any) => 
        currentTab.value?.statuses.includes(item.status)
      )
      const currentUserName = userStore.getUser()?.name || ''
      const isManager = canApprove.value
      const isPendingConfirmTab = currentTab.value?.key === '待确认'
      workList.value = filteredItems.sort((a: any, b: any) => {
        if (isManager && isPendingConfirmTab) {
          const aIsOwn = a.maintenance_personnel === currentUserName
          const bIsOwn = b.maintenance_personnel === currentUserName
          if (aIsOwn && !bIsOwn) return -1
          if (!aIsOwn && bIsOwn) return 1
        }
        const dateA = new Date(a.updated_at || a.created_at || 0).getTime()
        const dateB = new Date(b.updated_at || b.created_at || 0).getTime()
        return dateB - dateA
      })
    }
  } catch (error) {
    console.error('Failed to fetch work list:', error)
  } finally {
    loading.value = false
    closeToast()
  }
}

const handleView = (item: any) => {
  router.push(`/periodic-inspection/${item.id}?tab=${activeTab.value}`)
}

const handleBack = () => {
  goBack('/')
}

const handleFeedback = (item: any) => {
  // TODO: 反馈功能还没实现
  console.log('反馈工单:', item)
}

/**
 * 处理审批操作
 * @param item 工单数据
 */
const handleApprove = (item: any) => {
  router.push(`/periodic-inspection/${item.id}?tab=${activeTab.value}&mode=approve`)
}

const handleUserReady = (_user: User) => {
  userReady.value = true
  fetchWorkList()
}

const handleUserChanged = (_user: User) => {
  fetchWorkList()
}

onMounted(() => {
  const tabParam = route.query.tab
  if (tabParam !== undefined && tabParam !== null) {
    const tabIndex = parseInt(tabParam as string, 10)
    if (!isNaN(tabIndex) && tabIndex >= 0 && tabIndex < tabs.value.length) {
      activeTab.value = tabIndex
    }
  }
})
</script>

<template>
  <div class="periodic-inspection-page">
    <van-nav-bar 
      title="定期巡检单" 
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
                  <van-tag :type="getStatusType(item.status)" size="medium">
                    {{ getDisplayStatus(item.status) }}
                  </van-tag>
                  <div class="work-id-wrapper">
                    <span class="work-id" :style="{ fontSize: getWorkIdFontSize(item.inspection_id) + 'px' }">{{ item.inspection_id }}</span>
                    <van-button size="mini" type="primary" plain class="copy-btn" @click.stop="copyOrderId(item.inspection_id)">复制单号</van-button>
                  </div>
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
                    <span class="label">填写内容</span>
                    <span class="value highlight">共{{ item.total_count || 5 }}项（已填写 {{ item.filled_count || 0 }} 项）</span>
                  </div>
                  <div class="info-row" v-if="currentTab?.key === '待确认' || currentTab?.key === '审批'">
                    <span class="label">提交时间</span>
                    <span class="value">{{ formatDateTime(item.updated_at) }}</span>
                  </div>
                </div>
                <div class="card-footer">
                  <van-button 
                    v-if="currentTab?.key === '待处理'"
                    type="default" 
                    size="small"
                    @click="handleFeedback(item)"
                  >
                    反馈
                  </van-button>
                  <van-button 
                    v-if="currentTab?.key === '审批'"
                    type="success" 
                    size="small"
                    @click="handleApprove(item)"
                  >
                    审批
                  </van-button>
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
.periodic-inspection-page {
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

.work-id-wrapper {
  display: flex;
  align-items: center;
  gap: 4px;
  flex: 1;
  min-width: 0;
  justify-content: flex-end;
  flex-wrap: nowrap;
}

.work-id {
  font-weight: 600;
  color: #323233;
  white-space: nowrap;
  text-align: right;
  flex: 1;
  min-width: 0;
}

.copy-btn {
  flex-shrink: 0;
  height: 24px;
  padding: 0 8px;
  font-size: 12px;
  white-space: nowrap;
  transform: scale(0.8);
  transform-origin: right center;
  margin-left: -4px;
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

.info-row .value.highlight {
  color: #1989fa;
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
