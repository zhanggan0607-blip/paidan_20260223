<script setup lang="ts">
defineOptions({ name: 'SpotWorkApplyPage' })
import { ref, onMounted, computed, onActivated, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import {
  showLoadingToast,
  closeToast,
  showSuccessToast,
  showFailToast,
  showConfirmDialog,
} from 'vant'
import { spotWorkService, projectInfoService, uploadService } from '../services'
import {
  formatDate,
  formatDateTime,
  processPhoto,
  getCurrentLocation,
  getStatusType,
  getDisplayStatus,
  getWorkIdFontSize,
} from '@sstcp/shared'
import { useUserStore } from '../stores/userStore'
const userStore = useUserStore()
import { useNavigation } from '../composables/useNavigation'
import { copyOrderId } from '../utils/clipboard'
import { getUploadUrl } from '../utils/uploadUrl'
import type { ProjectInfo } from '../types/api'

const router = useRouter()
const route = useRoute()
const { goBack } = useNavigation()

const activeTab = ref(0)
const loading = ref(false)
const workList = ref<any[]>([])
const userReady = ref(false)

const canApprove = computed(() => userStore.canApproveSpotWork())

const applyFormData = ref({
  projectId: '',
  projectIdDisplay: '',
  projectName: '',
  clientContact: '',
  clientContactInfo: '',
  workDateStart: formatDate(new Date()),
  workDateEnd: formatDate(new Date()),
  workContent: '',
  remark: '',
})

const projectList = ref<ProjectInfo[]>([])
const showProjectPicker = ref(false)
const showStartDatePicker = ref(false)
const showEndDatePicker = ref(false)
const selectedProjectName = ref('')
const submitLoading = ref(false)
const workerCount = ref(0)
const generatedWorkId = ref('')

const currentPhotos = ref<string[]>([])
const showPhotoPopup = ref(false)
const signature = ref('')

const minDate = new Date(2020, 0, 1)
const maxDate = new Date(2030, 11, 31)

const startDatePickerValue = ref([
  new Date().getFullYear().toString(),
  (new Date().getMonth() + 1).toString().padStart(2, '0'),
  new Date().getDate().toString().padStart(2, '0'),
])

const endDatePickerValue = ref([
  new Date().getFullYear().toString(),
  (new Date().getMonth() + 1).toString().padStart(2, '0'),
  new Date().getDate().toString().padStart(2, '0'),
])

const workDays = computed(() => {
  if (!applyFormData.value.workDateStart || !applyFormData.value.workDateEnd) return 0
  const start = new Date(applyFormData.value.workDateStart)
  const end = new Date(applyFormData.value.workDateEnd)
  const diffTime = Math.abs(end.getTime() - start.getTime())
  const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24)) + 1
  return diffDays
})

const baseTabs = [
  { key: '申报用工', title: '申报用工', statuses: [], color: 'var(--color-success)' },
  { key: '待确认', title: '待确认', statuses: ['待确认'], color: 'var(--color-warning)' },
  { key: '已完成', title: '已完成', statuses: ['已确认', '已完成'], color: 'var(--color-primary)' },
]

const approvalTab = {
  key: '审批',
  title: '审批',
  statuses: ['待确认'],
  color: 'var(--color-primary)',
}

const tabs = computed(() => {
  if (canApprove.value) {
    return [approvalTab, ...baseTabs]
  }
  return baseTabs
})

const currentTab = computed(() => tabs.value[activeTab.value])
const currentTabColor = computed(() => tabs.value[activeTab.value]?.color || '#1989fa')

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
 * 获取工单列表
 */
