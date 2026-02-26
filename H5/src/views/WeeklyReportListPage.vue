<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { showLoadingToast, closeToast } from 'vant'
import api from '../utils/api'
import type { ApiResponse } from '../types'
import { formatDate, formatDateTime } from '../config/constants'
import UserSelector from '../components/UserSelector.vue'
import { userStore } from '../stores/userStore'
import { useNavigation } from '../composables/useNavigation'

interface WeeklyReportItem {
  id: number
  report_id: string
  project_id: string
  project_name: string
  week_start_date: string
  week_end_date: string
  report_date: string
  work_summary: string
  work_content: string
  next_week_plan: string
  issues: string
  suggestions: string
  status: string
  created_by: string
  created_at: string
  updated_at: string
}

const router = useRouter()
const { goBack } = useNavigation()

const loading = ref(false)
const reportList = ref<WeeklyReportItem[]>([])

/**
 * 获取状态名称
 */
const getStatusName = (status: string) => {
  const statusMap: Record<string, string> = {
    'draft': '草稿',
    'submitted': '已提交',
    'approved': '已审核',
    'rejected': '已退回'
  }
  return statusMap[status] || status
}

/**
 * 获取状态颜色
 */
const getStatusColor = (status: string) => {
  const colorMap: Record<string, string> = {
    'draft': '#969799',
    'submitted': '#1989fa',
    'approved': '#07c160',
    'rejected': '#ee0a24'
  }
  return colorMap[status] || '#969799'
}

/**
 * 获取周报列表
 */
const fetchReportList = async () => {
  loading.value = true
  showLoadingToast({ message: '加载中...', forbidClick: true })
  
  try {
    const params: Record<string, any> = { 
      page: 0,
      size: 100
    }
    
    const user = userStore.getUser()
    if (user && user.name) {
      params.created_by = user.name
    }
    
    const response = await api.get<unknown, ApiResponse<{ content: WeeklyReportItem[] }>>('/weekly-report', { 
      params
    })
    
    if (response.code === 200) {
      reportList.value = response.data?.content || []
    }
  } catch (error) {
    console.error('Failed to fetch report list:', error)
  } finally {
    loading.value = false
    closeToast()
  }
}

/**
 * 查看详情
 */
const handleView = (item: WeeklyReportItem) => {
  router.push(`/weekly-report-detail/${item.id}`)
}

/**
 * 编辑
 */
const handleEdit = (item: WeeklyReportItem) => {
  router.push(`/weekly-report-edit/${item.id}`)
}

const handleBack = () => {
  goBack()
}

const handleUserChanged = () => {
  fetchReportList()
}

onMounted(() => {
  fetchReportList()
})
</script>

<template>
  <div class="weekly-report-list-page">
    <van-nav-bar 
      title="已报部门周报" 
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
        <UserSelector @userChanged="handleUserChanged" />
      </template>
    </van-nav-bar>
    
    <van-pull-refresh v-model="loading" @refresh="fetchReportList">
      <van-list :loading="loading" :finished="true">
        <div class="report-list">
          <div 
            v-for="item in reportList" 
            :key="item.id"
            class="report-card"
          >
            <div class="card-header">
              <van-tag :color="getStatusColor(item.status)" size="medium">
                {{ getStatusName(item.status) }}
              </van-tag>
              <span class="report-id">{{ item.report_id }}</span>
            </div>
            <div class="card-body">
              <div class="info-row">
                <span class="label">项目名称</span>
                <span class="value">{{ item.project_name }}</span>
              </div>
              <div class="info-row">
                <span class="label">项目编号</span>
                <span class="value">{{ item.project_id }}</span>
              </div>
              <div class="info-row">
                <span class="label">部门周报周期</span>
                <span class="value">{{ formatDate(item.week_start_date) }} ~ {{ formatDate(item.week_end_date) }}</span>
              </div>
              <div class="info-row">
                <span class="label">提交人</span>
                <span class="value">{{ item.created_by || '-' }}</span>
              </div>
              <div class="info-row" v-if="item.work_summary">
                <span class="label">工作总结</span>
                <span class="value">{{ item.work_summary }}</span>
              </div>
              <div class="info-row">
                <span class="label">提交时间</span>
                <span class="value">{{ formatDateTime(item.created_at) }}</span>
              </div>
            </div>
            <div class="card-footer">
              <van-button 
                type="primary" 
                size="small"
                @click="handleView(item)"
              >
                查看详情
              </van-button>
              <van-button 
                v-if="item.status === 'draft' || item.status === 'rejected'"
                type="default" 
                size="small"
                @click="handleEdit(item)"
              >
                编辑
              </van-button>
            </div>
          </div>
        </div>
        <van-empty v-if="!loading && reportList.length === 0" description="暂无数据" />
      </van-list>
    </van-pull-refresh>
  </div>
</template>

<style scoped>
.weekly-report-list-page {
  min-height: 100vh;
  background-color: #f5f7fa;
}

.report-list {
  padding: 12px;
}

.report-card {
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
}

.report-id {
  font-weight: 600;
  color: #323233;
  font-size: 13px;
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
  min-width: 80px;
}

.nav-left {
  display: flex;
  align-items: center;
  gap: 4px;
  color: #323233;
}

:deep(.van-pull-refresh) {
  min-height: calc(100vh - 46px);
}
</style>
