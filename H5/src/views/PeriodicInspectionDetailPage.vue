<script setup lang="ts">
import { ref, onMounted, onActivated, computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { showLoadingToast, closeToast, showSuccessToast, showFailToast, showConfirmDialog } from 'vant'
import api from '../utils/api'
import type { ApiResponse } from '../types'
import { WORK_STATUS, formatDate } from '../config/constants'
import UserSelector from '../components/UserSelector.vue'

const router = useRouter()
const route = useRoute()

interface WorkPlanDetail {
  id: number
  inspection_id: string
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
  created_at: string
  updated_at: string
}

interface InspectionSystem {
  id: number
  name: string
  inspected: boolean
  photos_uploaded: boolean
  inspection_content: string
  inspection_result: string
  photos: string[]
  check_content?: string
  check_standard?: string
  level: number
  parent_id: number | null
}

interface InspectionItem {
  id: number
  item_code: string
  item_name: string
  item_type: string
  level: number
  parent_id: number | null
  check_content?: string
  check_standard?: string
  children?: InspectionItem[]
}

const loading = ref(false)
const detail = ref<WorkPlanDetail | null>(null)
const inspectionSystems = ref<InspectionSystem[]>([])
const inspectionItemsLoading = ref(false)

const showDatePicker = ref(false)
const currentDate = ref(['2024', '01', '01'])
const formData = ref({
  execution_date: '',
  execution_result: '',
  remarks: '',
  signature: ''
})

const currentInspectionSystem = ref<InspectionSystem | null>(null)
const showInspectionPopup = ref(false)
const showPhotoPopup = ref(false)

const isEditable = computed(() => {
  return detail.value?.status === WORK_STATUS.NOT_STARTED || 
         detail.value?.status === WORK_STATUS.IN_PROGRESS ||
         detail.value?.status === WORK_STATUS.RETURNED
})

const allInspected = computed(() => {
  return inspectionSystems.value.every(sys => sys.inspected)
})

const allPhotosUploaded = computed(() => {
  return inspectionSystems.value.every(sys => sys.photos_uploaded)
})

const canSign = computed(() => {
  return allInspected.value && allPhotosUploaded.value
})

const canSubmit = computed(() => {
  return canSign.value && formData.value.signature
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
    const response = await api.get<unknown, ApiResponse<WorkPlanDetail>>(`/periodic-inspection/${id}`)
    if (response.code === 200) {
      detail.value = response.data
    }
  } catch (error) {
    console.error('Failed to fetch detail:', error)
    showFailToast('加载失败')
  } finally {
    loading.value = false
    closeToast()
  }
}

/**
 * 从后端API获取巡检事项树形数据
 * 将三级检查项转换为巡检记录列表
 */
const fetchInspectionItems = async () => {
  inspectionItemsLoading.value = true
  try {
    const response = await api.get<unknown, ApiResponse<InspectionItem[]>>('/inspection-item/tree')
    if (response.code === 200 && response.data) {
      const items = flattenInspectionItems(response.data)
      inspectionSystems.value = items.map(item => ({
        id: item.id,
        name: item.item_name,
        inspected: false,
        photos_uploaded: false,
        inspection_content: '',
        inspection_result: '',
        photos: [],
        check_content: item.check_content || '',
        check_standard: item.check_standard || '',
        level: item.level,
        parent_id: item.parent_id
      }))
    }
  } catch (error) {
    console.error('Failed to fetch inspection items:', error)
  } finally {
    inspectionItemsLoading.value = false
  }
}

/**
 * 将树形巡检事项数据扁平化，只提取三级检查项
 */
const flattenInspectionItems = (items: InspectionItem[]): InspectionItem[] => {
  const result: InspectionItem[] = []
  const flatten = (itemList: InspectionItem[]) => {
    for (const item of itemList) {
      if (item.level === 3) {
        result.push(item)
      }
      if (item.children && item.children.length > 0) {
        flatten(item.children)
      }
    }
  }
  flatten(items)
  return result
}

const loadSignature = () => {
  const signatureData = localStorage.getItem('periodic_inspection_signature')
  if (signatureData) {
    formData.value.signature = signatureData
  }
}

const handleInspection = (system: InspectionSystem) => {
  if (!isEditable.value) return
  currentInspectionSystem.value = { ...system }
  showInspectionPopup.value = true
}

const handleInspectionSave = () => {
  if (!currentInspectionSystem.value) return
  
  const index = inspectionSystems.value.findIndex(s => s.id === currentInspectionSystem.value!.id)
  if (index !== -1) {
    currentInspectionSystem.value.inspected = true
    inspectionSystems.value[index] = { ...currentInspectionSystem.value }
  }
  showInspectionPopup.value = false
  showSuccessToast('保存成功')
}

const handlePhotoUpload = (system: InspectionSystem) => {
  if (!isEditable.value) return
  currentInspectionSystem.value = { ...system }
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
        if (currentInspectionSystem.value) {
          currentInspectionSystem.value.photos.push(response.data.url)
        }
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
    if (currentInspectionSystem.value) {
      currentInspectionSystem.value.photos.splice(index, 1)
    }
  } catch {
  }
}

