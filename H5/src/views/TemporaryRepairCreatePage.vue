<script setup lang="ts">
import { ref, onMounted, computed, onActivated } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { showLoadingToast, closeToast, showToast, showSuccessToast, showFailToast, showConfirmDialog } from 'vant'
import api from '../utils/api'
import type { ApiResponse } from '../types'
import { formatDate } from '../config/constants'
import UserSelector from '../components/UserSelector.vue'
import { userStore, type User } from '../stores/userStore'
import { processPhoto, getCurrentLocation } from '../utils/watermark'
import { useNavigation } from '../composables/useNavigation'

interface ProjectInfo {
  id: number
  project_id: string
  project_name: string
  client_name: string
  client_contact?: string
  client_contact_info?: string
}

const router = useRouter()
const route = useRoute()
const { goBack } = useNavigation()

const loading = ref(false)
const userReady = ref(false)

const formData = ref({
  projectId: '',
  projectIdDisplay: '',
  projectName: '',
  clientName: '',
  clientContact: '',
  clientContactInfo: '',
  planStartDate: formatDate(new Date()),
  planEndDate: formatDate(new Date()),
  remarks: ''
})

const projectList = ref<ProjectInfo[]>([])
const showProjectPicker = ref(false)
const showDateRangePicker = ref(false)
const selectedProjectName = ref('')
const submitLoading = ref(false)
const generatedWorkId = ref('')

const currentPhotos = ref<string[]>([])
const showPhotoPopup = ref(false)
const signature = ref('')

const minDate = new Date(2020, 0, 1)
const maxDate = new Date(2030, 11, 31)

const dateDisplayText = computed(() => {
  if (formData.value.planStartDate === formData.value.planEndDate) {
    return formData.value.planStartDate
  }
  return `${formData.value.planStartDate} 至 ${formData.value.planEndDate}`
})

/**
 * 获取项目列表
 */
const fetchProjectList = async () => {
  try {
    const response = await api.get<unknown, ApiResponse<ProjectInfo[]>>('/project-info/all/list')
    if (response.code === 200) {
      projectList.value = response.data || []
    }
  } catch (error) {
    console.error('Failed to fetch project list:', error)
  }
}

/**
 * 处理项目选择确认
 */
const handleProjectConfirm = ({ selectedOptions, selectedValues }: { selectedOptions: Array<{ text: string; value: string }>, selectedValues: string[] }) => {
  const selectedValue = selectedValues && selectedValues.length > 0 ? selectedValues[0] : null
  if (selectedValue) {
    const project = projectList.value.find(p => p.id.toString() === selectedValue)
    if (project) {
      formData.value.projectId = project.project_id
      formData.value.projectIdDisplay = project.project_id
      formData.value.projectName = project.project_name
      formData.value.clientName = project.client_name || ''
      formData.value.clientContact = project.client_contact || ''
      formData.value.clientContactInfo = project.client_contact_info || ''
      selectedProjectName.value = project.project_name
    }
  } else if (selectedOptions && selectedOptions.length > 0) {
    const selected = selectedOptions[0]
    if (selected) {
      const project = projectList.value.find(p => p.id.toString() === selected.value)
      if (project) {
        formData.value.projectId = project.project_id
        formData.value.projectIdDisplay = project.project_id
        formData.value.projectName = project.project_name
        formData.value.clientName = project.client_name || ''
        formData.value.clientContact = project.client_contact || ''
        formData.value.clientContactInfo = project.client_contact_info || ''
        selectedProjectName.value = project.project_name
      }
    }
  }
  showProjectPicker.value = false
}

/**
 * 处理日期范围选择确认
 */
const handleDateRangeConfirm = (values: Date[]) => {
  if (values && values.length === 2) {
    formData.value.planStartDate = formatDate(values[0])
    formData.value.planEndDate = formatDate(values[1])
  }
  showDateRangePicker.value = false
}

/**
 * 提交临时维修单
 */
