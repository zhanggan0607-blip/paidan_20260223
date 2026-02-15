<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { showLoadingToast, closeToast, showSuccessToast, showFailToast, showConfirmDialog } from 'vant'
import api from '../utils/api'
import type { ApiResponse } from '../types'
import { WORK_STATUS, formatDate } from '../config/constants'

const router = useRouter()

const activeTab = ref(0)
const loading = ref(false)
const workList = ref<any[]>([])

const tabs = [
  { key: '待处理', title: '待处理', statuses: ['待执行', '执行中', '已退回'] },
  { key: '待确认', title: '待确认', statuses: ['待确认'] },
  { key: '已完成', title: '已完成', statuses: ['已完成'] }
]

const currentTab = computed(() => tabs[activeTab.value])

const getStatusType = (status: string) => {
  switch (status) {
    case '已完成':
      return 'success'
    case '执行中':
      return 'primary'
    case '待执行':
      return 'default'
    case '已退回':
      return 'warning'
    case '待确认':
      return 'warning'
    default:
      return 'default'
  }
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
  router.push(`/periodic-inspection/${item.id}`)
}

const handleFeedback = async (item: any) => {
  try {
    await showConfirmDialog({
      title: '提示',
      message: '确认要反馈该工单吗？'
    })
    showLoadingToast({ message: '处理中...', forbidClick: true })
    const response = await api.put<unknown, ApiResponse<any>>(`/periodic-inspection/${item.id}`, {
      ...item,
      status: '待确认'
    })
    if (response.code === 200) {
      showSuccessToast('反馈成功')
      fetchWorkList()
    }
  } catch (error) {
    if (error !== 'cancel') {
      console.error('Failed to feedback:', error)
      showFailToast('反馈失败')
    }
  } finally {
    closeToast()
  }
}

onMounted(() => {
  fetchWorkList()
})
</script>

<template>
  <div class="periodic-inspection-page">
    <van-nav-bar 
      title="定期巡检单" 
      fixed 
      placeholder 
      @click-left="router.back()" 
    >
      <template #left>
        <div class="nav-left" @click="router.back()">
          <van-icon name="arrow-left" />
          <span>返回</span>
        </div>
      </template>
    </van-nav-bar>
    
    <van-tabs v-model:active="activeTab" sticky @change="fetchWorkList">
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
                  <span class="work-id" :style="{ fontSize: getWorkIdFontSize(item.inspection_id) + 'px' }">{{ item.inspection_id }}</span>
                  <van-tag :type="getStatusType(item.status)" size="medium">
                    {{ item.status }}
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
                    <span class="label">填写内容</span>
                    <span class="value highlight">已填写 {{ item.filled_count || 0 }} 项</span>
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
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
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
</style>
