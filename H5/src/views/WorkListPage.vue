<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
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

const currentTab = computed(() => {
  const tabKey = type.value
  const found = tabs.find(t => t.key === tabKey)
  return found ?? tabs[0]!
})

const pageTitle = computed(() => currentTab.value?.title || '工单列表')

const displayList = computed(() => {
  const tabKey = currentTab.value?.key
  if (tabKey === 'overdue') {
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
  if (tabKey === 'expiring') {
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
      params: { page: 0, size: 1000 }
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
      params: { page: 0, size: 1000 }
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
    let endpoint = ''
    const params: any = { page: 0, size: 1000 }
    
    switch (tabKey) {
      case 'completed':
        endpoint = '/periodic-inspection'
        params.status = '已完成'
        break
      case 'periodic':
        endpoint = '/periodic-inspection'
        break
      case 'repair':
        endpoint = '/temporary-repair'
        break
      case 'spot':
        endpoint = '/spot-work'
        break
      default:
        endpoint = '/work-plan'
        if (currentTab.value?.planType) {
          params.plan_type = currentTab.value.planType
        }
        if (currentTab.value?.status) {
          params.status = currentTab.value.status
        }
    }
    
    const response = await api.get<unknown, ApiResponse<{ items: any[], content: any[], total: number }>>(endpoint, { params })
    if (response.code === 200) {
      let items = response.data?.items || response.data?.content || []
      
      if (tabKey === 'completed') {
        const [repairRes, spotRes] = await Promise.all([
          api.get<unknown, ApiResponse<{ items: any[] }>>('/temporary-repair', { params: { page: 0, size: 1000, status: '已完成' } }),
          api.get<unknown, ApiResponse<{ items: any[] }>>('/spot-work', { params: { page: 0, size: 1000, status: '已完成' } })
        ])
        
        if (repairRes.code === 200 && repairRes.data?.items) {
          items = items.concat(repairRes.data.items.map((item: any) => ({ ...item, planType: '临时维修' })))
        }
        if (spotRes.code === 200 && spotRes.data?.items) {
          items = items.concat(spotRes.data.items.map((item: any) => ({ ...item, planType: '零星用工' })))
        }
        
        const currentYear = new Date().getFullYear()
        items = items.filter((item: any) => {
          const endDate = item.plan_end_date || item.planEndDate
          if (!endDate) return false
          const year = new Date(endDate).getFullYear()
          return year === currentYear
        })
      }
      
      workList.value = items.map((item: any) => ({
        id: item.id,
        projectName: item.project_name || item.projectName,
        planStartDate: item.plan_start_date || item.planStartDate,
        planEndDate: item.plan_end_date || item.planEndDate,
        status: item.status,
        planType: item.plan_type || item.planType || currentTab.value?.planType,
        workOrderNo: item.inspection_id || item.repair_id || item.work_id
      }))
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
      router.push(`/work-detail/${item.id}`)
    }
  }
}

const handleUserChanged = () => {
  fetchWorkList()
}

const getStatusLabel = (item: WorkPlanItem) => {
  const tabKey = currentTab.value?.key
  if (tabKey === 'expiring') {
    return `${formatDate(item.planStartDate)} | ${item.status}`
  }
  let label = `${formatDate(item.planEndDate)} | ${item.status}`
  if (tabKey === 'completed') {
    label += ` | ${item.planType}`
  }
  return label
}

onMounted(() => {
  fetchWorkList()
})
</script>

<template>
  <div class="work-list-page">
    <van-nav-bar 
      :title="pageTitle" 
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
    
    <van-pull-refresh v-model="loading" @refresh="fetchWorkList">
      <van-list :loading="loading" :finished="true">
        <van-cell-group inset>
          <van-cell 
            v-for="item in displayList" 
            :key="item.id"
            :title="item.projectName"
            :label="getStatusLabel(item)"
            is-link
            @click="handleItemClick(item)"
          >
            <template #value>
              <div class="cell-value">
                <van-tag 
                  v-if="currentTab.key === 'overdue' && item.overdueDays" 
                  type="danger" 
                  class="alert-tag"
                >
                  超{{ item.overdueDays }}天
                </van-tag>
                <van-tag 
                  v-if="currentTab.key === 'expiring' && item.daysRemaining !== undefined" 
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
