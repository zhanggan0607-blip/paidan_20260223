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
import { formatDate, processPhoto, getCurrentLocation, getWorkIdFontSize } from '@sstcp/shared'
import { WORK_STATUS } from '../config/constants'
import { useUserStore } from '../stores/userStore'
const userStore = useUserStore()
import OperationLogTimeline from '../components/OperationLogTimeline.vue'
import { useNavigation } from '../composables'
import { copyOrderId } from '../utils/clipboard'
import type { TemporaryRepair } from '../types/api'

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
  const user = userStore.currentUser
  if (!user || !detail.value) return false
  const workerName = detail.value.maintenance_personnel
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
  const signatureData = localStorage.getItem('temporary_repair_signature')
  if (signatureData) {
    formData.value.signature = signatureData
    
    if (detail.value?.id && isEditable.value) {
      try {
        const saveData = {
          signature: signatureData,
        }
        const response = await temporaryRepairService.patch(detail.value.id, saveData)
        if (response.code === 200) {
          localStorage.removeItem('temporary_repair_signature')
        } else {
          console.error('签字数据保存失败:', response.message)
        }
      } catch (error) {
        console.error('保存签字数据失败:', error)
      }
    }
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
    input.multiple = true
    input.capture = 'environment'

    input.onchange = async (e: Event) => {
      const target = e.target as HTMLInputElement
      const allFiles = target.files
      if (!allFiles || allFiles.length === 0) return

      const remaining = 9 - currentPhotos.value.length
      if (remaining <= 0) {
        showFailToast('已达到最大上传数量')
        return
      }
      const files = Array.from(allFiles).slice(0, remaining)

      showLoadingToast({ message: `处理中(0/${files.length})...`, forbidClick: true })

      const processedFiles: File[] = []
      let processFailed = 0

      for (let i = 0; i < files.length; i++) {
        try {
          showLoadingToast({ message: `处理中(${i + 1}/${files.length})...`, forbidClick: true })
          const userName = userStore.currentUser?.name || '未知用户'
          const location = await getCurrentLocation()
          const processedFile = await processPhoto(files[i], {
            userName,
            includeLocation: true,
            latitude: location?.latitude,
            longitude: location?.longitude,
          })
          processedFiles.push(processedFile)
        } catch (error) {
          console.error('Failed to process photo:', error)
          processFailed++
        }
      }

      if (processedFiles.length === 0) {
        closeToast()
        showFailToast('图片处理失败')
        return
      }

      showLoadingToast({ message: `上传中(${processedFiles.length}张)...`, forbidClick: true })

      try {
        const response = await uploadService.uploadFiles(processedFiles)
        let uploadedCount = 0
        let failedCount = processFailed

        if (response.code === 200 && response.data) {
          const successList = response.data.success || response.data
          if (Array.isArray(successList)) {
            for (const item of successList) {
              if (item.url) {
                currentPhotos.value.push(item.url)
                uploadedCount++
              }
            }
          }
          const failedList = response.data.failed || []
          failedCount += failedList.length
        } else {
          failedCount += processedFiles.length
        }

        closeToast()
        if (uploadedCount > 0) {
          const photosToSave = [...currentPhotos.value]
          const detailId = detail.value?.id
          if (detailId) {
            showLoadingToast({ message: '保存中...', forbidClick: true })
            try {
              const saveData = {
                photos: photosToSave,
                signature: formData.value.signature,
                remarks: formData.value.remarks,
                fault_description: formData.value.fault_description,
                solution: formData.value.solution,
              }
              await temporaryRepairService.patch(detailId, saveData)
            } catch (saveError) {
              console.error('保存失败:', saveError)
            }
          }
          closeToast()
          showSuccessToast(`成功上传${uploadedCount}张图片${failedCount > 0 ? `，${failedCount}张失败` : ''}`)
        } else {
          showFailToast('上传失败')
        }
      } catch (error) {
        console.error('Batch upload failed:', error)
        closeToast()
        showFailToast('上传失败')
      }
    }

    input.click()
  }
}

