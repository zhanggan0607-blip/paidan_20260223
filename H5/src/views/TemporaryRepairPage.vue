<script setup lang="ts">
import { ref, onMounted, computed, onActivated } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { showLoadingToast, closeToast } from 'vant'
import { temporaryRepairService } from '../services'
import {
  formatDate,
  formatDateTime,
  getWorkIdFontSize,
  getStatusType,
  getDisplayStatus,
  BASE_WORK_TABS,
  APPROVAL_TAB,
} from '@sstcp/shared'
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

const canApprove = computed(() => userStore.canApproveTemporaryRepair())

const CREATE_TAB = {
  key: '新增工单',
  title: '新增工单',
  isCreate: true,
  color: '#07c160',
}

const tabs = computed(() => {
  const baseTabs = canApprove.value ? [APPROVAL_TAB, ...BASE_WORK_TABS] : BASE_WORK_TABS
  return [...baseTabs, CREATE_TAB]
})

const currentTab = computed(() => tabs.value[activeTab.value])
const currentTabColor = computed(() => tabs.value[activeTab.value]?.color || '#1989fa')

/**
 * 获取工单列表
 * 排序规则：
 * 1. 执行中tab中，所有角色只能看到自己的工单
 * 2. 审批tab中，显示其他人提交的待确认工单
 * 3. 待确认tab中，显示自己提交的待确认工单
 * 4. 时间最近的排最上面
 */
const fetchWorkList = async () => {
  if (!userReady.value) return
  loading.value = true
  showLoadingToast({ message: '加载中...', forbidClick: true })
  try {
    const response = await temporaryRepairService.getList({
      page: 0,
      size: 100,
    })
    if (response.code === 200) {
      const allItems = response.data?.content || []
      const currentUserName = userStore.getUser()?.name || ''
      const isInProgressTab = currentTab.value?.key === '执行中'
      const isApprovalTab = currentTab.value?.key === '审批'
      const isPendingConfirmTab = currentTab.value?.key === '待确认'

      const tabStatuses = (currentTab.value as { statuses?: string[] })?.statuses || []
      let filteredItems = allItems.filter((item: any) => tabStatuses.includes(item.status))

      if (isInProgressTab) {
        filteredItems = filteredItems.filter(
          (item: any) => item.maintenance_personnel === currentUserName
        )
      }

      if (isApprovalTab) {
        filteredItems = filteredItems.filter(
          (item: any) => item.maintenance_personnel !== currentUserName
        )
      }

      if (isPendingConfirmTab) {
        filteredItems = filteredItems.filter(
          (item: any) => item.maintenance_personnel === currentUserName
        )
      }

      workList.value = filteredItems.sort((a: any, b: any) => {
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
  router.push(`/temporary-repair/${item.id}?tab=${activeTab.value}`)
}

const handleBack = () => {
  goBack()
}

/**
 * 处理新增操作
 */
const handleCreate = () => {
  router.push('/temporary-repair/create')
}

/**
 * 处理标签页切换
 */
const handleTabChange = () => {
  const tab = currentTab.value as {
    key: string
    title: string
    statuses?: string[]
    isCreate?: boolean
    color: string
  }
  if (tab?.isCreate) {
    handleCreate()
    return
  }
  fetchWorkList()
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

onActivated(() => {
  if (userReady.value) {
    fetchWorkList()
  }
})
</script>

<template>
  <div class="temporary-repair-page">
    <van-nav-bar title="临时维修" fixed placeholder @click-left="handleBack">
      <template #left>
        <div class="nav-left">
          <van-icon name="arrow-left" />
          <span>返回</span>
        </div>
      </template>
      <template #right>
        <div class="nav-right">
          <UserSelector @user-changed="handleUserChanged" @ready="handleUserReady" />
        </div>
      </template>
    </van-nav-bar>

    <van-tabs v-model:active="activeTab" sticky :color="currentTabColor" @change="handleTabChange">
      <van-tab v-for="tab in tabs" :key="tab.key" :title="tab.title">
        <van-pull-refresh v-model="loading" @refresh="fetchWorkList">
          <van-list :loading="loading" :finished="true">
            <div class="work-list">
              <div v-for="item in workList" :key="item.id" class="work-card">
                <div class="card-header">
                  <van-tag :type="getStatusType(item.status)" size="medium">
                    {{ getDisplayStatus(item.status) }}
                  </van-tag>
                  <div class="work-id-wrapper">
                    <span
                      class="work-id"
                      :style="{ fontSize: getWorkIdFontSize(item.repair_id) + 'px' }"
                      >{{ item.repair_id }}</span
                    >
                    <van-button
                      size="mini"
                      type="primary"
                      plain
                      class="copy-btn"
                      @click.stop="copyOrderId(item.repair_id)"
                      >复制单号</van-button
                    >
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
                    <span class="value"
                      >{{ formatDate(item.plan_start_date) }} --
                      {{ formatDate(item.plan_end_date) }}</span
                    >
                  </div>
                  <div class="info-row">
                    <span class="label">报修内容</span>
                    <span class="value">{{ item.remarks || '-' }}</span>
                  </div>
                  <div
                    v-if="currentTab?.key === '待确认' || currentTab?.key === '审批'"
                    class="info-row"
                  >
                    <span class="label">提交时间</span>
                    <span class="value">{{ formatDateTime(item.updated_at) }}</span>
                  </div>
                </div>
                <div class="card-footer">
                  <van-button type="primary" size="small" @click="handleView(item)">
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
.temporary-repair-page {
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

.nav-right {
  display: flex;
  align-items: center;
  gap: 12px;
}
</style>
