<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { showToast, showConfirmDialog, showSuccessToast } from 'vant'
import api from '../utils/api'
import type { ApiResponse } from '../types'
import SearchInput from '../components/SearchInput.vue'

const router = useRouter()
const route = useRoute()

interface Customer {
  id: number
  name: string
  address: string | null
  contact_person: string
  phone: string
  contact_position: string | null
}

interface ProjectInfo {
  id?: number
  project_id: string
  project_name: string
  completion_date: string
  maintenance_end_date: string
  maintenance_period: string
  client_name: string
  address: string
  project_abbr: string
  project_manager: string
  client_contact: string
  client_contact_position: string
  client_contact_info: string
}

const loading = ref(false)
const isEdit = ref(false)
const projectId = ref<number | null>(null)

const formData = ref<ProjectInfo>({
  project_id: '',
  project_name: '',
  completion_date: '',
  maintenance_end_date: '',
  maintenance_period: '',
  client_name: '',
  address: '',
  project_abbr: '',
  project_manager: '',
  client_contact: '',
  client_contact_position: '',
  client_contact_info: ''
})

const showClientPicker = ref(false)
const showPeriodPicker = ref(false)
const showStartDatePicker = ref(false)
const showEndDatePicker = ref(false)
const customerList = ref<Customer[]>([])
const customerLoading = ref(false)
const searchKeyword = ref('')
const startDateValue = ref<string[]>(['2024', '01', '01'])
const endDateValue = ref<string[]>(['2024', '12', '31'])

const periodOptions = [
  { text: '每天', value: '每天' },
  { text: '每周', value: '每周' },
  { text: '每月', value: '每月' },
  { text: '每季度', value: '每季度' },
  { text: '每半年', value: '每半年' }
]

const filteredCustomers = computed(() => {
  if (!searchKeyword.value) {
    return customerList.value
  }
  return customerList.value.filter(c => 
    c.name.toLowerCase().includes(searchKeyword.value.toLowerCase())
  )
})

const minDate = new Date(2020, 0, 1)
const maxDate = new Date(2030, 11, 31)

const fetchCustomers = async () => {
  customerLoading.value = true
  try {
    const response = await api.get<unknown, ApiResponse<{ content: Customer[] }>>('/customer?size=100')
    if (response.code === 200 && response.data) {
      customerList.value = response.data.content || []
    }
  } catch (error) {
    console.error('Failed to fetch customers:', error)
  } finally {
    customerLoading.value = false
  }
}

const fetchProjectInfo = async (id: number) => {
  loading.value = true
  try {
    const response = await api.get<unknown, ApiResponse<ProjectInfo>>(`/project-info/${id}`)
    if (response.code === 200 && response.data) {
      const completionDate = response.data.completion_date ? response.data.completion_date.split('T')[0] ?? '' : ''
      const maintenanceEndDate = response.data.maintenance_end_date ? response.data.maintenance_end_date.split('T')[0] ?? '' : ''
      formData.value = {
        ...response.data,
        completion_date: completionDate,
        maintenance_end_date: maintenanceEndDate
      }
      if (completionDate) {
        const parts = completionDate.split('-')
        startDateValue.value = [parts[0] ?? '', parts[1] ?? '', parts[2] ?? '']
      }
      if (maintenanceEndDate) {
        const parts = maintenanceEndDate.split('-')
        endDateValue.value = [parts[0] ?? '', parts[1] ?? '', parts[2] ?? '']
      }
    }
  } catch (error) {
    console.error('Failed to fetch project info:', error)
    showToast('获取项目信息失败')
  } finally {
    loading.value = false
  }
}

const onClientSelect = (customer: Customer) => {
  formData.value.client_name = customer.name
  formData.value.address = customer.address || ''
  formData.value.client_contact = customer.contact_person
  formData.value.client_contact_info = customer.phone
  formData.value.client_contact_position = customer.contact_position || ''
  showClientPicker.value = false
  searchKeyword.value = ''
}

const onClientInput = (value: string) => {
  formData.value.client_name = value
}

const onPeriodConfirm = ({ selectedValues }: { selectedValues: string[] }) => {
  formData.value.maintenance_period = selectedValues[0] ?? ''
  showPeriodPicker.value = false
}

const onStartDateConfirm = ({ selectedValues }: { selectedValues: string[] }) => {
  const [year, month, day] = selectedValues
  formData.value.completion_date = `${year}-${month}-${day}`
  showStartDatePicker.value = false
}

