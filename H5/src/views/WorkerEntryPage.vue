<script setup lang="ts">
import { ref, onMounted, onActivated } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import {
  showLoadingToast,
  closeToast,
  showSuccessToast,
  showFailToast,
  showConfirmDialog,
} from 'vant'
import { spotWorkService, ocrService, uploadService } from '../services'
import { useUserStore } from '../stores/userStore'
const userStore = useUserStore()
import {
  compressImage,
  blobToFile,
  getCurrentLocation,
  validateIdCard,
  maskIdCard,
} from '@sstcp/shared'
import { useNavigation } from '../composables'

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

const route = useRoute()
const router = useRouter()
const { goBack } = useNavigation()

const projectId = ref('')
const projectName = ref('')
const workDateStart = ref('')
const workDateEnd = ref('')
const fromPath = ref('')

const workerList = ref<WorkerInfo[]>([])
const showAddPopup = ref(false)
const loading = ref(false)
const isInitialized = ref(false)

const currentWorker = ref<WorkerInfo>({
  name: '',
  gender: '',
  birthDate: '',
  address: '',
  idCardNumber: '',
  issuingAuthority: '',
  validPeriod: '',
  idCardFront: '',
  idCardBack: '',
})

const editingIndex = ref(-1)

const showImageSourceSheet = ref(false)
const currentUploadSide = ref<'front' | 'back'>('front')

const showExistingWorkerSheet = ref(false)
const existingWorkers = ref<WorkerInfo[]>([])
const existingWorkersLoading = ref(false)

/**
 * 获取已录入的施工人员列表
 */
const fetchExistingWorkers = async () => {
  existingWorkersLoading.value = true
  try {
    const response = await spotWorkService.getAllWorkers()
    if (response.code === 200 && response.data) {
      existingWorkers.value = response.data.map((w: any) => ({
        name: w.name,
        gender: w.gender,
        birthDate: w.birthDate,
        address: w.address,
        idCardNumber: w.idCardNumber,
        issuingAuthority: w.issuingAuthority,
        validPeriod: w.validPeriod,
        idCardFront: w.idCardFront,
        idCardBack: w.idCardBack,
      }))
    }
  } catch (error) {
    console.error('Failed to fetch existing workers:', error)
  } finally {
    existingWorkersLoading.value = false
  }
}

/**
 * 打开选择已录入人员弹窗
 */
const handleSelectExistingWorker = async () => {
  showExistingWorkerSheet.value = true
  if (existingWorkers.value.length === 0) {
    await fetchExistingWorkers()
  }
}

/**
 * 选择已录入人员
 * @param worker - 选中的人员信息
 */
const handleExistingWorkerSelect = async (worker: WorkerInfo) => {
  const checkResponse = await spotWorkService.checkIdCardExists(worker.idCardNumber || '', {
    project_id: projectId.value,
    start_date: workDateStart.value,
    end_date: workDateEnd.value,
  })
  if (checkResponse.code === 200 && checkResponse.data?.exists) {
    const existingInfo = checkResponse.data

    const alreadyInList = workerList.value.some((w) => w.idCardNumber === worker.idCardNumber)

    if (alreadyInList) {
      showFailToast('该人员已在当前列表中')
      return
    }

    if (existingInfo.duplicate_in_work) {
      showFailToast(
        `该身份证已在本工单中录入！\n姓名：${existingInfo.name}\n同一工单中同一身份证只能上传一次`
      )
      return
    }

    if (!existingInfo.can_reuse) {
      showFailToast(
        `该身份证已录入未完成工单！\n姓名：${existingInfo.name}\n项目：${existingInfo.project_name}\n工单号：${existingInfo.work_id}\n状态：${existingInfo.work_status}`
      )
      return
    }
  }

  workerList.value.push({ ...worker })
  showExistingWorkerSheet.value = false
  showSuccessToast(`已添加：${worker.name}`)
}

