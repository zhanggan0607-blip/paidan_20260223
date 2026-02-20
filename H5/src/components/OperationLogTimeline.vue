<script setup lang="ts">
import { ref, onMounted, watch } from 'vue'
import api from '../utils/api'
import type { ApiResponse } from '../types'

interface OperationLog {
  id: number
  work_order_type: string
  work_order_id: number
  work_order_no: string
  operator_name: string
  operator_id: number | null
  operation_type_code: string
  operation_type_name: string
  color_code: string | null
  operation_remark: string | null
  created_at: string
}

const props = defineProps<{
  workOrderType: string
  workOrderId: number
}>()

const logs = ref<OperationLog[]>([])
const loading = ref(false)

/**
 * 格式化日期时间为 年-月-日 时:分 格式
 * @param dateStr ISO日期字符串
 */
const formatDateTime = (dateStr: string): string => {
  if (!dateStr) return '-'
  try {
    const date = new Date(dateStr)
    const year = date.getFullYear()
    const month = String(date.getMonth() + 1).padStart(2, '0')
    const day = String(date.getDate()).padStart(2, '0')
    const hours = String(date.getHours()).padStart(2, '0')
    const minutes = String(date.getMinutes()).padStart(2, '0')
    return `${year}-${month}-${day} ${hours}:${minutes}`
  } catch {
    return dateStr
  }
}

/**
 * 获取操作类型的颜色
 * @param log 操作日志
 */
const getOperationTypeColor = (log: OperationLog): string => {
  return log.color_code || '#969799'
}

const fetchLogs = async () => {
  if (!props.workOrderId) return
  
  loading.value = true
  try {
    const response = await api.get<unknown, ApiResponse<OperationLog[]>>(
      `/work-order-operation-log?work_order_type=${props.workOrderType}&work_order_id=${props.workOrderId}`
    )
    if (response.code === 200) {
      logs.value = response.data || []
    }
  } catch (error) {
    console.error('Failed to fetch operation logs:', error)
  } finally {
    loading.value = false
  }
}

watch(() => props.workOrderId, () => {
  if (props.workOrderId) {
    fetchLogs()
  }
}, { immediate: true })

onMounted(() => {
  if (props.workOrderId) {
    fetchLogs()
  }
})

defineExpose({
  refresh: fetchLogs
})
</script>

<template>
  <van-cell-group inset title="内部确认区" v-if="logs.length > 0 || loading">
    <div class="operation-log-container">
      <div v-if="loading" class="loading-container">
        <van-loading size="20px">加载中...</van-loading>
      </div>
      <div v-else-if="logs.length === 0" class="empty-container">
        暂无操作记录
      </div>
      <div v-else class="timeline">
        <div 
          v-for="log in logs" 
          :key="log.id" 
          class="timeline-item"
        >
          <div 
            class="timeline-dot" 
            :style="{ background: getOperationTypeColor(log) }"
          ></div>
          <div class="timeline-content">
            <div class="timeline-header">
              <span class="operator-name">{{ log.operator_name }}</span>
              <span 
                class="operation-type" 
                :style="{ background: getOperationTypeColor(log) }"
              >
                {{ log.operation_type_name }}
              </span>
            </div>
            <div class="timeline-time">{{ formatDateTime(log.created_at) }}</div>
            <div v-if="log.operation_remark" class="timeline-remark">
              {{ log.operation_remark }}
            </div>
          </div>
        </div>
      </div>
    </div>
  </van-cell-group>
</template>

<style scoped>
.operation-log-container {
  padding: 12px 16px;
  background: #fff;
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
  top: 8px;
  bottom: 8px;
  width: 1px;
  background: #ebedf0;
}

.timeline-item {
  position: relative;
  padding-bottom: 16px;
}

.timeline-item:last-child {
  padding-bottom: 0;
}

.timeline-dot {
  position: absolute;
  left: -20px;
  top: 6px;
  width: 12px;
  height: 12px;
  border-radius: 50%;
  border: 2px solid #fff;
  box-shadow: 0 0 0 1px #ebedf0;
}

.timeline-content {
  background: #f7f8fa;
  border-radius: 8px;
  padding: 10px 12px;
}

.timeline-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 4px;
}

.operator-name {
  font-size: 14px;
  font-weight: 500;
  color: #323233;
}

.operation-type {
  font-size: 12px;
  padding: 2px 8px;
  border-radius: 4px;
  color: #fff;
}

.timeline-time {
  font-size: 12px;
  color: #969799;
}

.timeline-remark {
  margin-top: 6px;
  font-size: 12px;
  color: #646566;
  line-height: 1.5;
}
</style>