const onEndDateConfirm = ({ selectedValues }: { selectedValues: string[] }) => {
  const [year, month, day] = selectedValues
  formData.value.maintenance_end_date = `${year}-${month}-${day}`
  showEndDatePicker.value = false
}

const validateForm = (): boolean => {
  if (!formData.value.project_id.trim()) {
    showToast('请输入项目编号')
    return false
  }
  if (!formData.value.project_name.trim()) {
    showToast('请输入项目名称')
    return false
  }
  if (!formData.value.completion_date) {
    showToast('请选择开始日期')
    return false
  }
  if (!formData.value.maintenance_end_date) {
    showToast('请选择结束日期')
    return false
  }
  if (!formData.value.maintenance_period) {
    showToast('请选择维保频率')
    return false
  }
  if (!formData.value.client_name.trim()) {
    showToast('请输入客户单位')
    return false
  }
  if (!formData.value.address.trim()) {
    showToast('请输入客户地址')
    return false
  }
  return true
}

const handleSubmit = async () => {
  if (!validateForm()) return

  try {
    const submitData = {
      ...formData.value,
      completion_date: formData.value.completion_date + 'T00:00:00',
      maintenance_end_date: formData.value.maintenance_end_date + 'T00:00:00'
    }

    let response
    if (isEdit.value && projectId.value) {
      response = await api.put<unknown, ApiResponse<ProjectInfo>>(`/project-info/${projectId.value}`, submitData)
    } else {
      response = await api.post<unknown, ApiResponse<ProjectInfo>>('/project-info', submitData)
    }

    if (response.code === 200) {
      showSuccessToast(isEdit.value ? '更新成功' : '创建成功')
      router.back()
    }
  } catch (error: any) {
    console.error('Failed to save project:', error)
    if (error.response?.data?.message) {
      showToast(error.response.data.message)
    } else {
      showToast('保存失败')
    }
  }
}

const handleDelete = async () => {
  if (!projectId.value) return

  try {
    await showConfirmDialog({
      title: '确认删除',
      message: '请确认是否要删除该项目？'
    })

    const response = await api.delete<unknown, ApiResponse<null>>(`/project-info/${projectId.value}`)
    if (response.code === 200) {
      showSuccessToast('删除成功')
      router.back()
    }
  } catch (error: any) {
    if (error !== 'cancel') {
      console.error('Failed to delete project:', error)
      showToast('删除失败')
    }
  }
}

const handleBack = () => {
  router.back()
}

onMounted(() => {
  fetchCustomers()
  
  const id = route.query.id
  if (id) {
    isEdit.value = true
    projectId.value = Number(id)
    fetchProjectInfo(projectId.value)
  }
})
</script>

