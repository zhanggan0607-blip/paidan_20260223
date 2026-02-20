<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { showLoadingToast, closeToast, showImagePreview } from 'vant'
import api from '../utils/api'
import type { ApiResponse } from '../types'
import { formatDate, formatDateTime } from '../config/constants'
import UserSelector from '../components/UserSelector.vue'

interface WeeklyReportDetail {
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
  images: string
  manager_signature: string
  manager_sign_time: string
  status: string
  approved_by: string
  approved_at: string
  reject_reason: string
  created_by: string
  created_at: string
  updated_at: string
}

interface OperationLogItem {
  id: number
  work_order_type: string
  work_order_id: number
  work_order_no: string
  operator_name: string
  operator_id: number | null
  operation_type_code: string
  operation_type_name: string
  operation_remark: string | null
  created_at: string
}

const route = useRoute()
const router = useRouter()

const loading = ref(false)
const reportDetail = ref<WeeklyReportDetail | null>(null)
const imageList = ref<string[]>([])
const operationLogs = ref<OperationLogItem[]>([])
const loadingLogs = ref(false)

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
 * 格式化操作时间
 */
const formatOperationTime = (dateStr: string) => {
  if (!dateStr) return '-'
  const date = new Date(dateStr)
  const year = date.getFullYear()
  const month = String(date.getMonth() + 1).padStart(2, '0')
  const day = String(date.getDate()).padStart(2, '0')
  const hours = String(date.getHours()).padStart(2, '0')
  const minutes = String(date.getMinutes()).padStart(2, '0')
  return `${year}-${month}-${day} ${hours}:${minutes}`
}

/**
 * 获取操作日志
 */
const fetchOperationLogs = async (reportId: number) => {
  if (!reportId) return
  loadingLogs.value = true
  try {
    const response = await api.get<unknown, ApiResponse<OperationLogItem[]>>(`/weekly-report/${reportId}/operation-logs`)
    if (response.code === 200) {
      operationLogs.value = response.data || []
    }
  } catch (error) {
    console.error('获取操作日志失败:', error)
    operationLogs.value = []
  } finally {
    loadingLogs.value = false
  }
}

/**
 * 获取周报详情
 */
const fetchReportDetail = async () => {
  const id = route.params.id
  if (!id) return
  
  loading.value = true
  showLoadingToast({ message: '加载中...', forbidClick: true })
  
  try {
    const response = await api.get<unknown, ApiResponse<WeeklyReportDetail>>(`/weekly-report/${id}`)
    
    if (response.code === 200 && response.data) {
      reportDetail.value = response.data
      
      if (response.data.images) {
        try {
          const imgs = JSON.parse(response.data.images)
          imageList.value = Array.isArray(imgs) ? imgs : []
        } catch {
          imageList.value = []
        }
      }
      
      fetchOperationLogs(response.data.id)
    }
  } catch (error) {
    console.error('Failed to fetch report detail:', error)
  } finally {
    loading.value = false
    closeToast()
  }
}

/**
 * 预览图片
 */
const handlePreviewImage = (index: number) => {
  showImagePreview({
    images: imageList.value,
    startPosition: index
  })
}

const handleBack = () => {
  router.back()
}

onMounted(() => {
  fetchReportDetail()
})
</script>

