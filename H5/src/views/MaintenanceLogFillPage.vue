<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import {
  showLoadingToast,
  closeToast,
  showSuccessToast,
  showFailToast,
  showConfirmDialog,
  showNotify,
} from 'vant'
import { maintenanceLogService, projectInfoService, uploadService } from '../services'
import type { ProjectInfo } from '../types/models'
import { formatDate, processPhoto, getCurrentLocation } from '@sstcp/shared'
import { userStore } from '../stores/userStore'
import { useNavigation } from '../composables/useNavigation'

interface LogImage {
  id?: number
  file: File | null
  url: string
  description: string
}

const { goBack } = useNavigation()

const formData = ref({
  projectId: '',
  projectName: '',
  logType: 'maintenance',
  logDate: formatDate(new Date()),
  workContent: '',
  remark: '',
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
  today.getDate().toString().padStart(2, '0'),
])

const selectedProjectName = ref('')
const isEditMode = ref(false)
const editLogId = ref<number | null>(null)

/**
 * 获取项目列表
 */
const fetchProjectList = async () => {
  try {
    const response = await projectInfoService.getAll()
    if (response.code === 200) {
      projectList.value = response.data || []
    }
  } catch (error) {
    console.error('Failed to fetch project list:', error)
  }
}

/**
 * 检查当天是否已有维保日志
 */
const checkTodayLog = async () => {
  try {
    const response = await maintenanceLogService.getToday()
    if (response.code === 200 && response.data) {
      isEditMode.value = true
      editLogId.value = response.data.id
      formData.value.projectId = response.data.project_id || ''
      formData.value.projectName = response.data.project_name || ''
      formData.value.logDate = response.data.log_date || formatDate(new Date())
      formData.value.workContent = response.data.work_content || ''
      formData.value.remark = response.data.remark || ''
      selectedProjectName.value = response.data.project_name || ''
      
      if (response.data.images) {
        const imageUrls = typeof response.data.images === 'string' 
          ? JSON.parse(response.data.images) 
          : response.data.images
        images.value = imageUrls.map((url: string) => ({
          url,
          file: null,
          description: '',
        }))
      }
    }
  } catch (error) {
    console.error('Failed to check today log:', error)
  }
}

/**
 * 项目选择确认
 */