const fetchWorkerList = async () => {
  if (!projectId.value) return

  try {
    const response = await spotWorkService.getWorkers({
      project_id: projectId.value,
      start_date: workDateStart.value,
      end_date: workDateEnd.value,
    })
    if (response.code === 200 && response.data) {
      workerList.value = response.data.map((w: any) => ({
        id: w.id,
        name: w.name,
        gender: w.gender,
        birthDate: w.birth_date,
        address: w.address,
        idCardNumber: w.id_card_number,
        issuingAuthority: w.issuing_authority,
        validPeriod: w.valid_period,
        idCardFront: w.id_card_front,
        idCardBack: w.id_card_back,
      }))
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
    idCardBack: '',
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
      message: '请确认是否要删除该施工人员？',
    })

    const worker = workerList.value[index]
    if (worker.id) {
      showLoadingToast({ message: '删除中...', forbidClick: true })
      const response = await spotWorkService.deleteWorker(worker.id)
      if (response.code !== 200) {
        showFailToast(response.message || '删除失败')
        return
      }
    }

    workerList.value.splice(index, 1)
    showSuccessToast('删除成功')
  } catch {
    closeToast()
  }
}

/**
 * 处理身份证上传 - 弹出选择框让用户选择拍照或从相册选择
 * @param side - 正面或反面
 */
const handleUploadIdCard = (side: 'front' | 'back') => {
  currentUploadSide.value = side
  showImageSourceSheet.value = true
}

const onIdCardImageError = (event: Event, field: 'idCardFront' | 'idCardBack') => {
  const img = event.target as HTMLImageElement
  img.style.display = 'none'
  const parent = img.parentElement
  if (parent) {
    const placeholder = document.createElement('div')
    placeholder.className = 'id-card-placeholder'
    placeholder.innerHTML = '<span style="color:#999;font-size:12px;">图片加载失败</span>'
    parent.appendChild(placeholder)
  }
}

/**
 * 选择图片来源后的处理
 * @param useCamera - 是否使用相机拍照
 */
const handleSelectImageSource = (useCamera: boolean) => {
  showImageSourceSheet.value = false
  selectImage(currentUploadSide.value, useCamera)
}

/**
 * 选择图片（拍照或从相册）
 * @param side - 正面或反面
 * @param useCamera - 是否使用相机拍照
 */
