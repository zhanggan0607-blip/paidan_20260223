<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { showLoadingToast, closeToast, showSuccessToast, showFailToast } from 'vant'
import api from '../utils/api'
import type { ApiResponse } from '../types'
import { formatDate } from '../config/constants'
import UserSelector from '../components/UserSelector.vue'

const router = useRouter()

const formData = ref({
  reportId: '',
  reportDate: formatDate(new Date()),
  workSummary: '',
  nextWeekPlan: '',
  issues: '',
  suggestions: ''
})

const showReportDatePicker = ref(false)
const loading = ref(false)
const minDate = new Date(2020, 0, 1)
const maxDate = new Date(2030, 11, 31)
const today = new Date()
const currentReportDate = ref<string[]>([
  today.getFullYear().toString(),
  (today.getMonth() + 1).toString().padStart(2, '0'),
  today.getDate().toString().padStart(2, '0')
])

/**
 * 生成周报编号
 */
const generateReportId = async () => {
  try {
    const response = await api.get<unknown, ApiResponse<{ report_id: string }>>('/weekly-report/generate-id', {
      params: { report_date: formData.value.reportDate }
    })
    
    if (response.code === 200 && response.data) {
      formData.value.reportId = response.data.report_id
    }
  } catch (error) {
    console.error('Failed to generate report id:', error)
    const todayStr = formData.value.reportDate.replace(/-/g, '')
    formData.value.reportId = `ZB-${todayStr}-01`
  }
}

/**
 * 填报日期选择确认
 */
const handleReportDateConfirm = ({ selectedValues }: { selectedValues: string[] }) => {
  if (selectedValues && selectedValues.length === 3) {
    const year = selectedValues[0]
    const month = selectedValues[1]?.padStart(2, '0') || '01'
    const day = selectedValues[2]?.padStart(2, '0') || '01'
    formData.value.reportDate = `${year}-${month}-${day}`
    generateReportId()
  }
  showReportDatePicker.value = false
}

/**
 * 提交表单
 */
const handleSubmit = async () => {
  if (!formData.value.workSummary) {
    showFailToast('请输入本周工作总结')
    return
  }
  
  loading.value = true
  showLoadingToast({ message: '提交中...', forbidClick: true })
  
  try {
    const response = await api.post<unknown, ApiResponse<null>>('/weekly-report', {
      report_id: formData.value.reportId,
      report_date: formData.value.reportDate,
      work_summary: formData.value.workSummary,
      next_week_plan: formData.value.nextWeekPlan,
      issues: formData.value.issues,
      suggestions: formData.value.suggestions
    })
    
    if (response.code === 200) {
      showSuccessToast('提交成功')
      router.push('/')
    } else {
      showFailToast(response.message || '提交失败')
    }
  } catch (error) {
    console.error('Failed to submit:', error)
    showFailToast('提交失败，请重试')
  } finally {
    loading.value = false
    closeToast()
  }
}

onMounted(() => {
  generateReportId()
})
</script>

<template>
  <div class="weekly-report-fill-page">
    <van-nav-bar 
      title="部门周报填报" 
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
        <UserSelector />
      </template>
    </van-nav-bar>
    
    <van-cell-group inset title="基本信息">
      <van-field 
        v-model="formData.reportDate"
        label="填报日期"
        placeholder="选择填报日期"
        is-link
        required
        readonly
        @click="showReportDatePicker = true"
      />
      <van-field 
        v-model="formData.reportId"
        label="周报编号"
        placeholder="自动生成"
        readonly
        disabled
      />
    </van-cell-group>

    <van-cell-group inset title="工作内容">
      <van-field 
        v-model="formData.workSummary" 
        label="本周工作总结" 
        placeholder="请输入本周工作总结"
        type="textarea"
        rows="4"
        maxlength="1000"
        show-word-limit
        required
      />
      <van-field 
        v-model="formData.nextWeekPlan" 
        label="下周工作计划" 
        placeholder="请输入下周工作计划"
        type="textarea"
        rows="3"
        maxlength="1000"
        show-word-limit
      />
      <van-field 
        v-model="formData.issues" 
        label="存在问题" 
        placeholder="请输入存在问题"
        type="textarea"
        rows="3"
        maxlength="500"
        show-word-limit
      />
      <van-field 
        v-model="formData.suggestions" 
        label="建议措施" 
        placeholder="请输入建议措施"
        type="textarea"
        rows="3"
        maxlength="500"
        show-word-limit
      />
    </van-cell-group>

    <div class="submit-btn">
      <van-button type="primary" block :loading="loading" @click="handleSubmit">
        提交
      </van-button>
    </div>

    <van-popup v-model:show="showReportDatePicker" position="bottom" round>
      <van-date-picker
        title="选择填报日期"
        v-model="currentReportDate"
        :min-date="minDate"
        :max-date="maxDate"
        @confirm="handleReportDateConfirm"
        @cancel="showReportDatePicker = false"
      />
    </van-popup>
  </div>
</template>

<style scoped>
.weekly-report-fill-page {
  min-height: 100vh;
  background-color: #f5f7fa;
}

:deep(.van-cell-group--inset) {
  margin: 12px;
}

.submit-btn {
  padding: 16px;
  margin-top: 16px;
}

.nav-left {
  display: flex;
  align-items: center;
  gap: 4px;
  color: #323233;
}
</style>
