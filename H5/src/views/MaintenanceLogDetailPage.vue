<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { showLoadingToast, closeToast, showFailToast, showImagePreview } from 'vant'
import api from '../utils/api'
import type { ApiResponse } from '../types'
import { formatDate, formatDateTime } from '../config/constants'
import UserSelector from '../components/UserSelector.vue'

interface MaintenanceLogDetail {
  id: number
  log_id: string
  project_id: string
  project_name: string
  log_type: string
  log_date: string
  work_content: string
  images: string | null
  remark: string
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

const router = useRouter()
const route = useRoute()

const loading = ref(false)
const logDetail = ref<MaintenanceLogDetail | null>(null)
const imageList = ref<string[]>([])
const operationLogs = ref<OperationLogItem[]>([])

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
 * 获取日志详情
 */
const fetchLogDetail = async () => {
  const id = route.params.id
  console.log('fetchLogDetail called, id:', id, 'route.params:', route.params)
  if (!id) {
    showFailToast('日志ID不存在')
    return
  }
  
  loading.value = true
  showLoadingToast({ message: '加载中...', forbidClick: true })
  
  try {
    const url = `/maintenance-log/${id}`
    console.log('Fetching detail from:', url)
    const response = await api.get<unknown, ApiResponse<MaintenanceLogDetail>>(url)
    console.log('Detail response:', response)
    
    if (response.code === 200 && response.data) {
      logDetail.value = response.data
      
      if (response.data.images) {
        try {
          imageList.value = JSON.parse(response.data.images)
        } catch {
          imageList.value = []
        }
      }
      
      // 获取操作日志
      fetchOperationLogs(Number(id))
    } else {
      showFailToast(response.message || '获取详情失败')
    }
  } catch (error) {
    console.error('Failed to fetch log detail:', error)
    showFailToast('获取详情失败')
  } finally {
    loading.value = false
    closeToast()
  }
}

/**
 * 获取操作日志
 */
const fetchOperationLogs = async (logId: number) => {
  try {
    const response = await api.get<unknown, ApiResponse<OperationLogItem[]>>(`/maintenance-log/${logId}/operation-logs`)
    if (response.code === 200) {
      operationLogs.value = response.data || []
    }
  } catch (error) {
    console.error('Failed to fetch operation logs:', error)
  }
}

/**
 * 预览图片
 */
const handlePreviewImage = (index: number) => {
  if (imageList.value.length > 0) {
    showImagePreview({
      images: imageList.value,
      startPosition: index
    })
  }
}

const handleBack = () => {
  router.back()
}

onMounted(() => {
  fetchLogDetail()
})
</script>

<template>
  <div class="maintenance-log-detail-page">
    <van-nav-bar 
      title="维保日志详情" 
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
    
    <div v-if="logDetail" class="detail-content">
      <van-cell-group inset title="基本信息">
        <van-cell title="日志编号" :value="logDetail.log_id" />
        <van-cell title="日志类型" :value="getLogTypeName(logDetail.log_type)" />
        <van-cell title="项目名称" :value="logDetail.project_name" />
        <van-cell title="项目编号" :value="logDetail.project_id" />
        <van-cell title="日志日期" :value="formatDate(logDetail.log_date)" />
        <van-cell title="提交人" :value="logDetail.created_by || '-'" />
        <van-cell title="提交时间" :value="formatDateTime(logDetail.created_at)" />
      </van-cell-group>
      
      <van-cell-group inset title="工作内容" v-if="logDetail.work_content">
        <div class="content-box">
          {{ logDetail.work_content }}
        </div>
      </van-cell-group>
      
      <van-cell-group inset title="备注" v-if="logDetail.remark">
        <div class="content-box">
          {{ logDetail.remark }}
        </div>
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
      
      <van-cell-group inset title="内部确认区" v-if="operationLogs.length > 0">
        <div class="operation-log-section">
          <div class="timeline">
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
    
    <van-empty v-else-if="!loading" description="暂无数据" />
  </div>
</template>

<style scoped>
.maintenance-log-detail-page {
  min-height: 100vh;
  background-color: #f5f7fa;
}

.detail-content {
  padding-bottom: 20px;
}

:deep(.van-cell-group--inset) {
  margin: 12px;
}

:deep(.van-cell__title) {
  flex: none;
  width: 28%;
  min-width: 90px;
}

:deep(.van-cell__value) {
  flex: 1;
  width: 72%;
}

.content-box {
  padding: 12px 16px;
  font-size: 14px;
  color: #323233;
  line-height: 1.6;
  white-space: pre-wrap;
  word-break: break-all;
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

.nav-left {
  display: flex;
  align-items: center;
  gap: 4px;
  color: #323233;
}

.operation-log-section {
  padding: 12px 16px;
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
  background: #e0e0e0;
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
