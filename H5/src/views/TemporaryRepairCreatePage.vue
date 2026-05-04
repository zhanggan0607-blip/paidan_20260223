<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { showLoadingToast, closeToast, showSuccessToast, showFailToast } from 'vant'
import { projectInfoService, temporaryRepairService, personnelService } from '../services'
import { formatDate } from '@sstcp/shared'
import { useNavigation } from '../composables/useNavigation'
import { useUserStore } from '../stores/userStore'
const userStore = useUserStore()
import type { ProjectInfo } from '../types/api'

const router = useRouter()
const { goBack } = useNavigation()

const userReady = ref(false)

const formData = ref({
  projectId: '',
  projectIdDisplay: '',
  projectName: '',
  clientName: '',
  clientContact: '',
  clientContactInfo: '',
  planStartDate: formatDate(new Date()),
  planEndDate: formatDate(new Date()),
  remarks: '',
  maintenancePersonnel: '',
})

const projectList = ref<ProjectInfo[]>([])
const maintenancePersonnelList = ref<any[]>([])
const showProjectPicker = ref(false)
const showMaintenancePersonnelPicker = ref(false)
const showDateRangePicker = ref(false)
const selectedProjectName = ref('')
const selectedMaintenancePersonnelName = ref('')
const submitLoading = ref(false)
const generatedWorkId = ref('')

const minDate = new Date(2020, 0, 1)
const maxDate = new Date(2030, 11, 31)

const dateDisplayText = computed(() => {
  if (formData.value.planStartDate === formData.value.planEndDate) {
    return formData.value.planStartDate
  }
  return `${formData.value.planStartDate} 至 ${formData.value.planEndDate}`
})

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
 * 获取运维人员列表
 */
const fetchMaintenancePersonnelList = async () => {
  try {
    const response = await personnelService.getAll()
    if (response.code === 200) {
      maintenancePersonnelList.value = (response.data || [])
    }
  } catch (error) {
    console.error('Failed to fetch maintenance personnel list:', error)
  }
}

/**
 * 处理项目选择确认
 * 选择项目后自动填充该项目的运维人员（project_manager）
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
      formData.value.projectId = project.project_id
      formData.value.projectIdDisplay = project.project_id
      formData.value.projectName = project.project_name
      formData.value.clientName = project.client_name || ''
      formData.value.clientContact = project.client_contact || ''
      formData.value.clientContactInfo = project.client_contact_info || ''
      selectedProjectName.value = project.project_name
      if (project.project_manager) {
        formData.value.maintenancePersonnel = project.project_manager
        selectedMaintenancePersonnelName.value = project.project_manager
      } else {
        formData.value.maintenancePersonnel = ''
        selectedMaintenancePersonnelName.value = ''
      }
    }
  } else if (selectedOptions && selectedOptions.length > 0) {
    const selected = selectedOptions[0]
    if (selected) {
      const project = projectList.value.find((p) => p.id.toString() === selected.value)
      if (project) {
        formData.value.projectId = project.project_id
        formData.value.projectIdDisplay = project.project_id
        formData.value.projectName = project.project_name
        formData.value.clientName = project.client_name || ''
        formData.value.clientContact = project.client_contact || ''
        formData.value.clientContactInfo = project.client_contact_info || ''
        selectedProjectName.value = project.project_name
        if (project.project_manager) {
          formData.value.maintenancePersonnel = project.project_manager
          selectedMaintenancePersonnelName.value = project.project_manager
        } else {
          formData.value.maintenancePersonnel = ''
          selectedMaintenancePersonnelName.value = ''
        }
      }
    }
  }
  showProjectPicker.value = false
}

/**
 * 处理运维人员选择确认
 */
const handleMaintenancePersonnelConfirm = ({
  selectedOptions,
  selectedValues,
}: {
  selectedOptions: Array<{ text: string; value: string }>
  selectedValues: string[]
}) => {
  const selectedValue = selectedValues && selectedValues.length > 0 ? selectedValues[0] : null
  if (selectedValue) {
    const personnel = maintenancePersonnelList.value.find((p) => p.id.toString() === selectedValue)
    if (personnel) {
      formData.value.maintenancePersonnel = personnel.name
      selectedMaintenancePersonnelName.value = personnel.name
    }
  } else if (selectedOptions && selectedOptions.length > 0) {
    const selected = selectedOptions[0]
    if (selected) {
      const personnel = maintenancePersonnelList.value.find((p) => p.id.toString() === selected.value)
      if (personnel) {
        formData.value.maintenancePersonnel = personnel.name
        selectedMaintenancePersonnelName.value = personnel.name
      }
    }
  }
  showMaintenancePersonnelPicker.value = false
}

/**
 * 处理日期范围选择确认
 */
const handleDateRangeConfirm = (values: Date[]) => {
  if (values && values.length === 2) {
    formData.value.planStartDate = formatDate(values[0])
    formData.value.planEndDate = formatDate(values[1])
  }
  showDateRangePicker.value = false
}

