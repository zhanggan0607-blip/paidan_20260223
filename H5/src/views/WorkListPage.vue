<script setup lang="ts">
import { ref, onMounted, computed, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { showLoadingToast, closeToast } from 'vant'
import {
  overdueAlertService,
  expiringSoonService,
  periodicInspectionService,
  temporaryRepairService,
  spotWorkService,
} from '../services'
import { formatDate, getWorkIdFontSize, getStatusType, getDisplayStatus } from '@sstcp/shared'
import { copyOrderId } from '../utils/clipboard'
import { useNavigation } from '../composables/useNavigation'
import type { OverdueAlertItem } from '../types/models'

const route = useRoute()
const router = useRouter()
const { goBack } = useNavigation()

const loading = ref(false)
const workList = ref<any[]>([])
const overdueList = ref<OverdueAlertItem[]>([])
const expiringList = ref<OverdueAlertItem[]>([])

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

const pageTitle = computed(() => currentTab.value?.title || '工单列表')

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
      }))
      .sort((a, b) => {
        const dateA = a.planStartDate ? new Date(a.planStartDate).getTime() : 0
        const dateB = b.planStartDate ? new Date(b.planStartDate).getTime() : 0
        return dateA - dateB
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
      }))
      .sort((a, b) => {
        const dateA = a.planStartDate ? new Date(a.planStartDate).getTime() : 0
        const dateB = b.planStartDate ? new Date(b.planStartDate).getTime() : 0
        return dateA - dateB
      })
  }
  return workList.value
})

const fetchOverdueList = async () => {
  loading.value = true
  showLoadingToast({ message: '加载中...', forbidClick: true })
  try {
    const response = await overdueAlertService.getList()
    if (response.code === 200) {
      overdueList.value = response.data?.items || []
    }
  } catch (error) {
    console.error('Failed to fetch overdue list:', error)
  } finally {
    loading.value = false
    closeToast()
  }
}

const fetchExpiringList = async () => {
  loading.value = true
  showLoadingToast({ message: '加载中...', forbidClick: true })
  try {
    const response = await expiringSoonService.getList()
    if (response.code === 200) {
      expiringList.value = response.data?.items || []
    }
  } catch (error) {
    console.error('Failed to fetch expiring list:', error)
  } finally {
    loading.value = false
    closeToast()
  }
}

