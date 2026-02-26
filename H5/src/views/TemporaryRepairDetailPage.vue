<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { showLoadingToast, closeToast, showSuccessToast, showFailToast, showConfirmDialog, showToast } from 'vant'
import api from '../utils/api'
import type { ApiResponse } from '../types'
import { WORK_STATUS, formatDate } from '../config/constants'
import UserSelector from '../components/UserSelector.vue'
import { userStore } from '../stores/userStore'
import OperationLogTimeline from '../components/OperationLogTimeline.vue'
import { processPhoto, getCurrentLocation } from '../utils/watermark'
import { useNavigation } from '../composables'

const router = useRouter()
const route = useRoute()
const { goBack } = useNavigation()

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
const operationLogRef = ref<InstanceType<typeof OperationLogTimeline> | null>(null)

const formData = ref({
  remarks: '',
  signature: ''
})

const currentPhotos = ref<string[]>([])
const showPhotoPopup = ref(false)

const isEditable = computed(() => {
  const status = detail.value?.status
  return status === WORK_STATUS.NOT_STARTED || 
         status === WORK_STATUS.RETURNED ||
         status === '未进行' ||
         status === '待提交'
})

const canSubmit = computed(() => {
  return currentPhotos.value.length > 0
})

const handleBackToList = () => {
  goBack()
}

const canApprove = computed(() => userStore.canApproveTemporaryRepair())

const isApproveMode = computed(() => {
  return route.query.mode === 'approve' && canApprove.value && detail.value?.status === WORK_STATUS.PENDING_CONFIRM
})

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

const handleSubmit = async () => {
  if (!canSubmit.value) {
    showFailToast('请上传现场图片')
    return
  }

  try {
    await showConfirmDialog({
      title: '提示',
      message: '确认提交工单吗？'
    })
    
    showLoadingToast({ message: '提交中...', forbidClick: true })
    
    const submitData = {
      photos: currentPhotos.value,
      signature: formData.value.signature,
      remarks: formData.value.remarks,
      status: WORK_STATUS.PENDING_CONFIRM
    }
    
    const response = await api.patch<unknown, ApiResponse<any>>(`/temporary-repair/${detail.value?.id}`, submitData)
    
    if (response.code === 200) {
      await addOperationLog('submit', '员工提交工单')
      localStorage.removeItem('temporary_repair_signature')
      showSuccessToast('提交成功')
      goBack()
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
      photos: currentPhotos.value,
      signature: formData.value.signature,
      remarks: formData.value.remarks
    }
    
    const response = await api.patch<unknown, ApiResponse<any>>(`/temporary-repair/${detail.value?.id}`, saveData)
    
    if (response.code === 200) {
      await addOperationLog('save', '员工保存工单')
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
    
    const response = await api.patch<unknown, ApiResponse<any>>(`/temporary-repair/${detail.value?.id}`, submitData)
    
    if (response.code === 200) {
      await addOperationLog('approve', '部门经理审批通过')
      showSuccessToast('审批通过')
      goBack()
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
    
    const response = await api.patch<unknown, ApiResponse<any>>(`/temporary-repair/${detail.value?.id}`, submitData)
    
    if (response.code === 200) {
      await addOperationLog('reject', '部门经理退回工单')
      showSuccessToast('已退回')
      goBack()
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

onMounted(() => {
  fetchDetail()
  loadSignature()
})

/**
 * 记录操作日志
 * @param operationTypeCode 操作类型编码
 * @param operationRemark 操作备注
 */
const addOperationLog = async (operationTypeCode: string, operationRemark?: string) => {
  if (!detail.value?.id) return
  
  const user = userStore.getUser()
  if (!user) return
  
  try {
    await api.post('/work-order-operation-log', {
      work_order_type: 'temporary_repair',
      work_order_id: detail.value.id,
      work_order_no: detail.value.repair_id,
      operator_name: user.name,
      operator_id: user.id,
      operation_type_code: operationTypeCode,
      operation_remark: operationRemark
    })
    
    if (operationLogRef.value) {
      operationLogRef.value.refresh()
    }
  } catch (error) {
    console.error('Failed to add operation log:', error)
  }
}
</script>

<template>
  <div class="temporary-repair-detail">
    <van-nav-bar 
      title="临时维修单" 
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
        <UserSelector />
      </template>
    </van-nav-bar>
    
    <div class="content" v-if="detail">
      <van-cell-group inset title="基本资料">
        <van-cell title="项目名称" :value="detail.project_name" />
        <van-cell title="工单编号">
          <template #value>
            <div class="order-id-cell">
              <div class="order-id-text" :style="{ fontSize: getWorkIdFontSize(detail.repair_id) + 'px' }">{{ detail.repair_id }}</div>
              <van-button size="mini" type="primary" plain @click.stop="copyOrderId(detail.repair_id)">复制单号</van-button>
            </div>
          </template>
        </van-cell>
        <van-cell title="维保开始日期" :value="formatDate(detail.plan_start_date)" />
        <van-cell title="维保截止日期" :value="formatDate(detail.plan_end_date)" />
        <van-cell title="客户单位" :value="detail.client_name || '-'" />
        <van-cell title="客户联系人" :value="detail.client_contact || '-'" />
        <van-cell title="客户联系方式" :value="detail.client_contact_info || '-'" />
      </van-cell-group>

      <van-cell-group inset title="报修内容">
        <van-field
          v-model="formData.remarks"
          rows="3"
          autosize
          label="报修内容"
          type="textarea"
          placeholder="请输入报修内容"
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
            <span :class="currentPhotos.length > 0 ? 'status-done' : 'status-action'">
              {{ currentPhotos.length > 0 ? `已上传${currentPhotos.length}张` : '去上传' }}
            </span>
          </template>
        </van-cell>
      </van-cell-group>

      <van-cell-group inset title="用户确认">
        <van-cell is-link @click="handleSignature" :disabled="!isEditable">
          <template #title>
            <span>用户签字</span>
          </template>
          <template #value>
            <img v-if="formData.signature" :src="formData.signature" class="signature-preview" loading="lazy" />
            <span v-else class="status-pending">待签字</span>
          </template>
        </van-cell>
      </van-cell-group>

      <OperationLogTimeline 
        v-if="detail?.id" 
        work-order-type="temporary_repair" 
        :work-order-id="detail.id"
        ref="operationLogRef"
      />

      <div class="action-buttons" v-if="isEditable">
        <van-button type="default" size="large" @click="handleSave">保存</van-button>
        <van-button type="primary" size="large" @click="handleSubmit" :disabled="!canSubmit">提交</van-button>
      </div>

      <div class="action-buttons" v-if="isApproveMode">
        <van-button type="danger" size="large" @click="handleApproveReject">退回</van-button>
        <van-button type="success" size="large" @click="handleApprovePass">审批通过</van-button>
      </div>
    </div>
    
    <van-empty v-else-if="!loading" description="暂无数据" />
    
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

:deep(.van-cell__title) {
  flex: none;
  width: 28%;
  min-width: 90px;
}

:deep(.van-cell__value) {
  flex: 1;
  width: 72%;
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
  background-color: #fff;
  border: 1px solid #e5e5e5;
  border-radius: 4px;
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
</style>
