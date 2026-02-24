<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { showLoadingToast, closeToast, showSuccessToast, showFailToast } from 'vant'
import api from '../utils/api'
import type { ApiResponse } from '../types'
import { formatDate } from '../config/constants'
import UserSelector from '../components/UserSelector.vue'
import { useNavigation } from '../composables/useNavigation'

interface ProjectInfo {
  id: number
  project_id: string
  project_name: string
  client_name: string
}

const router = useRouter()
const { goBack } = useNavigation()

const formData = ref({
  projectId: '',
  projectName: '',
  workDateStart: formatDate(new Date()),
  workDateEnd: formatDate(new Date()),
  workContent: '',
  remark: ''
})

const projectList = ref<ProjectInfo[]>([])
const showProjectPicker = ref(false)
const showDateRangePicker = ref(false)
const loading = ref(false)

const selectedProjectName = ref('')

const minDate = new Date(2020, 0, 1)
const maxDate = new Date(2030, 11, 31)

const dateDisplayText = computed(() => {
  if (formData.value.workDateStart === formData.value.workDateEnd) {
    return formData.value.workDateStart
  }
  return `${formData.value.workDateStart} 至 ${formData.value.workDateEnd}`
})

const fetchProjectList = async () => {
  try {
    const response = await api.get<unknown, ApiResponse<ProjectInfo[]>>('/project-info/all/list')
    if (response.code === 200) {
      projectList.value = response.data || []
    }
  } catch (error) {
    console.error('Failed to fetch project list:', error)
  }
}

const handleProjectConfirm = ({ selectedOptions, selectedValues }: { selectedOptions: Array<{ text: string; value: string }>, selectedValues: string[] }) => {
  const selectedValue = selectedValues && selectedValues.length > 0 ? selectedValues[0] : null
  if (selectedValue) {
    const project = projectList.value.find(p => p.id.toString() === selectedValue)
    if (project) {
      formData.value.projectId = project.project_id
      formData.value.projectName = project.project_name
      selectedProjectName.value = project.project_name
    }
  } else if (selectedOptions && selectedOptions.length > 0) {
    const selected = selectedOptions[0]
    if (selected) {
      const project = projectList.value.find(p => p.id.toString() === selected.value)
      if (project) {
        formData.value.projectId = project.project_id
        formData.value.projectName = project.project_name
        selectedProjectName.value = project.project_name
      }
    }
  }
  showProjectPicker.value = false
}

const handleDateRangeConfirm = (values: Date[]) => {
  if (values && values.length === 2) {
    formData.value.workDateStart = formatDate(values[0])
    formData.value.workDateEnd = formatDate(values[1])
  }
  showDateRangePicker.value = false
}

const handleWorkerEntry = () => {
  router.push({
    path: '/spot-work/worker-entry',
    query: {
      projectId: formData.value.projectId,
      projectName: formData.value.projectName,
      workDateStart: formData.value.workDateStart,
      workDateEnd: formData.value.workDateEnd
    }
  })
}

const handleSubmit = async () => {
  if (!formData.value.projectName) {
    showFailToast('请选择项目名称')
    return
  }
  if (!formData.value.workContent) {
    showFailToast('请输入工作内容')
    return
  }
  
  loading.value = true
  showLoadingToast({ message: '提交中...', forbidClick: true })
  
  try {
    const response = await api.post<unknown, ApiResponse<null>>('/spot-work/quick-fill', {
      project_id: formData.value.projectId,
      project_name: formData.value.projectName,
      plan_start_date: formData.value.workDateStart,
      plan_end_date: formData.value.workDateEnd,
      work_content: formData.value.workContent,
      remark: formData.value.remark
    })
    if (response.code === 200) {
      showSuccessToast('提交成功')
      goBack('/')
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

const handleBack = () => {
  goBack('/')
}

const projectColumns = computed(() => {
  return projectList.value.map(p => ({
    text: p.project_name,
    value: p.id.toString(),
    project_id: p.project_id,
    client_name: p.client_name
  }))
})

onMounted(() => {
  fetchProjectList()
})
</script>

<template>
  <div class="quick-fill-page">
    <van-nav-bar 
      title="申报用工" 
      fixed 
      placeholder 
    >
      <template #left>
        <div class="nav-left" @click="handleBack">
          <van-icon name="arrow-left" />
          <span>返回</span>
        </div>
      </template>
      <template #right>
        <UserSelector />
      </template>
    </van-nav-bar>
    
    <van-cell-group inset title="基本信息">
      <van-cell 
        :title="selectedProjectName || '请选择项目'"
        label="项目名称"
        is-link
        required
        @click="showProjectPicker = true"
      />
      <van-cell 
        :title="dateDisplayText"
        label="用工日期"
        is-link
        required
        @click="showDateRangePicker = true"
      />
      <van-field 
        v-model="formData.workContent" 
        label="工作内容" 
        placeholder="请输入工作内容"
        type="textarea"
        rows="3"
        maxlength="800"
        show-word-limit
        required
      />
      <van-cell 
        is-link 
        @click="handleWorkerEntry"
      >
        <template #title>
          <van-button type="primary" size="small">施工人员录入</van-button>
        </template>
      </van-cell>
      <van-field 
        v-model="formData.remark" 
        label="备注" 
        placeholder="请输入备注"
        type="textarea"
        rows="2"
      />
    </van-cell-group>

    <div class="submit-btn">
      <van-button type="primary" block :loading="loading" @click="handleSubmit">
        提交
      </van-button>
    </div>

    <van-popup v-model:show="showProjectPicker" position="bottom" round>
      <van-picker
        title="选择项目"
        :columns="projectColumns"
        @confirm="handleProjectConfirm"
        @cancel="showProjectPicker = false"
      />
    </van-popup>

    <van-calendar 
      v-model:show="showDateRangePicker" 
      type="range"
      title="选择用工日期"
      :min-date="minDate"
      :max-date="maxDate"
      :poppable="true"
      :show-confirm="true"
      @confirm="handleDateRangeConfirm"
      color="#1989fa"
    />
  </div>
</template>

<style scoped>
.quick-fill-page {
  min-height: 100vh;
  background-color: #f5f7fa;
}

:deep(.van-cell-group--inset) {
  margin: 12px;
}

.submit-btn {
  padding: 16px;
  margin-top: 16px;
}

.nav-left {
  display: flex;
  align-items: center;
  gap: 4px;
  color: #323233;
}
</style>
