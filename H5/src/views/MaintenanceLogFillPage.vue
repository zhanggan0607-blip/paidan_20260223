<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { showLoadingToast, closeToast, showSuccessToast, showFailToast, showConfirmDialog } from 'vant'
import api from '../utils/api'
import type { ApiResponse } from '../types'
import { formatDate } from '../config/constants'
import UserSelector from '../components/UserSelector.vue'
import { userStore } from '../stores/userStore'
import { processPhoto } from '../utils/watermark'

// TODO: 维保日志填报页面 - 考虑加入草稿自动保存功能
// FIXME: 图片上传失败时没有重试机制
// TODO: 表单数据应该支持本地缓存，防止页面刷新丢失
interface ProjectInfo {
  id: number
  project_id: string
  project_name: string
  client_name: string
}

interface LogImage {
  id?: number
  file: File | null
  url: string
  description: string
}

const router = useRouter()

const pageTitle = '维保日志填报'
const formData = ref({
  projectId: '',
  projectName: '',
  logType: 'maintenance',
  logDate: formatDate(new Date()),
  workContent: '',
  remark: ''
})

const projectList = ref<ProjectInfo[]>([])
const showProjectPicker = ref(false)
const showDatePicker = ref(false)
const loading = ref(false)
const images = ref<LogImage[]>([])
const minDate = new Date(2020, 0, 1)
const maxDate = new Date(2030, 11, 31)
const today = new Date()
const currentDate = ref<string[]>([
  today.getFullYear().toString(),
  (today.getMonth() + 1).toString().padStart(2, '0'),
  today.getDate().toString().padStart(2, '0')
])

const selectedProjectName = ref('')

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
 * 项目选择确认
 */
const handleProjectConfirm = ({ selectedOptions, selectedValues }: { selectedOptions: Array<{ text: string; value: string }>, selectedValues: string[] }) => {
  const selectedValue = selectedValues && selectedValues.length > 0 ? selectedValues[0] : null
  if (selectedValue) {
    const project = projectList.value.find(p => p.id.toString() === selectedValue)
    if (project) {
      formData.value.projectId = project.project_id
      formData.value.projectName = project.project_name
      selectedProjectName.value = project.project_name
    }
  } else if (selectedOptions && selectedOptions.length > 0) {
    const selected = selectedOptions[0]
    if (selected) {
      const project = projectList.value.find(p => p.id.toString() === selected.value)
      if (project) {
        formData.value.projectId = project.project_id
        formData.value.projectName = project.project_name
        selectedProjectName.value = project.project_name
      }
    }
  }
  showProjectPicker.value = false
}

/**
 * 日期选择确认
 */
const handleDateConfirm = ({ selectedValues }: { selectedValues: string[] }) => {
  if (selectedValues && selectedValues.length === 3) {
    const year = selectedValues[0]
    const month = selectedValues[1]?.padStart(2, '0') || '01'
    const day = selectedValues[2]?.padStart(2, '0') || '01'
    formData.value.logDate = `${year}-${month}-${day}`
  }
  showDatePicker.value = false
}

/**
 * 拍照上传
 */
const handleTakePhoto = async () => {
  const input = document.createElement('input')
  input.type = 'file'
  input.accept = 'image/*'
  input.capture = 'environment'
  
  input.onchange = async (e: Event) => {
    const target = e.target as HTMLInputElement
    const file = target.files?.[0]
    if (file) {
      showLoadingToast({ message: '处理中...', forbidClick: true })
      try {
        const userName = userStore.getUser()?.name || '未知用户'
        const processedFile = await processPhoto(file, userName)
        const url = URL.createObjectURL(processedFile)
        images.value.push({
          file: processedFile,
          url: url,
          description: ''
        })
      } catch (error) {
        console.error('Failed to process photo:', error)
        const url = URL.createObjectURL(file)
        images.value.push({
          file: file,
          url: url,
          description: ''
        })
      } finally {
        closeToast()
      }
    }
  }
  
  input.click()
}

/**
 * 删除图片
 */
const handleDeleteImage = async (index: number) => {
  try {
    await showConfirmDialog({
      title: '提示',
      message: '请确认是否要删除该图片？'
    })
    const img = images.value[index]
    if (img && img.url && img.url.startsWith('blob:')) {
      URL.revokeObjectURL(img.url)
    }
    images.value.splice(index, 1)
  } catch {
    // 用户取消
  }
}

/**
 * 上传单张图片
 */
const uploadImage = async (image: LogImage): Promise<string | null> => {
  if (!image.file) return null
  
  const formDataObj = new FormData()
  formDataObj.append('file', image.file)
  
  try {
    const response = await api.post<unknown, ApiResponse<{ url: string }>>('/upload', formDataObj, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    })
    if (response.code === 200 && response.data) {
      return response.data.url
    }
    return null
  } catch (error) {
    console.error('Failed to upload image:', error)
    return null
  }
}

