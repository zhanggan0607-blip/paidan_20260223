<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { showLoadingToast, closeToast, showSuccessToast, showFailToast, showConfirmDialog } from 'vant'
import api from '../utils/api'
import type { ApiResponse } from '../types'
import UserSelector from '../components/UserSelector.vue'
import { userStore } from '../stores/userStore'
import { processPhoto, getCurrentLocation } from '../utils/watermark'
import { validateIdCard } from '../utils/idCardValidator'

// TODO: 工人录入页面 - 身份证OCR识别功能待完善
// FIXME: 身份证验证逻辑应该更严格，包括有效期校验
// TODO: 考虑加入人脸识别功能验证身份
interface WorkerInfo {
  id?: number
  name?: string
  gender?: string
  birthDate?: string
  address?: string
  idCardNumber?: string
  issuingAuthority?: string
  validPeriod?: string
  idCardFront?: string
  idCardBack?: string
}

const router = useRouter()
const route = useRoute()

const projectId = ref('')
const projectName = ref('')
const workDateStart = ref('')
const workDateEnd = ref('')

const workerList = ref<WorkerInfo[]>([])
const showAddPopup = ref(false)
const loading = ref(false)

const currentWorker = ref<WorkerInfo>({
  name: '',
  gender: '',
  birthDate: '',
  address: '',
  idCardNumber: '',
  issuingAuthority: '',
  validPeriod: '',
  idCardFront: '',
  idCardBack: ''
})

const editingIndex = ref(-1)

const fetchWorkerList = async () => {
  if (!projectId.value) return
  
  try {
    const response = await api.get<unknown, ApiResponse<WorkerInfo[]>>('/spot-work/workers', {
      params: {
        project_id: projectId.value,
        start_date: workDateStart.value,
        end_date: workDateEnd.value
      }
    })
    if (response.code === 200) {
      workerList.value = response.data || []
    }
  } catch (error) {
    console.error('Failed to fetch worker list:', error)
  }
}

const handleAddWorker = () => {
  editingIndex.value = -1
  currentWorker.value = {
    name: '',
    gender: '',
    birthDate: '',
    address: '',
    idCardNumber: '',
    issuingAuthority: '',
    validPeriod: '',
    idCardFront: '',
    idCardBack: ''
  }
  showAddPopup.value = true
}

const handleEditWorker = (index: number) => {
  editingIndex.value = index
  currentWorker.value = { ...workerList.value[index] }
  showAddPopup.value = true
}

const handleDeleteWorker = async (index: number) => {
  try {
    await showConfirmDialog({
      title: '提示',
      message: '请确认是否要删除该施工人员？'
    })
    
    workerList.value.splice(index, 1)
    showSuccessToast('删除成功')
  } catch {
  }
}