const tryCaptureOnIOS = () => {
  isIOSUploading = true
  const input = document.createElement('input')
  input.type = 'file'
  input.accept = 'image/*'
  input.multiple = true
  input.style.position = 'fixed'
  input.style.top = '0'
  input.style.left = '0'
  input.style.width = '100%'
  input.style.height = '100%'
  input.style.opacity = '0'
  input.style.zIndex = '999999'

  input.onchange = async (e: Event) => {
    const target = e.target as HTMLInputElement
    const allFiles = target.files
    if (!allFiles || allFiles.length === 0) {
      isIOSUploading = false
      return
    }

    if (document.body.contains(input)) {
      document.body.removeChild(input)
    }

    const remaining = 9 - currentPhotos.value.length
    if (remaining <= 0) {
      isIOSUploading = false
      showFailToast('已达到最大上传数量')
      return
    }
    const files = Array.from(allFiles).slice(0, remaining)

    showLoadingToast({ message: `上传中(0/${files.length})...`, forbidClick: true, duration: 0 })

    let uploadedCount = 0
    let failedCount = 0

    for (const file of files) {
      try {
        let fileToUpload = file

        if (file.size > 500 * 1024) {
          showLoadingToast({ message: `压缩中(${uploadedCount + 1}/${files.length})...`, forbidClick: true, duration: 0 })

          const compressedBlob = await compressImage(file, 500)
          fileToUpload = new File([compressedBlob], file.name, { type: 'image/jpeg' })
        }

        showLoadingToast({ message: `添加水印(${uploadedCount + 1}/${files.length})...`, forbidClick: true, duration: 0 })
        const userName = userStore.currentUser?.name || '未知用户'
        const location = await getCurrentLocation()
        const watermarkedFile = await processPhoto(fileToUpload, {
          userName,
          includeLocation: true,
          latitude: location?.latitude,
          longitude: location?.longitude,
        })

        showLoadingToast({ message: `上传中(${uploadedCount + 1}/${files.length})...`, forbidClick: true, duration: 0 })

        const reader = new FileReader()

        const base64Data = await new Promise<string>((resolve, reject) => {
          reader.onload = (ev) => resolve(ev.target?.result as string)
          reader.onerror = reject
          reader.readAsDataURL(watermarkedFile)
        })

        if (!base64Data) {
          failedCount++
          continue
        }

        const response = await uploadService.uploadImageBase64(base64Data, fileToUpload.name)

        if (response.code === 200 && response.data) {
          currentPhotos.value.push(response.data.url)
          uploadedCount++
        } else {
          console.error('上传失败:', response.message)
          failedCount++
        }
      } catch (uploadError: any) {
        console.error('上传请求失败:', uploadError)
        failedCount++
      }
    }

    if (uploadedCount > 0) {
      const photosToSave = [...currentPhotos.value]
      const detailId = detail.value?.id
      if (detailId) {
        const saveData = {
          photos: photosToSave,
          signature: formData.value.signature,
          remarks: formData.value.remarks,
          fault_description: formData.value.fault_description,
          solution: formData.value.solution,
        }

        closeToast()
        showLoadingToast({ message: '保存中...', forbidClick: true, duration: 0 })

        try {
          const saveResponse = await temporaryRepairService.patch(detailId, saveData)
          closeToast()
          isIOSUploading = false
          if (saveResponse.code === 200) {
            showSuccessToast(`成功上传${uploadedCount}张图片${failedCount > 0 ? `，${failedCount}张失败` : ''}`)
          } else {
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
        showSuccessToast(`成功上传${uploadedCount}张图片${failedCount > 0 ? `，${failedCount}张失败` : ''}`)
      }
    } else {
      closeToast()
      isIOSUploading = false
      showFailToast('上传失败')
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
  const user = userStore.currentUser

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
      await fetchDetail()
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

      const currentStatus = detail.value?.status
      if (currentStatus === WORK_STATUS.IN_PROGRESS || currentStatus === WORK_STATUS.RETURNED) {
        try {
          const submitResponse = await temporaryRepairService.submit(detail.value?.id!)
          if (submitResponse.code === 200) {
            showSuccessToast('更新成功，已自动提交审核')
          } else {
            showSuccessToast('更新成功，但提交审核失败')
          }
        } catch (submitError) {
          console.error('提交审核失败:', submitError)
          showSuccessToast('更新成功，但提交审核失败')
        }
      } else {
        showSuccessToast('更新成功')
      }

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
  if (!detail.value?.id || !isEditable.value) {
    return
  }

  if (isIOSUploading) {
    return
  }

  if (autoSaveTimer) {
    clearTimeout(autoSaveTimer)
  }

  autoSaveTimer = setTimeout(async () => {
    if (isIOSUploading) {
      return
    }
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

      const response = await temporaryRepairService.patch(detail.value?.id!, saveData)
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

  const user = userStore.currentUser
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
  
  if (!userStore.isLoggedIn) {
    console.warn('User not logged in, redirecting to login page')
    router.push('/login')
    return
  }

  const user = userStore.currentUser
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
    if (!userStore.isLoggedIn) {
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
            <div v-if="isEditable" class="photo-tip">支持拍照或从相册选择，最多上传9张，可多选</div>
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
