<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { showLoadingToast, closeToast, showSuccessToast, showFailToast } from 'vant'
import api from '../utils/api'
import type { ApiResponse } from '../types'
import { formatDate } from '../config/constants'

const router = useRouter()

const formData = ref({
  projectName: '',
  workDate: formatDate(new Date()),
  workContent: '',
  workers: '',
  remark: ''
})

const showDatePicker = ref(false)
const loading = ref(false)

const handleSubmit = async () => {
  if (!formData.value.projectName) {
    showFailToast('请输入项目名称')
    return
  }
  if (!formData.value.workContent) {
    showFailToast('请输入工作内容')
    return
  }
  
  loading.value = true
  showLoadingToast({ message: '提交中...', forbidClick: true })
  
  try {
    const response = await api.post<unknown, ApiResponse<null>>('/work-plan/spot-work/quick-fill', formData.value)
    if (response.success) {
      showSuccessToast('提交成功')
      router.back()
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

const handleDateConfirm = (value: Date) => {
  formData.value.workDate = formatDate(value)
  showDatePicker.value = false
}
</script>

<template>
  <div class="quick-fill-page">
    <van-nav-bar 
      title="零星用工快捷填报" 
      left-arrow 
      fixed 
      placeholder 
      @click-left="router.back()" 
    />
    
    <van-cell-group inset title="基本信息">
      <van-field 
        v-model="formData.projectName" 
        label="项目名称" 
        placeholder="请输入项目名称"
        required
      />
      <van-field 
        v-model="formData.workDate" 
        label="工作日期" 
        placeholder="请选择日期"
        readonly
        is-link
        @click="showDatePicker = true"
      />
      <van-field 
        v-model="formData.workContent" 
        label="工作内容" 
        placeholder="请输入工作内容"
        type="textarea"
        rows="3"
        required
      />
      <van-field 
        v-model="formData.workers" 
        label="施工人员" 
        placeholder="请输入施工人员"
      />
      <van-field 
        v-model="formData.remark" 
        label="备注" 
        placeholder="请输入备注"
        type="textarea"
        rows="2"
      />
    </van-cell-group>

    <div class="submit-btn">
      <van-button type="primary" block :loading="loading" @click="handleSubmit">
        提交
      </van-button>
    </div>

    <van-popup v-model:show="showDatePicker" position="bottom" round>
      <van-date-picker 
        title="选择日期" 
        @confirm="handleDateConfirm"
        @cancel="showDatePicker = false"
      />
    </van-popup>
  </div>
</template>

<style scoped>
.quick-fill-page {
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
</style>