const fetchWorkList = async () => {
  if (!userReady.value) return
  if (currentTab.value?.key === '申报用工') return

  loading.value = true
  showLoadingToast({ message: '加载中...', forbidClick: true })
  try {
    const response = await spotWorkService.getList({
      page: 0,
      size: 100,
    })
    if (response.code === 200) {
      const allItems = (response.data as any)?.items || []
      const filteredItems = allItems.filter((item: any) =>
        currentTab.value?.statuses.includes(item.status)
      )
      workList.value = filteredItems.sort((a: any, b: any) => {
        const dateA = new Date(a.created_at || 0).getTime()
        const dateB = new Date(b.created_at || 0).getTime()
        if (dateB !== dateA) return dateB - dateA
        return (b.id || 0) - (a.id || 0)
      })
    }
  } catch (error) {
    console.error('Failed to fetch work list:', error)
  } finally {
    loading.value = false
    closeToast()
  }
}

/**
 * 处理项目选择确认
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
      applyFormData.value.projectId = project.project_id
      applyFormData.value.projectIdDisplay = project.project_id
      applyFormData.value.projectName = project.project_name
      selectedProjectName.value = project.project_name
      applyFormData.value.clientContact = project.client_contact || ''
      applyFormData.value.clientContactInfo = project.client_contact_info || ''
    }
  } else if (selectedOptions && selectedOptions.length > 0) {
    const selected = selectedOptions[0]
    if (selected) {
      const project = projectList.value.find((p) => p.id.toString() === selected.value)
      if (project) {
        applyFormData.value.projectId = project.project_id
        applyFormData.value.projectIdDisplay = project.project_id
        applyFormData.value.projectName = project.project_name
        selectedProjectName.value = project.project_name
        applyFormData.value.clientContact = project.client_contact || ''
        applyFormData.value.clientContactInfo = project.client_contact_info || ''
      }
    }
  }
  showProjectPicker.value = false
}

/**
 * 处理开始日期选择确认
 */
const handleStartDateConfirm = ({ selectedValues }: { selectedValues: string[] }) => {
  if (selectedValues && selectedValues.length === 3) {
    const [year, month, day] = selectedValues
    applyFormData.value.workDateStart = `${year}-${month}-${day}`
    startDatePickerValue.value = selectedValues
  }
  showStartDatePicker.value = false
}

/**
 * 处理结束日期选择确认
 */
const handleEndDateConfirm = ({ selectedValues }: { selectedValues: string[] }) => {
  if (selectedValues && selectedValues.length === 3) {
    const [year, month, day] = selectedValues
    applyFormData.value.workDateEnd = `${year}-${month}-${day}`
    endDatePickerValue.value = selectedValues
  }
  showEndDatePicker.value = false
}

/**
 * 跳转到施工人员录入页面
 */
const FORM_STORAGE_KEY = 'spot_work_apply_form'

const saveFormToStorage = () => {
  const data = {
    applyFormData: applyFormData.value,
    selectedProjectName: selectedProjectName.value,
    currentPhotos: currentPhotos.value,
    workerCount: workerCount.value,
    startDatePickerValue: startDatePickerValue.value,
    endDatePickerValue: endDatePickerValue.value,
  }
  sessionStorage.setItem(FORM_STORAGE_KEY, JSON.stringify(data))
}

const restoreFormFromStorage = () => {
  const saved = sessionStorage.getItem(FORM_STORAGE_KEY)
  if (saved) {
    try {
      const data = JSON.parse(saved)
      if (data.applyFormData) {
        applyFormData.value = { ...applyFormData.value, ...data.applyFormData }
      }
      if (data.selectedProjectName) {
        selectedProjectName.value = data.selectedProjectName
      }
      if (data.currentPhotos && data.currentPhotos.length > 0) {
        currentPhotos.value = data.currentPhotos
      }
      if (data.workerCount !== undefined) {
        workerCount.value = data.workerCount
      }
      if (data.startDatePickerValue) {
        startDatePickerValue.value = data.startDatePickerValue
      }
      if (data.endDatePickerValue) {
        endDatePickerValue.value = data.endDatePickerValue
      }
    } catch (e) {
      console.error('Failed to restore form data:', e)
    }
  }
}

const clearFormStorage = () => {
  sessionStorage.removeItem(FORM_STORAGE_KEY)
}

