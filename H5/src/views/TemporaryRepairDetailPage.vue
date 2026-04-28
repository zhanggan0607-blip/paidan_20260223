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
import { temporaryRepairService, uploadService, operationLogService } from '../services'
import { formatDate } from '@sstcp/shared'
import { WORK_STATUS } from '../config/constants'
import { userStore } from '../stores/userStore'
import OperationLogTimeline from '../components/OperationLogTimeline.vue'
import { useNavigation } from '../composables'
import { copyOrderId } from '../utils/clipboard'
import type { TemporaryRepair } from '../types/models'

const router = useRouter()
const route = useRoute()
const { goBack } = useNavigation()

const loading = ref(false)
const detail = ref<TemporaryRepair | null>(null)
const operationLogRef = ref<InstanceType<typeof OperationLogTimeline> | null>(null)
const isSubmitting = ref(false)
const isInitialized = ref(false)

const formData = ref({
  remarks: '',
  signature: '',
  fault_description: '',
  solution: '',
})

const currentPhotos = ref<string[]>([])
const showPhotoPopup = ref(false)
const showRejectDialog = ref(false)
const rejectReason = ref('')

const canApprove = computed(() => userStore.canApproveTemporaryRepair())

const isApproveMode = computed(() => {
  return canApprove.value && detail.value?.status === WORK_STATUS.PENDING_CONFIRM
})

const isWorker = computed(() => {
  const user = userStore.getUser()
  if (!user || !detail.value) return false
  const workerName = detail.value.maintenance_personnel
  console.log('=== isWorker 计算属性 ===')
  console.log('当前用户:', user.name)
  console.log('工单维护人员:', workerName)
  console.log('匹配结果:', workerName === user.name)
  console.log('==================')
  return workerName === user.name
})

const isEditable = computed(() => {
  const status = detail.value?.status
  if (status === WORK_STATUS.COMPLETED) return false
  return status === WORK_STATUS.IN_PROGRESS || 
         status === WORK_STATUS.PENDING_CONFIRM || 
         status === WORK_STATUS.RETURNED
})

const canSubmit = computed(() => {
  if (currentPhotos.value.length === 0 || !formData.value.signature) return false
  if (!isWorker.value) return false
  const status = detail.value?.status
  return status === WORK_STATUS.IN_PROGRESS || status === WORK_STATUS.RETURNED
})

const canUpdate = computed(() => {
  const status = detail.value?.status
  return status === WORK_STATUS.PENDING_CONFIRM || status === WORK_STATUS.IN_PROGRESS || status === WORK_STATUS.RETURNED
})

const handleBackToList = () => {
  goBack()
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
    const response = await temporaryRepairService.getById(Number(id))
    if (response.code === 200 && response.data) {
      detail.value = response.data
      formData.value.remarks = response.data.remarks || ''
      formData.value.signature = response.data.signature || ''
      formData.value.fault_description = response.data.fault_description || ''
      formData.value.solution = response.data.solution || ''
      currentPhotos.value = response.data.photos || []
    } else {
      console.error('API returned non-200:', response)
      showFailToast(response.message || '加载数据失败')
    }
  } catch (error: any) {
    console.error('Failed to fetch detail:', error)
    if (error.status === 403) {
      showFailToast('无权查看此工单')
    } else if (error.status === 401) {
      showFailToast('请先登录')
      router.push('/login')
    } else if (error.status === 404) {
      showFailToast('工单不存在')
    } else {
      showFailToast(error.message || '加载失败')
    }
  } finally {
    loading.value = false
    closeToast()
  }
}