const handleUploadIdCard = (side: 'front' | 'back') => {
  const input = document.createElement('input')
  input.type = 'file'
  input.accept = 'image/*'
  input.capture = 'environment'
  
  input.onchange = async (e: Event) => {
    const target = e.target as HTMLInputElement
    const file = target.files?.[0]
    if (!file) return
    
    showLoadingToast({ message: '正在识别身份证...', forbidClick: true })
    
    try {
      const originalBase64 = await fileToBase64(file)
      
      try {
        const ocrResponse = await api.post<unknown, ApiResponse<{
          name?: string
          gender?: string
          birthDate?: string
          address?: string
          idCardNumber?: string
          issuingAuthority?: string
          validPeriod?: string
        }>>('/ocr/idcard', {
          imageBase64: originalBase64,
          side: side === 'front' ? 'face' : 'back'
        })
        
        if (ocrResponse.code === 200 && ocrResponse.data) {
          const ocrData = ocrResponse.data
          
          if (side === 'front') {
            if (ocrData.name) currentWorker.value.name = ocrData.name
            if (ocrData.gender) currentWorker.value.gender = ocrData.gender
            if (ocrData.birthDate) currentWorker.value.birthDate = ocrData.birthDate
            if (ocrData.address) currentWorker.value.address = ocrData.address
            if (ocrData.idCardNumber) {
              currentWorker.value.idCardNumber = ocrData.idCardNumber
              const validation = validateIdCard(ocrData.idCardNumber)
              if (!validation.valid) {
                idCardError.value = validation.message
              } else {
                idCardError.value = ''
              }
            }
          } else {
            if (ocrData.issuingAuthority) currentWorker.value.issuingAuthority = ocrData.issuingAuthority
            if (ocrData.validPeriod) currentWorker.value.validPeriod = ocrData.validPeriod
          }
          
          if (side === 'front' && !ocrData.name && !ocrData.idCardNumber) {
            showFailToast('身份证识别失败，请确保图片清晰')
          } else if (side === 'back' && !ocrData.issuingAuthority && !ocrData.validPeriod) {
            showFailToast('身份证反面识别失败，请确保图片清晰')
          }
        } else if (ocrResponse.code !== 200) {
          showFailToast(ocrResponse.message || 'OCR识别失败')
        }
      } catch (ocrError) {
        console.error('OCR识别失败:', ocrError)
        showFailToast('OCR识别失败，请手动填写信息')
      }
      
      showLoadingToast({ message: '处理图片...', forbidClick: true })
      
      const userName = userStore.getUser()?.name || '未知用户'
      const location = await getCurrentLocation()
      const processedFile = await processPhoto(file, {
        userName,
        includeLocation: true,
        latitude: location?.latitude,
        longitude: location?.longitude
      })
      
      showLoadingToast({ message: '上传图片...', forbidClick: true })
      
      const formDataObj = new FormData()
      formDataObj.append('file', processedFile)
      
      const response = await api.post<unknown, ApiResponse<{ url: string }>>('/upload', formDataObj, {
        headers: { 'Content-Type': 'multipart/form-data' }
      })
      
      if (response.code === 200 && response.data) {
        const imageUrl = response.data.url
        if (side === 'front') {
          currentWorker.value.idCardFront = imageUrl
        } else {
          currentWorker.value.idCardBack = imageUrl
        }
        
        showSuccessToast('上传成功')
      } else {
        showFailToast(response.message || '上传失败')
      }
    } catch (error: any) {
      console.error('Failed to upload:', error)
      const errorMsg = error?.message || error?.data?.message || '上传失败，请重试'
      showFailToast(errorMsg)
    } finally {
      closeToast()
    }
  }
  
  input.click()
}

const fileToBase64 = (file: File): Promise<string> => {
  return new Promise((resolve, reject) => {
    const reader = new FileReader()
    reader.onload = () => {
      const result = reader.result as string
      const base64 = result.split(',')[1] || ''
      resolve(base64)
    }
    reader.onerror = reject
    reader.readAsDataURL(file)
  })
}

const idCardError = ref('')

const handleIdCardChange = () => {
  const idCard = currentWorker.value.idCardNumber
  if (!idCard) {
    idCardError.value = ''
    return
  }
  
  if (idCard.length === 18) {
    const validation = validateIdCard(idCard)
    if (validation.valid) {
      idCardError.value = ''
      if (validation.birthDate) {
        currentWorker.value.birthDate = validation.birthDate
      }
      if (validation.gender) {
        currentWorker.value.gender = validation.gender
      }
    } else {
      idCardError.value = validation.message
    }
  } else if (idCard.length > 0) {
    idCardError.value = idCard.length < 18 ? `已输入${idCard.length}位，还需${18 - idCard.length}位` : '身份证号码超出18位'
  } else {
    idCardError.value = ''
  }
}

const handleSaveWorker = () => {
  if (!currentWorker.value.name) {
    showFailToast('请输入姓名')
    return
  }
  if (!currentWorker.value.gender) {
    showFailToast('请输入性别')
    return
  }
  if (!currentWorker.value.birthDate) {
    showFailToast('请输入出生日期')
    return
  }
  if (!currentWorker.value.address) {
    showFailToast('请输入住址')
    return
  }
  if (!currentWorker.value.idCardNumber) {
    showFailToast('请输入身份证号码')
    return
  }
  
  const idCardValidation = validateIdCard(currentWorker.value.idCardNumber)
  if (!idCardValidation.valid) {
    showFailToast(idCardValidation.message)
    return
  }
  
  if (idCardValidation.birthDate && currentWorker.value.birthDate !== idCardValidation.birthDate) {
    showFailToast(`身份证号码与出生日期不匹配，根据身份证应为${idCardValidation.birthDate}`)
    return
  }
  
  if (idCardValidation.gender && currentWorker.value.gender !== idCardValidation.gender) {
    showFailToast(`身份证号码与性别不匹配，根据身份证应为${idCardValidation.gender}`)
    return
  }
  
  if (!currentWorker.value.issuingAuthority) {
    showFailToast('请输入签发机关')
    return
  }
  if (!currentWorker.value.validPeriod) {
    showFailToast('请输入有效期限')
    return
  }
  if (!currentWorker.value.idCardFront) {
    showFailToast('请上传身份证正面照片')
    return
  }
  if (!currentWorker.value.idCardBack) {
    showFailToast('请上传身份证反面照片')
    return
  }
  
  if (editingIndex.value >= 0) {
    workerList.value[editingIndex.value] = { ...currentWorker.value }
  } else {
    workerList.value.push({ ...currentWorker.value })
  }
  
  showAddPopup.value = false
  showSuccessToast('保存成功')
}

