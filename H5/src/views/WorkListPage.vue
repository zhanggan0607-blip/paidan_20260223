<script setup lang="ts">
import { ref, onMounted, computed, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { showLoadingToast, closeToast } from 'vant'
import api from '../utils/api'
import type { ApiResponse } from '../types'
import { WORK_STATUS, formatDate } from '../config/constants'
import UserSelector from '../components/UserSelector.vue'

interface AlertItem {
  id: string
  workOrderNo: string
  project_id: string
  projectName: string
  customerName: string
  workOrderType: string
  planStartDate: string
  planEndDate: string
  workOrderStatus: string
  overdueDays?: number
  daysRemaining?: number
  executor: string
}

interface WorkPlanItem {
  id: number
  projectName: string
  planStartDate?: string
  planEndDate: string
  status: string
  planType: string
  workOrderNo?: string
  overdueDays?: number
  daysRemaining?: number
}

const route = useRoute()
const router = useRouter()

const activeTab = ref(0)
const loading = ref(false)
const workList = ref<WorkPlanItem[]>([])
const overdueList = ref<AlertItem[]>([])
const expiringList = ref<AlertItem[]>([])

const type = computed(() => route.query.type as string || 'expiring')

const tabs = [
  { key: 'expiring', title: '临期工单', status: null, planType: null },
  { key: 'overdue', title: '超期工单', status: null, planType: null },
  { key: 'completed', title: '本年完成', status: '已完成', planType: null },
  { key: 'periodic', title: '定期巡检', status: null, planType: '定期巡检' },
  { key: 'repair', title: '临时维修', status: null, planType: '临时维修' },
  { key: 'spot', title: '零星用工', status: null, planType: '零星用工' }
]

const currentTab = computed(() => tabs[activeTab.value])

const displayList = computed(() => {
  if (currentTab.value?.key === 'overdue') {
    return overdueList.value.map(item => ({
      id: parseInt(item.id),
      projectName: item.projectName,
      planStartDate: item.planStartDate,
      planEndDate: item.planEndDate,
      status: item.workOrderStatus,
      planType: item.workOrderType,
      workOrderNo: item.workOrderNo,
      overdueDays: item.overdueDays,
      daysRemaining: item.daysRemaining
    }))
  }
  if (currentTab.value?.key === 'expiring') {
    return expiringList.value.map(item => ({
      id: parseInt(item.id),
      projectName: item.projectName,
      planStartDate: item.planStartDate,
      planEndDate: item.planEndDate,
      status: item.workOrderStatus,
      planType: item.workOrderType,
      workOrderNo: item.workOrderNo,
      overdueDays: item.overdueDays,
      daysRemaining: item.daysRemaining
    }))
  }
  return workList.value
})

const fetchOverdueList = async () => {
  loading.value = true
  showLoadingToast({ message: '加载中...', forbidClick: true })
  try {
    const response = await api.get<unknown, ApiResponse<{ items: AlertItem[], total: number }>>('/overdue-alert', {
      params: { page: 0, size: 100 }
    })
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
    const response = await api.get<unknown, ApiResponse<{ items: AlertItem[], total: number }>>('/expiring-soon', {
      params: { page: 0, size: 100 }
    })
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
  if (currentTab.value?.key === 'overdue') {
    await fetchOverdueList()
    return
  }
  
  if (currentTab.value?.key === 'expiring') {
    await fetchExpiringList()
    return
  }
  
  loading.value = true
  showLoadingToast({ message: '加载中...', forbidClick: true })
  try {
    const params: any = { page: 0, size: 100 }
    if (currentTab.value?.planType) {
      params.plan_type = currentTab.value.planType
    }
    if (currentTab.value?.status) {
      params.status = currentTab.value.status
    }
    const response = await api.get<unknown, ApiResponse<{ content: WorkPlanItem[] }>>('/work-plan', { params })
    if (response.code === 200) {
      workList.value = response.data?.content || []
    }
  } catch (error) {
    console.error('Failed to fetch work list:', error)
  } finally {
    loading.value = false
    closeToast()
  }
}

const getAlertItem = (id: number): AlertItem | undefined => {
  const idStr = String(id)
  return overdueList.value.find(o => o.id === idStr) || expiringList.value.find(e => e.id === idStr)
}

const handleItemClick = (item: any) => {
  if (currentTab.value?.key === 'overdue' || currentTab.value?.key === 'expiring') {
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
    router.push(`/work-detail/${item.id}`)
  }
}

const handleUserChanged = () => {
  fetchWorkList()
}

watch(activeTab, () => {
  fetchWorkList()
})

onMounted(() => {
  const tabIndex = tabs.findIndex(t => t.key === type.value)
  if (tabIndex >= 0) {
    activeTab.value = tabIndex
  }
  fetchWorkList()
})
</script>

<template>
  <div class="work-list-page">
    <van-nav-bar 
      title="工单列表" 
      fixed 
      placeholder 
    >
      <template #left>
        <div class="nav-left" @click="router.push('/')">
          <van-icon name="arrow-left" />
          <span>返回</span>
        </div>
      </template>
      <template #right>
        <UserSelector @userChanged="handleUserChanged" />
      </template>
    </van-nav-bar>
    
    <van-tabs v-model:active="activeTab" sticky>
      <van-tab v-for="tab in tabs" :key="tab.key" :title="tab.title">
        <van-pull-refresh v-model="loading" @refresh="fetchWorkList">
          <van-list :loading="loading" :finished="true">
            <van-cell-group inset>
              <van-cell 
                v-for="item in displayList" 
                :key="item.id"
                :title="item.projectName"
                :label="tab.key === 'expiring' ? `${formatDate(item.planStartDate)} | ${item.status}` : `${formatDate(item.planEndDate)} | ${item.status}`"
                is-link
                @click="handleItemClick(item)"
              >
                <template #value>
                  <div class="cell-value">
                    <van-tag 
                      v-if="tab.key === 'overdue' && item.overdueDays" 
                      type="danger" 
                      class="alert-tag"
                    >
                      超{{ item.overdueDays }}天
                    </van-tag>
                    <van-tag 
                      v-if="tab.key === 'expiring' && item.daysRemaining !== undefined" 
                      type="warning" 
                      class="alert-tag"
                    >
                      {{ item.daysRemaining }}天后开始
                    </van-tag>
                    <van-tag :type="item.status === WORK_STATUS.COMPLETED ? 'success' : 'primary'">
                      {{ item.status }}
                    </van-tag>
                  </div>
                </template>
              </van-cell>
            </van-cell-group>
            <van-empty v-if="!loading && displayList.length === 0" description="暂无数据" />
          </van-list>
        </van-pull-refresh>
      </van-tab>
    </van-tabs>
  </div>
</template>

<style scoped>
.work-list-page {
  min-height: 100vh;
  background-color: #f5f7fa;
}

:deep(.van-cell-group--inset) {
  margin: 12px;
}

.cell-value {
  display: flex;
  align-items: center;
  gap: 8px;
}

.alert-tag {
  font-weight: bold;
}
</style>