const fetchWorkList = async () => {
  const tabKey = currentTab.value?.key

  if (tabKey === 'overdue') {
    await fetchOverdueList()
    return
  }

  if (tabKey === 'expiring') {
    await fetchExpiringList()
    return
  }

  loading.value = true
  showLoadingToast({ message: '加载中...', forbidClick: true })
  try {
    let items: any[] = []

    switch (tabKey) {
      case 'completed': {
        const completedStatuses = ['已完成']
        const currentYear = new Date().getFullYear()

        const [inspectionRes, repairRes, spotRes] = await Promise.all([
          periodicInspectionService.getList({ page: 0, size: 1000 }),
          temporaryRepairService.getList({ page: 0, size: 1000 }),
          spotWorkService.getList({ page: 0, size: 1000 }),
        ])

        if (inspectionRes.code === 200) {
          const inspectionItems = inspectionRes.data?.items || inspectionRes.data?.content || []
          const completedInspections = inspectionItems
            .filter((item: any) => completedStatuses.includes(item.status))
            .filter((item: any) => {
              const completionDate = item.actual_completion_date
              if (!completionDate) return false
              return new Date(completionDate).getFullYear() === currentYear
            })
          items = items.concat(
            completedInspections.map((item: any) => ({ ...item, planType: '定期巡检' }))
          )
        }

        if (repairRes.code === 200) {
          const repairItems = repairRes.data?.items || repairRes.data?.content || []
          const completedRepairs = repairItems
            .filter((item: any) => completedStatuses.includes(item.status))
            .filter((item: any) => {
              const completionDate = item.actual_completion_date
              if (!completionDate) return false
              return new Date(completionDate).getFullYear() === currentYear
            })
          items = items.concat(
            completedRepairs.map((item: any) => ({ ...item, planType: '临时维修' }))
          )
        }

        if (spotRes.code === 200) {
          const spotItems = spotRes.data?.items || spotRes.data?.content || []
          const completedSpotWorks = spotItems
            .filter((item: any) => completedStatuses.includes(item.status))
            .filter((item: any) => {
              const completionDate = item.actual_completion_date
              if (!completionDate) return false
              return new Date(completionDate).getFullYear() === currentYear
            })
          items = items.concat(
            completedSpotWorks.map((item: any) => ({ ...item, planType: '零星用工' }))
          )
        }
        break
      }

      case 'periodic': {
        const response = await periodicInspectionService.getList({ page: 0, size: 1000 })
        if (response.code === 200) {
          const validStatuses = ['执行中', '待确认', '已退回']
          items = (response.data?.items || response.data?.content || [])
            .filter((item: any) => validStatuses.includes(item.status))
            .map((item: any) => ({
              ...item,
              planType: '定期巡检',
            }))
        }
        break
      }

      case 'repair': {
        const response = await temporaryRepairService.getList({ page: 0, size: 1000 })
        if (response.code === 200) {
          const validStatuses = ['执行中', '待确认', '已退回']
          items = (response.data?.items || response.data?.content || [])
            .filter((item: any) => validStatuses.includes(item.status))
            .map((item: any) => ({
              ...item,
              planType: '临时维修',
            }))
        }
        break
      }

      case 'spot': {
        const response = await spotWorkService.getList({ page: 0, size: 1000 })
        if (response.code === 200) {
          const validStatuses = ['执行中', '待确认', '已退回']
          items = (response.data?.items || response.data?.content || [])
            .filter((item: any) => validStatuses.includes(item.status))
            .map((item: any) => ({
              ...item,
              planType: '零星用工',
            }))
        }
        break
      }
    }

    workList.value = items
      .map((item: any) => ({
        id: item.id,
        uniqueKey: `${item.planType}-${item.id}`,
        projectName: item.project_name || item.projectName,
        planStartDate: item.plan_start_date || item.planStartDate,
        planEndDate: item.plan_end_date || item.planEndDate,
        status: item.status,
        planType: item.planType,
        workOrderNo: item.inspection_id || item.repair_id || item.work_id,
        clientName: item.client_name || item.clientName,
        totalCount: item.total_count,
        filledCount: item.filled_count,
        updatedAt: item.updated_at,
      }))
      .sort((a, b) => {
        const dateA = a.planStartDate ? new Date(a.planStartDate).getTime() : 0
        const dateB = b.planStartDate ? new Date(b.planStartDate).getTime() : 0
        return dateA - dateB
      })
  } catch (error) {
    console.error('Failed to fetch work list:', error)
  } finally {
    loading.value = false
    closeToast()
  }
}

const getAlertItem = (id: number): OverdueAlertItem | undefined => {
  const idStr = String(id)
  return (
    overdueList.value.find((o) => o.id === idStr) || expiringList.value.find((e) => e.id === idStr)
  )
}

const handleItemClick = (item: any) => {
  const tabKey = currentTab.value?.key
  if (tabKey === 'overdue' || tabKey === 'expiring') {
    const alertItem = getAlertItem(item.id)
    if (alertItem) {
      if (alertItem.workOrderType === '定期巡检') {
        router.push(`/periodic-inspection/${item.id}`)
      } else if (alertItem.workOrderType === '临时维修') {
        router.push(`/temporary-repair/${item.id}`)
      } else if (alertItem.workOrderType === '零星用工') {
        router.push(`/spot-work/${item.id}`)
      }
    }
  } else {
    const planType = item.planType || currentTab.value?.planType
    if (planType === '定期巡检') {
      router.push(`/periodic-inspection/${item.id}`)
    } else if (planType === '临时维修') {
      router.push(`/temporary-repair/${item.id}`)
    } else if (planType === '零星用工') {
      router.push(`/spot-work/${item.id}`)
    } else {
      router.push(`/periodic-inspection/${item.id}`)
    }
  }
}

const handleBack = () => {
  goBack()
}

onMounted(() => {
  fetchWorkList()
})

watch(type, () => {
  fetchWorkList()
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

    <van-pull-refresh v-model="loading" @refresh="fetchWorkList">
      <van-list :loading="loading" :finished="true">
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
      </van-list>
    </van-pull-refresh>
  </div>
</template>

<style scoped>
.work-list-page {
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

.info-row .value.error {
  color: #ee0a24;
  font-weight: 500;
}

.info-row .value.warning {
  color: #ff976a;
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

.nav-left {
  display: flex;
  align-items: center;
  gap: 4px;
}
</style>