const handleSubmit = async () => {
  if (workerList.value.length === 0) {
    showFailToast('请至少添加一名施工人员')
    return
  }
  
  loading.value = true
  showLoadingToast({ message: '提交中...', forbidClick: true })
  
  try {
    const response = await api.post<unknown, ApiResponse<null>>('/spot-work/workers', {
      project_id: projectId.value,
      project_name: projectName.value,
      start_date: workDateStart.value,
      end_date: workDateEnd.value,
      workers: workerList.value
    })
    if (response.code === 200) {
      const personCount = workerList.value.length
      let dayCount = 1
      if (workDateStart.value && workDateEnd.value) {
        const startDate = new Date(workDateStart.value)
        const endDate = new Date(workDateEnd.value)
        const diffTime = Math.abs(endDate.getTime() - startDate.getTime())
        dayCount = Math.ceil(diffTime / (1000 * 60 * 60 * 24)) + 1
      }
      const workDays = personCount * dayCount
      showSuccessToast(`提交成功，共${personCount}人，${workDays}工天（${personCount}人×${dayCount}天）`)
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

onMounted(() => {
  projectId.value = route.query.projectId as string || ''
  projectName.value = route.query.projectName as string || ''
  workDateStart.value = route.query.workDateStart as string || ''
  workDateEnd.value = route.query.workDateEnd as string || ''
  
  if (projectId.value) {
    fetchWorkerList()
  }
})
</script>

<template>
  <div class="worker-entry-page">
    <van-nav-bar 
      title="施工人员录入" 
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
    
    <div class="page-info" v-if="projectName">
      <van-cell-group inset>
        <van-cell title="项目名称" :value="projectName" />
        <van-cell title="用工周期" :value="workDateStart === workDateEnd ? workDateStart : `${workDateStart} 至 ${workDateEnd}`" />
      </van-cell-group>
    </div>

    <van-cell-group inset title="施工人员列表">
      <van-cell 
        v-if="workerList.length > 0" 
        :title="workerList.length + ' 人'" 
        label="施工人数" 
        title-class="worker-count-title"
      />
      <van-empty v-if="workerList.length === 0" description="暂无施工人员" />
      <van-swipe-cell v-for="(worker, index) in workerList" :key="index">
        <van-cell is-link @click="handleEditWorker(index)">
          <template #title>
            <div class="worker-item">
              <div class="worker-name">{{ worker.name }}</div>
              <div class="worker-id">{{ worker.idCardNumber }}</div>
            </div>
          </template>
          <template #value>
            <div class="worker-photos">
              <van-icon v-if="worker.idCardFront" name="idcard" class="photo-icon done" />
              <van-icon v-else name="idcard" class="photo-icon pending" />
              <van-icon v-if="worker.idCardBack" name="idcard" class="photo-icon done" />
              <van-icon v-else name="idcard" class="photo-icon pending" />
            </div>
          </template>
        </van-cell>
        <template #right>
          <van-button square type="danger" text="删除" @click="handleDeleteWorker(index)" />
        </template>
      </van-swipe-cell>
      
      <div class="add-btn">
        <van-button type="primary" block icon="plus" @click="handleAddWorker">
          添加施工人员
        </van-button>
      </div>
    </van-cell-group>

    <div class="submit-btn" v-if="workerList.length > 0">
      <van-button type="primary" block :loading="loading" @click="handleSubmit">
        提交（{{ workerList.length }}人）
      </van-button>
    </div>

    <van-popup 
      v-model:show="showAddPopup" 
      position="bottom" 
      round 
      :style="{ height: '90%' }"
    >
      <div class="popup-content">
        <div class="popup-header">
          <span class="popup-title">{{ editingIndex >= 0 ? '编辑施工人员' : '添加施工人员' }}</span>
          <van-icon name="cross" @click="showAddPopup = false" />
        </div>
        <div class="popup-body">
          <van-cell-group inset title="身份证照片">
            <van-cell title="身份证正面" is-link @click="handleUploadIdCard('front')">
              <template #value>
                <div class="id-card-preview">
                  <img v-if="currentWorker.idCardFront" :src="currentWorker.idCardFront" alt="正面" loading="lazy" />
                  <div v-else class="id-card-placeholder">
                    <van-icon name="photograph" size="24" />
                    <span>点击拍照</span>
                  </div>
                </div>
              </template>
            </van-cell>
            <van-cell title="身份证反面" is-link @click="handleUploadIdCard('back')">
              <template #value>
                <div class="id-card-preview">
                  <img v-if="currentWorker.idCardBack" :src="currentWorker.idCardBack" alt="反面" loading="lazy" />
                  <div v-else class="id-card-placeholder">
                    <van-icon name="photograph" size="24" />
                    <span>点击拍照</span>
                  </div>
                </div>
              </template>
            </van-cell>
          </van-cell-group>

          <van-cell-group inset title="身份信息">
            <van-field 
              v-model="currentWorker.name" 
              label="姓名" 
              placeholder="请输入姓名"
              required
            />
            <van-field 
              v-model="currentWorker.idCardNumber" 
              label="身份证号" 
              placeholder="请输入18位身份证号码"
              required
              maxlength="18"
              @input="handleIdCardChange"
              :error-message="idCardError"
            />
            <van-field 
              v-model="currentWorker.gender" 
              label="性别" 
              placeholder="输入身份证后自动填充"
              readonly
              required
            />
            <van-field 
              v-model="currentWorker.birthDate" 
              label="出生日期" 
              placeholder="输入身份证后自动填充"
              readonly
              required
            />
            <van-field 
              v-model="currentWorker.address" 
              label="住址" 
              placeholder="请输入住址"
              type="textarea"
              rows="2"
              autosize
              required
            />
          </van-cell-group>

          <van-cell-group inset title="证件信息">
            <van-field 
              v-model="currentWorker.issuingAuthority" 
              label="签发机关" 
              placeholder="请输入签发机关"
              required
            />
            <van-field 
              v-model="currentWorker.validPeriod" 
              label="有效期限" 
              placeholder="请输入有效期限"
              required
            />
          </van-cell-group>
        </div>
        <div class="popup-footer">
          <van-button type="primary" block @click="handleSaveWorker">
            保存
          </van-button>
        </div>
      </div>
    </van-popup>
  </div>
</template>

<style scoped>
.worker-entry-page {
  min-height: 100vh;
  background-color: #f5f7fa;
}

:deep(.van-cell-group--inset) {
  margin: 12px;
}

.page-info {
  margin-bottom: 8px;
}

.worker-count-title {
  font-size: 18px;
  font-weight: bold;
  color: #1989fa;
}

.worker-item {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.worker-name {
  font-size: 14px;
  font-weight: 500;
}

.worker-id {
  font-size: 12px;
  color: #969799;
}

.worker-photos {
  display: flex;
  gap: 8px;
}

.photo-icon {
  font-size: 20px;
}

.photo-icon.done {
  color: #07c160;
}

.photo-icon.pending {
  color: #c8c9cc;
}

.add-btn {
  padding: 16px;
}

.submit-btn {
  padding: 16px;
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  background: #fff;
}

.nav-left {
  display: flex;
  align-items: center;
  gap: 4px;
  color: #323233;
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
  padding-bottom: 80px;
}

.popup-footer {
  padding: 12px;
  padding-bottom: max(12px, env(safe-area-inset-bottom));
  border-top: 1px solid #ebedf0;
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  background: #fff;
}

.id-card-preview {
  width: 80px;
  height: 50px;
  border-radius: 4px;
  overflow: hidden;
  background: #f7f8fa;
  display: flex;
  align-items: center;
  justify-content: center;
}

.id-card-preview img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.id-card-placeholder {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 4px;
  color: #969799;
  font-size: 10px;
}
</style>
