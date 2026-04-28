<script setup lang="ts">
import { ref, onMounted, onActivated, computed, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import {
  showLoadingToast,
  closeToast,
  showSuccessToast,
  showFailToast,
  showConfirmDialog,
  showImagePreview,
} from 'vant'
import { spotWorkService, uploadService, operationLogService } from '../services'
import { formatDate, getWorkIdFontSize, processPhoto, getCurrentLocation } from '@sstcp/shared'
import { WORK_STATUS } from '../config/constants'
import { copyOrderId } from '../utils/clipboard'
import { useNavigation } from '../composables'
import { userStore } from '../stores/userStore'
import OperationLogTimeline from '../components/OperationLogTimeline.vue'
import type { SpotWork, SpotWorkWorker } from '../types/models'

const router = useRouter()
const route = useRoute()
const { goBack } = useNavigation()

const loading = ref(false)
const detail = ref<SpotWork | null>(null)
const operationLogRef = ref<InstanceType<typeof OperationLogTimeline> | null>(null)
const isSubmitting = ref(false)
const isInitialized = ref(false)

const formData = ref({
  work_content: '',
  remarks: '',
  signature: '',
})

const currentPhotos = ref<string[]>([])
const showPhotoPopup = ref(false)
const showWorkerPopup = ref(false)
const currentWorker = ref<SpotWorkWorker | null>(null)
const showRejectDialog = ref(false)
const rejectReason = ref('')

const isEditable = computed(() => {
  const status = detail.value?.status
  if (status === WORK_STATUS.COMPLETED) return false
  return status === WORK_STATUS.IN_PROGRESS || 
         status === WORK_STATUS.PENDING_CONFIRM || 
         status === WORK_STATUS.RETURNED
})

const canSubmit = computed(() => {
  if (!formData.value.work_content) return false
  if (!isWorker.value) return false
  const status = detail.value?.status
  return status === WORK_STATUS.IN_PROGRESS || status === WORK_STATUS.RETURNED
})

const canUpdate = computed(() => {
  const status = detail.value?.status
  return status === WORK_STATUS.PENDING_CONFIRM || status === WORK_STATUS.IN_PROGRESS || status === WORK_STATUS.RETURNED
})

const canApprove = computed(() => userStore.canApproveSpotWork())

const isApproveMode = computed(() => {
  return canApprove.value && detail.value?.status === WORK_STATUS.PENDING_CONFIRM
})

const isWorker = computed(() => {
  const user = userStore.getUser()
  if (!user || !detail.value) return false
  return detail.value.maintenance_personnel === user.name
})

const handleBackToList = () => {
  goBack()
}

const showWorkerDetail = (worker: SpotWorkWorker) => {
  currentWorker.value = worker
  showWorkerPopup.value = true
}

/**
 * 获取状态样式类名
 * @param status 状态
 * @returns 样式类名
 */
const getStatusClass = (status: string) => {
  if (status === '执行中') {
    return 'status-pending'
  }
  if (status === '待确认') {
    return 'status-waiting'
  }
  if (status === '已完成') {
    return 'status-completed'
  }
  if (status === '已退回') {
    return 'status-returned'
  }
  return ''
}

const fetchDetail = async () => {
  const id = route.params.id
  if (!id) return

  loading.value = true
  showLoadingToast({ message: '加载中...', forbidClick: true })

  try {
    const response = await spotWorkService.getById(Number(id))
    if (response.code === 200) {
      detail.value = response.data
      if (response.data) {
        formData.value.work_content = response.data.work_content || ''
        formData.value.remarks = response.data.remarks || ''
        formData.value.signature = response.data.signature || ''
        if (response.data.photos) {
          try {
            currentPhotos.value =
              typeof response.data.photos === 'string'
                ? JSON.parse(response.data.photos)
                : response.data.photos
          } catch {
            currentPhotos.value = []
          }
        } else {
          currentPhotos.value = []
        }
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
  const signatureData = localStorage.getItem('spot_work_signature')
  if (signatureData) {
    formData.value.signature = signatureData
  }
}

const handlePhotoUpload = () => {
  showPhotoPopup.value = true
}

const handlePhotoCapture = () => {
  const ua = navigator.userAgent.toLowerCase()
  const isIOS = /iphone|ipad|ipod/.test(ua) || (navigator.platform === 'MacIntel' && navigator.maxTouchPoints > 1)
  const isDingTalk = /dingtalk|ddwebview|dd/.test(ua)
  const isMobile = /mobile|android|iphone|ipad|ipod|blackberry|iemobile|opera mini/i.test(ua)
  const useBase64Upload = isIOS || isDingTalk || isMobile || navigator.maxTouchPoints > 1

  if (useBase64Upload) {
    tryCaptureOnIOS()
  } else {
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
          longitude: location?.longitude,
        })

        const formDataObj = new FormData()
        formDataObj.append('file', processedFile)

        const response = await uploadService.uploadFile(processedFile)

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
}

/**
 * iOS设备拍照上传
 */
let isIOSUploading = false

const tryCaptureOnIOS = () => {
  isIOSUploading = true
  const input = document.createElement('input')
  input.type = 'file'
  input.accept = 'image/*'
  input.style.position = 'fixed'
  input.style.top = '0'
  input.style.left = '0'
  input.style.width = '100%'
  input.style.height = '100%'
  input.style.opacity = '0'
  input.style.zIndex = '999999'

  input.onchange = async (e: Event) => {
    const target = e.target as HTMLInputElement
    const file = target.files?.[0]
    if (!file) {
      isIOSUploading = false
      return
    }

    if (document.body.contains(input)) {
      document.body.removeChild(input)
    }

    showLoadingToast({ message: '上传中...', forbidClick: true, duration: 0 })

    try {
      console.log('=== iOS零星用工拍照上传流程 ===')
      console.log('原始文件大小:', file.size, 'bytes')
      
      let fileToUpload = file
      
      if (file.size > 500 * 1024) {
        console.log('图片太大，开始压缩...')
        showLoadingToast({ message: '压缩中...', forbidClick: true, duration: 0 })
        
        const compressedBlob = await compressImage(file, 500)
        fileToUpload = new File([compressedBlob], file.name, { type: 'image/jpeg' })
        console.log('压缩后文件大小:', fileToUpload.size, 'bytes')
      }

      console.log('开始上传（使用Base64方式）...')
      const reader = new FileReader()
      
      reader.onload = async (e) => {
        try {
          const base64Data = e.target?.result as string
          console.log('Base64数据长度:', base64Data.length)
          
          const response = await uploadService.uploadImageBase64(base64Data, fileToUpload.name)
          console.log('上传响应:', response)

          if (response.code === 200 && response.data) {
            console.log('上传成功，URL:', response.data.url)
            currentPhotos.value.push(response.data.url)
            console.log('currentPhotos现在有:', currentPhotos.value.length, '张')
            
            const photosToSave = [...currentPhotos.value]
            
            const detailId = detail.value?.id
            if (detailId) {
              console.log('=== iOS直接保存到后端 ===')
              const saveData = {
                work_content: formData.value.work_content,
                photos: photosToSave,
                signature: formData.value.signature,
                remarks: formData.value.remarks,
              }
              console.log('保存数据:', JSON.stringify(saveData, null, 2))
              
              closeToast()
              showLoadingToast({ message: '正在保存...', forbidClick: true })
              
              const saveResponse = await spotWorkService.patch(detailId, saveData)
              console.log('iOS保存结果:', saveResponse)
              closeToast()
              isIOSUploading = false
              if (saveResponse.code === 200) {
                showSuccessToast('上传并保存成功')
              } else {
                showFailToast('保存失败: ' + (saveResponse.message || '未知错误'))
              }
            } else {
              closeToast()
              isIOSUploading = false
              showSuccessToast('上传成功')
            }
          } else {
            console.error('上传失败:', response.message)
            closeToast()
            isIOSUploading = false
            showFailToast(response.message || '上传失败')
          }
        } catch (uploadError: any) {
          console.error('上传请求失败:', uploadError)
          closeToast()
          isIOSUploading = false
          showFailToast('上传失败')
        }
      }
      
      reader.onerror = (error) => {
        console.error('FileReader错误:', error)
        closeToast()
        isIOSUploading = false
        showFailToast('读取文件失败')
      }
      
      reader.readAsDataURL(fileToUpload)
      
    } catch (error: any) {
      console.error('Failed to process photo:', error)
      closeToast()
      isIOSUploading = false
      showFailToast('处理图片失败')
    }
  }

  document.body.appendChild(input)
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

const handleRemovePhoto = async (index: number) => {
  try {
    await showConfirmDialog({
      title: '提示',
      message: '是否要删除，新增的图片会重新打水印',
    })
    currentPhotos.value.splice(index, 1)
  } catch {}
}

const handlePhotoSave = () => {
  showPhotoPopup.value = false
  showSuccessToast('保存成功')
}

const getFullImageUrl = (url: string): string => {
  if (!url) return ''
  if (url.startsWith('http://') || url.startsWith('https://') || url.startsWith('data:')) {
    return url
  }
  return window.location.origin + url
}

const handlePreviewPhoto = (index: number) => {
  const fullUrls = currentPhotos.value.map((url) => getFullImageUrl(url))
  showImagePreview({
    images: fullUrls,
    startPosition: index,
    closeable: true,
    showIndex: true,
  })
}

const handleSignature = () => {
  router.push({
    path: '/signature',
    query: {
      from: route.fullPath,
      type: 'spot-work',
    },
  })
}

/**
 * 查看签字图片
 */
const handleViewSignature = () => {
  if (formData.value.signature) {
    showImagePreview([formData.value.signature])
  } else {
    showFailToast('暂无签字')
  }
}

const handleSubmit = async () => {
  if (!canSubmit.value) {
    const status = detail.value?.status
    if (status === WORK_STATUS.PENDING_CONFIRM) {
      showFailToast('工单已提交，等待审批中')
    } else if (status === WORK_STATUS.COMPLETED) {
      showFailToast('工单已完成')
    } else {
      showFailToast('请填写工作内容')
    }
    return
  }

  try {
    await showConfirmDialog({
      title: '提示',
      message: '确认提交工单吗？',
    })

    showLoadingToast({ message: '提交中...', forbidClick: true })

    const submitData = {
      work_content: formData.value.work_content,
      photos: currentPhotos.value,
      signature: formData.value.signature,
      status: WORK_STATUS.PENDING_CONFIRM,
      remarks: formData.value.remarks,
    }

    const response = await spotWorkService.patch(detail.value?.id!, submitData)

    if (response.code === 200) {
      await addOperationLog('submit', '员工提交工单')
      localStorage.removeItem('spot_work_signature')
      showSuccessToast('提交成功')
      router.push({ path: '/work-list', query: { type: 'spot' } })
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

const handleRecall = async () => {
  try {
    await showConfirmDialog({
      title: '确认撤回',
      message: '撤回后工单将回到执行中状态，您可以继续编辑。',
    })

    const response = await spotWorkService.recall(detail.value?.id!)
    if (response.code === 200) {
      showSuccessToast('撤回成功')
      await loadData()
    } else {
      showFailToast(response.message || '撤回失败')
    }
  } catch (error: any) {
    if (error !== 'cancel') {
      console.error('撤回失败:', error)
      if (error.response?.data?.detail) {
        showFailToast(error.response.data.detail)
      } else {
        showFailToast('撤回失败')
      }
    }
  }
}

const handleUpdate = async () => {
  if (!canUpdate.value) {
    showFailToast('当前状态不允许更新')
    return
  }

  try {
    await showConfirmDialog({
      title: '提示',
      message: '确认更新工单内容吗？',
    })

    showLoadingToast({ message: '更新中...', forbidClick: true })

    const updateData = {
      work_content: formData.value.work_content,
      photos: currentPhotos.value,
      signature: formData.value.signature,
      remarks: formData.value.remarks,
    }

    const response = await spotWorkService.patch(detail.value?.id!, updateData)

    if (response.code === 200) {
      await addOperationLog('update', '员工更新工单内容')
      showSuccessToast('更新成功')
      await fetchDetail()
    }
  } catch (error) {
    if (error !== 'cancel') {
      console.error('Failed to update:', error)
      showFailToast('更新失败')
    }
  } finally {
    closeToast()
  }
}

let autoSaveTimer: ReturnType<typeof setTimeout> | null = null

/**
 * 自动保存内容到后端（防抖）
 */
const autoSaveContent = async () => {
  if (!detail.value?.id || !isEditable.value) return

  if (isIOSUploading) {
    console.log('自动保存被跳过: iOS正在上传')
    return
  }

  if (autoSaveTimer) {
    clearTimeout(autoSaveTimer)
  }

  autoSaveTimer = setTimeout(async () => {
    if (isIOSUploading) {
      console.log('自动保存被跳过: iOS正在上传')
      return
    }
    try {
      const saveData: Record<string, any> = {
        work_content: formData.value.work_content,
        signature: formData.value.signature,
        remarks: formData.value.remarks,
      }
      if (currentPhotos.value.length > 0) {
        saveData.photos = currentPhotos.value
      }

      await spotWorkService.patch(detail.value?.id!, saveData)
    } catch (error) {
      console.error('Auto save failed:', error)
    }
  }, 1000)
}

watch(
  () => formData.value.work_content,
  () => {
    autoSaveContent()
  }
)

watch(
  () => formData.value.remarks,
  () => {
    autoSaveContent()
  }
)

watch(
  () => currentPhotos.value.length,
  () => {
    autoSaveContent()
  }
)

/**
 * 审批通过
 */
const handleApprovePass = async () => {
  if (!detail.value?.id) return

  if (isSubmitting.value) {
    showFailToast('正在处理中，请勿重复提交')
    return
  }

  try {
    await showConfirmDialog({
      title: '审批确认',
      message: '确认审批通过该工单吗？',
    })

    isSubmitting.value = true
    showLoadingToast({ message: '处理中...', forbidClick: true })

    const submitData = {
      status: '已完成',
    }

    const response = await spotWorkService.patch(detail.value?.id!, submitData)

    if (response.code === 200) {
      await addOperationLog('approve', '部门经理审批通过')
      showSuccessToast('审批通过')
      router.push({ path: '/work-list', query: { type: 'spot' } })
    }
  } catch (error) {
    if (error !== 'cancel') {
      console.error('Failed to approve:', error)
      showFailToast('审批失败')
    }
  } finally {
    closeToast()
    isSubmitting.value = false
  }
}

/**
 * 审批退回 - 显示退回原因输入弹窗
 */
const handleApproveReject = () => {
  if (!detail.value?.id) return

  if (isSubmitting.value) {
    showFailToast('正在处理中，请勿重复提交')
    return
  }

  rejectReason.value = ''
  showRejectDialog.value = true
}

/**
 * 确认退回
 */
const confirmReject = async () => {
  if (!detail.value?.id) return

  const reason = rejectReason.value.trim()
  if (!reason) {
    showFailToast('请输入工单退回原因')
    return
  }
  if (reason.length < 10) {
    showFailToast('退回原因至少需要10个字符')
    return
  }
  if (reason.length > 500) {
    showFailToast('退回原因不能超过500个字符')
    return
  }

  try {
    await showConfirmDialog({
      title: '退回确认',
      message: '确认退回该工单吗？退回后员工需重新填写。',
      confirmButtonText: '确认退回',
      confirmButtonColor: 'var(--color-danger)',
    })

    showRejectDialog.value = false
    isSubmitting.value = true
    showLoadingToast({ message: '处理中...', forbidClick: true })

    const submitData = {
      status: '已退回',
      reject_reason: reason,
    }

    const response = await spotWorkService.patch(detail.value?.id!, submitData)

    if (response.code === 200) {
      await addOperationLog('reject', `部门经理退回工单，原因：${reason}`)
      showSuccessToast('已退回')
      router.push({ path: '/work-list', query: { type: 'spot' } })
    }
  } catch (error) {
    if (error !== 'cancel') {
      console.error('Failed to reject:', error)
      showFailToast('退回失败')
    }
  } finally {
    closeToast()
    isSubmitting.value = false
  }
}

onMounted(async () => {
  if (isInitialized.value) return
  
  if (userStore.isLoggedIn()) {
    const user = userStore.getUser()
    if (user) {
      isInitialized.value = true
      await fetchDetail()
      loadSignature()
    }
  }
})

onActivated(async () => {
  if (!isInitialized.value && userStore.isLoggedIn()) {
    isInitialized.value = true
    await fetchDetail()
    loadSignature()
  }
})

watch(
  () => route.params.id,
  async (newId, oldId) => {
    if (newId && newId !== oldId) {
      await fetchDetail()
      loadSignature()
    }
  }
)

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
    await operationLogService.create({
      work_order_type: 'spot_work',
      work_order_id: detail.value.id,
      work_order_no: detail.value.work_id,
      operator_name: user.name,
      operator_id: user.id,
      operation_type_code: operationTypeCode,
      operation_remark: operationRemark,
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
  <div class="spot-work-detail">
    <van-nav-bar fixed placeholder @click-left="handleBackToList">
      <template #left>
        <div class="nav-left">
          <van-icon name="arrow-left" />
          <span>返回</span>
        </div>
      </template>
    </van-nav-bar>

    <div v-if="detail" class="content">
      <van-cell-group inset title="基本资料">
        <van-cell title="项目名称" :value="detail.project_name" />
        <van-cell title="项目编号" :value="detail.project_id" />
        <van-cell title="工单编号">
          <template #value>
            <div class="order-id-cell">
              <div
                class="order-id-text"
                :style="{ fontSize: getWorkIdFontSize(detail.work_id) + 'px' }"
              >
                {{ detail.work_id }}
              </div>
              <van-button size="mini" type="primary" plain @click.stop="copyOrderId(detail.work_id)"
                >复制单号</van-button
              >
            </div>
          </template>
        </van-cell>
        <van-cell
          title="用工周期"
          :value="`${formatDate(detail.plan_start_date)} 至 ${formatDate(detail.plan_end_date)}`"
        />
        <van-cell v-if="detail.work_days" title="用工天数" :value="detail.work_days + ' 工天'" />
        <van-cell title="客户单位" :value="detail.client_name || '-'" />
        <van-cell title="客户联系人" :value="detail.client_contact || '-'" />
        <van-cell title="客户联系电话" :value="detail.client_contact_info || '-'" />
        <van-cell title="状态">
          <template #value>
            <span class="status-tag" :class="getStatusClass(detail.status)">{{
              detail.status
            }}</span>
          </template>
        </van-cell>
      </van-cell-group>

      <van-cell-group inset title="工作内容">
        <van-field name="work_content"
          v-model="formData.work_content"
          rows="3"
          autosize
          label="工作内容"
          type="textarea"
          placeholder="请输入工作内容"
          show-word-limit
          maxlength="800"
          :readonly="!isEditable"
        />
      </van-cell-group>

      <van-cell-group inset title="工人信息">
        <van-cell v-if="detail.workers && detail.workers.length > 0">
          <template #title>
            <div class="workers-summary">
              <span>共 {{ detail.worker_count }} 人，{{ detail.work_days }} 工天</span>
            </div>
          </template>
        </van-cell>
        <van-cell
          v-for="(worker, index) in detail.workers"
          :key="worker.id || index"
          :title="worker.name"
          :label="worker.id_card_number"
          is-link
          @click="showWorkerDetail(worker)"
        >
          <template #value>
            <div class="worker-photos">
              <van-icon v-if="worker.id_card_front" name="idcard" class="photo-icon done" />
              <van-icon v-else name="idcard" class="photo-icon pending" />
              <van-icon v-if="worker.id_card_back" name="idcard" class="photo-icon done" />
              <van-icon v-else name="idcard" class="photo-icon pending" />
            </div>
          </template>
        </van-cell>
        <van-empty
          v-if="!detail.workers || detail.workers.length === 0"
          description="暂无工人信息"
          image-size="60"
        />
      </van-cell-group>

      <van-cell-group inset title="图片上传">
        <van-cell is-link @click="handlePhotoUpload">
          <template #title>
            <span>现场图片</span>
          </template>
          <template #value>
            <span :class="currentPhotos.length > 0 ? 'status-done' : 'status-pending'">
              {{ currentPhotos.length > 0 ? `已上传${currentPhotos.length}张` : '暂无图片' }}
            </span>
          </template>
        </van-cell>
      </van-cell-group>

      <van-cell-group inset title="班组签字">
        <van-cell v-if="isEditable" is-link @click="handleSignature">
          <template #title>
            <span>班组签字</span>
          </template>
          <template #value>
            <img
              v-if="formData.signature"
              :src="formData.signature"
              class="signature-preview"
              loading="lazy"
            />
            <span v-else class="status-action">待签字</span>
          </template>
        </van-cell>
        <van-cell v-else is-link @click="handleViewSignature">
          <template #title>
            <span>班组签字</span>
          </template>
          <template #value>
            <img
              v-if="formData.signature"
              :src="formData.signature"
              class="signature-preview"
              loading="lazy"
            />
            <span v-else class="status-pending">暂无签字</span>
          </template>
        </van-cell>
      </van-cell-group>

      <OperationLogTimeline
        v-if="detail?.id"
        ref="operationLogRef"
        work-order-type="spot_work"
        :work-order-id="detail.id"
      />

      <div v-if="canUpdate" class="action-buttons">
        <van-button type="primary" size="large" @click="handleUpdate"
          >更新</van-button
        >
      </div>

      <div v-else-if="isEditable" class="action-buttons">
        <van-button v-if="detail?.status === WORK_STATUS.PENDING_CONFIRM && isWorker" type="warning" size="large" @click="handleRecall"
          >撤回</van-button
        >
        <van-button type="primary" size="large" :disabled="!canSubmit" @click="handleSubmit"
          >提交</van-button
        >
      </div>

      <div v-if="isApproveMode" class="action-buttons">
        <van-button type="danger" size="large" :disabled="isSubmitting" @click="handleApproveReject"
          >退回</van-button
        >
        <van-button type="success" size="large" :disabled="isSubmitting" @click="handleApprovePass"
          >审批通过</van-button
        >
      </div>
    </div>

    <van-empty v-else-if="!loading" description="暂无数据" />

    <van-popup v-model:show="showPhotoPopup" position="bottom" round :style="{ height: '60%' }">
      <div class="popup-content">
        <div class="popup-header">
          <span class="popup-title">现场图片</span>
          <van-icon name="cross" @click="showPhotoPopup = false" />
        </div>
        <div class="popup-body">
          <div class="photo-section">
            <div v-if="currentPhotos.length === 0" class="empty-photos">
              <van-icon name="photo-o" size="48" color="#dcdee0" />
              <span>暂无现场图片</span>
            </div>
            <div v-else class="photo-grid">
              <div v-for="(photo, index) in currentPhotos" :key="index" class="photo-item" @click="handlePreviewPhoto(index)">
                <img :src="photo" alt="现场照片" loading="lazy" />
                <van-icon
                  v-if="isEditable"
                  name="delete"
                  class="delete-icon"
                  @click.stop="handleRemovePhoto(index)"
                />
              </div>
            </div>
            <div v-if="isEditable && currentPhotos.length < 9" class="photo-add-wrapper">
              <div class="photo-add" @click="handlePhotoCapture">
                <van-icon name="photograph" size="24" />
                <span>拍照</span>
              </div>
            </div>
            <div v-if="isEditable" class="photo-tip">只支持拍照，最多上传9张</div>
          </div>
        </div>
        <div v-if="isEditable" class="popup-footer">
          <van-button type="primary" block @click="handlePhotoSave">保存</van-button>
        </div>
        <div v-else class="popup-footer">
          <van-button type="default" block @click="showPhotoPopup = false">关闭</van-button>
        </div>
      </div>
    </van-popup>

    <van-popup v-model:show="showWorkerPopup" position="bottom" round :style="{ height: '70%' }">
      <div v-if="currentWorker" class="popup-content">
        <div class="popup-header">
          <span class="popup-title">工人详情</span>
          <van-icon name="cross" @click="showWorkerPopup = false" />
        </div>
        <div class="popup-body">
          <van-cell-group inset>
            <van-cell title="姓名" :value="currentWorker.name" />
            <van-cell title="性别" :value="currentWorker.gender" />
            <van-cell title="出生日期" :value="currentWorker.birth_date" />
            <van-cell title="身份证号" :value="currentWorker.id_card_number" />
            <van-cell title="住址" :value="currentWorker.address" />
            <van-cell title="签发机关" :value="currentWorker.issuing_authority" />
            <van-cell title="有效期限" :value="currentWorker.valid_period" />
          </van-cell-group>
          <div class="id-card-section">
            <div class="id-card-item">
              <div class="id-card-label">身份证正面</div>
              <div class="id-card-preview-large">
                <img
                  v-if="currentWorker.id_card_front"
                  :src="currentWorker.id_card_front"
                  alt="身份证正面"
                  loading="lazy"
                />
                <div v-else class="no-photo">暂无照片</div>
              </div>
            </div>
            <div class="id-card-item">
              <div class="id-card-label">身份证反面</div>
              <div class="id-card-preview-large">
                <img
                  v-if="currentWorker.id_card_back"
                  :src="currentWorker.id_card_back"
                  alt="身份证反面"
                  loading="lazy"
                />
                <div v-else class="no-photo">暂无照片</div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </van-popup>

    <van-popup v-model:show="showRejectDialog" position="bottom" round :style="{ height: '40%' }">
      <div class="popup-content">
        <div class="popup-header">
          <span class="popup-title">退回原因</span>
          <van-icon name="cross" @click="showRejectDialog = false" />
        </div>
        <div class="popup-body">
          <van-field name="reject_reason"
            v-model="rejectReason"
            rows="4"
            autosize
            type="textarea"
            maxlength="500"
            show-word-limit
            placeholder="请输入退回原因（10-500字符）"
            class="reject-reason-input"
          />
          <div class="reject-tip">退回原因需清晰、具体，说明工单被退回的具体问题</div>
        </div>
        <div class="popup-footer">
          <van-button type="default" @click="showRejectDialog = false">取消</van-button>
          <van-button type="danger" @click="confirmReject">确认退回</van-button>
        </div>
      </div>
    </van-popup>
  </div>
</template>

<style scoped>
.spot-work-detail {
  min-height: 100vh;
  background-color: var(--color-bg-page);
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
  color: var(--color-bg-card);
  background-color: var(--color-success);
  border-radius: 4px;
}

.status-pending {
  display: inline-block;
  padding: 2px 8px;
  font-size: 12px;
  color: var(--color-bg-card);
  background-color: var(--color-primary);
  border-radius: 4px;
}

.status-action {
  display: inline-block;
  padding: 3px 10px;
  font-size: 14px;
  color: var(--color-bg-card);
  background-color: var(--color-warning);
  border-radius: 4px;
}

.id-card-section {
  display: flex;
  gap: 12px;
  padding: 12px 16px;
  background: var(--color-bg-card);
}

.id-card-item {
  flex: 1;
}

.id-card-label {
  font-size: 12px;
  color: var(--color-text-secondary);
  margin-bottom: 8px;
}

.id-card-upload {
  width: 100%;
  aspect-ratio: 1.5;
  border: 1px dashed var(--color-border-light);
  border-radius: 8px;
  overflow: hidden;
  display: flex;
  align-items: center;
  justify-content: center;
}

.id-card-upload img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.upload-placeholder {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 4px;
  color: var(--color-text-secondary);
  font-size: 12px;
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
  color: var(--color-danger);
  background: rgba(255, 255, 255, 0.8);
  border-radius: 50%;
  padding: 2px;
}

.photo-add {
  aspect-ratio: 1;
  border: 1px dashed var(--color-border-light);
  border-radius: 8px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 4px;
  color: var(--color-text-secondary);
  font-size: 12px;
}

.photo-add-wrapper {
  margin-top: 8px;
}

.empty-photos {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 40px 0;
  color: var(--color-text-secondary);
  gap: 12px;
}

.empty-photos span {
  font-size: 14px;
}

.photo-tip {
  margin-top: 8px;
  font-size: 12px;
  color: var(--color-text-secondary);
}

.signature-preview {
  width: 80px;
  height: 40px;
  object-fit: contain;
  background-color: var(--color-bg-card);
  border: 1px solid var(--color-border);
  border-radius: 4px;
}

.action-buttons {
  padding: 12px 16px;
  background: var(--color-bg-card);
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
  border-bottom: 1px solid var(--color-border-light);
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
  border-top: 1px solid var(--color-border-light);
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
  color: var(--color-text-primary);
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

.workers-summary {
  font-size: 14px;
  color: var(--color-primary);
  font-weight: 500;
}

.worker-photos {
  display: flex;
  gap: 8px;
}

.photo-icon {
  font-size: 18px;
}

.photo-icon.done {
  color: var(--color-success);
}

.photo-icon.pending {
  color: var(--color-text-placeholder);
}

.id-card-preview-large {
  width: 100%;
  aspect-ratio: 1.5;
  border-radius: 8px;
  overflow: hidden;
  background: var(--color-bg-page);
  display: flex;
  align-items: center;
  justify-content: center;
}

.id-card-preview-large img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.no-photo {
  color: var(--color-text-secondary);
  font-size: 12px;
}

.status-tag {
  display: inline-block;
  padding: 2px 8px;
  border-radius: 4px;
  font-size: 12px;
  font-weight: 500;
}

.status-pending {
  background: var(--color-warning-subtle);
  color: var(--color-warning);
}

.status-waiting {
  background: var(--color-info-subtle);
  color: var(--color-primary);
}

.status-confirmed {
  background: var(--color-success-subtle);
  color: var(--color-success);
}

.status-completed {
  background: var(--color-info-subtle);
  color: var(--color-info);
}

.status-returned {
  background: var(--color-danger-subtle);
  color: var(--color-danger);
}

.status-cancelled {
  background: var(--color-bg-page);
  color: var(--color-text-secondary);
}

.reject-reason-input {
  margin: 12px 16px;
  background: var(--color-bg-page);
  border-radius: 8px;
}

.reject-tip {
  margin: 0 16px;
  font-size: 12px;
  color: var(--color-text-secondary);
  line-height: 1.5;
}

.popup-footer {
  padding: 12px 16px;
  padding-bottom: max(12px, env(safe-area-inset-bottom));
  border-top: 1px solid var(--color-border-light);
  display: flex;
  gap: 12px;
}

.popup-footer .van-button {
  flex: 1;
  min-height: 44px;
  font-size: 16px;
  border-radius: 8px;
}
</style>