<template>
  <div class="weekly-report-detail-page">
    <van-nav-bar 
      title="部门周报详情" 
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
        <UserSelector />
      </template>
    </van-nav-bar>
    
    <div class="detail-content" v-if="reportDetail">
      <van-cell-group inset title="基本信息">
        <van-cell title="部门周报编号" :value="reportDetail.report_id" />
        <van-cell title="项目名称" :value="reportDetail.project_name" />
        <van-cell title="项目编号" :value="reportDetail.project_id" />
        <van-cell title="部门周报周期" :value="`${formatDate(reportDetail.week_start_date)} ~ ${formatDate(reportDetail.week_end_date)}`" />
        <van-cell title="填报日期" :value="formatDate(reportDetail.report_date)" />
        <van-cell title="提交人" :value="reportDetail.created_by || '-'" />
        <van-cell title="提交时间" :value="formatDateTime(reportDetail.created_at)" />
        <van-cell title="状态">
          <template #value>
            <van-tag :color="getStatusColor(reportDetail.status)">
              {{ getStatusName(reportDetail.status) }}
            </van-tag>
          </template>
        </van-cell>
      </van-cell-group>

      <van-cell-group inset title="工作内容">
        <van-cell title="本周工作总结" :label="reportDetail.work_summary" />
        <van-cell v-if="reportDetail.work_content" title="具体工作内容" :label="reportDetail.work_content" />
        <van-cell v-if="reportDetail.next_week_plan" title="下周工作计划" :label="reportDetail.next_week_plan" />
      </van-cell-group>

      <van-cell-group inset title="问题与建议" v-if="reportDetail.issues || reportDetail.suggestions">
        <van-cell v-if="reportDetail.issues" title="存在问题" :label="reportDetail.issues" />
        <van-cell v-if="reportDetail.suggestions" title="建议措施" :label="reportDetail.suggestions" />
      </van-cell-group>

      <van-cell-group inset title="现场照片" v-if="imageList.length > 0">
        <div class="image-section">
          <div class="image-list">
            <div 
              v-for="(img, index) in imageList" 
              :key="index"
              class="image-item"
              @click="handlePreviewImage(index)"
            >
              <img :src="img" alt="现场照片" loading="lazy" />
            </div>
          </div>
        </div>
      </van-cell-group>

      <van-cell-group inset title="签字信息" v-if="reportDetail.manager_signature">
        <van-cell title="部门经理签字">
          <template #value>
            <img :src="reportDetail.manager_signature" class="signature-img" loading="lazy" />
          </template>
        </van-cell>
        <van-cell v-if="reportDetail.manager_sign_time" title="签字时间" :value="formatDateTime(reportDetail.manager_sign_time)" />
      </van-cell-group>

      <van-cell-group inset title="审核信息" v-if="reportDetail.approved_by || reportDetail.reject_reason">
        <van-cell v-if="reportDetail.approved_by" title="审核人" :value="reportDetail.approved_by" />
        <van-cell v-if="reportDetail.approved_at" title="审核时间" :value="formatDateTime(reportDetail.approved_at)" />
        <van-cell v-if="reportDetail.reject_reason" title="退回原因" :value="reportDetail.reject_reason" />
      </van-cell-group>

      <van-cell-group inset title="内部确认区" v-if="operationLogs.length > 0 || !loadingLogs">
        <div class="operation-log-section">
          <div v-if="loadingLogs" class="loading-container">
            <van-loading size="20px">加载中...</van-loading>
          </div>
          <div v-else-if="operationLogs.length === 0" class="empty-container">
            暂无操作记录
          </div>
          <div v-else class="timeline">
            <div 
              v-for="(log, index) in operationLogs" 
              :key="log.id" 
              class="timeline-item"
              :class="{ 'last': index === operationLogs.length - 1 }"
            >
              <div class="timeline-dot"></div>
              <div class="timeline-content">
                <span class="timeline-time">{{ formatOperationTime(log.created_at) }}</span>
                <span class="timeline-operator">{{ log.operator_name }}</span>
                <span class="timeline-action">{{ log.operation_type_name }}</span>
              </div>
            </div>
          </div>
        </div>
      </van-cell-group>
    </div>
    
    <van-empty v-if="!loading && !reportDetail" description="暂无数据" />
  </div>
</template>

<style scoped>
.weekly-report-detail-page {
  min-height: 100vh;
  background-color: #f5f7fa;
}

.detail-content {
  padding-bottom: 20px;
}

:deep(.van-cell-group--inset) {
  margin: 12px;
}

.nav-left {
  display: flex;
  align-items: center;
  gap: 4px;
  color: #323233;
}

.image-section {
  padding: 12px 16px;
}

.image-list {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
}

.image-item {
  width: 80px;
  height: 80px;
  border-radius: 8px;
  overflow: hidden;
}

.image-item img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.signature-img {
  max-width: 150px;
  max-height: 60px;
}

:deep(.van-cell__label) {
  white-space: pre-wrap;
  word-break: break-all;
}

.operation-log-section {
  padding: 12px 16px;
}

.loading-container,
.empty-container {
  padding: 16px;
  text-align: center;
  color: #969799;
  font-size: 14px;
}

.timeline {
  position: relative;
  padding-left: 20px;
}

.timeline::before {
  content: '';
  position: absolute;
  left: 6px;
  top: 0;
  bottom: 0;
  width: 2px;
  background: #ebedf0;
}

.timeline-item {
  position: relative;
  padding-bottom: 12px;
}

.timeline-item.last {
  padding-bottom: 0;
}

.timeline-dot {
  position: absolute;
  left: -16px;
  top: 4px;
  width: 10px;
  height: 10px;
  border-radius: 50%;
  background: #1989fa;
  border: 2px solid #fff;
  box-shadow: 0 0 0 2px #1989fa;
}

.timeline-content {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
}

.timeline-time {
  font-size: 13px;
  color: #666;
  font-family: monospace;
}

.timeline-operator {
  font-size: 13px;
  color: #333;
  font-weight: 500;
}

.timeline-action {
  font-size: 12px;
  color: #1989fa;
  background: #e8f4ff;
  padding: 2px 6px;
  border-radius: 4px;
}
</style>