const loadSignature = async () => {
  console.log('=== 加载签字数据 ===')
  const signatureData = localStorage.getItem('temporary_repair_signature')
  console.log('localStorage中的签字数据:', signatureData ? '存在(长度:' + signatureData.length + ')' : '不存在')
  if (signatureData) {
    formData.value.signature = signatureData
    console.log('签字数据已加载到formData')
    
    if (detail.value?.id && isEditable.value) {
      try {
        console.log('立即保存签字数据到后端...')
        const saveData = {
          signature: signatureData,
        }
        const response = await temporaryRepairService.patch(detail.value.id, saveData)
        if (response.code === 200) {
          console.log('签字数据保存成功，清除localStorage')
          localStorage.removeItem('temporary_repair_signature')
        } else {
          console.error('签字数据保存失败:', response.message)
        }
      } catch (error) {
        console.error('保存签字数据失败:', error)
      }
    }
  }
  console.log('formData.signature:', formData.value.signature ? '存在(长度:' + formData.value.signature.length + ')' : '不存在')
  console.log('==================')
}

const handlePhotoUpload = () => {
  console.log('=== 照片查看/上传调试 ===')
  console.log('isEditable:', isEditable.value)
  console.log('isWorker:', isWorker.value)
  console.log('status:', detail.value?.status)
  console.log('maintenance_personnel:', detail.value?.maintenance_personnel)
  console.log('user.name:', userStore.getUser()?.name)
  console.log('==================')
  showPhotoPopup.value = true
}

const handlePhotoCapture = () => {
  console.log('========================================')
  console.log('========= 2026-03-25 v10 =========')
  console.log('========================================')
  console.log('=== handlePhotoCapture 被调用 ===')
  const ua = navigator.userAgent.toLowerCase()
  console.log('navigator.userAgent:', navigator.userAgent)
  console.log('navigator.platform:', navigator.platform)
  console.log('navigator.maxTouchPoints:', navigator.maxTouchPoints)
  
  const isIOS = /iphone|ipad|ipod/.test(ua) || (navigator.platform === 'MacIntel' && navigator.maxTouchPoints > 1)
  const isDingTalk = /dingtalk|ddwebview|dd/.test(ua)
  const isMobile = /mobile|android|iphone|ipad|ipod|blackberry|iemobile|opera mini/i.test(ua)
  const useBase64Upload = isIOS || isDingTalk || isMobile || navigator.maxTouchPoints > 1
  
  console.log('isIOS检测结果:', isIOS)
  console.log('isDingTalk检测结果:', isDingTalk)
  console.log('isMobile检测结果:', isMobile)
  console.log('navigator.maxTouchPoints > 1:', navigator.maxTouchPoints > 1)
  console.log('useBase64Upload:', useBase64Upload)

  tryCaptureOnIOS()
}

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
      console.log('=== iOS拍照上传流程 ===')
      console.log('原始文件大小:', file.size, 'bytes')
      console.log('文件类型:', file.type)
      
      const userName = userStore.getUser()?.name || '未知用户'
      console.log('用户名:', userName)
      
      let fileToUpload = file
      
      if (file.size > 500 * 1024) {
        console.log('图片太大，开始压缩...')
        showLoadingToast({ message: '压缩中...', forbidClick: true, duration: 0 })
        
        const compressedBlob = await compressImage(file, 500)
        fileToUpload = new File([compressedBlob], file.name, { type: 'image/jpeg' })
        console.log('压缩后文件大小:', fileToUpload.size, 'bytes')
      }

      console.log('开始上传（使用Base64方式）...')
      console.log('文件大小:', fileToUpload.size, 'bytes')
      
      const reader = new FileReader()
      
      reader.onload = async (e) => {
        try {
          const base64Data = e.target?.result as string
          if (!base64Data) {
            throw new Error('无法读取文件数据')
          }
          console.log('Base64数据长度:', base64Data.length)
          
          const response = await uploadService.uploadImageBase64(base64Data, fileToUpload.name)
          console.log('上传响应:', response)

          if (response.code === 200 && response.data) {
            console.log('上传成功，URL:', response.data.url)
            const newPhotoUrl = response.data.url
            console.log('newPhotoUrl:', newPhotoUrl)
            console.log('push前 currentPhotos:', JSON.stringify(currentPhotos.value))
            currentPhotos.value.push(newPhotoUrl)
            console.log('push后 currentPhotos:', JSON.stringify(currentPhotos.value))
            console.log('currentPhotos.value.length:', currentPhotos.value.length)
            
            const photosToSave = [...currentPhotos.value]
            console.log('photosToSave:', JSON.stringify(photosToSave))
            
            console.log('=== 检查保存条件 ===')
            console.log('detail.value?.id:', detail.value?.id)
            
            const detailId = detail.value?.id
            if (detailId) {
              console.log('=== iOS直接保存到后端 ===')
              const saveData = {
                photos: photosToSave,
                signature: formData.value.signature,
                remarks: formData.value.remarks,
                fault_description: formData.value.fault_description,
                solution: formData.value.solution,
              }
              console.log('保存数据:', JSON.stringify(saveData, null, 2))
              
              closeToast()
              showLoadingToast({ message: '保存中...', forbidClick: true, duration: 0 })
              
              try {
                console.log('调用temporaryRepairService.patch, id:', detailId)
                const saveResponse = await temporaryRepairService.patch(detailId, saveData)
                console.log('iOS保存结果:', saveResponse)
                closeToast()
                isIOSUploading = false
                if (saveResponse.code === 200) {
                  console.log('保存成功! photos:', saveResponse.data?.photos)
                  showSuccessToast('上传并保存成功')
                } else {
                  console.error('保存失败:', saveResponse.message)
                  showFailToast('保存失败: ' + (saveResponse.message || '未知错误'))
                }
              } catch (saveError: any) {
                console.error('保存请求失败:', saveError)
                closeToast()
                isIOSUploading = false
                showFailToast('保存请求失败: ' + (saveError.message || ''))
              }
            } else {
              closeToast()
              isIOSUploading = false
              console.error('条件不满足: detail.value?.id=', detailId)
              showFailToast('无法保存：缺少工单ID')
            }
          } else {
            console.error('上传失败:', response.message)
            closeToast()
            isIOSUploading = false
            showFailToast('上传失败: ' + (response.message || '未知错误'))
          }
        } catch (uploadError: any) {
          console.error('上传请求失败:', uploadError)
          closeToast()
          isIOSUploading = false
          showFailToast('上传失败: ' + (uploadError.message || ''))
        }
      }
      
      reader.onerror = (error) => {
        console.error('FileReader错误:', error)
        closeToast()
        isIOSUploading = false
        showFailToast('读取文件失败')
      }
      
      console.log('开始readAsDataURL...')
      reader.readAsDataURL(fileToUpload)
      
    } catch (error: any) {
      console.error('处理流程失败:', error)
      closeToast()
      isIOSUploading = false
      showFailToast('处理失败: ' + (error.message || ''))
    }
  }

  document.body.appendChild(input)
  input.click()
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

