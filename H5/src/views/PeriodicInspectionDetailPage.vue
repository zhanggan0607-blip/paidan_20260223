<script setup lang="ts">
import { ref, onMounted, onActivated, computed, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { showLoadingToast, closeToast, showSuccessToast, showFailToast, showConfirmDialog, showToast, showImagePreview } from 'vant'
import api from '../utils/api'
import type { ApiResponse } from '../types'
import { WORK_STATUS, formatDate } from '../config/constants'
import UserSelector from '../components/UserSelector.vue'
import { authService, type User } from '../services/auth'

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
  execution_result: string
  remarks: string
  signature: string
  created_at: string
  updated_at: string
}

interface MaintenancePlan {
  id: number
  plan_id: string
  plan_name: string
  project_id: string
  project_name: string
  equipment_name: string
  equipment_location: string
  maintenance_content: string
  maintenance_requirements: string
  maintenance_standard: string
  plan_status: string
  execution_status: string
  responsible_person: string
  plan_start_date: string
  plan_end_date: string
  inspection_items?: string
}

interface InspectionItemData {
  inspection_item: string
  inspection_content: string
  check_requirements: string
  brief_description: string
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
  equipment_name?: string
  equipment_location?: string
  inspection_item?: string
  brief_description?: string
}

const loading = ref(false)
const detail = ref<WorkPlanDetail | null>(null)
const inspectionSystems = ref<InspectionSystem[]>([])
const inspectionItemsLoading = ref(false)
const currentUser = ref<User | null>(null)

const formData = ref({
  execution_result: '',
  remarks: '',
  signature: ''
})

const currentInspectionSystem = ref<InspectionSystem | null>(null)
const showInspectionPopup = ref(false)

const isApproveMode = computed(() => {
  return route.query.mode === 'approve'
})

const canApprove = computed(() => {
  return authService.canApprovePeriodicInspection(currentUser.value)
})