const handlePhotoSave = () => {
  if (!currentInspectionSystem.value) return
  
  const index = inspectionSystems.value.findIndex(s => s.id === currentInspectionSystem.value!.id)
  if (index !== -1) {
    currentInspectionSystem.value.photos_uploaded = currentInspectionSystem.value.photos.length > 0
    inspectionSystems.value[index] = { ...currentInspectionSystem.value }
  }
  showPhotoPopup.value = false
  showSuccessToast('保存成功')
}

const handleSignature = () => {
  if (!canSign.value) {
    showFailToast('请先完成巡检记录和图片上传')
    return
  }
  router.push({
    path: '/signature',
    query: { 
      from: route.fullPath,
      type: 'periodic-inspection'
    }
  })
}

const handleDateConfirm = ({ selectedValues }: { selectedValues: string[] }) => {
  formData.value.execution_date = selectedValues.join('-')
  showDatePicker.value = false
}

const handleSubmit = async () => {
  if (!canSubmit.value) {
    showFailToast('请完成所有必填项')
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
      inspection_systems: inspectionSystems.value,
      work_plan_id: detail.value?.id
    }
    
    const response = await api.post<unknown, ApiResponse<any>>('/periodic-inspection', submitData)
    
    if (response.code === 200) {
      localStorage.removeItem('periodic_inspection_signature')
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
      inspection_systems: inspectionSystems.value,
      work_plan_id: detail.value?.id,
      status: WORK_STATUS.IN_PROGRESS
    }
    
    const response = await api.put<unknown, ApiResponse<any>>(`/work-plan/${detail.value?.id}`, saveData)
    
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
  fetchInspectionItems()
  loadSignature()
})

onActivated(() => {
  loadSignature()
})
</script>

