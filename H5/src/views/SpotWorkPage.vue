<script setup lang="ts">
import { ref, onMounted, computed, onActivated } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { showLoadingToast, closeToast } from 'vant'
import { spotWorkService } from '../services'
import {
  formatDate,
  formatDateTime,
  getWorkIdFontSize,
  getStatusType,
  getDisplayStatus,
  BASE_WORK_TABS,
  APPROVAL_TAB,
  sortByTimestampDesc,
} from '@sstcp/shared'
import { copyOrderId } from '../utils/clipboard'
import { useUserStore } from '../stores/userStore'
const userStore = useUserStore()
import { useNavigation } from '../composables/useNavigation'
import { apiCache, CACHE_KEYS, CACHE_TTL } from '../utils/apiCache'

const router = useRouter()
const route = useRoute()
const { goBack } = useNavigation()

const activeTab = ref(0)
const loading = ref(false)
const workList = ref<any[]>([])
const userReady = ref(false)
const isInitialized = ref(false)

const canApprove = computed(() => userStore.canApproveSpotWork())

const tabs = computed(() => {
  if (canApprove.value) {
    return [APPROVAL_TAB, ...BASE_WORK_TABS]
  }
  return BASE_WORK_TABS
})

const currentTab = computed(() => tabs.value[activeTab.value])
const currentTabColor = computed(() => tabs.value[activeTab.value]?.color || '#1989fa')

const allItemsCache = ref<any[]>([])

const fetchWorkList = async (forceRefresh = false) => {
  if (!userReady.value) return
  loading.value = true
  showLoadingToast({ message: '加载中...', forbidClick: true })
  try {
    const currentUserName = userStore.currentUser?.name || ''
    const tabKey = currentTab.value?.key
    const isInProgressTab = tabKey === '执行中'
    const isApprovalTab = tabKey === '审批'
    const isPendingConfirmTab = tabKey === '待确认'

    if (isApprovalTab || isPendingConfirmTab) {
      const cacheKey = CACHE_KEYS.SPOT_WORK_PENDING
      if (!forceRefresh) {
        const cached = apiCache.get<any[]>(cacheKey)
        if (cached) {
          allItemsCache.value = cached
        }
      }
      
      if (forceRefresh || allItemsCache.value.length === 0) {
        const response = await spotWorkService.getList({
          page: 0,
          size: 100,
          status: '待确认',
        })
        if (response.code === 200) {
          allItemsCache.value = response.data?.items || []
          apiCache.set(cacheKey, allItemsCache.value, CACHE_TTL.SHORT)
        }
      }

      let filteredItems = allItemsCache.value
      if (isApprovalTab) {
        filteredItems = filteredItems.filter(
          (item: any) => item.maintenance_personnel !== currentUserName
        )
      } else {
        filteredItems = filteredItems.filter(
          (item: any) => item.maintenance_personnel === currentUserName
        )
      }

      workList.value = sortByTimestampDesc(filteredItems, {
        secondarySortKey: 'id'
      })
    } else {
      const tabStatuses = (currentTab.value as { statuses?: string[] })?.statuses || []
      
      if (tabStatuses.length > 0) {
        const responses = await Promise.all(
          tabStatuses.map(status =>
            spotWorkService.getList({ page: 0, size: 100, status })
          )
        )
        let allItems = responses
          .filter(r => r.code === 200)
          .flatMap(r => r.data?.items || r.data?.content || [])

        if (isInProgressTab && !canApprove.value) {
          allItems = allItems.filter(
            (item: any) => item.maintenance_personnel === currentUserName
          )
        }

        workList.value = sortByTimestampDesc(allItems, {
          secondarySortKey: 'id'
        })
      } else {
        workList.value = []
      }
    }
  } catch (error) {
    console.error('Failed to fetch work list:', error)
  } finally {
    loading.value = false
    closeToast()
  }
}

const handleView = (item: any) => {
  router.push(`/spot-work/${item.id}?tab=${activeTab.value}`)
}

const handleBack = () => {
  goBack()
}

onMounted(() => {
  if (isInitialized.value) return
  isInitialized.value = true
  userReady.value = true
  fetchWorkList()
  const tabParam = route.query.tab
  if (tabParam !== undefined && tabParam !== null) {
    const tabIndex = parseInt(tabParam as string, 10)
    if (!isNaN(tabIndex) && tabIndex >= 0 && tabIndex < tabs.value.length) {
      activeTab.value = tabIndex
    }
  }
})

onActivated(() => {
  if (!isInitialized.value) {
    isInitialized.value = true
    userReady.value = true
    fetchWorkList()
  }
})
</script>

<template>
  <div class="spot-work-page">
    <van-nav-bar fixed placeholder @click-left="handleBack">
      <template #left>
        <div class="nav-left">
          <van-icon name="arrow-left" />
          <span>返回</span>
        </div>
      </template>
    </van-nav-bar>

    <van-tabs v-model:active="activeTab" sticky :color="currentTabColor" @change="fetchWorkList">
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
                      :style="{ fontSize: getWorkIdFontSize(item.work_id) + 'px' }"
                      >{{ item.work_id }}</span
                    >
                    <van-button
                      size="mini"
                      type="primary"
                      plain
                      class="copy-btn"
                      @click.stop="copyOrderId(item.work_id)"
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
                    <span class="label">备注</span>
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
.spot-work-page {
  min-height: 100vh;
  background-color: var(--color-bg-page);
}

.work-list {
  padding: 12px;
}

.work-card {
  background: var(--color-bg-card);
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
  background: var(--color-bg-page);
  border-bottom: 1px solid var(--color-border-light);
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
  color: var(--color-text-primary);
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
  color: var(--color-text-secondary);
  flex-shrink: 0;
  width: 70px;
}

.info-row .value {
  color: var(--color-text-primary);
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
  border-top: 1px solid var(--color-border-light);
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
