<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { showLoadingToast, closeToast } from 'vant'
import api from '../utils/api'
import type { ApiResponse } from '../types'
import { WORK_STATUS, formatDate } from '../config/constants'

const router = useRouter()

const activeTab = ref(0)
const loading = ref(false)
const workList = ref<any[]>([])

const tabs = [
  { key: '未进行', title: '待处理' },
  { key: '进行中', title: '进行中' },
  { key: '已完成', title: '已完成' }
]

const currentTab = computed(() => tabs[activeTab.value])

const fetchWorkList = async () => {
  loading.value = true
  showLoadingToast({ message: '加载中...', forbidClick: true })
  try {
    const response = await api.get<unknown, ApiResponse<any>>('/work-plan', { 
      params: { 
        plan_type: '定期巡检',
        status: currentTab.value?.key,
        page: 0,
        size: 100
      } 
    })
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
  router.push(`/periodic-inspection/${item.id}`)
}

onMounted(() => {
  fetchWorkList()
})
</script>

<template>
  <div class="periodic-inspection-page">
    <van-nav-bar 
      title="定期巡检" 
      left-arrow 
      fixed 
      placeholder 
      @click-left="router.back()" 
    />
    
    <van-tabs v-model:active="activeTab" sticky @change="fetchWorkList">
      <van-tab v-for="tab in tabs" :key="tab.key" :title="tab.title">
        <van-pull-refresh v-model="loading" @refresh="fetchWorkList">
          <van-list :loading="loading" :finished="true">
            <van-cell-group inset>
              <van-cell 
                v-for="item in workList" 
                :key="item.id"
                :title="item.projectName"
                :label="`${formatDate(item.planEndDate)} | ${item.remarks || ''}`"
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
.periodic-inspection-page {
  min-height: 100vh;
  background-color: #f5f7fa;
}

:deep(.van-cell-group--inset) {
  margin: 12px;
}
</style>
