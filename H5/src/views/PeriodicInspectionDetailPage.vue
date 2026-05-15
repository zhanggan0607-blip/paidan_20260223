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
import {
  periodicInspectionService,
  maintenancePlanService,
  inspectionItemService,
  uploadService,
  operationLogService,
} from '../services'
import { formatDate, processPhoto, getCurrentLocation, getWorkIdFontSize } from '@sstcp/shared'
import { WORK_STATUS } from '../config/constants'
import { useUserStore } from '../stores/userStore'
const userStore = useUserStore()
import OperationLogTimeline from '../components/OperationLogTimeline.vue'
import { useNavigation } from '../composables'
import { copyOrderId } from '../utils/clipboard'
import { getUploadUrl } from '../utils/uploadUrl'

const router = useRouter()
const route = useRoute()
const { goBack } = useNavigation()

interface WorkPlanDetail {
  id: number
  inspection_id: string
  plan_id?: string
  plan_type?: string
  project_id: string
  project_name: string
  plan_start_date: string
  plan_end_date: string
  client_name?: string
  client_contact?: string
  client_contact_info?: string
  address?: string
  maintenance_personnel?: string
  status: string
  execution_result?: string
  remarks?: string
  signature?: string
  created_at: string
  updated_at: string
}

interface InspectionItemData {
  inspection_item: string
  inspection_content: string
  check_requirements: string
  brief_description: string
}

