<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { showLoadingToast, closeToast, showFailToast } from 'vant'
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

const router = useRouter()
const route = useRoute()

const loading = ref(false)
const logDetail = ref<MaintenanceLogDetail | null>(null)
const imageList = ref<string[]>([])

/**
 * 获取日志类型名称
 */
const getLogTypeName = (logType: string) => {
  const typeMap: Record<string, string> = {
    'spot': '用工日志',
    'inspection': '巡检日志',
    'repair': '维修日志'
  }
  return typeMap[logType] || logType
}

/**
 * 获取日志详情
 */
const fetchLogDetail = async () => {
  const id = route.params.id
  if (!id) {
    showFailToast('日志ID不存在')
    return
  }
  
  loading.value = true
  showLoadingToast({ message: '加载中...', forbidClick: true })
  
  try {
    const response = await api.get<unknown, ApiResponse<MaintenanceLogDetail>>(`/maintenance-log/${id}`)
    
    if (response.code === 200 && response.data) {
      logDetail.value = response.data
      
      if (response.data.images) {
        try {
          imageList.value = JSON.parse(response.data.images)
        } catch {
          imageList.value = []
        }
      }
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
 * 预览图片
 */
const handlePreviewImage = (index: number) => {
  if (imageList.value.length > 0) {
    const { ImagePreview } = require('vant')
    ImagePreview({
      images: imageList.value,
      startPosition: index
    })
  }
}

const handleBack = () => {
  router.push('/maintenance-log-list')
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
              <img :src="img" alt="现场照片" />
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
</style>
