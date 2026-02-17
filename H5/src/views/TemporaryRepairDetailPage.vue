<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { showLoadingToast, closeToast, showSuccessToast, showFailToast, showConfirmDialog } from 'vant'
import api from '../utils/api'
import type { ApiResponse } from '../types'
import { WORK_STATUS, formatDate } from '../config/constants'
import UserSelector from '../components/UserSelector.vue'

const router = useRouter()
const route = useRoute()

interface RepairDetail {
  id: number
  repair_id: string
  plan_type: string
  project_id: string
  project_name: string
  plan_start_date: string
  plan_end_date: string
  client_name: string
  client_contact: string
  client_contact_info: string
  address: string
  maintenance_personnel: string
  status: string
  remarks: string
  fault_description: string
  solution: string
  photos: string[]
  signature: string
  created_at: string
  updated_at: string
}

const loading = ref(false)
const detail = ref<RepairDetail | null>(null)

const showDatePicker = ref(false)
const currentDate = ref(['2024', '01', '01'])
const formData = ref({
  execution_date: '',
  fault_description: '',
  solution: '',
  remarks: '',
  signature: ''
})

const currentPhotos = ref<string[]>([])
const showPhotoPopup = ref(false)

const isEditable = computed(() => {
  return detail.value?.status === WORK_STATUS.NOT_STARTED || 
         detail.value?.status === WORK_STATUS.RETURNED
})

const canSubmit = computed(() => {
  return formData.value.fault_description && 
         formData.value.solution
})

const minDate = computed(() => {
  if (detail.value?.plan_start_date) {
    return new Date(detail.value.plan_start_date)
  }
  return new Date(2020, 0, 1)
})

const maxDate = computed(() => {
  return new Date()
})

const fetchDetail = async () => {
  const id = route.params.id
  if (!id) return
  
  loading.value = true
  showLoadingToast({ message: '加载中...', forbidClick: true })
  
  try {
    const response = await api.get<unknown, ApiResponse<RepairDetail>>(`/temporary-repair/${id}`)
    if (response.code === 200) {
      detail.value = response.data
      if (response.data) {
        formData.value.fault_description = response.data.fault_description || ''
        formData.value.solution = response.data.solution || ''
        formData.value.remarks = response.data.remarks || ''
        formData.value.signature = response.data.signature || ''
        currentPhotos.value = response.data.photos || []
      }
    }
  } catch (error) {
    console.error('Failed to fetch detail:', error)
    showFailToast('加载失败')
  } finally {
    loading.value = false
    closeToast()
  }
}

const loadSignature = () => {
  const signatureData = localStorage.getItem('temporary_repair_signature')
  if (signatureData) {
    formData.value.signature = signatureData
  }
}

const handlePhotoUpload = () => {
  if (!isEditable.value) return
  showPhotoPopup.value = true
}

const handlePhotoCapture = () => {
  const input = document.createElement('input')
  input.type = 'file'
  input.accept = 'image/*'
  input.capture = 'environment'
  
  input.onchange = async (e: Event) => {
    const target = e.target as HTMLInputElement
    const file = target.files?.[0]
    if (!file) return
    
    showLoadingToast({ message: '上传中...', forbidClick: true })
    
    try {
      const formDataObj = new FormData()
      formDataObj.append('file', file)
      
      const response = await api.post<unknown, ApiResponse<{ url: string }>>('/upload', formDataObj, {
        headers: { 'Content-Type': 'multipart/form-data' }
      })
      
      if (response.code === 200 && response.data) {
        currentPhotos.value.push(response.data.url)
        showSuccessToast('上传成功')
      }
    } catch (error) {
      console.error('Failed to upload photo:', error)
      showFailToast('上传失败')
    } finally {
      closeToast()
    }
  }
  
  input.click()
}

const handleRemovePhoto = async (index: number) => {
  try {
    await showConfirmDialog({
      title: '提示',
      message: '是否要删除，新增的图片会重新打水印'
    })
    currentPhotos.value.splice(index, 1)
  } catch {
  }
}

const handlePhotoSave = () => {
  showPhotoPopup.value = false
  showSuccessToast('保存成功')
}

const handleSignature = () => {
  router.push({
    path: '/signature',
    query: { 
      from: route.fullPath,
      type: 'temporary-repair'
    }
  })
}