<template>
  <div class="project-info-page">
    <van-nav-bar 
      :title="isEdit ? '编辑项目信息' : '新增项目信息'" 
      fixed 
      placeholder
    >
      <template #left>
        <div class="nav-left" @click="handleBack">
          <van-icon name="arrow-left" />
          <span>返回</span>
        </div>
      </template>
      <template #right v-if="isEdit">
        <van-icon name="delete-o" @click="handleDelete" />
      </template>
    </van-nav-bar>

    <van-loading v-if="loading" class="loading-overlay" />

    <div class="form-container">
      <van-cell-group inset>
        <van-field
          v-model="formData.project_id"
          label="项目编号"
          placeholder="请输入项目编号"
          required
          :rules="[{ required: true, message: '请输入项目编号' }]"
        />
        
        <van-field
          v-model="formData.project_name"
          label="项目名称"
          placeholder="请输入项目名称"
          required
          :rules="[{ required: true, message: '请输入项目名称' }]"
        />

        <van-field
          v-model="formData.project_abbr"
          label="项目简称"
          placeholder="请输入项目简称"
        />

        <van-field
          v-model="formData.completion_date"
          is-link
          readonly
          label="开始日期"
          placeholder="请选择开始日期"
          required
          @click="showStartDatePicker = true"
        />

        <van-field
          v-model="formData.maintenance_end_date"
          is-link
          readonly
          label="结束日期"
          placeholder="请选择结束日期"
          required
          @click="showEndDatePicker = true"
        />

        <van-field
          v-model="formData.maintenance_period"
          is-link
          readonly
          label="维保频率"
          placeholder="请选择维保频率"
          required
          @click="showPeriodPicker = true"
        />

        <van-field
          v-model="formData.client_name"
          is-link
          label="客户单位"
          placeholder="请选择或输入客户单位"
          required
          @click="showClientPicker = true"
          @update:model-value="onClientInput"
        />

        <van-field
          v-model="formData.address"
          label="客户地址"
          placeholder="请输入客户地址"
          required
        />

        <van-field
          v-model="formData.project_manager"
          label="项目负责人"
          placeholder="请输入项目负责人"
        />

        <van-field
          v-model="formData.client_contact"
          label="客户联系人"
          placeholder="请输入客户联系人"
        />

        <van-field
          v-model="formData.client_contact_position"
          label="联系人职位"
          placeholder="请输入联系人职位"
        />

        <van-field
          v-model="formData.client_contact_info"
          label="联系方式"
          placeholder="请输入联系方式"
        />
      </van-cell-group>

      <div class="submit-btn">
        <van-button type="primary" block @click="handleSubmit">
          {{ isEdit ? '保存修改' : '提交' }}
        </van-button>
      </div>
    </div>

    <van-popup 
      v-model:show="showClientPicker" 
      position="bottom" 
      round
      :style="{ height: '60%' }"
    >
      <div class="client-picker">
        <div class="picker-header">
          <span class="picker-title">选择客户单位</span>
          <van-icon name="cross" @click="showClientPicker = false" />
        </div>
        
        <SearchInput
          v-model="searchKeyword"
          field-key="ProjectInfoPage_customer"
          placeholder="搜索客户单位"
          @input="searchKeyword = $event"
        />

        <van-loading v-if="customerLoading" class="picker-loading" />
        
        <div class="client-list" v-else>
          <van-cell 
            v-for="customer in filteredCustomers" 
            :key="customer.id"
            :title="customer.name"
            :label="customer.address || '暂无地址'"
            is-link
            @click="onClientSelect(customer)"
          />
          
          <van-empty v-if="filteredCustomers.length === 0" description="暂无客户数据" />
        </div>

        <div class="custom-input-section">
          <van-field
            v-model="formData.client_name"
            placeholder="或直接输入客户单位名称"
            clearable
          />
          <van-button type="primary" size="small" @click="showClientPicker = false">
            确定
          </van-button>
        </div>
      </div>
    </van-popup>

    <van-popup v-model:show="showPeriodPicker" position="bottom" round>
      <van-picker
        :columns="periodOptions"
        @confirm="onPeriodConfirm"
        @cancel="showPeriodPicker = false"
      />
    </van-popup>

    <van-popup v-model:show="showStartDatePicker" position="bottom" round>
      <van-date-picker
        v-model="startDateValue"
        title="选择开始日期"
        :min-date="minDate"
        :max-date="maxDate"
        @confirm="onStartDateConfirm"
        @cancel="showStartDatePicker = false"
      />
    </van-popup>

    <van-popup v-model:show="showEndDatePicker" position="bottom" round>
      <van-date-picker
        v-model="endDateValue"
        title="选择结束日期"
        :min-date="minDate"
        :max-date="maxDate"
        @confirm="onEndDateConfirm"
        @cancel="showEndDatePicker = false"
      />
    </van-popup>
  </div>
</template>

<style scoped>
.project-info-page {
  min-height: 100vh;
  background-color: #f5f7fa;
}

.loading-overlay {
  position: fixed;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
}

.form-container {
  padding: 12px;
  padding-bottom: 80px;
}

.submit-btn {
  margin-top: 16px;
  padding: 0 16px;
}

.client-picker {
  height: 100%;
  display: flex;
  flex-direction: column;
}

.picker-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px;
  border-bottom: 1px solid #ebedf0;
}

.picker-title {
  font-size: 16px;
  font-weight: 500;
}

.picker-loading {
  padding: 20px;
  text-align: center;
}

.client-list {
  flex: 1;
  overflow-y: auto;
}

.custom-input-section {
  display: flex;
  align-items: center;
  padding: 12px;
  border-top: 1px solid #ebedf0;
  gap: 8px;
}

.custom-input-section .van-field {
  flex: 1;
}

:deep(.van-cell-group--inset) {
  margin: 0;
}

:deep(.van-field__label) {
  width: 90px;
}
</style>
