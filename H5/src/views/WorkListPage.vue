<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { showLoadingToast, closeToast } from 'vant'
import api from '../utils/api'
import type { ApiResponse } from '../types'
import { WORK_STATUS, formatDate } from '../config/constants'

const route = useRoute()
const router = useRouter()

const activeTab = ref(0)
const loading = ref(false)
const workList = ref<any[]>([])

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

const fetchWorkList = async () => {
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
    const response = await api.get<unknown, ApiResponse<any>>('/work-plan', { params })
    if (response.success) {
      workList.value = response.data?.content || []
    }
  } catch (error) {
    console.error('Failed to fetch work list:', error)
  } finally {
    loading.value = false
    closeToast()
  }
}

const handleItemClick = (item: any) => {
  router.push(`/work-detail/${item.id}`)
}

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
      left-arrow 
      fixed 
      placeholder 
      @click-left="router.back()" 
    />
    
    <van-tabs v-model:active="activeTab" sticky>
      <van-tab v-for="tab in tabs" :key="tab.key" :title="tab.title">
        <van-pull-refresh v-model="loading" @refresh="fetchWorkList">
          <van-list :loading="loading" :finished="true">
            <van-cell-group inset>
              <van-cell 
                v-for="item in workList" 
                :key="item.id"
                :title="item.projectName"
                :label="`${formatDate(item.planEndDate)} | ${item.status}`"
                is-link
                @click="handleItemClick(item)"
              >
                <template #value>
                  <van-tag :type="item.status === WORK_STATUS.COMPLETED ? 'success' : 'primary'">
                    {{ item.status }}
                  </van-tag>
                </template>
              </van-cell>
            </van-cell-group>
            <van-empty v-if="!loading && workList.length === 0" description="暂无数据" />
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
</style>