const handleSubmit = async () => {
  if (!formData.value.projectName) {
    showFailToast('请选择项目名称')
    return
  }
  if (!formData.value.remarks) {
    showFailToast('请输入报修内容')
    return
  }
  if (currentPhotos.value.length === 0) {
    showFailToast('请上传现场照片')
    return
  }
  
  submitLoading.value = true
  showLoadingToast({ message: '提交中...', forbidClick: true })
  
  try {
    const today = new Date()
    const todayStr = today.toISOString().slice(0, 10).replace(/-/g, '')
    const prefix = `WX-${formData.value.projectId}-${todayStr}`
    
    const countResponse = await api.get<unknown, ApiResponse<any>>('/temporary-repair', { 
      params: { page: 0, size: 1, repair_id: prefix }
    })
    let sequence = '01'
    if (countResponse.code === 200) {
      const items = countResponse.data?.content || []
      const matchingItems = items.filter((item: any) => item.repair_id && item.repair_id.startsWith(prefix))
      if (matchingItems.length > 0) {
        const lastId = matchingItems[0].repair_id
        const lastSeq = parseInt(lastId.split('-').pop() || '0')
        sequence = String(lastSeq + 1).padStart(2, '0')
      }
    }
    
    const repairId = `${prefix}-${sequence}`
    
    const response = await api.post<unknown, ApiResponse<{repair_id: string}>>('/temporary-repair', {
      repair_id: repairId,
      project_id: formData.value.projectId,
      project_name: formData.value.projectName,
      plan_start_date: formData.value.planStartDate,
      plan_end_date: formData.value.planEndDate,
      client_name: formData.value.clientName,
      client_contact: formData.value.clientContact,
      client_contact_info: formData.value.clientContactInfo,
      remarks: formData.value.remarks,
      photos: JSON.stringify(currentPhotos.value),
      signature: signature.value,
      status: '待确认'
    })
    
    if (response.code === 200) {
      generatedWorkId.value = repairId
      showSuccessToast({
        message: `提交成功\n工单号：${repairId}`,
        duration: 3000
      })
      formData.value = {
        projectId: '',
        projectIdDisplay: '',
        projectName: '',
        clientName: '',
        clientContact: '',
        clientContactInfo: '',
        planStartDate: formatDate(new Date()),
        planEndDate: formatDate(new Date()),
        remarks: ''
      }
      selectedProjectName.value = ''
      currentPhotos.value = []
      signature.value = ''
      localStorage.removeItem('temporary_repair_create_signature')
      
      router.push('/temporary-repair')
    } else {
      showFailToast(response.message || '提交失败')
    }
  } catch (error) {
    console.error('Failed to submit:', error)
    showFailToast('提交失败，请重试')
  } finally {
    submitLoading.value = false
    closeToast()
  }
}

const handleBack = () => {
  goBack('/')
}

const handleUserReady = (_user: User) => {
  userReady.value = true
  fetchProjectList()
}

const handleUserChanged = (_user: User) => {
  fetchProjectList()
}

const projectColumns = computed(() => {
  return projectList.value.map(p => ({
    text: p.project_name,
    value: p.id.toString(),
    project_id: p.project_id,
    client_name: p.client_name,
    client_contact: p.client_contact,
    client_contact_info: p.client_contact_info
  }))
})

/**
 * 处理现场图片上传弹窗
 */
const handlePhotoUpload = () => {
  showPhotoPopup.value = true
}

/**
 * 拍照上传
 */