<template>
  <div class="periodic-inspection-detail">
    <van-nav-bar 
      title="定期巡检单" 
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
        <van-cell title="工单编号" :value="detail.inspection_id" />
        <van-cell title="维保开始日期" :value="formatDate(detail.plan_start_date)" />
        <van-cell title="维保截止日期" :value="formatDate(detail.plan_end_date)" />
        <van-cell title="客户单位" :value="detail.client_name || '-'" />
        <van-cell title="客户联系人" :value="detail.client_contact || '-'" />
        <van-cell title="客户联系方式" :value="detail.client_contact_info || '-'" />
      </van-cell-group>

      <van-cell-group inset title="巡检记录">
        <div class="section-tip">巡检事项来自PC管理端配置，请依次完成各项巡检</div>
        <div v-if="inspectionItemsLoading" class="loading-container">
          <van-loading size="24px">加载巡检事项...</van-loading>
        </div>
        <van-empty v-else-if="inspectionSystems.length === 0" description="暂无巡检事项，请在PC管理端配置" />
        <van-cell 
          v-else
          v-for="system in inspectionSystems" 
          :key="system.id"
          :title="system.name"
          is-link
          @click="handleInspection(system)"
        >
          <template #value>
            <span :class="system.inspected ? 'status-done' : 'status-pending'">
              {{ system.inspected ? '已处理' : '去处理' }}
            </span>
          </template>
        </van-cell>
      </van-cell-group>

      <van-cell-group inset title="图片上传">
        <div v-if="inspectionItemsLoading" class="loading-container">
          <van-loading size="24px">加载中...</van-loading>
        </div>
        <van-empty v-else-if="inspectionSystems.length === 0" description="暂无巡检事项" />
        <van-cell 
          v-else
          v-for="system in inspectionSystems" 
          :key="system.id"
          :title="system.name"
          is-link
          @click="handlePhotoUpload(system)"
        >
          <template #value>
            <span :class="system.photos_uploaded ? 'status-done' : 'status-pending'">
              {{ system.photos_uploaded ? '已上传' : '去上传' }}
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
        />
        
        <van-field
          v-model="formData.execution_result"
          rows="3"
          autosize
          label="处理内容"
          type="textarea"
          placeholder="请输入处理内容"
          show-word-limit
          maxlength="500"
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
        />
      </van-cell-group>

      <van-cell-group inset title="用户确认">
        <div class="section-tip">
          此条目，在巡检记录填写、图片上传的所有条目均已处理/已上传，才显示，才能提交进入用户签字，此项为必填
        </div>
        <van-cell is-link @click="handleSignature" :disabled="!canSign">
          <template #title>
            <span>用户签字</span>
          </template>
          <template #value>
            <img v-if="formData.signature" :src="formData.signature" class="signature-preview" />
            <span v-else :class="canSign ? 'status-pending' : 'status-disabled'">
              {{ canSign ? '待签字' : '需完成巡检和上传' }}
            </span>
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
      v-model:show="showInspectionPopup" 
      position="bottom" 
      round 
      :style="{ height: '70%' }"
    >
      <div class="popup-content" v-if="currentInspectionSystem">
        <div class="popup-header">
          <span class="popup-title">{{ currentInspectionSystem.name }} - 巡检记录</span>
          <van-icon name="cross" @click="showInspectionPopup = false" />
        </div>
        <div class="popup-body">
          <div v-if="currentInspectionSystem.check_content || currentInspectionSystem.check_standard" class="check-reference">
            <div v-if="currentInspectionSystem.check_content" class="check-item">
              <div class="check-label">检查内容参考：</div>
              <div class="check-value">{{ currentInspectionSystem.check_content }}</div>
            </div>
            <div v-if="currentInspectionSystem.check_standard" class="check-item">
              <div class="check-label">检查标准参考：</div>
              <div class="check-value">{{ currentInspectionSystem.check_standard }}</div>
            </div>
          </div>
          <van-field
            v-model="currentInspectionSystem.inspection_content"
            rows="3"
            autosize
            label="巡检内容"
            type="textarea"
            placeholder="请输入巡检内容"
          />
          <van-field
            v-model="currentInspectionSystem.inspection_result"
            rows="3"
            autosize
            label="巡检结果"
            type="textarea"
            placeholder="请输入巡检结果"
          />
        </div>
        <div class="popup-footer">
          <van-button type="primary" block @click="handleInspectionSave">保存</van-button>
        </div>
      </div>
    </van-popup>

    <van-popup 
      v-model:show="showPhotoPopup" 
      position="bottom" 
      round 
      :style="{ height: '60%' }"
    >
      <div class="popup-content" v-if="currentInspectionSystem">
        <div class="popup-header">
          <span class="popup-title">{{ currentInspectionSystem.name }} - 图片上传</span>
          <van-icon name="cross" @click="showPhotoPopup = false" />
        </div>
        <div class="popup-body">
          <div class="photo-section">
            <div class="photo-grid">
              <div 
                v-for="(photo, index) in currentInspectionSystem.photos" 
                :key="index" 
                class="photo-item"
              >
                <img :src="photo" alt="现场照片" />
                <van-icon name="delete" class="delete-icon" @click.stop="handleRemovePhoto(index)" />
              </div>
              <div class="photo-add" @click="handlePhotoCapture" v-if="currentInspectionSystem.photos.length < 9">
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
.periodic-inspection-detail {
  min-height: 100vh;
  background-color: #f5f7fa;
}

.content {
  padding-bottom: 20px;
}

:deep(.van-cell-group--inset) {
  margin: 12px;
}

.section-tip {
  padding: 8px 16px;
  font-size: 12px;
  color: #969799;
  background: #fafafa;
}

.loading-container {
  padding: 16px;
  display: flex;
  justify-content: center;
  align-items: center;
}

.status-done {
  color: #07c160;
}

.status-pending {
  color: #1989fa;
}

.status-disabled {
  color: #c8c9cc;
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

.check-reference {
  padding: 12px 16px;
  background: #f7f8fa;
  border-bottom: 1px solid #ebedf0;
}

.check-item {
  margin-bottom: 8px;
}

.check-item:last-child {
  margin-bottom: 0;
}

.check-label {
  font-size: 12px;
  color: #969799;
  margin-bottom: 4px;
}

.check-value {
  font-size: 14px;
  color: #323233;
  line-height: 1.5;
}
</style>