const handleDateConfirm = ({ selectedValues }: { selectedValues: string[] }) => {
  formData.value.execution_date = selectedValues.join('-')
  showDatePicker.value = false
}

const handleSubmit = async () => {
  if (!canSubmit.value) {
    showFailToast('请填写故障描述和解决方案')
    return
  }

  try {
    await showConfirmDialog({
      title: '提示',
      message: '确认提交工单吗？'
    })
    
    showLoadingToast({ message: '提交中...', forbidClick: true })
    
    const submitData = {
      ...formData.value,
      photos: currentPhotos.value,
      status: WORK_STATUS.PENDING_CONFIRM
    }
    
    const response = await api.put<unknown, ApiResponse<any>>(`/temporary-repair/${detail.value?.id}`, submitData)
    
    if (response.code === 200) {
      localStorage.removeItem('temporary_repair_signature')
      showSuccessToast('提交成功')
      router.back()
    }
  } catch (error) {
    if (error !== 'cancel') {
      console.error('Failed to submit:', error)
      showFailToast('提交失败')
    }
  } finally {
    closeToast()
  }
}

const handleSave = async () => {
  showLoadingToast({ message: '保存中...', forbidClick: true })
  
  try {
    const saveData = {
      ...formData.value,
      photos: currentPhotos.value
    }
    
    const response = await api.put<unknown, ApiResponse<any>>(`/temporary-repair/${detail.value?.id}`, saveData)
    
    if (response.code === 200) {
      showSuccessToast('保存成功')
    }
  } catch (error) {
    console.error('Failed to save:', error)
    showFailToast('保存失败')
  } finally {
    closeToast()
  }
}

onMounted(() => {
  fetchDetail()
  loadSignature()
})
</script>

<template>
  <div class="temporary-repair-detail">
    <van-nav-bar 
      title="临时维修单" 
      fixed 
      placeholder 
    >
      <template #left>
        <div class="nav-left" @click="router.back()">
          <van-icon name="arrow-left" />
          <span>返回</span>
        </div>
      </template>
      <template #right>
        <UserSelector />
      </template>
    </van-nav-bar>
    
    <div class="content" v-if="detail">
      <van-cell-group inset title="基本资料">
        <van-cell title="项目名称" :value="detail.project_name" />
        <van-cell title="工单编号" :value="detail.repair_id" />
        <van-cell title="维保开始日期" :value="formatDate(detail.plan_start_date)" />
        <van-cell title="维保截止日期" :value="formatDate(detail.plan_end_date)" />
        <van-cell title="客户单位" :value="detail.client_name || '-'" />
        <van-cell title="客户联系人" :value="detail.client_contact || '-'" />
        <van-cell title="客户联系方式" :value="detail.client_contact_info || '-'" />
      </van-cell-group>

      <van-cell-group inset title="维修内容">
        <van-field
          v-model="formData.fault_description"
          rows="3"
          autosize
          label="故障描述"
          type="textarea"
          placeholder="请输入故障描述"
          show-word-limit
          maxlength="500"
          :readonly="!isEditable"
        />
        
        <van-field
          v-model="formData.solution"
          rows="3"
          autosize
          label="解决方案"
          type="textarea"
          placeholder="请输入解决方案"
          show-word-limit
          maxlength="500"
          :readonly="!isEditable"
        />
      </van-cell-group>

      <van-cell-group inset title="图片上传">
        <van-cell is-link @click="handlePhotoUpload" :disabled="!isEditable">
          <template #title>
            <span>现场图片</span>
          </template>
          <template #value>
            <span :class="currentPhotos.length > 0 ? 'status-done' : 'status-pending'">
              {{ currentPhotos.length > 0 ? `已上传${currentPhotos.length}张` : '去上传' }}
            </span>
          </template>
        </van-cell>
      </van-cell-group>

      <van-cell-group inset title="其他信息">
        <van-cell 
          title="执行日期" 
          :value="formData.execution_date || '请选择'" 
          is-link 
          @click="showDatePicker = true"
          :disabled="!isEditable"
        />
        
        <van-field
          v-model="formData.remarks"
          rows="2"
          autosize
          label="备注说明"
          type="textarea"
          placeholder="请输入备注说明"
          show-word-limit
          maxlength="200"
          :readonly="!isEditable"
        />
      </van-cell-group>

      <van-cell-group inset title="用户确认">
        <van-cell is-link @click="handleSignature" :disabled="!isEditable">
          <template #title>
            <span>用户签字</span>
          </template>
          <template #value>
            <img v-if="formData.signature" :src="formData.signature" class="signature-preview" />
            <span v-else class="status-pending">待签字</span>
          </template>
        </van-cell>
      </van-cell-group>

      <div class="action-buttons" v-if="isEditable">
        <van-button type="default" size="large" @click="handleSave">保存</van-button>
        <van-button type="primary" size="large" @click="handleSubmit" :disabled="!canSubmit">提交</van-button>
      </div>
    </div>
    
    <van-empty v-else-if="!loading" description="暂无数据" />
    
    <van-popup v-model:show="showDatePicker" position="bottom" round>
      <van-date-picker
        v-model="currentDate"
        title="选择执行日期"
        :min-date="minDate"
        :max-date="maxDate"
        @confirm="handleDateConfirm"
        @cancel="showDatePicker = false"
      />
    </van-popup>

    <van-popup 
      v-model:show="showPhotoPopup" 
      position="bottom" 
      round 
      :style="{ height: '60%' }"
    >
      <div class="popup-content">
        <div class="popup-header">
          <span class="popup-title">现场图片</span>
          <van-icon name="cross" @click="showPhotoPopup = false" />
        </div>
        <div class="popup-body">
          <div class="photo-section">
            <div class="photo-grid">
              <div 
                v-for="(photo, index) in currentPhotos" 
                :key="index" 
                class="photo-item"
              >
                <img :src="photo" alt="现场照片" />
                <van-icon name="delete" class="delete-icon" @click.stop="handleRemovePhoto(index)" />
              </div>
              <div class="photo-add" @click="handlePhotoCapture" v-if="currentPhotos.length < 9">
                <van-icon name="photograph" size="24" />
                <span>拍照</span>
              </div>
            </div>
            <div class="photo-tip">只支持拍照，最多上传9张</div>
          </div>
        </div>
        <div class="popup-footer">
          <van-button type="primary" block @click="handlePhotoSave">保存</van-button>
        </div>
      </div>
    </van-popup>
  </div>