/**
 * 获取完整图片URL
 */
const getFullImageUrl = (url: string): string => {
  if (!url) return ''
  if (url.startsWith('http://') || url.startsWith('https://') || url.startsWith('data:')) {
    return url
  }
  return window.location.origin + url
}

/**
 * 预览图片
 * @param index 图片索引
 */
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
      type: 'temporary-repair',
    },
  })
}

/**
 * 查看签字图片
 */
const handleViewSignature = () => {
  if (formData.value.signature) {
    showImagePreview({
      images: [getFullImageUrl(formData.value.signature)],
      closeable: true,
    })
  } else {
    showFailToast('暂无签字')
  }
}

const handleSubmit = async () => {
  const user = userStore.getUser()
  console.log('=== 提交调试信息 ===')
  console.log('当前用户:', user?.name)
  console.log('工单维护人员:', detail.value?.maintenance_personnel)
  console.log('工单状态:', detail.value?.status)
  console.log('照片数量:', currentPhotos.value.length)
  console.log('签名数据:', formData.value.signature ? '已存在' : '不存在')
  console.log('isWorker:', isWorker.value)
  console.log('isEditable:', isEditable.value)
  console.log('canSubmit:', canSubmit.value)
  console.log('===================')

  const status = detail.value?.status

  if (!isWorker.value) {
    showFailToast('您不是此工单的负责人，无法提交')
    return
  }

  if (status === WORK_STATUS.PENDING_CONFIRM) {
    showFailToast('工单已提交，等待审批中')
    return
  } else if (status === WORK_STATUS.COMPLETED) {
    showFailToast('工单已完成')
    return
  }

  if (currentPhotos.value.length === 0) {
    showFailToast('请上传现场图片')
    return
  }

  if (!formData.value.signature) {
    showFailToast('请完成用户签字确认')
    return
  }

  if (!canSubmit.value) {
    showFailToast('当前状态不允许提交')
    return
  }

  try {
    await showConfirmDialog({
      title: '提示',
      message: '确认提交工单吗？',
    })

    showLoadingToast({ message: '提交中...', forbidClick: true })

    const submitData = {
      photos: currentPhotos.value,
      signature: formData.value.signature,
      remarks: formData.value.remarks,
      fault_description: formData.value.fault_description,
      solution: formData.value.solution,
      status: WORK_STATUS.PENDING_CONFIRM,
    }

    const response = await temporaryRepairService.patch(detail.value?.id!, submitData)

    if (response.code === 200) {
      await addOperationLog('submit', '员工提交工单')
      localStorage.removeItem('temporary_repair_signature')
      showSuccessToast('提交成功')
      router.push({ path: '/work-list', query: { type: 'repair' } })
    }
  } catch (error: any) {
    console.error('提交失败:', error)
    if (error.response?.data?.detail) {
      showFailToast(error.response.data.detail)
    } else if (error !== 'cancel') {
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

    const response = await temporaryRepairService.recall(detail.value?.id!)
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
      photos: currentPhotos.value,
      signature: formData.value.signature,
      remarks: formData.value.remarks,
      fault_description: formData.value.fault_description,
      solution: formData.value.solution,
    }

    const response = await temporaryRepairService.patch(detail.value?.id!, updateData)

    if (response.code === 200) {
      await addOperationLog('update', '员工更新工单内容')
      showSuccessToast('更新成功')
      await fetchDetail()
    }
  } catch (error: any) {
    if (error !== 'cancel') {
      console.error('Failed to update:', error)
      showFailToast('更新失败')
    }
  } finally {
    closeToast()
  }
}