const handlePhotoCapture = () => {
  const input = document.createElement('input')
  input.type = 'file'
  input.accept = 'image/*'
  input.capture = 'environment'
  
  input.onchange = async (e: Event) => {
    const target = e.target as HTMLInputElement
    const file = target.files?.[0]
    if (!file) return
    
    showLoadingToast({ message: '处理中...', forbidClick: true })
    
    try {
      const userName = userStore.getUser()?.name || '未知用户'
      const location = await getCurrentLocation()
      const processedFile = await processPhoto(file, {
        userName,
        includeLocation: true,
        latitude: location?.latitude,
        longitude: location?.longitude
      })
      
      const formDataObj = new FormData()
      formDataObj.append('file', processedFile)
      
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

/**
 * 删除图片
 */
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

/**
 * 保存图片
 */
const handlePhotoSave = () => {
  showPhotoPopup.value = false
  showSuccessToast('保存成功')
}

/**
 * 跳转签字页面
 */
const handleSignature = () => {
  router.push({
    path: '/signature',
    query: { 
      from: route.fullPath,
      type: 'temporary-repair-create'
    }
  })
}

/**
 * 加载签字
 */
const loadSignature = () => {
  const signatureData = localStorage.getItem('temporary_repair_create_signature')
  if (signatureData) {
    signature.value = signatureData
  }
}

onMounted(() => {
  fetchProjectList()
  loadSignature()
})

onActivated(() => {
  loadSignature()
})
</script>

<template>
  <div class="temporary-repair-create-page">
    <van-nav-bar 
      title="新增临时维修单" 
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
        <UserSelector @userChanged="handleUserChanged" @ready="handleUserReady" />
      </template>
    </van-nav-bar>
    
    <van-cell-group inset title="基本信息" class="form-group">
      <van-cell 
        :title="selectedProjectName || '选择项目'"
        label="项目名称"
        is-link
        required
        @click="showProjectPicker = true"
      />
      <van-cell 
        v-if="formData.projectIdDisplay"
        :title="formData.projectIdDisplay"
        label="项目编号"
      />
      <van-cell 
        :title="dateDisplayText"
        label="维修周期"
        is-link
        required
        @click="showDateRangePicker = true"
      />
      <van-cell 
        v-if="formData.clientName"
        title="客户单位"
        :value="formData.clientName"
      />
      <van-field 
        v-model="formData.clientContact" 
        label="客户联系人" 
        placeholder="请输入客户联系人"
      />
      <van-field 
        v-model="formData.clientContactInfo" 
        label="客户联系电话" 
        placeholder="请输入客户联系电话"
        type="tel"
      />
      <van-field 
        v-model="formData.remarks" 
        label="报修内容" 
        placeholder="请输入报修内容"
        type="textarea"
        rows="3"
        maxlength="500"
        show-word-limit
        required
      />
    </van-cell-group>

    <van-cell-group inset title="图片上传" class="form-group">
      <van-cell is-link @click="handlePhotoUpload" required>
        <template #title>
          <span>现场图片</span>
        </template>
        <template #value>
          <span :class="currentPhotos.length > 0 ? 'status-done' : 'status-action'">
            {{ currentPhotos.length > 0 ? `已上传${currentPhotos.length}张` : '去上传' }}
          </span>
        </template>
      </van-cell>
    </van-cell-group>

    <van-cell-group inset title="签字确认" class="form-group">
      <van-cell is-link @click="handleSignature">
        <template #title>
          <span>用户签字</span>
        </template>
        <template #value>
          <img v-if="signature" :src="signature" class="signature-preview" loading="lazy" />
          <span v-else class="status-pending">待签字</span>
        </template>
      </van-cell>
    </van-cell-group>

    <div class="submit-btn">
      <van-button type="primary" block :loading="submitLoading" @click="handleSubmit">
        提交
      </van-button>
    </div>
    
    <div v-if="generatedWorkId" class="work-id-result">
      <van-notice-bar
        :text="'工单已生成，单号：' + generatedWorkId"
        left-icon="info-o"
        color="#1989fa"
        background="#ecf9ff"
      />
    </div>

    <van-popup v-model:show="showProjectPicker" position="bottom" round>
      <van-picker
        title="选择项目"
        :columns="projectColumns"
        @confirm="handleProjectConfirm"
        @cancel="showProjectPicker = false"
      />
    </van-popup>

    <van-calendar 
      v-model:show="showDateRangePicker" 
      type="range"
      title="选择维修周期"
      :min-date="minDate"
      :max-date="maxDate"
      :poppable="true"
      :show-confirm="true"
      @confirm="handleDateRangeConfirm"
      color="#1989fa"
    />

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
                <img :src="photo" alt="现场照片" loading="lazy" />
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
.temporary-repair-create-page {
  min-height: 100vh;
  background-color: #f5f7fa;
}

.form-group {
  margin: 12px;
}

.submit-btn {
  padding: 16px;
  margin-top: 16px;
}

.work-id-result {
  padding: 0 16px 16px;
}

.nav-left {
  display: flex;
  align-items: center;
  gap: 4px;
  color: #323233;
}

:deep(.van-cell-group--inset) {
  margin: 12px;
}

.status-done {
  display: inline-block;
  padding: 2px 8px;
  font-size: 12px;
  color: #fff;
  background-color: #07c160;
  border-radius: 4px;
}

.status-pending {
  display: inline-block;
  padding: 2px 8px;
  font-size: 12px;
  color: #fff;
  background-color: #1989fa;
  border-radius: 4px;
}

.status-action {
  display: inline-block;
  padding: 3px 10px;
  font-size: 14px;
  color: #fff;
  background-color: #ff976a;
  border-radius: 4px;
}

.signature-preview {
  width: 80px;
  height: 40px;
  object-fit: contain;
  background-color: #fff;
  border: 1px solid #e5e5e5;
  border-radius: 4px;
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
</style>