/**
 * 提交临时维修单
 */
const handleSubmit = async () => {
  if (!formData.value?.projectName) {
    showFailToast('请选择项目名称')
    return
  }
  if (!formData.value?.maintenancePersonnel) {
    showFailToast('请选择运维人员')
    return
  }
  if (!formData.value?.remarks) {
    showFailToast('请输入报修内容')
    return
  }

  submitLoading.value = true
  showLoadingToast({ message: '提交中...', forbidClick: true })

  try {
    const response = await temporaryRepairService.create({
      project_id: formData.value.projectId,
      project_name: formData.value.projectName,
      plan_start_date: formData.value.planStartDate,
      plan_end_date: formData.value.planEndDate,
      client_name: formData.value.clientName,
      client_contact: formData.value.clientContact,
      client_contact_info: formData.value.clientContactInfo,
      remarks: formData.value.remarks,
      maintenance_personnel: formData.value.maintenancePersonnel,
    } as any)

    if (response.code === 200) {
      const repairId = response.data?.repair_id || '已生成'
      generatedWorkId.value = repairId
      showSuccessToast({
        message: `提交成功\n工单号：${repairId}`,
        duration: 3000,
      })
      formData.value = {
        projectId: '',
        projectIdDisplay: '',
        projectName: '',
        clientName: '',
        clientContact: '',
        clientContactInfo: '',
        planStartDate: formatDate(new Date()),
        planEndDate: formatDate(new Date()),
        remarks: '',
        maintenancePersonnel: '',
      }
      selectedProjectName.value = ''
      selectedMaintenancePersonnelName.value = ''

      router.push('/temporary-repair')
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

const handleBack = () => {
  goBack()
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

const maintenancePersonnelColumns = computed(() => {
  return maintenancePersonnelList.value.map((p) => ({
    text: p.name,
    value: p.id.toString(),
  }))
})

onMounted(() => {
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
  userReady.value = true
  fetchProjectList()
  fetchMaintenancePersonnelList()
})
</script>

<template>
  <div class="temporary-repair-create-page">
    <van-nav-bar fixed placeholder @click-left="handleBack">
      <template #left>
        <div class="nav-left">
          <van-icon name="arrow-left" />
          <span>返回</span>
        </div>
      </template>
    </van-nav-bar>

    <van-cell-group inset title="基本信息" class="form-group">
      <van-cell
        :title="selectedProjectName || '选择项目'"
        label="项目名称"
        is-link
        required
        @click="showProjectPicker = true"
      />
      <van-cell
        v-if="formData.projectIdDisplay"
        :title="formData.projectIdDisplay"
        label="项目编号"
      />
      <van-cell
        :title="selectedMaintenancePersonnelName || '选择运维人员'"
        label="运维人员"
        is-link
        required
        @click="showMaintenancePersonnelPicker = true"
      />
      <van-cell
        :title="dateDisplayText"
        label="维修周期"
        is-link
        required
        @click="showDateRangePicker = true"
      />
      <van-cell v-if="formData.clientName" title="客户单位" :value="formData.clientName" />
      <van-field name="client_contact"
        v-model="formData.clientContact"
        label="客户联系人"
        placeholder="请输入客户联系人"
      />
      <van-field name="client_contact_info"
        v-model="formData.clientContactInfo"
        label="客户联系电话"
        placeholder="请输入客户联系电话"
        type="tel"
      />
      <van-field name="remarks"
        v-model="formData.remarks"
        label="报修内容"
        placeholder="请输入报修内容"
        type="textarea"
        rows="3"
        maxlength="500"
        show-word-limit
        required
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

    <van-popup v-model:show="showProjectPicker" position="bottom" round>
      <van-picker name="选择项目"
        title="选择项目"
        :columns="projectColumns"
        @confirm="handleProjectConfirm"
        @cancel="showProjectPicker = false"
      />
    </van-popup>

    <van-popup v-model:show="showMaintenancePersonnelPicker" position="bottom" round>
      <van-picker name="选择运维人员"
        title="选择运维人员"
        :columns="maintenancePersonnelColumns"
        @confirm="handleMaintenancePersonnelConfirm"
        @cancel="showMaintenancePersonnelPicker = false"
      />
    </van-popup>

    <van-calendar
      v-model:show="showDateRangePicker"
      type="range"
      title="选择维修周期"
      :min-date="minDate"
      :max-date="maxDate"
      :poppable="true"
      :show-confirm="true"
      color="var(--color-primary)"
      @confirm="handleDateRangeConfirm"
    />
  </div>
</template>

<style scoped>
.temporary-repair-create-page {
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

.nav-left {
  display: flex;
  align-items: center;
  gap: 4px;
  color: var(--color-nav-text);
}

:deep(.van-cell-group--inset) {
  margin: 12px;
}
</style>