const handleProjectConfirm = ({
  selectedOptions,
  selectedValues,
}: {
  selectedOptions: Array<{ text: string; value: string }>
  selectedValues: string[]
}) => {
  const selectedValue = selectedValues && selectedValues.length > 0 ? selectedValues[0] : null
  if (selectedValue) {
    const project = projectList.value.find((p) => p.id.toString() === selectedValue)
    if (project) {
      formData.value.projectId = project.project_id
      formData.value.projectName = project.project_name
      selectedProjectName.value = project.project_name
    }
  } else if (selectedOptions && selectedOptions.length > 0) {
    const selected = selectedOptions[0]
    if (selected) {
      const project = projectList.value.find((p) => p.id.toString() === selected.value)
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
  const ua = navigator.userAgent.toLowerCase()
  const isIOS = /iphone|ipad|ipod/.test(ua) || (navigator.platform === 'MacIntel' && navigator.maxTouchPoints > 1)
  const isDingTalk = /dingtalk|ddwebview|dd/.test(ua)
  const isMobile = /mobile|android|iphone|ipad|ipod|blackberry|iemobile|opera mini/i.test(ua)
  const useBase64Upload = isIOS || isDingTalk || isMobile || navigator.maxTouchPoints > 1

  const input = document.createElement('input')
  input.type = 'file'
  input.accept = 'image/*'
  if (!useBase64Upload) {
    input.capture = 'environment'
  }

  input.onchange = async (e: Event) => {
    const target = e.target as HTMLInputElement
    const file = target.files?.[0]
    if (file) {
      showLoadingToast({ message: '处理中...', forbidClick: true })
      try {
        let fileToUpload = file
        
        if (useBase64Upload) {
          if (file.size > 500 * 1024) {
            showLoadingToast({ message: '压缩中...', forbidClick: true })
            const compressedBlob = await compressImage(file, 500)
            fileToUpload = new File([compressedBlob], file.name, { type: 'image/jpeg' })
          }
          
          const reader = new FileReader()
          const base64Data = await new Promise<string>((resolve, reject) => {
            reader.onload = (e) => resolve(e.target?.result as string)
            reader.onerror = reject
            reader.readAsDataURL(fileToUpload)
          })
          
          const response = await uploadService.uploadImageBase64(base64Data, fileToUpload.name)
          if (response.code === 200 && response.data) {
            images.value.push({
              file: null,
              url: response.data.url,
              description: '',
            })
          }
        } else {
          const userName = userStore.getUser()?.name || '未知用户'
          const location = await getCurrentLocation()
          const processedFile = await processPhoto(file, {
            userName,
            includeLocation: true,
            latitude: location?.latitude,
            longitude: location?.longitude,
          })
          const url = URL.createObjectURL(processedFile)
          images.value.push({
            file: processedFile,
            url: url,
            description: '',
          })
        }
      } catch (error) {
        console.error('Failed to process photo:', error)
        const url = URL.createObjectURL(file)
        images.value.push({
          file: file,
          url: url,
          description: '',
        })
      } finally {
        closeToast()
      }
    }
  }

  input.click()
}

/**
 * 压缩图片到指定大小（KB）
 * @param file 原文件
 * @param maxSizeKB 最大大小（KB）
 * @returns 压缩后的Blob
 */
const compressImage = (file: File, maxSizeKB: number): Promise<Blob> => {
  return new Promise((resolve, reject) => {
    const img = new Image()
    const reader = new FileReader()
    
    reader.onload = (e) => {
      img.src = e.target?.result as string
    }
    
    img.onload = () => {
      const canvas = document.createElement('canvas')
      const ctx = canvas.getContext('2d')!
      
      let width = img.width
      let height = img.height
      
      const maxDimension = 1920
      if (width > maxDimension || height > maxDimension) {
        if (width > height) {
          height = Math.round((height * maxDimension) / width)
          width = maxDimension
        } else {
          width = Math.round((width * maxDimension) / height)
          height = maxDimension
        }
      }
      
      canvas.width = width
      canvas.height = height
      ctx.drawImage(img, 0, 0, width, height)
      
      canvas.toBlob(
        (blob) => {
          if (!blob) {
            reject(new Error('图片压缩失败'))
            return
          }
          
          if (blob.size <= maxSizeKB * 1024) {
            resolve(blob)
            return
          }
          
          const quality = Math.sqrt((maxSizeKB * 1024) / blob.size)
          canvas.toBlob(
            (compressedBlob) => {
              if (compressedBlob) {
                resolve(compressedBlob)
              } else {
                resolve(blob)
              }
            },
            'image/jpeg',
            Math.max(0.1, Math.min(quality, 0.9))
          )
        },
        'image/jpeg',
        0.9
      )
    }
    
    img.onerror = () => {
      reject(new Error('图片加载失败'))
    }
    
    reader.onerror = () => {
      reject(new Error('文件读取失败'))
    }
    
    reader.readAsDataURL(file)
  })
}

/**
 * 删除图片
 */
const handleDeleteImage = async (index: number) => {
  try {
    await showConfirmDialog({
      title: '提示',
      message: '请确认是否要删除该图片？',
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

  try {
    const response = await uploadService.uploadFile(image.file)
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
      } else if (image.url && !image.url.startsWith('blob:')) {
        uploadedUrls.push(image.url)
      }
    }

    const submitData = {
      project_id: formData.value.projectId,
      project_name: formData.value.projectName,
      log_date: formData.value.logDate,
      work_content: formData.value.workContent || undefined,
      images: uploadedUrls.length > 0 ? uploadedUrls : undefined,
      remark: formData.value.remark || undefined,
    }

    let response
    if (isEditMode.value && editLogId.value) {
      response = await maintenanceLogService.update(editLogId.value, submitData)
    } else {
      response = await maintenanceLogService.create(submitData)
    }

    if (response.code === 200) {
      showSuccessToast(isEditMode.value ? '修改成功' : '提交成功')
      showNotify({
        type: 'warning',
        message: '日志只可当日可修改',
        duration: 4000,
        position: 'top',
      })
      setTimeout(() => {
        goBack()
      }, 500)
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

const handleBack = () => {
  goBack()
}

const projectColumns = computed(() => {
  return projectList.value.map((p) => ({
    text: p.project_name,
    value: p.id.toString(),
    project_id: p.project_id,
    client_name: p.client_name,
  }))
})

onMounted(async () => {
  showLoadingToast({ message: '加载中...', forbidClick: true })
  try {
    await fetchProjectList()
    await checkTodayLog()
  } finally {
    closeToast()
  }
})
</script>

<template>
  <div class="maintenance-log-fill-page">
    <van-nav-bar fixed placeholder @click-left="handleBack">
      <template #left>
        <div class="nav-left">
          <van-icon name="arrow-left" />
          <span>返回</span>
        </div>
      </template>
    </van-nav-bar>

    <van-cell-group inset title="基本信息">
      <div class="two-column-form">
        <div class="form-row">
          <van-cell
            :title="selectedProjectName || '选择项目'"
            label="项目名称"
            is-link
            class="form-cell"
            @click="showProjectPicker = true"
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
            class="form-cell"
          />
        </div>
      </div>
      <van-field name="work_content"
        v-model="formData.workContent"
        label="工作内容"
        placeholder="请输入工作内容"
        type="textarea"
        rows="3"
        maxlength="800"
        show-word-limit
        required
      />
      <van-field name="remark"
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
          <div v-for="(image, index) in images" :key="index" class="image-item">
            <img :src="image.url" alt="现场照片" loading="lazy" />
            <van-icon name="delete" class="delete-icon" @click="handleDeleteImage(index)" />
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
        {{ isEditMode ? '保存修改' : '提交' }}
      </van-button>
    </div>

    <van-popup v-model:show="showProjectPicker" position="bottom" round destroy-on-close>
      <van-picker name="选择项目"
        title="选择项目"
        :columns="projectColumns"
        :loading="projectList.length === 0"
        @confirm="handleProjectConfirm"
        @cancel="showProjectPicker = false"
      />
    </van-popup>

    <van-popup v-model:show="showDatePicker" position="bottom" round>
      <van-date-picker
        v-model="currentDate"
        title="选择填写日期"
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
  background-color: var(--color-bg-page);
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
  color: var(--color-text-primary);
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
  color: var(--color-bg-card);
  border-radius: 50%;
  padding: 4px;
  font-size: 14px;
}

.image-add {
  width: 80px;
  height: 80px;
  border: 1px dashed var(--color-border-light);
  border-radius: 8px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  color: var(--color-text-secondary);
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
  border-bottom: 1px solid var(--color-border-light);
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
  color: var(--color-text-secondary);
}

.form-cell :deep(.van-cell__value) {
  font-size: 14px;
  color: var(--color-text-primary);
}
</style>
