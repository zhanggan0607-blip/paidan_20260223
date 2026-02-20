<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { showLoadingToast, closeToast } from 'vant'
import api from '../utils/api'
import type { ApiResponse } from '../types'
import { formatDate, formatDateTime } from '../config/constants'
import UserSelector from '../components/UserSelector.vue'
import { authService, type User } from '../services/auth'

interface MaintenanceLogItem {
  id: number
  log_id: string
  project_id: string
  project_name: string
  log_type: string
  log_date: string
  work_content: string
  images: string
  remark: string
  created_by: string
  created_at: string
  updated_at: string
}

const router = useRouter()

const loading = ref(false)
const logList = ref<MaintenanceLogItem[]>([])
const currentUser = ref<User | null>(null)

const pageTitle = computed(() => {
  if (authService.isDepartmentManager(currentUser.value)) {
    return '已填报部门周报'
  }
  return '已填报日志'
})

/**
 * 根据日志编号长度计算字体大小
 */
const getLogIdFontSize = (logId: string) => {
  if (!logId) return 14
  const len = logId.length
  if (len <= 18) return 14
  if (len <= 22) return 12
  if (len <= 26) return 11
  if (len <= 30) return 10
  if (len <= 35) return 9
  if (len <= 40) return 8
  return 7
}

/**
 * 获取日志类型名称
 */
const getLogTypeName = (logType: string) => {
  const typeMap: Record<string, string> = {
    'maintenance': '维修日志',
    'spot': '维修日志',
    'repair': '维修日志'
  }
  return typeMap[logType] || '维修日志'
}

/**
 * 获取日志列表
 */
const fetchLogList = async () => {
  loading.value = true
  showLoadingToast({ message: '加载中...', forbidClick: true })
  
  try {
    const params: Record<string, any> = { 
      page: 0,
      size: 100
    }
    
    // 部门经理能看到所有数据，普通员工只能看到自己的数据
    if (currentUser.value && currentUser.value.name && !authService.isDepartmentManager(currentUser.value)) {
      params.created_by = currentUser.value.name
    }
    
    const response = await api.get<unknown, ApiResponse<{ content: MaintenanceLogItem[] }>>('/maintenance-log', { 
      params
    })
    
    if (response.code === 200) {
      logList.value = response.data?.content || []
    }
  } catch (error) {
    console.error('Failed to fetch log list:', error)
  } finally {
    loading.value = false
    closeToast()
  }
}

/**
 * 查看详情
 */
const handleView = (item: MaintenanceLogItem) => {
  router.push(`/maintenance-log-detail/${item.id}`)
}

const handleBack = () => {
  router.push('/')
}

const handleUserChanged = () => {
  fetchLogList()
}

onMounted(() => {
  currentUser.value = authService.getCurrentUser()
  fetchLogList()
})
</script>

<template>
  <div class="maintenance-log-page">
    <van-nav-bar 
      :title="pageTitle" 
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
    
    <van-pull-refresh v-model="loading" @refresh="fetchLogList">
      <van-list :loading="loading" :finished="true">
        <div class="log-list">
          <div 
            v-for="item in logList" 
            :key="item.id"
            class="log-card"
          >
            <div class="card-header">
              <van-tag type="success" size="medium">
                {{ getLogTypeName(item.log_type) }}
              </van-tag>
              <span class="log-id" :style="{ fontSize: getLogIdFontSize(item.log_id) + 'px' }">
                {{ item.log_id }}
              </span>
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
                <span class="label">日志日期</span>
                <span class="value">{{ formatDate(item.log_date) }}</span>
              </div>
              <div class="info-row" v-if="item.work_content">
                <span class="label">工作内容</span>
                <span class="value">{{ item.work_content }}</span>
              </div>
              <div class="info-row" v-if="item.remark">
                <span class="label">备注</span>
                <span class="value">{{ item.remark }}</span>
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
            </div>
          </div>
        </div>
        <van-empty v-if="!loading && logList.length === 0" description="暂无维保日志" />
      </van-list>
    </van-pull-refresh>
  </div>
</template>

<style scoped>
.maintenance-log-page {
  min-height: 100vh;
  background-color: #f5f7fa;
}

.log-list {
  padding: 12px;
}

.log-card {
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

.log-id {
  font-weight: 600;
  color: #323233;
  white-space: nowrap;
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