const selectImage = async (side: 'front' | 'back', useCamera: boolean) => {
  const ua = navigator.userAgent.toLowerCase()
  const isIOS =
    /iphone|ipad|ipod/.test(ua) ||
    (navigator.platform === 'MacIntel' && navigator.maxTouchPoints > 1)
  const isDingTalk = /dingtalk|ddwebview|dd/.test(ua)
  const isMobile = /mobile|android|iphone|ipad|ipod|blackberry|iemobile|opera mini/i.test(ua)
  const useNativeCapture =
    useCamera && !isIOS && !isDingTalk && !isMobile && navigator.maxTouchPoints <= 1

  const input = document.createElement('input')
  input.type = 'file'
  input.accept = isIOS ? 'image/jpeg,image/png' : 'image/*'

  if (useNativeCapture) {
    input.capture = 'environment'
  }

  input.onchange = async (e: Event) => {
    const target = e.target as HTMLInputElement
    const file = target.files?.[0]
    if (!file) return

    showLoadingToast({ message: '正在压缩图片...', forbidClick: true })

    try {
      let compressedFile: File | null = null
      let compressedBase64: string
      try {
        const compressedBlob = await compressImage(file, 200)
        compressedFile = blobToFile(compressedBlob, file.name)
        compressedBase64 = await fileToBase64(compressedFile)
      } catch {
        compressedBase64 = await fileToBase64(file)
      }

      const localPreview = `data:image/jpeg;base64,${compressedBase64}`
      if (side === 'front') {
        currentWorker.value.idCardFront = localPreview
      } else {
        currentWorker.value.idCardBack = localPreview
      }

      let ocrFailed = false

      const ocrPromise = (async () => {
        try {
          showLoadingToast({ message: '正在识别身份证...', forbidClick: true })
          const ocrResponse = await ocrService.recognizeIDCard({
            imageBase64: compressedBase64,
            side: side === 'front' ? 'face' : 'back',
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
                  spotWorkService
                    .checkIdCardExists(ocrData.idCardNumber, {
                      project_id: projectId.value,
                      start_date: workDateStart.value,
                      end_date: workDateEnd.value,
                    })
                    .then((checkResponse) => {
                      if (checkResponse.code === 200 && checkResponse.data?.exists) {
                        const existingInfo = checkResponse.data
                        if (existingInfo.duplicate_in_work) {
                          idCardError.value = '该身份证号码已在本工单中录入，不能重复上传'
                          showFailToast(
                            `该身份证已在本工单中录入！\n姓名：${existingInfo.name}\n同一工单中同一身份证只能上传一次`
                          )
                        } else if (!existingInfo.can_reuse) {
                          idCardError.value = '该身份证号码已存在，不能重复录入'
                          showFailToast(
                            `该身份证已录入未完成工单！\n姓名：${existingInfo.name}\n项目：${existingInfo.project_name}\n工单号：${existingInfo.work_id}\n状态：${existingInfo.work_status}`
                          )
                        } else {
                          showSuccessToast(
                            `该身份证已完成工单，可继续录入\n姓名：${existingInfo.name}\n原工单：${existingInfo.work_id}`
                          )
                        }
                      }
                    })
                    .catch((checkError: any) => {
                      console.error('检查身份证失败:', checkError)
                    })
                }
              }
            } else {
              if (ocrData.issuingAuthority)
                currentWorker.value.issuingAuthority = ocrData.issuingAuthority
              if (ocrData.validPeriod) currentWorker.value.validPeriod = ocrData.validPeriod
            }

            if (side === 'front' && !ocrData.name && !ocrData.idCardNumber) {
              showFailToast('身份证识别失败，请确保图片清晰')
              ocrFailed = true
            } else if (side === 'back' && !ocrData.issuingAuthority && !ocrData.validPeriod) {
              showFailToast('身份证反面识别失败，请确保图片清晰')
              ocrFailed = true
            }
          } else if (ocrResponse.code !== 200) {
            showFailToast(ocrResponse.message || 'OCR识别失败')
            ocrFailed = true
          }
        } catch (ocrError) {
          console.error('OCR识别失败:', ocrError)
          showFailToast('OCR识别失败，请手动填写信息')
          ocrFailed = true
        }
      })()

      const uploadFile = compressedFile || file
      const uploadPromise = (async () => {
        try {
          const response = await uploadService.uploadFile(uploadFile)
          if (response.code === 200 && response.data) {
            const imageUrl = response.data.url
            if (side === 'front') {
              currentWorker.value.idCardFront = imageUrl
            } else {
              currentWorker.value.idCardBack = imageUrl
            }
          } else {
            console.error('图片上传失败:', response.message)
          }
        } catch (uploadError) {
          console.error('图片上传失败:', uploadError)
        }
      })()

      await ocrPromise
      if (!ocrFailed) {
        closeToast()
      }
      uploadPromise.catch(() => {})
    } catch (error: any) {
      console.error('Failed to upload:', error)
      if (side === 'front') {
        currentWorker.value.idCardFront = ''
      } else {
        currentWorker.value.idCardBack = ''
      }
      const errorMsg = error?.message || error?.data?.message || '上传失败，请重试'
      showFailToast(errorMsg)
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
    idCardError.value =
      idCard.length < 18
        ? `已输入${idCard.length}位，还需${18 - idCard.length}位`
        : '身份证号码超出18位'
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

  const duplicateInList = workerList.value.some(
    (w, idx) => w.idCardNumber === currentWorker.value.idCardNumber && idx !== editingIndex.value
  )
  if (duplicateInList) {
    showFailToast('该身份证号码已在当前列表中，同一工单中同一身份证只能上传一次')
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

/**
 * 提交表单
 */
const handleSubmit = async () => {
  if (workerList.value.length === 0) {
    showFailToast('请至少添加一名施工人员')
    return
  }

  for (let i = 0; i < workerList.value.length; i++) {
    const worker = workerList.value[i]
    if (!worker.name || !worker.idCardNumber || !worker.idCardFront || !worker.idCardBack) {
      showFailToast(`第${i + 1}个施工人员信息不完整，请检查`)
      return
    }
  }

  loading.value = true
  showLoadingToast({ message: '提交中...', forbidClick: true })

  try {
    const workersData = workerList.value.map((worker) => {
      const data: any = {
        name: worker.name,
        idCardNumber: worker.idCardNumber,
        idCardFront: worker.idCardFront,
        idCardBack: worker.idCardBack,
      }
      if (worker.gender) data.gender = worker.gender
      if (worker.birthDate) data.birthDate = worker.birthDate
      if (worker.address) data.address = worker.address
      if (worker.issuingAuthority) data.issuingAuthority = worker.issuingAuthority
      if (worker.validPeriod) data.validPeriod = worker.validPeriod
      return data
    })

    const response = await spotWorkService.saveWorkers({
      project_id: projectId.value,
      project_name: projectName.value,
      start_date: workDateStart.value,
      end_date: workDateEnd.value,
      workers: workersData,
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
      showSuccessToast(
        `提交成功，共${personCount}人，${workDays}工天（${personCount}人×${dayCount}天）`
      )
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

/**
 * 处理返回操作
 */
const handleBack = () => {
  if (fromPath.value) {
    router.push(fromPath.value)
  } else {
    goBack()
  }
}

onMounted(() => {
  if (isInitialized.value) return
  isInitialized.value = true
  projectId.value = (route.query.projectId as string) || ''
  projectName.value = (route.query.projectName as string) || ''
  workDateStart.value = (route.query.workDateStart as string) || ''
  workDateEnd.value = (route.query.workDateEnd as string) || ''
  fromPath.value = (route.query.from as string) || ''

  if (projectId.value) {
    fetchWorkerList()
  }
})

onActivated(() => {
  if (!isInitialized.value) {
    isInitialized.value = true
    projectId.value = (route.query.projectId as string) || ''
    projectName.value = (route.query.projectName as string) || ''
    workDateStart.value = (route.query.workDateStart as string) || ''
    workDateEnd.value = (route.query.workDateEnd as string) || ''
    fromPath.value = (route.query.from as string) || ''

    if (projectId.value) {
      fetchWorkerList()
    }
  }
})
</script>

<template>
  <div class="worker-entry-page">
    <van-nav-bar fixed placeholder @click-left="handleBack()">
      <template #left>
        <div class="nav-left">
          <van-icon name="arrow-left" />
          <span>返回</span>
        </div>
      </template>
    </van-nav-bar>

    <div v-if="projectName" class="page-info">
      <van-cell-group inset>
        <van-cell title="项目名称" :value="projectName" />
        <van-cell
          title="用工周期"
          :value="
            workDateStart === workDateEnd ? workDateStart : `${workDateStart} 至 ${workDateEnd}`
          "
        />
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
              <div class="worker-id">{{ maskIdCard(worker.idCardNumber) }}</div>
            </div>
          </template>
          <template #value>
            <div class="worker-photos">
              <img
                v-if="worker.idCardFront"
                :src="worker.idCardFront"
                class="photo-thumb"
                @error="
                  (e: Event) => {
                    ;(e.target as HTMLImageElement).style.display = 'none'
                  }
                "
              />
              <van-icon v-else name="idcard" class="photo-icon pending" />
              <img
                v-if="worker.idCardBack"
                :src="worker.idCardBack"
                class="photo-thumb"
                @error="
                  (e: Event) => {
                    ;(e.target as HTMLImageElement).style.display = 'none'
                  }
                "
              />
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
        <van-button
          type="default"
          block
          icon="friends-o"
          class="select-existing-btn"
          @click="handleSelectExistingWorker"
        >
          从已录入人员选择
        </van-button>
      </div>
    </van-cell-group>

    <div v-if="workerList.length > 0" class="submit-btn">
      <van-button type="primary" block :loading="loading" @click="handleSubmit">
        提交（{{ workerList.length }}人）
      </van-button>
    </div>

    <van-popup v-model:show="showAddPopup" position="bottom" round :style="{ height: '90%' }">
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
                  <img
                    v-if="currentWorker.idCardFront"
                    :src="currentWorker.idCardFront"
                    alt="正面"
                    loading="lazy"
                    @error="onIdCardImageError($event, 'idCardFront')"
                  />
                  <div v-else class="id-card-placeholder">
                    <van-icon name="photograph" size="24" />
                    <span>点击上传</span>
                  </div>
                </div>
              </template>
            </van-cell>
            <van-cell title="身份证反面" is-link @click="handleUploadIdCard('back')">
              <template #value>
                <div class="id-card-preview">
                  <img
                    v-if="currentWorker.idCardBack"
                    :src="currentWorker.idCardBack"
                    alt="反面"
                    loading="lazy"
                    @error="onIdCardImageError($event, 'idCardBack')"
                  />
                  <div v-else class="id-card-placeholder">
                    <van-icon name="photograph" size="24" />
                    <span>点击上传</span>
                  </div>
                </div>
              </template>
            </van-cell>
          </van-cell-group>

          <van-cell-group inset title="身份信息">
            <van-field
              v-model="currentWorker.name"
              name="name"
              label="姓名"
              placeholder="请输入姓名"
              required
            />
            <van-field
              v-model="currentWorker.idCardNumber"
              name="id_card_number"
              label="身份证号"
              placeholder="请输入18位身份证号码"
              required
              maxlength="18"
              :error-message="idCardError"
              @input="handleIdCardChange"
            />
            <van-field
              v-model="currentWorker.gender"
              name="gender"
              label="性别"
              placeholder="输入身份证后自动填充"
              readonly
              required
            />
            <van-field
              v-model="currentWorker.birthDate"
              name="birth_date"
              label="出生日期"
              placeholder="输入身份证后自动填充"
              readonly
              required
            />
            <van-field
              v-model="currentWorker.address"
              name="address"
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
              name="issuing_authority"
              label="签发机关"
              placeholder="请输入签发机关"
              required
            />
            <van-field
              v-model="currentWorker.validPeriod"
              name="valid_period"
              label="有效期限"
              placeholder="请输入有效期限"
              required
            />
          </van-cell-group>
        </div>
        <div class="popup-footer">
          <van-button type="primary" block @click="handleSaveWorker"> 保存 </van-button>
        </div>
      </div>
    </van-popup>

    <van-action-sheet
      v-model:show="showImageSourceSheet"
      :actions="[{ name: '拍照' }, { name: '从相册选择' }]"
      cancel-text="取消"
      close-on-click-action
      @select="(_action, index) => handleSelectImageSource(index === 0)"
    />

    <van-popup
      v-model:show="showExistingWorkerSheet"
      position="bottom"
      round
      :style="{ height: '60%' }"
    >
      <div class="existing-worker-popup">
        <div class="popup-header">
          <span class="popup-title">选择已录入人员</span>
          <van-icon name="cross" @click="showExistingWorkerSheet = false" />
        </div>
        <div class="popup-body">
          <van-loading v-if="existingWorkersLoading" class="loading-center" />
          <van-empty v-else-if="existingWorkers.length === 0" description="暂无已录入人员" />
          <van-cell-group v-else inset>
            <van-cell
              v-for="(worker, index) in existingWorkers"
              :key="worker.idCardNumber || index"
              is-link
              @click="handleExistingWorkerSelect(worker)"
            >
              <template #title>
                <div class="worker-item">
                  <div class="worker-name">{{ worker.name }}</div>
                  <div class="worker-id">{{ maskIdCard(worker.idCardNumber) }}</div>
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
          </van-cell-group>
        </div>
      </div>
    </van-popup>
  </div>
</template>

<style scoped>
.worker-entry-page {
  min-height: 100vh;
  background-color: var(--color-bg-page);
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
  color: var(--color-primary);
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
  color: var(--color-text-secondary);
}

.worker-photos {
  display: flex;
  gap: 8px;
}

.photo-icon {
  font-size: 20px;
}

.photo-icon.done {
  color: var(--color-success);
}

.photo-icon.pending {
  color: var(--color-text-placeholder);
}

.photo-thumb {
  width: 36px;
  height: 24px;
  object-fit: cover;
  border-radius: 2px;
}

.add-btn {
  padding: 16px;
}

.select-existing-btn {
  margin-top: 12px;
}

.submit-btn {
  padding: 16px;
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  background: var(--color-bg-card);
}

.nav-left {
  display: flex;
  align-items: center;
  gap: 4px;
  color: var(--color-nav-text);
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
  padding-bottom: 80px;
}

.popup-footer {
  padding: 12px;
  padding-bottom: max(12px, env(safe-area-inset-bottom));
  border-top: 1px solid var(--color-border-light);
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  background: var(--color-bg-card);
}

.id-card-preview {
  width: 80px;
  height: 50px;
  border-radius: 4px;
  overflow: hidden;
  background: var(--color-bg-page);
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
  color: var(--color-text-secondary);
  font-size: 10px;
}

.existing-worker-popup {
  height: 100%;
  display: flex;
  flex-direction: column;
}

.loading-center {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 200px;
}
</style>