</template>

<style scoped>
.temporary-repair-detail {
  min-height: 100vh;
  background-color: #f5f7fa;
}

.content {
  padding-bottom: 20px;
}

:deep(.van-cell-group--inset) {
  margin: 12px;
}

.status-done {
  color: #07c160;
}

.status-pending {
  color: #1989fa;
}

.photo-section {
  padding: 12px 16px;
}

.photo-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 8px;
}

.photo-item {
  position: relative;
  aspect-ratio: 1;
  border-radius: 8px;
  overflow: hidden;
}

.photo-item img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.delete-icon {
  position: absolute;
  top: 4px;
  right: 4px;
  font-size: 18px;
  color: #ee0a24;
  background: rgba(255, 255, 255, 0.8);
  border-radius: 50%;
  padding: 2px;
}

.photo-add {
  aspect-ratio: 1;
  border: 1px dashed #dcdee0;
  border-radius: 8px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 4px;
  color: #969799;
  font-size: 12px;
}

.photo-tip {
  margin-top: 8px;
  font-size: 12px;
  color: #969799;
}

.signature-preview {
  width: 80px;
  height: 40px;
  object-fit: contain;
}

.action-buttons {
  padding: 12px 16px;
  background: #fff;
  display: flex;
  flex-direction: row;
  gap: 12px;
  width: 100%;
  box-sizing: border-box;
  margin-top: 12px;
}

.action-buttons :deep(.van-button) {
  flex: 1;
  margin: 0;
  height: 44px;
  font-size: 16px;
}

.popup-content {
  height: 100%;
  display: flex;
  flex-direction: column;
}

.popup-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px;
  border-bottom: 1px solid #ebedf0;
}

.popup-title {
  font-size: 16px;
  font-weight: 500;
}

.popup-body {
  flex: 1;
  overflow-y: auto;
  padding: 12px 0;
}

.popup-footer {
  padding: 12px;
  padding-bottom: max(12px, env(safe-area-inset-bottom));
  border-top: 1px solid #ebedf0;
}

.popup-footer .van-button {
  min-height: 44px;
  font-size: 16px;
  border-radius: 8px;
}
</style>