const handleWorkerEntry = () => {
  if (!applyFormData.value.projectId) {
    showFailToast('请先选择项目')
    return
  }
  if (!applyFormData.value.projectName) {
    showFailToast('请先选择项目')
    return
  }
  saveFormToStorage()
  router.push({
    path: '/spot-work/worker-entry',
    query: {
      projectId: applyFormData.value.projectId,
      projectName: applyFormData.value.projectName,
      workDateStart: applyFormData.value.workDateStart,
      workDateEnd: applyFormData.value.workDateEnd,
      from: route.fullPath,
    },
  })
}

/**
 * 提交申报用工表单
 */
const handleSubmit = async () => {
  if (!applyFormData.value.projectName) {
    showFailToast('请选择项目名称')
    return
  }
  if (!applyFormData.value.workContent) {
    showFailToast('请输入工作内容')
    return
  }
  if (workerCount.value <= 0) {
    showFailToast('请录入施工人员')
    return
  }
  if (currentPhotos.value.length === 0) {
    showFailToast('请上传现场照片')
    return
  }
  if (!signature.value) {
    showFailToast('请完成班组签字')
    return
  }

  submitLoading.value = true
  showLoadingToast({ message: '提交中...', forbidClick: true })

  try {
    const response = await spotWorkService.quickFill({
      project_id: applyFormData.value.projectId,
      project_name: applyFormData.value.projectName,
      plan_start_date: applyFormData.value.workDateStart,
      plan_end_date: applyFormData.value.workDateEnd,
      work_content: applyFormData.value.workContent,
      remark: applyFormData.value.remark,
      worker_count: workerCount.value,
      client_contact: applyFormData.value.clientContact,
      client_contact_info: applyFormData.value.clientContactInfo,
      photos: currentPhotos.value,
      signature: signature.value,
    })
    if (response.code === 200) {
      generatedWorkId.value = response.data?.work_id || ''
      showSuccessToast({
        message: `提交成功\n工单号：${generatedWorkId.value}`,
        duration: 3000,
      })
      applyFormData.value = {
        projectId: '',
        projectIdDisplay: '',
        projectName: '',
        clientContact: '',
        clientContactInfo: '',
        workDateStart: formatDate(new Date()),
        workDateEnd: formatDate(new Date()),
        workContent: '',
        remark: '',
      }
      selectedProjectName.value = ''
      workerCount.value = 0
      currentPhotos.value = []
      signature.value = ''
      localStorage.removeItem('spot_work_apply_signature')
      clearFormStorage()

      goBack()
    } else {
      showFailToast(response.message || '提交失败')
    }
  } catch (error) {
    console.error('Failed to submit:', error)
    showFailToast('提交失败，请重试')
  } finally {
    submitLoading.value = false
    closeToast()
  }
}

const handleView = (item: any) => {
  router.push(`/spot-work/${item.id}?tab=${activeTab.value}`)
}

const handleBack = () => {
  goBack()
}

/**
 * 处理审批操作
 */
const handleApprove = (item: any) => {
  router.push(`/spot-work/${item.id}?tab=${activeTab.value}&mode=approve`)
}

const projectColumns = computed(() => {
  return projectList.value.map((p) => ({
    text: p.project_name,
    value: p.id.toString(),
    project_id: p.project_id,
    client_name: p.client_name,
    client_contact: p.client_contact,
    client_contact_info: p.client_contact_info,
  }))
})

/**
 * 获取施工人员数量
 */
const fetchWorkerCount = async () => {
  if (!applyFormData.value.projectId) {
    workerCount.value = 0
    return
  }

  try {
    const response = await spotWorkService.getWorkersByProject(
      applyFormData.value.projectId,
      applyFormData.value.workDateStart,
      applyFormData.value.workDateEnd
    )
    if (response.code === 200) {
      workerCount.value = response.data?.length || 0
    }
  } catch (error) {
    console.error('Failed to fetch worker count:', error)
  }
}

/**
 * 处理现场图片上传弹窗
 */
const handlePhotoUpload = () => {
  showPhotoPopup.value = true
}