interface InspectionItemTree {
  id: number
  item_name: string
  item_type: string
  level: number
  parent_id: number | null
  check_content: string | null
  check_standard: string | null
  children?: InspectionItemTree[]
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
const errorMessage = ref('')
const inspectionSystems = ref<InspectionSystem[]>([])
const inspectionItemsLoading = ref(false)
const operationLogRef = ref<InstanceType<typeof OperationLogTimeline> | null>(null)
const isSubmitting = ref(false)
const isInitialized = ref(false)

const formData = ref({
  execution_result: '',
  remarks: '',
  signature: '',
})

const currentInspectionSystem = ref<InspectionSystem | null>(null)
const showInspectionPopup = ref(false)
const showRejectDialog = ref(false)
const rejectReason = ref('')

const isApproveMode = computed(() => {
  return canApprove.value && detail.value?.status === WORK_STATUS.PENDING_CONFIRM
})

const canApprove = computed(() => {
  return userStore.canApprovePeriodicInspection()
})

const isWorker = computed(() => {
  const user = userStore.currentUser
  if (!user || !detail.value) return false
  const workerName = detail.value.maintenance_personnel?.trim()
  const userName = user.name?.trim()
  if (!workerName || !userName) return false
  if (workerName === userName) return true
  if (workerName.toLowerCase() === userName.toLowerCase()) return true
  const normalize = (s: string) => s.replace(/\s+/g, '').toLowerCase()
  return normalize(workerName) === normalize(userName)
})

const isEditable = computed(() => {
  if (!isWorker.value && !userStore.isManager()) return false
  const status = detail.value?.status
  if (status === WORK_STATUS.COMPLETED) return false
  return (
    status === WORK_STATUS.IN_PROGRESS ||
    status === WORK_STATUS.PENDING_CONFIRM ||
    status === WORK_STATUS.RETURNED
  )
})

const allInspected = computed(() => {
  return inspectionSystems.value.every((sys) => sys.inspected)
})

const allPhotosUploaded = computed(() => {
  return inspectionSystems.value.every((sys) => sys.photos_uploaded)
})

const canSign = computed(() => {
  return allInspected.value && allPhotosUploaded.value
})

const canSubmit = computed(() => {
  if (!canSign.value || !formData.value.signature) return false
  if (!isWorker.value && !userStore.isManager()) return false
  return detail.value?.status === WORK_STATUS.IN_PROGRESS
})

const canUpdate = computed(() => {
  if (!isWorker.value && !userStore.isManager()) return false
  const status = detail.value?.status
  return status === WORK_STATUS.PENDING_CONFIRM || status === WORK_STATUS.RETURNED
})

const totalCount = computed(() => {
  return inspectionSystems.value.length || 0
})

const filledCount = computed(() => {
  return inspectionSystems.value.filter((sys) => sys.inspected).length || 0
})

const handleBackToList = () => {
  goBack()
}

const getFullImageUrl = (url: string): string => getUploadUrl(url) || ''

const previewPhoto = (photos: string[], startIndex: number) => {
  if (!photos || photos.length === 0) return
  const fullUrls = photos.map((url) => getFullImageUrl(url))
  showImagePreview({
    images: fullUrls,
    startPosition: startIndex,
    closeable: true,
    showIndex: true,
  })
}

const fetchDetail = async () => {
  const id = route.params.id
  if (!id) return

  loading.value = true
  errorMessage.value = ''
  showLoadingToast({ message: '加载中...', forbidClick: true })

  try {
    const response = await periodicInspectionService.getById(Number(id))
    if (response.code === 200) {
      detail.value = response.data
      if (response.data) {
        formData.value.execution_result = response.data.execution_result || ''
        formData.value.remarks = response.data.remarks || ''
        formData.value.signature = response.data.signature || ''
      }
    }
  } catch (error: any) {
    console.error('Failed to fetch detail:', error)
    if (error?.status === 403) {
      errorMessage.value = '您没有权限查看此工单'
    } else if (error?.status === 404) {
      errorMessage.value = '工单不存在或已被删除'
    } else {
      errorMessage.value = error?.message || '加载失败'
    }
    showFailToast(errorMessage.value)
  } finally {
    loading.value = false
    closeToast()
  }
}

/**
 * 从巡检事项表获取默认的巡检事项
 * 当维保计划没有配置inspection_items时使用
 */
const fetchDefaultInspectionItems = async (): Promise<InspectionSystem[]> => {
  try {
    const response = await inspectionItemService.getTree()
    if (response.code === 200 && response.data) {
      const allItems: InspectionSystem[] = []
      let itemIndex = 0

      const processTreeItems = (items: InspectionItemTree[]) => {
        items.forEach((item) => {
          if (item.level === 3) {
            allItems.push({
              id: item.id,
              name: item.item_name,
              inspected: false,
              photos_uploaded: false,
              inspection_content: item.check_content || '',
              inspection_result: '',
              photos: [],
              check_content: item.check_content || '',
              check_standard: item.check_standard || '',
              equipment_name: '',
              equipment_location: '',
              inspection_item: item.item_name,
              brief_description: '',
            })
            itemIndex++
          }
          if (item.children && item.children.length > 0) {
            processTreeItems(item.children)
          }
        })
      }

      processTreeItems(response.data as any)
      return allItems
    }
  } catch (error) {
    console.error('Failed to fetch default inspection items:', error)
  }
  return []
}

/**
 * 从后端API获取关联维保计划的巡检事项
 * 优先通过定期巡检单的 plan_id 获取对应维保计划的 inspection_items
 * 如果没有关联维保计划，则从巡检事项表获取默认数据
 */
const fetchInspectionItems = async () => {
  if (!detail.value) {
    return
  }

  inspectionItemsLoading.value = true
  try {
    const allItems: InspectionSystem[] = []

    if (detail.value.plan_id) {
      const response = await maintenancePlanService.getByPlanId(detail.value.plan_id)
      if (response.code === 200 && response.data) {
        const plan = response.data
        if (plan.inspection_items) {
          try {
            let items: InspectionItemData[]
            if (typeof plan.inspection_items === 'string') {
              items = JSON.parse(plan.inspection_items)
            } else {
              items = plan.inspection_items
            }
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
                brief_description: item.brief_description || '',
              })
            })
          } catch (e) {
            console.error('解析巡查项数据失败:', e)
          }
        }
      }
    }

    if (allItems.length === 0) {
      const defaultItems = await fetchDefaultInspectionItems()
      inspectionSystems.value = defaultItems
    } else {
      inspectionSystems.value = allItems
    }

    await loadSavedRecords()
  } catch (error) {
    console.error('Failed to fetch maintenance plan:', error)
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
    const response = await periodicInspectionService.getRecordsByInspectionId(
      detail.value.inspection_id
    )
    if (response.code === 200 && response.data) {
      response.data.forEach((savedRecord: any) => {
        const index = inspectionSystems.value.findIndex(
          (item) => String(item.id) === String(savedRecord.item_id)
        )
        if (index !== -1) {
          const sysItem = inspectionSystems.value[index]!
          sysItem.inspected = savedRecord.inspected
          const savedPhotos = savedRecord.photos
          sysItem.photos = Array.isArray(savedPhotos) ? savedPhotos : (savedPhotos ? JSON.parse(savedPhotos) : [])
          sysItem.photos_uploaded =
            savedRecord.photos_uploaded || (savedRecord.photos && savedRecord.photos.length > 0)
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
      inspection_result: system.inspection_result,
    }

    await periodicInspectionService.createRecord(recordData)
  } catch (error: any) {
    console.error('Failed to save record:', error)
    showFailToast('巡检记录保存失败，请重试')
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
  if (system.inspected) {
    currentInspectionSystem.value = { ...system }
    showInspectionPopup.value = true
    return
  }

  if (!isEditable.value) {
    showFailToast('当前工单状态不可编辑')
    return
  }

  try {
    await showConfirmDialog({
      title: '确认巡检',
      message: '是否已完成该巡检项？确认后将进行拍照记录。',
      confirmButtonText: '确认完成',
      cancelButtonText: '取消',
    })

    await showConfirmDialog({
      title: '拍照记录',
      message: '请拍摄现场照片作为巡检记录',
      confirmButtonText: '开始拍照',
      cancelButtonText: '稍后拍照',
    })

    handlePhotoCaptureForItem(system, true)
  } catch {}
}

const handleInspectionSave = async () => {
  if (!currentInspectionSystem.value) return

  const index = inspectionSystems.value.findIndex((s) => s.id === currentInspectionSystem.value!.id)
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

  const ua = navigator.userAgent.toLowerCase()
  const isIOS =
    /iphone|ipad|ipod/.test(ua) ||
    (/mac/i.test(navigator.userAgent) && navigator.maxTouchPoints > 1)
  const isDingTalk = /dingtalk|ddwebview|dd/.test(ua)
  const isMobile = /mobile|android|iphone|ipad|ipod|blackberry|iemobile|opera mini/i.test(ua)
  const useBase64Upload = isIOS || isDingTalk || isMobile || navigator.maxTouchPoints > 1

  if (useBase64Upload) {
    tryCaptureOnIOSForItem(system, markAsInspected)
  } else {
    const input = document.createElement('input')
    input.type = 'file'
    input.accept = 'image/jpeg,image/png'
    input.multiple = true
    input.capture = 'environment'

    input.onchange = async (e: Event) => {
      const target = e.target as HTMLInputElement
      const allFiles = target.files
      if (!allFiles || allFiles.length === 0) return

      const remaining = 9 - system.photos.length
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
          try {
            const processedFile = await processPhoto(files[i], {
              userName,
              includeLocation: true,
              latitude: location?.latitude,
              longitude: location?.longitude,
            })
            processedFiles.push(processedFile)
          } catch (watermarkError) {
            console.warn('水印处理失败，使用原图:', watermarkError)
            processedFiles.push(files[i])
          }
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
                const index = inspectionSystems.value.findIndex((s) => s.id === system.id)
                if (index !== -1) {
                  const item_ref = inspectionSystems.value[index]!
                  item_ref.photos.push(item.url)
                  item_ref.photos_uploaded = item_ref.photos.length > 0
                  if (markAsInspected) {
                    item_ref.inspected = true
                  }
                }
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
          const index = inspectionSystems.value.findIndex((s) => s.id === system.id)
          if (index !== -1) {
            await saveRecordToBackend(inspectionSystems.value[index])
          }
          showSuccessToast(
            `成功上传${uploadedCount}张图片${failedCount > 0 ? `，${failedCount}张失败` : ''}`
          )
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

/**
 * iOS设备拍照上传（巡检项专用）
 * @param system 巡检项
 * @param markAsInspected 拍照完成后是否自动标记为已完成
 */
const tryCaptureOnIOSForItem = (system: InspectionSystem, markAsInspected: boolean = false) => {
  const input = document.createElement('input')
  input.type = 'file'
  input.accept = 'image/jpeg,image/png'
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
    if (!allFiles || allFiles.length === 0) return

    if (document.body.contains(input)) {
      document.body.removeChild(input)
    }

    const remaining = 9 - system.photos.length
    if (remaining <= 0) {
      showFailToast('已达到最大上传数量')
      return
    }
    const files = Array.from(allFiles).slice(0, remaining)

    showLoadingToast({ message: `上传中(0/${files.length})...`, forbidClick: true, duration: 0 })

    let uploadedCount = 0
    let failedCount = 0

    for (const file of files) {
      try {
        showLoadingToast({
          message: `处理中(${uploadedCount + failedCount + 1}/${files.length})...`,
          forbidClick: true,
          duration: 0,
        })
        const userName = userStore.currentUser?.name || '未知用户'
        let watermarkedFile: File
        try {
          const location = await getCurrentLocation()
          watermarkedFile = await processPhoto(file, {
            userName,
            includeLocation: true,
            latitude: location?.latitude,
            longitude: location?.longitude,
          })
        } catch (watermarkError: any) {
          console.warn('水印处理失败，使用原图上传:', watermarkError)
          watermarkedFile = file
        }

        showLoadingToast({
          message: `上传中(${uploadedCount + failedCount + 1}/${files.length}) 0%...`,
          forbidClick: true,
          duration: 0,
        })

        const reader = new FileReader()

        const base64Data = await new Promise<string>((resolve, reject) => {
          reader.onload = (ev) => resolve(ev.target?.result as string)
          reader.onerror = reject
          reader.readAsDataURL(watermarkedFile)
        })

        const response = await uploadService.uploadImageBase64(
          base64Data,
          watermarkedFile.name,
          (progress) => {
            showLoadingToast({
              message: `上传中(${uploadedCount + failedCount + 1}/${files.length}) ${progress.percent}%...`,
              forbidClick: true,
              duration: 0,
            })
          }
        )

        if (response.code === 200 && response.data) {
          const index = inspectionSystems.value.findIndex((s) => s.id === system.id)
          if (index !== -1) {
            const item = inspectionSystems.value[index]!
            item.photos.push(response.data.url)
            item.photos_uploaded = item.photos.length > 0
            if (markAsInspected) {
              item.inspected = true
            }
          }
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

    closeToast()
    if (uploadedCount > 0) {
      const index = inspectionSystems.value.findIndex((s) => s.id === system.id)
      if (index !== -1) {
        await saveRecordToBackend(inspectionSystems.value[index])
      }
      showSuccessToast(
        `成功上传${uploadedCount}张图片${failedCount > 0 ? `，${failedCount}张失败` : ''}`
      )
    } else {
      showFailToast('上传失败')
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

/**
 * 删除指定巡检项的照片
 * @param system 巡检项
 * @param photoIndex 照片索引
 */
const handleRemovePhotoForItem = async (system: InspectionSystem, photoIndex: number) => {
  try {
    await showConfirmDialog({
      title: '提示',
      message: '是否要删除，新增的图片会重新打水印',
    })
    const index = inspectionSystems.value.findIndex((s) => s.id === system.id)
    if (index !== -1) {
      const item = inspectionSystems.value[index]!
      const removedPhoto = item.photos[photoIndex]
      item.photos.splice(photoIndex, 1)
      item.photos_uploaded = item.photos.length > 0
      try {
        await saveRecordToBackend(item)
      } catch (saveError) {
        item.photos.splice(photoIndex, 0, removedPhoto)
        item.photos_uploaded = item.photos.length > 0
        showFailToast('删除失败，请重试')
      }
    }
  } catch {}
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
      inspectionId: detail.value?.id,
    },
  })
}

const handleSubmit = async () => {
  if (!canSubmit.value) {
    const status = detail.value?.status
    if (status === WORK_STATUS.PENDING_CONFIRM) {
      showFailToast('工单已提交，等待审批中')
    } else if (status === WORK_STATUS.RETURNED) {
      showFailToast('工单已退回，请使用更新按钮重新提交')
    } else if (status === WORK_STATUS.COMPLETED) {
      showFailToast('工单已完成')
    } else {
      showFailToast('请完成所有必填项')
    }
    return
  }

  try {
    await showConfirmDialog({
      title: '提示',
      message: '确认提交工单吗？',
    })

    showLoadingToast({ message: '提交中...', forbidClick: true })

    const patchData = {
      execution_result: formData.value.execution_result,
      remarks: formData.value.remarks,
      signature: formData.value.signature,
      total_count: totalCount.value,
      filled_count: filledCount.value,
    }

    const patchResponse = await periodicInspectionService.patch(detail.value?.id!, patchData)

    if (patchResponse.code !== 200) {
      showFailToast('保存工单数据失败')
      return
    }

    const response = await periodicInspectionService.submit(detail.value?.id!)

    if (response.code === 200) {
      await addOperationLog('submit', '员工提交工单')
      localStorage.removeItem('periodic_inspection_signature')
      showSuccessToast('提交成功')
      router.push('/periodic-inspection')
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

    const response = await periodicInspectionService.recall(detail.value?.id!)
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

    const currentStatus = detail.value?.status
    const updateData: Record<string, any> = {
      execution_result: formData.value.execution_result,
      remarks: formData.value.remarks,
      signature: formData.value.signature,
      total_count: totalCount.value,
      filled_count: filledCount.value,
    }

    if (currentStatus === WORK_STATUS.RETURNED) {
      updateData.status = WORK_STATUS.PENDING_CONFIRM
    }

    const response = await periodicInspectionService.patch(detail.value?.id!, updateData)

    if (response.code === 200) {
      if (currentStatus === WORK_STATUS.RETURNED) {
        await addOperationLog('update', '员工更新工单并重新提交审核')
        showSuccessToast('更新成功，已重新提交审核')
      } else {
        await addOperationLog('update', '员工更新工单内容')
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

const handleResubmit = async () => {
  if (!canUpdate.value) {
    showFailToast('当前状态不允许重新提交')
    return
  }

  if (!allInspected.value) {
    showFailToast('请完成所有巡检项')
    return
  }

  if (!allPhotosUploaded.value) {
    showFailToast('请上传所有巡检项照片')
    return
  }

  if (!formData.value.signature) {
    showFailToast('请完成用户签字确认')
    return
  }

  try {
    await showConfirmDialog({
      title: '提示',
      message: '确认重新提交工单吗？提交后将进入审批流程。',
    })

    showLoadingToast({ message: '提交中...', forbidClick: true })

    const patchData = {
      execution_result: formData.value.execution_result,
      remarks: formData.value.remarks,
      signature: formData.value.signature,
      total_count: totalCount.value,
      filled_count: filledCount.value,
    }

    const patchResponse = await periodicInspectionService.patch(detail.value?.id!, patchData)

    if (patchResponse.code !== 200) {
      showFailToast('保存工单数据失败')
      return
    }

    const response = await periodicInspectionService.submit(detail.value?.id!)

    if (response.code === 200) {
      await addOperationLog('resubmit', '员工修改后重新提交工单')
      localStorage.removeItem('periodic_inspection_signature')
      showSuccessToast('重新提交成功，等待审批')
      router.push('/periodic-inspection')
    }
  } catch (error: any) {
    if (error !== 'cancel') {
      console.error('重新提交失败:', error)
      if (error.response?.data?.detail) {
        showFailToast(error.response.data.detail)
      } else {
        showFailToast('重新提交失败')
      }
    }
  } finally {
    closeToast()
  }
}

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

    const response = await periodicInspectionService.approve(detail.value?.id!, true)

    if (response.code === 200) {
      await addOperationLog('approve', '部门经理审批通过')
      showSuccessToast('审批通过')
      router.push('/periodic-inspection')
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

    const response = await periodicInspectionService.reject(detail.value?.id!, reason)

    if (response.code === 200) {
      await addOperationLog('reject', `部门经理退回工单，原因：${reason}`)
      showSuccessToast('已退回')
      router.push('/periodic-inspection')
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
        filled_count: filledCount.value,
      }

      await periodicInspectionService.patch(detail.value?.id!, saveData)
    } catch (error) {
      console.error('Auto save failed:', error)
    }
  }, 1000)
}

watch(
  () => formData.value.execution_result,
  () => {
    autoSaveFieldContent()
  }
)

watch(
  () => formData.value.remarks,
  () => {
    autoSaveFieldContent()
  }
)

let inspectionFieldSaveTimer: ReturnType<typeof setTimeout> | null = null

const autoSaveInspectionFields = (system: InspectionSystem) => {
  if (!detail.value?.id || !isEditable.value) return

  if (inspectionFieldSaveTimer) {
    clearTimeout(inspectionFieldSaveTimer)
  }

  inspectionFieldSaveTimer = setTimeout(async () => {
    try {
      await saveRecordToBackend(system)
    } catch (error) {
      console.error('Auto save inspection field failed:', error)
    }
  }, 1000)
}

const handleInspectionFieldChange = (system: InspectionSystem) => {
  autoSaveInspectionFields(system)
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
      work_order_type: 'periodic_inspection',
      work_order_id: detail.value.id,
      work_order_no: detail.value.inspection_id,
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
  isInitialized.value = true
  await fetchDetail()
  await fetchInspectionItems()
  loadSignature()
})

onActivated(async () => {
  if (!isInitialized.value) {
    isInitialized.value = true
    await fetchDetail()
    await fetchInspectionItems()
    loadSignature()
  }
})

watch(
  () => route.params.id,
  async (newId, oldId) => {
    if (newId && newId !== oldId) {
      await fetchDetail()
      await fetchInspectionItems()
      loadSignature()
    }
  }
)
</script>

<template>
  <div class="periodic-inspection-detail">
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
                :style="{ fontSize: getWorkIdFontSize(detail.inspection_id) + 'px' }"
              >
                {{ detail.inspection_id }}
              </div>
              <van-button
                size="mini"
                type="primary"
                plain
                @click.stop="copyOrderId(detail.inspection_id)"
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

      <van-cell-group inset>
        <template #title>
          <span class="required-label"><span class="required-star">*</span>巡检记录</span>
        </template>
        <div class="section-tip">巡检事项来自项目维保计划，请依次完成各项巡检</div>
        <div v-if="inspectionItemsLoading" class="loading-container">
          <van-loading size="24px">加载巡检事项...</van-loading>
        </div>
        <van-empty
          v-else-if="inspectionSystems.length === 0"
          description="暂无巡检事项，请在PC管理端配置项目维保计划"
        />
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
            <div v-if="system.check_content || system.brief_description" class="inspection-detail">
              <div v-if="system.check_content" class="detail-row">
                <span class="detail-label">检查要求:</span>
                <span class="detail-value">{{ system.check_content }}</span>
              </div>
              <div v-if="system.brief_description" class="detail-row">
                <span class="detail-label">简要说明:</span>
                <span class="detail-value">{{ system.brief_description }}</span>
              </div>
            </div>

            <div class="inspection-inline-fields">
              <van-field
                v-model="system.inspection_content"
                rows="2"
                autosize
                label="巡检内容"
                type="textarea"
                placeholder="请输入巡检内容"
                :readonly="!isEditable"
                class="inline-field"
                @update:model-value="handleInspectionFieldChange(system)"
              />
              <van-field
                v-model="system.inspection_result"
                rows="2"
                autosize
                label="巡检结果"
                type="textarea"
                placeholder="请输入巡检结果"
                :readonly="!isEditable"
                class="inline-field"
                @update:model-value="handleInspectionFieldChange(system)"
              />
            </div>

            <div class="photo-section-inline">
              <div class="photo-grid-inline">
                <div
                  v-for="(photo, photoIdx) in system.photos"
                  :key="photoIdx"
                  class="photo-item-inline"
                  @click="previewPhoto(system.photos, photoIdx)"
                >
                  <img :src="getUploadUrl(photo)" alt="现场照片" loading="lazy" />
                  <van-icon
                    v-if="isEditable"
                    name="delete"
                    class="delete-icon-inline"
                    @click.stop="handleRemovePhotoForItem(system, photoIdx)"
                  />
                </div>
                <div
                  v-if="isEditable && system.photos.length < 9"
                  class="photo-add-inline"
                  @click="handlePhotoCaptureForItem(system, true)"
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
          name="execution_result"
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
          name="remarks"
          rows="2"
          autosize
          label="处理结果"
          type="textarea"
          placeholder="请输入处理结果"
          show-word-limit
          maxlength="200"
        />
      </van-cell-group>

      <van-cell-group v-if="canSign" inset>
        <template #title>
          <span class="required-label"><span class="required-star">*</span>用户签字</span>
        </template>
        <van-cell is-link @click="handleSignature">
          <template #value>
            <img
              v-if="formData.signature"
              :src="formData.signature"
              class="signature-preview"
              loading="lazy"
            />
            <span v-else class="status-pending">待签字</span>
          </template>
        </van-cell>
      </van-cell-group>

      <OperationLogTimeline
        v-if="detail?.id"
        ref="operationLogRef"
        work-order-type="periodic_inspection"
        :work-order-id="detail.id"
      />

      <div v-if="canUpdate" class="action-buttons">
        <van-notice-bar
          v-if="detail?.status === WORK_STATUS.RETURNED"
          left-icon="warning-o"
          text="工单已退回，请修改内容后点击重新提交"
          color="#ed6a0c"
          background="#fffbe8"
          style="margin-bottom: 12px;"
        />
        <van-notice-bar
          v-else-if="detail?.status === WORK_STATUS.PENDING_CONFIRM"
          left-icon="info-o"
          text="工单待审批中，可修改内容后点击更新"
          color="#1989fa"
          background="#e8f4ff"
          style="margin-bottom: 12px;"
        />
        <van-button
          v-if="detail?.status === WORK_STATUS.RETURNED"
          type="primary"
          size="large"
          @click="handleResubmit"
        >重新提交</van-button>
        <van-button
          v-else
          type="primary"
          size="large"
          @click="handleUpdate"
        >更新</van-button>
      </div>

      <div
        v-else-if="(isWorker || userStore.isManager()) && detail?.status === WORK_STATUS.IN_PROGRESS"
        class="action-buttons"
      >
        <van-button type="primary" size="large" :disabled="!canSubmit" @click="handleSubmit"
          >提交</van-button
        >
      </div>

      <div v-if="isApproveMode && canApprove" class="action-buttons">
        <van-button type="danger" size="large" :disabled="isSubmitting" @click="handleApproveReject"
          >退回</van-button
        >
        <van-button type="success" size="large" :disabled="isSubmitting" @click="handleApprovePass"
          >通过</van-button
        >
      </div>
    </div>

    <van-empty v-else-if="!loading && errorMessage" :description="errorMessage" image="error" />
    <van-empty v-else-if="!loading" description="暂无数据" />

    <van-popup
      v-model:show="showInspectionPopup"
      position="bottom"
      round
      :style="{ height: '70%' }"
    >
      <div v-if="currentInspectionSystem" class="popup-content">
        <div class="popup-header">
          <span class="popup-title">{{ currentInspectionSystem.name }} - 巡检记录</span>
          <van-icon name="cross" @click="showInspectionPopup = false" />
        </div>
        <div class="popup-body">
          <div
            v-if="currentInspectionSystem.check_content || currentInspectionSystem.check_standard"
            class="check-reference"
          >
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
            name="inspection_content"
            rows="3"
            autosize
            label="巡检内容"
            type="textarea"
            placeholder="请输入巡检内容"
            :readonly="!isEditable"
          />
          <van-field
            v-model="currentInspectionSystem.inspection_result"
            name="inspection_result"
            rows="3"
            autosize
            label="巡检结果"
            type="textarea"
            placeholder="请输入巡检结果"
            :readonly="!isEditable"
          />
        </div>
        <div v-if="isEditable" class="popup-footer">
          <van-button type="primary" block @click="handleInspectionSave">保存</van-button>
        </div>
        <div v-else class="popup-footer">
          <van-button type="default" block @click="showInspectionPopup = false">关闭</van-button>
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
          <van-field
            v-model="rejectReason"
            name="reject_reason"
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
.periodic-inspection-detail {
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

.section-tip {
  padding: 8px 16px;
  font-size: 12px;
  color: var(--color-text-secondary);
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

.status-disabled {
  color: var(--color-text-placeholder);
}

.inspection-list {
  padding: 0 12px 12px;
}

.inspection-item-card {
  background: var(--color-bg-card);
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
  color: var(--color-text-primary);
}

.inspection-index {
  font-size: 14px;
  color: var(--color-text-primary);
  font-weight: 500;
  margin-right: 4px;
}

.inspection-detail {
  margin-top: 8px;
  padding: 8px 12px;
  background: var(--color-bg-page);
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
  color: var(--color-text-secondary);
  flex-shrink: 0;
  min-width: 60px;
}

.detail-value {
  color: var(--color-text-primary);
  flex: 1;
  word-break: break-all;
}

.inspection-inline-fields {
  margin-top: 8px;
  padding: 0 4px;
}

.inspection-inline-fields .inline-field {
  margin-bottom: 4px;
  background: var(--color-bg-page);
  border-radius: 4px;
}

.inspection-inline-fields .inline-field :deep(.van-field__label) {
  font-size: 12px;
  color: var(--color-text-secondary);
  width: 60px;
}

.inspection-inline-fields .inline-field :deep(.van-field__control) {
  font-size: 13px;
}

.inspection-subtitle {
  font-size: 12px;
  color: var(--color-text-secondary);
  margin-top: 4px;
}

.photo-section-inline {
  margin-top: 12px;
  padding-top: 12px;
  border-top: 1px solid var(--color-border-light);
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
  color: var(--color-bg-card);
  background: rgba(0, 0, 0, 0.5);
  border-radius: 50%;
  padding: 2px;
}

.photo-add-inline {
  aspect-ratio: 1;
  border: 2px dashed var(--color-border-light);
  border-radius: 8px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 4px;
  color: var(--color-text-secondary);
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

.check-reference {
  padding: 12px 16px;
  background: var(--color-bg-page);
  border-bottom: 1px solid var(--color-border-light);
}

.check-item {
  margin-bottom: 8px;
}

.check-item:last-child {
  margin-bottom: 0;
}

.check-label {
  font-size: 12px;
  color: var(--color-text-secondary);
  margin-bottom: 4px;
}

.check-value {
  font-size: 14px;
  color: var(--color-text-primary);
  line-height: 1.5;
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

.required-label {
  font-weight: 500;
}

.required-star {
  color: var(--color-danger);
  margin-right: 2px;
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