let autoSaveTimer: ReturnType<typeof setTimeout> | null = null
let isIOSUploading = false

/**
 * 自动保存内容到后端（防抖）
 */
const autoSaveContent = async () => {
  console.log('=== autoSaveContent 被调用 ===')
  console.log('detail.value?.id:', detail.value?.id)
  console.log('isEditable.value:', isEditable.value)
  console.log('currentPhotos.value.length:', currentPhotos.value.length)
  console.log('isIOSUploading:', isIOSUploading)

  if (!detail.value?.id || !isEditable.value) {
    console.log('自动保存被跳过: id或isEditable不满足条件')
    return
  }

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
    console.log('=== 开始执行自动保存 ===')
    try {
      const saveData: Record<string, any> = {
        signature: formData.value.signature,
        remarks: formData.value.remarks,
        fault_description: formData.value.fault_description,
        solution: formData.value.solution,
      }
      if (currentPhotos.value.length > 0) {
        saveData.photos = currentPhotos.value
      }
      console.log('保存数据:', JSON.stringify({ ...saveData, photos: saveData.photos ? `[${(saveData.photos as string[]).length}张照片]` : '不更新' }))

      const response = await temporaryRepairService.patch(detail.value?.id!, saveData)
      console.log('保存结果:', response)
    } catch (error) {
      console.error('Auto save failed:', error)
    }
  }, 1000)
}

watch(
  () => formData.value.remarks,
  () => {
    autoSaveContent()
  }
)

watch(
  () => formData.value.signature,
  () => {
    autoSaveContent()
  }
)

watch(
  () => formData.value.fault_description,
  () => {
    autoSaveContent()
  }
)