/**
 * 拍照上传
 */
const handlePhotoCapture = () => {
  const ua = navigator.userAgent.toLowerCase()
  const isIOS =
    /iphone|ipad|ipod/.test(ua) ||
    (/mac/i.test(navigator.userAgent) && navigator.maxTouchPoints > 1)
  const isDingTalk = /dingtalk|ddwebview|dd/.test(ua)
  const isMobile = /mobile|android|iphone|ipad|ipod|blackberry|iemobile|opera mini/i.test(ua)
  const useBase64Upload = isIOS || isDingTalk || isMobile || navigator.maxTouchPoints > 1

  const input = document.createElement('input')
  input.type = 'file'
  input.accept = isIOS ? 'image/jpeg,image/png' : 'image/*'
  input.multiple = true

  if (useBase64Upload) {
    input.style.position = 'fixed'
    input.style.top = '0'
    input.style.left = '0'
    input.style.width = '100%'
    input.style.height = '100%'
    input.style.opacity = '0'
    input.style.zIndex = '999999'
  } else {
    input.capture = 'environment'
  }

  input.onchange = async (e: Event) => {
    const target = e.target as HTMLInputElement
    const allFiles = target.files
    if (!allFiles || allFiles.length === 0) {
      if (document.body.contains(input)) document.body.removeChild(input)
      return
    }

    if (document.body.contains(input)) document.body.removeChild(input)

    const remaining = 9 - currentPhotos.value.length
    if (remaining <= 0) {
      showFailToast('已达到最大上传数量')
      return
    }
    const files = Array.from(allFiles).slice(0, remaining)

    showLoadingToast({ message: `处理中(0/${files.length})...`, forbidClick: true })

    if (useBase64Upload) {
      let uploadedCount = 0
      let failedCount = 0

      for (const file of files) {
        try {
          showLoadingToast({
            message: `处理中(${uploadedCount + failedCount + 1}/${files.length})...`,
            forbidClick: true,
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
            message: `上传中(${uploadedCount + failedCount + 1}/${files.length})...`,
            forbidClick: true,
          })
          const reader = new FileReader()
          const base64Data = await new Promise<string>((resolve, reject) => {
            reader.onload = (ev) => resolve(ev.target?.result as string)
            reader.onerror = reject
            reader.readAsDataURL(watermarkedFile)
          })

          const response = await uploadService.uploadImageBase64(base64Data, watermarkedFile.name)

          if (response.code === 200 && response.data) {
            currentPhotos.value.push(response.data.url)
            uploadedCount++
          } else {
            failedCount++
          }
        } catch (error) {
          console.error('Failed to upload photo:', error)
          failedCount++
        }
      }

      closeToast()
      if (uploadedCount > 0) {
        showSuccessToast(
          `成功上传${uploadedCount}张图片${failedCount > 0 ? `，${failedCount}张失败` : ''}`
        )
      } else {
        showFailToast('上传失败')
      }
    } else {
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
  }

  if (useBase64Upload) {
    document.body.appendChild(input)
  }
  input.click()
}

/**
 * 压缩图片到指定大小（KB）
 * @param file 原文件
 * @param maxSizeKB 最大大小（KB）
 * @returns 压缩后的Blob
 */
const handleRemovePhoto = async (index: number) => {
  try {
    await showConfirmDialog({
      title: '提示',
      message: '是否要删除，新增的图片会重新打水印',
    })
    currentPhotos.value.splice(index, 1)
  } catch {}
}

/**
 * 保存图片
 */
const handlePhotoSave = () => {
  if (currentPhotos.value.length === 0) {
    showFailToast('请至少上传一张现场照片')
    return
  }
  showPhotoPopup.value = false
  showSuccessToast(`已保存${currentPhotos.value.length}张照片`)
}

/**
 * 跳转签字页面
 */
const handleSignature = () => {
  saveFormToStorage()
  router.push({
    path: '/signature',
    query: {
      from: route.fullPath,
      type: 'spot-work-apply',
    },
  })
}

/**
 * 加载签字
 */
const loadSignature = () => {
  const signatureData = localStorage.getItem('spot_work_apply_signature')
  if (signatureData) {
    signature.value = signatureData
  }
}

// 自动保存表单数据到 sessionStorage
watch(
  () => [
    applyFormData.value,
    selectedProjectName.value,
    currentPhotos.value,
    workerCount.value,
    startDatePickerValue.value,
    endDatePickerValue.value,
  ],
  () => {
    saveFormToStorage()
  },
  { deep: true }
)

onMounted(() => {
  userReady.value = true
  fetchProjectList()
  fetchWorkList()
  loadSignature()
  restoreFormFromStorage()
  const tabParam = route.query.tab
  if (tabParam !== undefined && tabParam !== null) {
    const tabIndex = parseInt(tabParam as string, 10)
    if (!isNaN(tabIndex) && tabIndex >= 0 && tabIndex < tabs.value.length) {
      activeTab.value = tabIndex
    }
  }
})

onActivated(() => {
  restoreFormFromStorage()
  fetchWorkerCount()
  loadSignature()
})
</script>

<template>
  <div class="spot-work-apply-page">
    <van-nav-bar fixed placeholder @click-left="handleBack">
      <template #left>
        <div class="nav-left">
          <van-icon name="arrow-left" />
          <span>返回</span>
        </div>
      </template>
    </van-nav-bar>

    <van-tabs v-model:active="activeTab" sticky :color="currentTabColor" @change="fetchWorkList">
      <van-tab v-for="tab in tabs" :key="tab.key" :title="tab.title">
        <template v-if="tab.key === '申报用工'">
          <van-cell-group inset title="基本信息" class="form-group">
            <van-cell
              :title="selectedProjectName || '选择项目'"
              label="项目名称"
              is-link
              required
              @click="showProjectPicker = true"
            />
            <van-cell
              v-if="applyFormData.projectIdDisplay"
              :title="applyFormData.projectIdDisplay"
              label="项目编号"
            />
            <van-cell
              :title="applyFormData.workDateStart"
              label="计划开始日期"
              is-link
              required
              @click="showStartDatePicker = true"
            />
            <van-cell
              :title="applyFormData.workDateEnd"
              label="计划结束日期"
              is-link
              required
              @click="showEndDatePicker = true"
            />
            <van-cell v-if="workDays > 0" title="用工天数" :value="workDays + ' 工天'" />
            <van-field
              v-model="applyFormData.clientContact"
              name="client_contact"
              label="客户联系人"
              placeholder="请输入客户联系人"
            />
            <van-field
              v-model="applyFormData.clientContactInfo"
              name="client_contact_info"
              label="客户联系电话"
              placeholder="请输入客户联系电话"
              type="tel"
            />
            <van-field
              v-model="applyFormData.workContent"
              name="work_content"
              label="工作内容"
              placeholder="请输入工作内容"
              type="textarea"
              rows="3"
              maxlength="800"
              show-word-limit
              required
            />
            <van-cell is-link required @click="handleWorkerEntry">
              <template #title>
                <van-button type="primary" size="small">施工人员录入</van-button>
              </template>
            </van-cell>
            <van-cell v-if="workerCount > 0" title="施工人数" :value="workerCount + ' 人'" />
            <van-cell is-link required @click="handlePhotoUpload">
              <template #title>
                <span>现场图片</span>
              </template>
              <template #value>
                <span :class="currentPhotos.length > 0 ? 'status-done' : 'status-action'">
                  {{ currentPhotos.length > 0 ? `已上传${currentPhotos.length}张` : '去上传' }}
                </span>
              </template>
            </van-cell>
            <van-cell is-link required @click="handleSignature">
              <template #title>
                <span>班组签字</span>
              </template>
              <template #value>
                <img v-if="signature" :src="signature" class="signature-preview" loading="lazy" />
                <span v-else class="status-pending">待签字</span>
              </template>
            </van-cell>
            <van-field
              v-model="applyFormData.remark"
              name="remark"
              label="备注"
              placeholder="请输入备注"
              type="textarea"
              rows="2"
            />
          </van-cell-group>

          <div class="submit-btn">
            <van-button type="primary" block :loading="submitLoading" @click="handleSubmit">
              提交
            </van-button>
          </div>

          <div v-if="generatedWorkId" class="work-id-result">
            <van-notice-bar
              :text="'工单已生成，单号：' + generatedWorkId"
              left-icon="info-o"
              color="var(--color-primary)"
              background="#ecf9ff"
            />
          </div>
        </template>

        <template v-else>
          <van-pull-refresh v-model="loading" @refresh="fetchWorkList">
            <van-list :loading="loading" :finished="true">
              <div class="work-list">
                <div v-for="item in workList" :key="item.id" class="work-card">
                  <div class="card-header">
                    <van-tag :type="getStatusType(item.status)" size="medium">
                      {{ getDisplayStatus(item.status) }}
                    </van-tag>
                    <div class="work-id-wrapper">
                      <span
                        class="work-id"
                        :style="{ fontSize: getWorkIdFontSize(item.work_id) + 'px' }"
                        >{{ item.work_id }}</span
                      >
                      <van-button
                        size="mini"
                        type="primary"
                        plain
                        class="copy-btn"
                        @click.stop="copyOrderId(item.work_id)"
                        >复制单号</van-button
                      >
                    </div>
                  </div>
                  <van-cell-group inset class="card-body-cells">
                    <van-cell title="项目名称" :value="item.project_name" />
                    <van-cell v-if="item.project_id" title="项目编号" :value="item.project_id" />
                    <van-cell
                      title="用工周期"
                      :value="`${formatDate(item.plan_start_date)} -- ${formatDate(item.plan_end_date)}`"
                    />
                    <van-cell
                      v-if="item.worker_count"
                      title="施工人数"
                      :value="item.worker_count + ' 人'"
                    />
                    <van-cell
                      v-if="item.work_days"
                      title="工天"
                      :value="item.work_days + ' 工天'"
                    />
                    <van-cell
                      v-if="item.client_contact"
                      title="客户联系人"
                      :value="item.client_contact"
                    />
                    <van-cell
                      v-if="item.client_contact_info"
                      title="客户联系电话"
                      :value="item.client_contact_info"
                    />
                    <van-cell
                      v-if="item.work_content"
                      title="工作内容"
                      :value="item.work_content"
                    />
                    <van-cell v-if="item.remarks" title="备注" :value="item.remarks" />
                    <van-cell
                      v-if="currentTab?.key === '待确认' || currentTab?.key === '审批'"
                      title="提交时间"
                      :value="formatDateTime(item.updated_at)"
                    />
                  </van-cell-group>
                  <div class="card-footer">
                    <van-button
                      v-if="currentTab?.key === '审批'"
                      type="success"
                      size="small"
                      @click="handleApprove(item)"
                    >
                      审批
                    </van-button>
                    <van-button type="primary" size="small" @click="handleView(item)">
                      查看
                    </van-button>
                  </div>
                </div>
              </div>
              <van-empty v-if="!loading && workList.length === 0" description="暂无数据" />
            </van-list>
          </van-pull-refresh>
        </template>
      </van-tab>
    </van-tabs>

    <van-popup v-model:show="showProjectPicker" position="bottom" round>
      <van-picker
        name="选择项目"
        title="选择项目"
        :columns="projectColumns"
        @confirm="handleProjectConfirm"
        @cancel="showProjectPicker = false"
      />
    </van-popup>

    <van-popup v-model:show="showStartDatePicker" position="bottom" round>
      <van-date-picker
        v-model="startDatePickerValue"
        title="选择开始日期"
        :min-date="minDate"
        :max-date="maxDate"
        @confirm="handleStartDateConfirm"
        @cancel="showStartDatePicker = false"
      />
    </van-popup>

    <van-popup v-model:show="showEndDatePicker" position="bottom" round>
      <van-date-picker
        v-model="endDatePickerValue"
        title="选择结束日期"
        :min-date="minDate"
        :max-date="maxDate"
        @confirm="handleEndDateConfirm"
        @cancel="showEndDatePicker = false"
      />
    </van-popup>

    <van-popup v-model:show="showPhotoPopup" position="bottom" round :style="{ height: '60%' }">
      <div class="popup-content">
        <div class="popup-header">
          <span class="popup-title">现场图片</span>
          <van-icon name="cross" @click="showPhotoPopup = false" />
        </div>
        <div class="popup-body">
          <div class="photo-section">
            <div class="photo-grid">
              <div v-for="(photo, index) in currentPhotos" :key="index" class="photo-item">
                <img :src="getUploadUrl(photo)" alt="现场照片" loading="lazy" />
                <van-icon
                  name="delete"
                  class="delete-icon"
                  @click.stop="handleRemovePhoto(index)"
                />
              </div>
              <div v-if="currentPhotos.length < 9" class="photo-add" @click="handlePhotoCapture">
                <van-icon name="photograph" size="24" />
                <span>拍照</span>
              </div>
            </div>
            <div class="photo-tip">支持拍照或从相册选择，最多上传9张，可多选</div>
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
.spot-work-apply-page {
  min-height: 100vh;
  background-color: var(--color-bg-page);
}

.form-group {
  margin: 12px;
}

.submit-btn {
  padding: 16px;
  margin-top: 16px;
}

.work-id-result {
  padding: 0 16px 16px;
}

.work-list {
  padding: 12px;
}

.work-card {
  background: var(--color-bg-card);
  border-radius: 8px;
  margin-bottom: 12px;
  overflow: hidden;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.08);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 16px;
  background: var(--color-bg-page);
  border-bottom: 1px solid var(--color-border-light);
  flex-wrap: nowrap;
}

