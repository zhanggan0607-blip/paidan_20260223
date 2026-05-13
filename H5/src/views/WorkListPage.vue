<script setup lang="ts">
import { ref, onMounted, computed, watch, onUnmounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import {
  overdueAlertService,
  expiringSoonService,
  periodicInspectionService,
  temporaryRepairService,
  spotWorkService,
  workOrderService,
} from '../services'
import { formatDate, getWorkIdFontSize, getStatusType, getDisplayStatus } from '@sstcp/shared'
import { copyOrderId } from '../utils/clipboard'
import { useNavigation } from '../composables/useNavigation'
import { useHeartbeatControl } from '../composables/useHeartbeatControl'
import { apiCache, CACHE_KEYS, CACHE_TTL } from '../utils/apiCache'
import type { OverdueAlertItem } from '../types/api'

const route = useRoute()
const router = useRouter()
const { goBack } = useNavigation()

const loading = ref(false)
const workList = ref<any[]>([])
const overdueList = ref<OverdueAlertItem[]>([])
const expiringList = ref<OverdueAlertItem[]>([])

const currentPage = ref(0)
const pageSize = 20
const hasMore = ref(true)
const total = ref(0)

let fetchTimer: ReturnType<typeof setTimeout> | null = null
let isFetching = false

const type = computed(() => (route.query.type as string) || 'expiring')

const tabs = [
  { key: 'expiring', title: '临期工单', status: null, planType: null },
  { key: 'overdue', title: '超期工单', status: null, planType: null },
  { key: 'completed', title: '本年完成', status: '已完成', planType: null },
  { key: 'periodic', title: '定期巡检', status: null, planType: '定期巡检' },
  { key: 'repair', title: '临时维修', status: null, planType: '临时维修' },
  { key: 'spot', title: '零星用工', status: null, planType: '零星用工' },
]

const currentTab = computed(() => {
  const tabKey = type.value
  const found = tabs.find((t) => t.key === tabKey)
  return found ?? tabs[0]!
})

const displayList = computed(() => {
  const tabKey = currentTab.value?.key
  if (tabKey === 'overdue') {
    return overdueList.value
      .map((item, index) => ({
        id: parseInt(item.id),
        uniqueKey: `overdue-${item.id}-${item.workOrderType}-${index}`,
        projectName: item.projectName,
        planStartDate: item.planStartDate,
        planEndDate: item.planEndDate,
        status: item.workOrderStatus,
        planType: item.workOrderType,
        workOrderNo: item.workOrderNo,
        overdueDays: item.overdueDays,
        daysRemaining: item.daysRemaining,
        clientName: item.customerName,
        totalCount: undefined,
        filledCount: undefined,
        createdAt: item.created_at,
      }))
      .sort((a, b) => {
        const dateA = a.createdAt ? new Date(a.createdAt).getTime() : 0
        const dateB = b.createdAt ? new Date(b.createdAt).getTime() : 0
        if (dateB !== dateA) return dateB - dateA
        return (b.id || 0) - (a.id || 0)
      })
  }
  if (tabKey === 'expiring') {
    return expiringList.value
      .map((item, index) => ({
        id: parseInt(item.id),
        uniqueKey: `expiring-${item.id}-${item.workOrderType}-${index}`,
        projectName: item.projectName,
        planStartDate: item.planStartDate,
        planEndDate: item.planEndDate,
        status: item.workOrderStatus,
        planType: item.workOrderType,
        workOrderNo: item.workOrderNo,
        overdueDays: item.overdueDays,
        daysRemaining: item.daysRemaining,
        clientName: item.customerName,
        totalCount: undefined,
        filledCount: undefined,
        createdAt: item.created_at,
      }))
      .sort((a, b) => {
        const dateA = a.createdAt ? new Date(a.createdAt).getTime() : 0
        const dateB = b.createdAt ? new Date(b.createdAt).getTime() : 0
        if (dateB !== dateA) return dateB - dateA
        return (b.id || 0) - (a.id || 0)
      })
  }
  return workList.value
})

const fetchOverdueList = async (useCache = true) => {
  if (isFetching) return
  isFetching = true
  loading.value = true
  try {
    const cacheKey = CACHE_KEYS.OVERDUE_ALERT
    if (useCache) {
      const cached = apiCache.get<OverdueAlertItem[]>(cacheKey)
      if (cached) {
        overdueList.value = cached
        loading.value = false
        return
      }
    }

    const response = await overdueAlertService.getList()
    if (response.code === 200) {
      overdueList.value = response.data?.items || []
      apiCache.set(cacheKey, overdueList.value, CACHE_TTL.MEDIUM)
    }
  } catch (error: any) {
    if (error?.status === 429) {
      await new Promise((r) => setTimeout(r, 2000))
      try {
        const retryResponse = await overdueAlertService.getList()
        if (retryResponse.code === 200) {
          overdueList.value = retryResponse.data?.items || []
          apiCache.set(cacheKey, overdueList.value, CACHE_TTL.MEDIUM)
        }
      } catch (retryError) {
        console.error('Retry failed for overdue list:', retryError)
      }
    } else {
      console.error('Failed to fetch overdue list:', error)
    }
  } finally {
    loading.value = false
    isFetching = false
  }
}

const fetchExpiringList = async (useCache = true) => {
  if (isFetching) return
  isFetching = true
  loading.value = true
  try {
    const cacheKey = CACHE_KEYS.EXPIRING_SOON
    if (useCache) {
      const cached = apiCache.get<OverdueAlertItem[]>(cacheKey)
      if (cached) {
        expiringList.value = cached
        loading.value = false
        return
      }
    }

    const response = await expiringSoonService.getList()
    if (response.code === 200) {
      expiringList.value = response.data?.items || []
      apiCache.set(cacheKey, expiringList.value, CACHE_TTL.MEDIUM)
    }
  } catch (error: any) {
    if (error?.status === 429) {
      await new Promise((r) => setTimeout(r, 2000))
      try {
        const retryResponse = await expiringSoonService.getList()
        if (retryResponse.code === 200) {
          expiringList.value = retryResponse.data?.items || []
          apiCache.set(cacheKey, expiringList.value, CACHE_TTL.MEDIUM)
        }
      } catch (retryError) {
        console.error('Retry failed for expiring list:', retryError)
      }
    } else {
      console.error('Failed to fetch expiring list:', error)
    }
  } finally {
    loading.value = false
    isFetching = false
  }
}

const fetchWorkList = async (isLoadMore = false) => {
  const tabKey = currentTab.value?.key

  if (tabKey === 'overdue') {
    await fetchOverdueList(!isLoadMore)
    return
  }

  if (tabKey === 'expiring') {
    await fetchExpiringList(!isLoadMore)
    return
  }

  if (isFetching) return
  isFetching = true

  if (!isLoadMore) {
    currentPage.value = 0
    hasMore.value = true
  }

  loading.value = true

  try {
    let items: any[] = []
    let totalCount = 0

    switch (tabKey) {
      case 'completed': {
        const cacheKey = `${CACHE_KEYS.WORK_ORDER_COMPLETED}_${currentPage.value}`
        const cached = apiCache.get<any>(cacheKey)

        if (cached && !isLoadMore) {
          items = cached.items
          totalCount = cached.total
        } else {
          const response = await workOrderService.getCompletedThisYear({
            page: currentPage.value,
            size: pageSize,
          })
          if (response.code === 200) {
            items = (response.data?.items || []).map((item: any) => ({
              id: item.id,
              planType: item.plan_type,
              orderTypeCode: item.order_type_code,
              project_name: item.project_name,
              projectName: item.project_name,
              plan_start_date: item.plan_start_date,
              planStartDate: item.plan_start_date,
              plan_end_date: item.plan_end_date,
              planEndDate: item.plan_end_date,
              status: item.status,
              inspection_id: item.order_type_code === 'inspection' ? item.order_id : null,
              repair_id: item.order_type_code === 'repair' ? item.order_id : null,
              work_id: item.order_type_code === 'spotwork' ? item.order_id : null,
              client_name: item.client_name,
              clientName: item.client_name,
            }))
            totalCount = response.data?.total || 0
            apiCache.set(cacheKey, { items, total: totalCount }, CACHE_TTL.SHORT)
          }
        }
        break
      }

      case 'periodic': {
        const validStatuses = '执行中,待确认,已退回'
        const response = await periodicInspectionService.getList({
          page: 0,
          size: 100,
          statuses: validStatuses,
        })
        if (response.code === 200) {
          items = (response.data?.items || response.data?.content || []).map((item: any) => ({
            ...item,
            planType: '定期巡检',
            orderTypeCode: 'inspection',
          }))
        }
        totalCount = items.length
        break
      }

      case 'repair': {
        const validStatuses = '执行中,待确认,已退回'
        const response = await temporaryRepairService.getList({
          page: 0,
          size: 100,
          statuses: validStatuses,
        })
        if (response.code === 200) {
          items = (response.data?.items || response.data?.content || []).map((item: any) => ({
            ...item,
            planType: '临时维修',
            orderTypeCode: 'repair',
          }))
        }
        totalCount = items.length
        break
      }

      case 'spot': {
        const validStatuses = '执行中,待确认,已退回'
        const response = await spotWorkService.getList({
          page: 0,
          size: 100,
          statuses: validStatuses,
        })
        if (response.code === 200) {
          items = (response.data?.items || response.data?.content || []).map((item: any) => ({
            ...item,
            planType: '零星用工',
            orderTypeCode: 'spotwork',
          }))
        }
        totalCount = items.length
        break
      }
    }

    const mappedItems = items
      .map((item: any) => ({
        id: item.id,
        uniqueKey: `${item.planType}-${item.id}`,
        projectName: item.project_name || item.projectName,
        planStartDate: item.plan_start_date || item.planStartDate,
        planEndDate: item.plan_end_date || item.planEndDate,
        status: item.status,
        planType: item.planType,
        orderTypeCode: item.orderTypeCode,
        workOrderNo: item.inspection_id || item.repair_id || item.work_id,
        clientName: item.client_name || item.clientName,
        totalCount: item.total_count,
        filledCount: item.filled_count,
        createdAt: item.created_at,
      }))
      .sort((a, b) => {
        const dateA = a.createdAt ? new Date(a.createdAt).getTime() : 0
        const dateB = b.createdAt ? new Date(b.createdAt).getTime() : 0
        if (dateB !== dateA) return dateB - dateA
        return (b.id || 0) - (a.id || 0)
      })

    if (tabKey === 'completed') {
      if (isLoadMore) {
        workList.value = [...workList.value, ...mappedItems]
      } else {
        workList.value = mappedItems
      }
      total.value = totalCount
      hasMore.value = workList.value.length < totalCount
    } else {
      workList.value = mappedItems
      hasMore.value = false
    }
  } catch (error) {
    console.error('Failed to fetch work list:', error)
  } finally {
    loading.value = false
    isFetching = false
  }
}

const onLoadMore = () => {
  if (loading.value || !hasMore.value || isFetching) return
  const tabKey = currentTab.value?.key
  if (tabKey === 'expiring' || tabKey === 'overdue') return
  currentPage.value++
  fetchWorkList(true)
}

const getAlertItem = (id: number, workOrderType?: string): OverdueAlertItem | undefined => {
  const idStr = String(id)
  if (workOrderType) {
    return (
      overdueList.value.find((o) => o.id === idStr && o.workOrderType === workOrderType) ||
      expiringList.value.find((e) => e.id === idStr && e.workOrderType === workOrderType)
    )
  }
  return (
    overdueList.value.find((o) => o.id === idStr) || expiringList.value.find((e) => e.id === idStr)
  )
}

const handleItemClick = (item: any) => {
  const tabKey = currentTab.value?.key
  const fromPath = route.fullPath
  if (tabKey === 'overdue' || tabKey === 'expiring') {
    const alertItem = getAlertItem(item.id, item.planType)
    if (alertItem) {
      if (alertItem.workOrderType === '定期巡检') {
        router.push({ path: `/periodic-inspection/${item.id}`, query: { from: fromPath } })
      } else if (alertItem.workOrderType === '临时维修') {
        router.push({ path: `/temporary-repair/${item.id}`, query: { from: fromPath } })
      } else if (alertItem.workOrderType === '零星用工') {
        router.push({ path: `/spot-work/${item.id}`, query: { from: fromPath } })
      }
    }
  } else {
    const orderTypeCode = item.orderTypeCode
    if (orderTypeCode === 'inspection') {
      router.push({ path: `/periodic-inspection/${item.id}`, query: { from: fromPath } })
    } else if (orderTypeCode === 'repair') {
      router.push({ path: `/temporary-repair/${item.id}`, query: { from: fromPath } })
    } else if (orderTypeCode === 'spotwork') {
      router.push({ path: `/spot-work/${item.id}`, query: { from: fromPath } })
    } else {
      const planType = item.planType || currentTab.value?.planType
      if (planType === '定期巡检') {
        router.push({ path: `/periodic-inspection/${item.id}`, query: { from: fromPath } })
      } else if (planType === '临时维修') {
        router.push({ path: `/temporary-repair/${item.id}`, query: { from: fromPath } })
      } else if (planType === '零星用工') {
        router.push({ path: `/spot-work/${item.id}`, query: { from: fromPath } })
      }
    }
  }
}

const handleBack = () => {
  goBack()
}

onMounted(() => {
  useHeartbeatControl.pause()
  fetchWorkList()
})

onUnmounted(() => {
  useHeartbeatControl.resume()
  if (fetchTimer) {
    clearTimeout(fetchTimer)
    fetchTimer = null
  }
})

watch(type, () => {
  if (fetchTimer) {
    clearTimeout(fetchTimer)
  }
  fetchTimer = setTimeout(() => {
    fetchWorkList()
  }, 300)
})
</script>

<template>
  <div class="work-list-page">
    <van-nav-bar fixed placeholder @click-left="handleBack">
      <template #left>
        <div class="nav-left">
          <van-icon name="arrow-left" />
          <span>返回</span>
        </div>
      </template>
    </van-nav-bar>

    <van-pull-refresh v-model="loading" @refresh="() => fetchWorkList(false)">
      <van-list
        :loading="loading"
        :finished="!hasMore || currentTab.key === 'expiring' || currentTab.key === 'overdue'"
        :immediate-check="false"
        @load="onLoadMore"
      >
        <div class="work-list">
          <div
            v-for="item in displayList"
            :key="item.uniqueKey"
            class="work-card"
            @click="handleItemClick(item)"
          >
            <div class="card-header">
              <van-tag :type="getStatusType(item.status)" size="medium">
                {{ getDisplayStatus(item.status) }}
              </van-tag>
              <div class="work-id-wrapper">
                <span
                  class="work-id"
                  :style="{ fontSize: getWorkIdFontSize(item.workOrderNo || '') + 'px' }"
                  >{{ item.workOrderNo }}</span
                >
                <van-button
                  size="mini"
                  type="primary"
                  plain
                  class="copy-btn"
                  @click.stop="copyOrderId(item.workOrderNo || '')"
                  >复制单号</van-button
                >
              </div>
            </div>
            <div class="card-body">
              <div class="info-row">
                <span class="label">项目名称</span>
                <span class="value">{{ item.projectName }}</span>
              </div>
              <div class="info-row">
                <span class="label">客户单位</span>
                <span class="value">{{ item.clientName || '-' }}</span>
              </div>
              <div class="info-row">
                <span class="label">运维时间</span>
                <span class="value"
                  >{{ formatDate(item.planStartDate) }} -- {{ formatDate(item.planEndDate) }}</span
                >
              </div>
              <div v-if="currentTab.key === 'periodic'" class="info-row">
                <span class="label">填写内容</span>
                <span class="value highlight"
                  >共{{ item.totalCount ?? 0 }}项（已填写 {{ item.filledCount ?? 0 }} 项）</span
                >
              </div>
              <div v-if="currentTab.key === 'completed'" class="info-row">
                <span class="label">工单类型</span>
                <span class="value">{{ item.planType }}</span>
              </div>
              <div v-if="currentTab.key === 'overdue' && item.overdueDays" class="info-row">
                <span class="label">超期天数</span>
                <span class="value error">超{{ item.overdueDays }}天</span>
              </div>
              <div
                v-if="currentTab.key === 'expiring' && item.daysRemaining !== undefined"
                class="info-row"
              >
                <span class="label">剩余天数</span>
                <span class="value warning">{{ item.daysRemaining }}天后开始</span>
              </div>
              <div
                v-if="currentTab.key === 'overdue' || currentTab.key === 'expiring'"
                class="info-row"
              >
                <span class="label">工单类型</span>
                <span class="value">{{ item.planType }}</span>
              </div>
            </div>
            <div class="card-footer">
              <van-button type="primary" size="small"> 查看 </van-button>
            </div>
          </div>
        </div>
        <van-empty v-if="!loading && displayList.length === 0" description="暂无数据" />
        <div v-if="hasMore && currentTab.key === 'completed'" class="load-more-tip">
          <span>已加载 {{ displayList.length }} / {{ total }} 条</span>
        </div>
      </van-list>
    </van-pull-refresh>
  </div>
</template>

<style scoped>
.work-list-page {
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
  -webkit-tap-highlight-color: transparent;
  contain: layout;
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

.info-row .value.highlight {
  color: var(--color-primary);
  font-weight: 500;
}

.info-row .value.error {
  color: var(--color-danger);
  font-weight: 500;
}

.info-row .value.warning {
  color: var(--color-warning);
  font-weight: 500;
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

.nav-left {
  display: flex;
  align-items: center;
  gap: 4px;
}

.load-more-tip {
  text-align: center;
  padding: 12px;
  color: var(--color-text-secondary);
  font-size: 12px;
}
</style>