/**
 * 提交表单
 */
const handleSubmit = async () => {
  if (!formData.value.projectName) {
    showFailToast('请选择项目名称')
    return
  }
  if (!formData.value.workContent) {
    showFailToast('请输入工作内容')
    return
  }
  
  loading.value = true
  showLoadingToast({ message: '提交中...', forbidClick: true })
  
  try {
    const uploadedUrls: string[] = []
    for (const image of images.value) {
      if (image.file) {
        const url = await uploadImage(image)
        if (url) {
          uploadedUrls.push(url)
        }
      }
    }
    
    const response = await api.post<unknown, ApiResponse<null>>('/maintenance-log', {
      project_id: formData.value.projectId,
      project_name: formData.value.projectName,
      log_type: formData.value.logType,
      log_date: formData.value.logDate,
      work_content: formData.value.workContent,
      remark: formData.value.remark,
      images: uploadedUrls
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

const projectColumns = computed(() => {
  return projectList.value.map(p => ({
    text: p.project_name,
    value: p.id.toString(),
    project_id: p.project_id,
    client_name: p.client_name
  }))
})

onMounted(() => {
  fetchProjectList()
})
</script>

<template>
  <div class="maintenance-log-fill-page">
    <van-nav-bar 
      :title="pageTitle" 
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
      <div class="two-column-form">
        <div class="form-row">
          <van-cell 
            :title="selectedProjectName || '选择项目'"
            label="项目名称"
            is-link
            required
            @click="showProjectPicker = true"
            class="form-cell"
          />
          <van-cell 
            v-if="formData.projectId"
            :title="formData.projectId"
            label="项目编号"
            class="form-cell"
          />
        </div>
        <div class="form-row">
          <van-cell 
            :title="formData.logDate"
            label="填写日期"
            is-link
            required
            @click="showDatePicker = true"
            class="form-cell"
          />
        </div>
      </div>
      <van-field 
        v-model="formData.workContent" 
        label="工作内容" 
        placeholder="请输入工作内容"
        type="textarea"
        rows="3"
        maxlength="800"
        show-word-limit
        required
      />
      <van-field 
        v-model="formData.remark" 
        label="备注" 
        placeholder="请输入备注"
        type="textarea"
        rows="2"
      />
    </van-cell-group>

    <van-cell-group inset title="现场照片">
      <div class="image-section">
        <div class="image-list">
          <div 
            v-for="(image, index) in images" 
            :key="index"
            class="image-item"
          >
            <img :src="image.url" alt="现场照片" loading="lazy" />
            <van-icon 
              name="delete" 
              class="delete-icon"
              @click="handleDeleteImage(index)"
            />
          </div>
          <div class="image-add" @click="handleTakePhoto">
            <van-icon name="photograph" size="24" />
            <span>拍照</span>
          </div>
        </div>
      </div>
    </van-cell-group>

    <div class="submit-btn">
      <van-button type="primary" block :loading="loading" @click="handleSubmit">
        提交
      </van-button>
    </div>

    <van-popup v-model:show="showProjectPicker" position="bottom" round destroy-on-close>
      <van-picker
        title="选择项目"
        :columns="projectColumns"
        :loading="projectList.length === 0"
        @confirm="handleProjectConfirm"
        @cancel="showProjectPicker = false"
      />
    </van-popup>

    <van-popup v-model:show="showDatePicker" position="bottom" round>
      <van-date-picker
        title="选择填写日期"
        v-model="currentDate"
        :min-date="minDate"
        :max-date="maxDate"
        @confirm="handleDateConfirm"
        @cancel="showDatePicker = false"
      />
    </van-popup>
  </div>
</template>

<style scoped>
.maintenance-log-fill-page {
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

.image-section {
  padding: 12px 16px;
}

.image-list {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
}

.image-item {
  position: relative;
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

.delete-icon {
  position: absolute;
  top: 4px;
  right: 4px;
  background: rgba(0, 0, 0, 0.5);
  color: #fff;
  border-radius: 50%;
  padding: 4px;
  font-size: 14px;
}

.image-add {
  width: 80px;
  height: 80px;
  border: 1px dashed #dcdee0;
  border-radius: 8px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  color: #969799;
  gap: 4px;
}

.image-add span {
  font-size: 12px;
}

.two-column-form {
  padding: 0;
}

.form-row {
  display: flex;
  border-bottom: 1px solid #ebedf0;
}

.form-row:last-child {
  border-bottom: none;
}

.form-cell {
  flex: 1;
  min-width: 0;
}

.form-cell :deep(.van-cell) {
  padding: 10px 12px;
}

.form-cell :deep(.van-cell__title) {
  font-size: 12px;
  color: #969799;
}

.form-cell :deep(.van-cell__value) {
  font-size: 14px;
  color: #323233;
}
</style>