watch(
  () => formData.value.solution,
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

    const response = await temporaryRepairService.patch(detail.value?.id!, submitData)

    if (response.code === 200) {
      await addOperationLog('approve', '部门经理审批通过')
      showSuccessToast('审批通过')
      router.push({ path: '/work-list', query: { type: 'repair' } })
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

    const response = await temporaryRepairService.patch(detail.value?.id!, submitData)

    if (response.code === 200) {
      await addOperationLog('reject', `部门经理退回工单，原因：${reason}`)
      showSuccessToast('已退回')
      router.push({ path: '/work-list', query: { type: 'repair' } })
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
      work_order_type: 'temporary_repair',
      work_order_id: detail.value.id,
      work_order_no: detail.value.repair_id,
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

onMounted(async () => {
  if (isInitialized.value) return
  
  if (!userStore.isLoggedIn()) {
    console.warn('User not logged in, redirecting to login page')
    router.push('/login')
    return
  }

  const user = userStore.getUser()
  if (!user) {
    console.warn('User data not found')
    showFailToast('用户信息不存在，请重新登录')
    router.push('/login')
    return
  }

  isInitialized.value = true
  await fetchDetail()
  loadSignature()
})

onActivated(async () => {
  if (!isInitialized.value) {
    if (!userStore.isLoggedIn()) {
      router.push('/login')
      return
    }
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
</script>

<template>
  <div class="temporary-repair-detail">
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
        <van-cell title="工单编号">
          <template #value>
            <div class="order-id-cell">
              <div
                class="order-id-text"
                :style="{ fontSize: getWorkIdFontSize(detail.repair_id) + 'px' }"
              >
                {{ detail.repair_id }}
              </div>
              <van-button
                size="mini"
                type="primary"
                plain
                @click.stop="copyOrderId(detail.repair_id)"
                >复制单号</van-button
              >
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
        <van-field name="remarks"
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

      <van-cell-group inset title="维修详情">
        <van-field name="fault_description"
          v-model="formData.fault_description"
          rows="2"
          autosize
          label="故障描述"
          type="textarea"
          placeholder="请输入故障描述"
          show-word-limit
          maxlength="500"
          :readonly="!isEditable"
        />
        <van-field name="solution"
          v-model="formData.solution"
          rows="2"
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
        <van-cell v-if="isEditable" is-link @click="handlePhotoUpload">
          <template #title>
            <span>现场图片</span>
          </template>
          <template #value>
            <span :class="currentPhotos.length > 0 ? 'status-done' : 'status-action'">
              {{ currentPhotos.length > 0 ? `已上传${currentPhotos.length}张` : '去上传' }}
            </span>
          </template>
        </van-cell>
        <van-cell v-else is-link @click="handlePhotoUpload">
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

      <van-cell-group inset title="用户确认">
        <van-cell v-if="isEditable" is-link @click="handleSignature">
          <template #title>
            <span>用户签字<span class="required-mark">*</span></span>
          </template>
          <template #value>
            <img
              v-if="formData.signature"
              :src="formData.signature"
              class="signature-preview"
              loading="lazy"
            />
            <span v-else class="status-action">待签字(必填)</span>
          </template>
        </van-cell>
        <van-cell v-else is-link @click="handleViewSignature">
          <template #title>
            <span>用户签字</span>
          </template>
          <template #value>
            <img
              v-if="formData.signature"
              :src="formData.signature"
              class="signature-preview"
              loading="lazy"
            />
            <span v-else class="status-pending">暂未签字</span>
          </template>
        </van-cell>
      </van-cell-group>

      <OperationLogTimeline
        v-if="detail?.id"
        ref="operationLogRef"
        work-order-type="temporary_repair"
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
.temporary-repair-detail {
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

.required-mark {
  color: var(--color-danger);
  margin-left: 2px;
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
  display: flex;
  gap: 12px;
}

.popup-footer .van-button {
  flex: 1;
}
</style>