const isEditable = computed(() => {
  if (isApproveMode.value) return false
  const status = detail.value?.status
  return status === WORK_STATUS.NOT_STARTED || 
         status === WORK_STATUS.IN_PROGRESS ||
         status === WORK_STATUS.RETURNED
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

const totalCount = computed(() => {
  return inspectionSystems.value.length || 0
})

const filledCount = computed(() => {
  return inspectionSystems.value.filter(sys => sys.inspected).length || 0
})

const returnTab = computed(() => {
  return route.query.tab as string || '0'
})

const handleBackToList = () => {
  router.push(`/periodic-inspection?tab=${returnTab.value}`)
}

/**
 * 复制工单编号到剪贴板
 * @param orderId 工单编号
 */
const copyOrderId = async (orderId: string) => {
  try {
    await navigator.clipboard.writeText(orderId)
    showToast('工单编号已复制')
  } catch {
    showToast('复制失败')
  }
}

/**
 * 根据工单编号长度计算字体大小
 * @param workId 工单编号
 * @returns 字体大小(px)
 */
const getWorkIdFontSize = (workId: string) => {
  if (!workId) return 14
  const len = workId.length
  if (len <= 18) return 14
  if (len <= 22) return 12
  if (len <= 26) return 11
  if (len <= 30) return 10
  if (len <= 35) return 9
  if (len <= 40) return 8
  return 7
}

/**
 * 预览图片
 * @param photos 图片列表
 * @param startIndex 起始索引
 */
const previewPhoto = (photos: string[], startIndex: number) => {
  if (!photos || photos.length === 0) return
  showImagePreview({
    images: photos,
    startPosition: startIndex,
    closeable: true,
    showIndex: true
  })
}

const fetchDetail = async () => {
  const id = route.params.id
  if (!id) return
  
  loading.value = true
  showLoadingToast({ message: '加载中...', forbidClick: true })
  
  try {
    const response = await api.get<unknown, ApiResponse<WorkPlanDetail>>(`/periodic-inspection/${id}`)
    if (response.code === 200) {
      detail.value = response.data
      if (response.data) {
        formData.value.execution_result = response.data.execution_result || ''
        formData.value.remarks = response.data.remarks || ''
        formData.value.signature = response.data.signature || ''
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

/**
 * 从后端API获取项目关联的维保事项
 * 将维保计划的inspection_items JSON字段解析为巡检记录列表
 * 与PC端WorkPlanManagement.vue保持一致的数据解析逻辑
 */
const fetchInspectionItems = async () => {
  if (!detail.value?.project_id) {
    return
  }
  
  inspectionItemsLoading.value = true
  try {
    const response = await api.get<unknown, ApiResponse<MaintenancePlan[]>>(`/maintenance-plan/project/${detail.value.project_id}`)
    if (response.code === 200 && response.data) {
      const orderStartDate = detail.value.plan_start_date ? new Date(detail.value.plan_start_date) : null
      const orderEndDate = detail.value.plan_end_date ? new Date(detail.value.plan_end_date) : null
      if (orderStartDate) orderStartDate.setHours(0, 0, 0, 0)
      if (orderEndDate) orderEndDate.setHours(0, 0, 0, 0)
      
      const filteredPlans = response.data.filter((plan: MaintenancePlan) => {
        if (!plan.plan_start_date || !plan.plan_end_date) return false
        const planStartDate = new Date(plan.plan_start_date)
        planStartDate.setHours(0, 0, 0, 0)
        const planEndDate = new Date(plan.plan_end_date)
        planEndDate.setHours(0, 0, 0, 0)
        if (orderStartDate && orderEndDate) {
          return orderStartDate <= planEndDate && orderEndDate >= planStartDate
        }
        return false
      })
      
      const allItems: InspectionSystem[] = []
      filteredPlans.forEach((plan: MaintenancePlan) => {
        if (plan.inspection_items) {
          try {
            const items: InspectionItemData[] = JSON.parse(plan.inspection_items)
            items.forEach((item: InspectionItemData, idx: number) => {
              allItems.push({
                id: plan.id * 1000 + idx,
                name: item.inspection_item || plan.maintenance_content || `维保事项${plan.id}`,
                inspected: false,
                photos_uploaded: false,
                inspection_content: item.inspection_content || '',
                inspection_result: '',
                photos: [],
                check_content: item.check_requirements || plan.maintenance_requirements || '',
                check_standard: plan.maintenance_standard || '',
                equipment_name: plan.equipment_name || '',
                equipment_location: plan.equipment_location || '',
                inspection_item: item.inspection_item || '',
                brief_description: item.brief_description || ''
              })
            })
          } catch (e) {
            console.error('解析巡查项数据失败:', e)
          }
        }
      })
      
      inspectionSystems.value = allItems
      
      await loadSavedRecords()
    }
  } catch (error) {
    console.error('Failed to fetch maintenance plans:', error)
  } finally {
    inspectionItemsLoading.value = false
  }
}

/**
 * 从后端加载已保存的巡检记录
 */
const loadSavedRecords = async () => {
  if (!detail.value?.inspection_id) return
  
  try {
    const response = await api.get<unknown, ApiResponse<any[]>>(`/periodic-inspection-record/inspection/${detail.value.inspection_id}`)
    if (response.code === 200 && response.data) {
      response.data.forEach((savedRecord: any) => {
        const index = inspectionSystems.value.findIndex(item => String(item.id) === String(savedRecord.item_id))
        if (index !== -1) {
          const sysItem = inspectionSystems.value[index]!
          sysItem.inspected = savedRecord.inspected
          sysItem.photos = savedRecord.photos || []
          sysItem.photos_uploaded = savedRecord.photos_uploaded || (savedRecord.photos && savedRecord.photos.length > 0)
          sysItem.inspection_result = savedRecord.inspection_result || ''
        }
      })
    }
  } catch (error) {
    console.error('Failed to load saved records:', error)
  }
}

/**
 * 保存单个巡检记录到后端
 * @param system 巡检项
 */
const saveRecordToBackend = async (system: InspectionSystem) => {
  if (!detail.value?.inspection_id) return
  
  try {
    const recordData = {
      inspection_id: detail.value.inspection_id,
      item_id: String(system.id),
      item_name: system.name,
      inspection_item: system.inspection_item,
      inspection_content: system.inspection_content,
      check_content: system.check_content,
      brief_description: system.brief_description,
      equipment_name: system.equipment_name,
      equipment_location: system.equipment_location,
      inspected: system.inspected,
      photos: system.photos,
      inspection_result: system.inspection_result
    }
    
    await api.post('/periodic-inspection-record', recordData)
  } catch (error) {
    console.error('Failed to save record:', error)
  }
}

const loadSignature = () => {
  const signatureData = localStorage.getItem('periodic_inspection_signature')
  if (signatureData) {
    formData.value.signature = signatureData
  }
}

/**
 * 点击去处理时，弹窗确认是否完成巡检
 * 确认后提示拍照，拍照完成后标记为已完成
 * @param system 巡检项
 */
const handleInspection = async (system: InspectionSystem) => {
  if (!isEditable.value) {
    showToast('当前工单状态不可编辑')
    return
  }
  
  if (system.inspected) {
    currentInspectionSystem.value = { ...system }
    showInspectionPopup.value = true
    return
  }
  
  try {
    await showConfirmDialog({
      title: '确认巡检',
      message: '是否已完成该巡检项？确认后将进行拍照记录。',
      confirmButtonText: '确认完成',
      cancelButtonText: '取消'
    })
    
    await showConfirmDialog({
      title: '拍照记录',
      message: '请拍摄现场照片作为巡检记录',
      confirmButtonText: '开始拍照',
      cancelButtonText: '稍后拍照'
    })
    
    handlePhotoCaptureForItem(system, true)
    
  } catch {
  }
}

const handleInspectionSave = async () => {
  if (!currentInspectionSystem.value) return
  
  const index = inspectionSystems.value.findIndex(s => s.id === currentInspectionSystem.value!.id)
  if (index !== -1) {
    currentInspectionSystem.value.inspected = true
    inspectionSystems.value[index] = { ...currentInspectionSystem.value }
    await saveRecordToBackend(inspectionSystems.value[index])
  }
  showInspectionPopup.value = false
  showSuccessToast('保存成功')
}

/**
 * 为指定巡检项拍照上传
 * @param system 巡检项
 * @param markAsInspected 拍照完成后是否自动标记为已完成
 */
const handlePhotoCaptureForItem = (system: InspectionSystem, markAsInspected: boolean = false) => {
  if (!isEditable.value) return
  
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
        const index = inspectionSystems.value.findIndex(s => s.id === system.id)
        if (index !== -1) {
          const item = inspectionSystems.value[index]!
          item.photos.push(response.data.url)
          item.photos_uploaded = item.photos.length > 0
          if (markAsInspected) {
            item.inspected = true
          }
          await saveRecordToBackend(item)
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

/**
 * 删除指定巡检项的照片
 * @param system 巡检项
 * @param photoIndex 照片索引
 */
const handleRemovePhotoForItem = async (system: InspectionSystem, photoIndex: number) => {
  try {
    await showConfirmDialog({
      title: '提示',
      message: '是否要删除，新增的图片会重新打水印'
    })
    const index = inspectionSystems.value.findIndex(s => s.id === system.id)
    if (index !== -1) {
      const item = inspectionSystems.value[index]!
      item.photos.splice(photoIndex, 1)
      item.photos_uploaded = item.photos.length > 0
      await saveRecordToBackend(item)
    }
  } catch {
  }
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
      type: 'periodic-inspection',
      inspectionId: detail.value?.id
    }
  })
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
      inspection_id: detail.value?.inspection_id,
      project_id: detail.value?.project_id,
      project_name: detail.value?.project_name,
      plan_start_date: detail.value?.plan_start_date,
      plan_end_date: detail.value?.plan_end_date,
      client_name: detail.value?.client_name,
      maintenance_personnel: detail.value?.maintenance_personnel,
      status: '待确认',
      execution_result: formData.value.execution_result,
      remarks: formData.value.remarks,
      signature: formData.value.signature,
      total_count: totalCount.value,
      filled_count: filledCount.value
    }
    
    const response = await api.put<unknown, ApiResponse<any>>(`/periodic-inspection/${detail.value?.id}`, submitData)
    
    if (response.code === 200) {
      localStorage.removeItem('periodic_inspection_signature')
      showSuccessToast('提交成功')
      router.push(`/periodic-inspection?tab=${returnTab.value}`)
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
      inspection_id: detail.value?.inspection_id,
      project_id: detail.value?.project_id,
      project_name: detail.value?.project_name,
      plan_start_date: detail.value?.plan_start_date,
      plan_end_date: detail.value?.plan_end_date,
      client_name: detail.value?.client_name,
      maintenance_personnel: detail.value?.maintenance_personnel,
      status: detail.value?.status || WORK_STATUS.IN_PROGRESS,
      execution_result: formData.value.execution_result,
      remarks: formData.value.remarks,
      signature: formData.value.signature,
      total_count: totalCount.value,
      filled_count: filledCount.value
    }
    
    const response = await api.put<unknown, ApiResponse<any>>(`/periodic-inspection/${detail.value?.id}`, saveData)
    
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

/**
 * 审批通过
 */
const handleApprovePass = async () => {
  if (!detail.value?.id) return
  
  try {
    await showConfirmDialog({
      title: '审批确认',
      message: '确认审批通过该工单吗？'
    })
    
    showLoadingToast({ message: '处理中...', forbidClick: true })
    
    const submitData = {
      status: '已确认'
    }
    
    const response = await api.patch<unknown, ApiResponse<any>>(`/periodic-inspection/${detail.value?.id}`, submitData)
    
    if (response.code === 200) {
      showSuccessToast('审批通过')
      router.push('/periodic-inspection?tab=3')
    }
  } catch (error) {
    if (error !== 'cancel') {
      console.error('Failed to approve:', error)
      showFailToast('审批失败')
    }
  } finally {
    closeToast()
  }
}

/**
 * 审批退回
 */
const handleApproveReject = async () => {
  if (!detail.value?.id) return
  
  try {
    await showConfirmDialog({
      title: '退回确认',
      message: '确认退回该工单吗？退回后员工需重新填写。',
      confirmButtonText: '确认退回',
      confirmButtonColor: '#ee0a24'
    })
    
    showLoadingToast({ message: '处理中...', forbidClick: true })
    
    const submitData = {
      status: '已退回'
    }
    
    const response = await api.patch<unknown, ApiResponse<any>>(`/periodic-inspection/${detail.value?.id}`, submitData)
    
    if (response.code === 200) {
      showSuccessToast('已退回')
      router.push('/periodic-inspection?tab=1')
    }
  } catch (error) {
    if (error !== 'cancel') {
      console.error('Failed to reject:', error)
      showFailToast('退回失败')
    }
  } finally {
    closeToast()
  }
}

let autoSaveTimer: ReturnType<typeof setTimeout> | null = null

/**
 * 自动保存现场处理内容到后端（防抖）
 * 如果内容有变化，清除签名要求重新签名
 */
const autoSaveFieldContent = async () => {
  if (!detail.value?.id || !isEditable.value) return
  
  if (autoSaveTimer) {
    clearTimeout(autoSaveTimer)
  }
  
  autoSaveTimer = setTimeout(async () => {
    try {
      const saveData = {
        inspection_id: detail.value?.inspection_id,
        project_id: detail.value?.project_id,
        project_name: detail.value?.project_name,
        plan_start_date: detail.value?.plan_start_date,
        plan_end_date: detail.value?.plan_end_date,
        client_name: detail.value?.client_name,
        maintenance_personnel: detail.value?.maintenance_personnel,
        status: detail.value?.status || WORK_STATUS.IN_PROGRESS,
        execution_result: formData.value.execution_result,
        remarks: formData.value.remarks,
        signature: formData.value.signature,
        total_count: totalCount.value,
        filled_count: filledCount.value
      }
      
      await api.put<unknown, ApiResponse<any>>(`/periodic-inspection/${detail.value?.id}`, saveData)
    } catch (error) {
      console.error('Auto save failed:', error)
    }
  }, 1000)
}

watch(() => formData.value.execution_result, () => {
  autoSaveFieldContent()
})

watch(() => formData.value.remarks, () => {
  autoSaveFieldContent()
})

const handleUserReady = (user: User) => {
  currentUser.value = user
}

onMounted(async () => {
  currentUser.value = authService.getCurrentUser()
  await fetchDetail()
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
        <div class="nav-left" @click="handleBackToList">
          <van-icon name="arrow-left" />
          <span>返回</span>
        </div>
      </template>
      <template #right>
        <UserSelector @ready="handleUserReady" />
      </template>
    </van-nav-bar>
    
    <div class="content" v-if="detail">
      <van-cell-group inset title="基本资料">
        <van-cell title="项目名称" :value="detail.project_name" />
        <van-cell title="工单编号">
          <template #value>
            <div class="order-id-cell">
              <div class="order-id-text" :style="{ fontSize: getWorkIdFontSize(detail.inspection_id) + 'px' }">{{ detail.inspection_id }}</div>
              <van-button size="mini" type="primary" plain @click.stop="copyOrderId(detail.inspection_id)">复制单号</van-button>
            </div>
          </template>
        </van-cell>
        <van-cell title="维保开始日期" :value="formatDate(detail.plan_start_date)" />
        <van-cell title="维保截止日期" :value="formatDate(detail.plan_end_date)" />
        <van-cell title="客户单位" :value="detail.client_name || '-'" />
        <van-cell title="客户联系人" :value="detail.client_contact || '-'" />
        <van-cell title="客户联系方式" :value="detail.client_contact_info || '-'" />
      </van-cell-group>

      <van-cell-group inset>
        <template #title>
          <span class="required-label"><span class="required-star">*</span>巡检记录</span>
        </template>
        <div class="section-tip">巡检事项来自项目维保计划，请依次完成各项巡检</div>
        <div v-if="inspectionItemsLoading" class="loading-container">
          <van-loading size="24px">加载巡检事项...</van-loading>
        </div>
        <van-empty v-else-if="inspectionSystems.length === 0" description="暂无巡检事项，请在PC管理端配置项目维保计划" />
        <div v-else class="inspection-list">
          <div 
            v-for="(system, index) in inspectionSystems" 
            :key="system.id"
            class="inspection-item-card"
          >
            <div class="inspection-item-header" @click="handleInspection(system)">
              <div class="inspection-item-left">
                <span class="inspection-index">{{ index + 1 }}.</span>
                <span class="inspection-title">{{ system.inspection_item || system.name }}</span>
              </div>
              <div class="inspection-item-right">
                <span :class="system.inspected ? 'status-done' : 'status-action'">
                  {{ system.inspected ? '已处理' : '去处理' }}
                </span>
                <van-icon name="arrow" />
              </div>
            </div>
            <div v-if="system.equipment_name" class="inspection-subtitle">设备: {{ system.equipment_name }}</div>
            <div class="inspection-detail" v-if="system.inspection_content || system.check_content || system.brief_description">
              <div class="detail-row" v-if="system.inspection_content">
                <span class="detail-label">巡查内容:</span>
                <span class="detail-value">{{ system.inspection_content }}</span>
              </div>
              <div class="detail-row" v-if="system.check_content">
                <span class="detail-label">检查要求:</span>
                <span class="detail-value">{{ system.check_content }}</span>
              </div>
              <div class="detail-row" v-if="system.brief_description">
                <span class="detail-label">简要说明:</span>
                <span class="detail-value">{{ system.brief_description }}</span>
              </div>
            </div>
            
            <div class="photo-section-inline">
              <div class="photo-grid-inline">
                <div 
                  v-for="(photo, photoIdx) in system.photos" 
                  :key="photoIdx" 
                  class="photo-item-inline"
                  @click="previewPhoto(system.photos, photoIdx)"
                >
                  <img :src="photo" alt="现场照片" />
                  <van-icon 
                    v-if="isEditable"
                    name="delete" 
                    class="delete-icon-inline" 
                    @click.stop="handleRemovePhotoForItem(system, photoIdx)" 
                  />
                </div>
                <div 
                  v-if="isEditable && system.inspected && system.photos.length < 9" 
                  class="photo-add-inline" 
                  @click="handlePhotoCaptureForItem(system)"
                >
                  <van-icon name="photograph" size="24" />
                  <span>拍照</span>
                </div>
              </div>
              <div class="photo-status">
                <span :class="system.photos_uploaded ? 'status-done' : 'status-pending'">
                  {{ system.photos_uploaded ? '已上传' : '待上传' }}
                </span>
              </div>
            </div>
          </div>
        </div>
      </van-cell-group>

      <van-cell-group inset title="现场处理">
        <van-field
          v-model="formData.execution_result"
          rows="3"
          autosize
          label="发现问题"
          type="textarea"
          placeholder="请输入发现问题"
          show-word-limit
          maxlength="500"
        />
        
        <van-field
          v-model="formData.remarks"
          rows="2"
          autosize
          label="处理结果"
          type="textarea"
          placeholder="请输入处理结果"
          show-word-limit
          maxlength="200"
        />
      </van-cell-group>

      <van-cell-group inset v-if="canSign">
        <template #title>
          <span class="required-label"><span class="required-star">*</span>用户签字</span>
        </template>
        <van-cell is-link @click="handleSignature">
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

      <div class="action-buttons" v-if="isApproveMode && canApprove">
        <van-button type="danger" size="large" @click="handleApproveReject">退回</van-button>
        <van-button type="success" size="large" @click="handleApprovePass">通过</van-button>
      </div>
    </div>
    
    <van-empty v-else-if="!loading" description="暂无数据" />

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

:deep(.van-cell__title) {
  flex: none;
  width: 28%;
  min-width: 90px;
}

:deep(.van-cell__value) {
  flex: 1;
  width: 72%;
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

.status-disabled {
  color: #c8c9cc;
}

.inspection-list {
  padding: 0 12px 12px;
}

.inspection-item-card {
  background: #fff;
  border-radius: 8px;
  margin-bottom: 12px;
  padding: 12px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
}

.inspection-item-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  cursor: pointer;
}

.inspection-item-left {
  display: flex;
  align-items: flex-start;
  flex: 1;
}

.inspection-item-right {
  display: flex;
  align-items: center;
  gap: 4px;
}

.inspection-title {
  font-size: 14px;
  color: #323233;
}

.inspection-index {
  font-size: 14px;
  color: #323233;
  font-weight: 500;
  margin-right: 4px;
}

.inspection-detail {
  margin-top: 8px;
  padding: 8px 12px;
  background: #f7f8fa;
  border-radius: 4px;
}

.detail-row {
  display: flex;
  margin-bottom: 4px;
  font-size: 12px;
  line-height: 1.5;
}

.detail-row:last-child {
  margin-bottom: 0;
}

.detail-label {
  color: #969799;
  flex-shrink: 0;
  min-width: 60px;
}

.detail-value {
  color: #323233;
  flex: 1;
  word-break: break-all;
}

.inspection-subtitle {
  font-size: 12px;
  color: #969799;
  margin-top: 4px;
}

.photo-section-inline {
  margin-top: 12px;
  padding-top: 12px;
  border-top: 1px solid #ebedf0;
}

.photo-grid-inline {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 10px;
}

.photo-item-inline {
  position: relative;
  aspect-ratio: 1;
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.photo-item-inline img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  cursor: pointer;
}

.delete-icon-inline {
  position: absolute;
  top: 4px;
  right: 4px;
  font-size: 18px;
  color: #fff;
  background: rgba(0, 0, 0, 0.5);
  border-radius: 50%;
  padding: 2px;
}

.photo-add-inline {
  aspect-ratio: 1;
  border: 2px dashed #dcdee0;
  border-radius: 8px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 4px;
  color: #969799;
  font-size: 12px;
  background: #fafafa;
}

.photo-status {
  margin-top: 8px;
  text-align: right;
  font-size: 12px;
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

.order-id-cell {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 4px;
}

.order-id-text {
  color: #323233;
  word-break: break-all;
  text-align: right;
}

.order-id-cell :deep(.van-button) {
  flex-shrink: 0;
  height: 24px;
  padding: 0 8px;
  font-size: 12px;
  white-space: nowrap;
  transform: scale(0.8);
  transform-origin: right center;
  margin-left: -4px;
}

.required-label {
  font-weight: 500;
}

.required-star {
  color: #ee0a24;
  margin-right: 2px;
}


</style>