.work-id-wrapper {
  display: flex;
  align-items: center;
  gap: 4px;
  flex: 1;
  min-width: 0;
  justify-content: flex-end;
  flex-wrap: nowrap;
}

.work-id {
  font-weight: 600;
  color: var(--color-text-primary);
  white-space: nowrap;
  text-align: right;
  flex: 1;
  min-width: 0;
}

.copy-btn {
  flex-shrink: 0;
  height: 24px;
  padding: 0 8px;
  font-size: 12px;
  white-space: nowrap;
  transform: scale(0.8);
  transform-origin: right center;
  margin-left: -4px;
}

.card-body-cells {
  margin: 0;
}

.card-body-cells :deep(.van-cell) {
  padding: 8px 12px;
}

.card-body-cells :deep(.van-cell__title) {
  flex: none;
  width: 70px;
  color: var(--color-text-secondary);
}

.card-body-cells :deep(.van-cell__value) {
  flex: 1;
  color: var(--color-text-primary);
}

.card-footer {
  display: flex;
  justify-content: flex-end;
  gap: 8px;
  padding: 12px 16px;
  border-top: 1px solid var(--color-border-light);
}

.card-footer .van-button {
  min-width: 60px;
}

.nav-left {
  display: flex;
  align-items: center;
  gap: 4px;
  color: var(--color-nav-text);
}

:deep(.van-tabs__nav) {
  padding-left: 0;
  padding-right: 0;
}

:deep(.van-tab) {
  flex: 1;
}

:deep(.van-pull-refresh) {
  min-height: calc(100vh - 46px - 44px);
}

:deep(.van-tabs__line) {
  transition: background-color 0.3s;
}

:deep(.van-cell-group--inset) {
  margin: 12px;
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

.signature-preview {
  width: 80px;
  height: 40px;
  object-fit: contain;
  background-color: var(--color-bg-card);
  border: 1px solid var(--color-border);
  border-radius: 4px;
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

.photo-tip {
  margin-top: 8px;
  font-size: 12px;
  color: var(--color-text-secondary);
}
</style>
