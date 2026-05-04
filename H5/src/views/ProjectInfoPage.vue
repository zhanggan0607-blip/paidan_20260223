<script setup lang="ts">
import { ref, onMounted, computed, onUnmounted } from 'vue'
import { useRoute } from 'vue-router'
import { showToast, showConfirmDialog, showSuccessToast } from 'vant'
import { projectInfoService, customerService, authService } from '../services'
import { SearchInput } from '@sstcp/shared'
import { useNavigation } from '../composables'
import { useUserStore } from '../stores/userStore'
const userStore = useUserStore()
import type { Customer, ProjectInfo } from '../types/api'
import type { CustomerContact } from '../services/customer'

const route = useRoute()
const { goBack } = useNavigation()

const loading = ref(false)
const isEdit = ref(false)
const projectId = ref<number | null>(null)
let sessionCheckInterval: ReturnType<typeof setInterval> | null = null

const formData = ref<Partial<ProjectInfo>>({
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
  client_contact_info: '',
})

const showClientPicker = ref(false)
const showContactPicker = ref(false)
const showPeriodPicker = ref(false)
const showStartDatePicker = ref(false)
const showEndDatePicker = ref(false)
const customerList = ref<Customer[]>([])
const contactList = ref<CustomerContact[]>([])
const customerLoading = ref(false)
const contactLoading = ref(false)
const searchKeyword = ref('')
const contactSearchKeyword = ref('')
const customContactName = ref('')
const customContactPhone = ref('')
const customContactPosition = ref('')
const startDateValue = ref<string[]>(['2024', '01', '01'])
const endDateValue = ref<string[]>(['2024', '12', '31'])

const periodOptions = [
  { text: '每天', value: '每天' },
  { text: '每周', value: '每周' },
  { text: '每月', value: '每月' },
  { text: '每季度', value: '每季度' },
  { text: '每半年', value: '每半年' },
]

const filteredCustomers = computed(() => {
  if (!searchKeyword.value) {
    return customerList.value
  }
  return customerList.value.filter((c) =>
    (c.name || c.customer_name || '').toLowerCase().includes(searchKeyword.value.toLowerCase())
  )
})

const filteredContacts = computed(() => {
  if (!contactSearchKeyword.value) {
    return contactList.value
  }
  return contactList.value.filter((c) =>
    (c.contact_person || '').toLowerCase().includes(contactSearchKeyword.value.toLowerCase())
  )
})

const minDate = new Date(2020, 0, 1)
const maxDate = new Date(2030, 11, 31)

const fetchCustomers = async () => {
  customerLoading.value = true
  try {
    const response = await customerService.getList({ size: 100 })
    if (response.code === 200 && response.data) {
      customerList.value = response.data.items || []
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
    const response = await projectInfoService.getById(id)
    if (response.code === 200 && response.data) {
      const completionDate = response.data.completion_date
        ? (response.data.completion_date.split('T')[0] ?? '')
        : ''
      const maintenanceEndDate = response.data.maintenance_end_date
        ? (response.data.maintenance_end_date.split('T')[0] ?? '')
        : ''
      formData.value = {
        ...response.data,
        completion_date: completionDate,
        maintenance_end_date: maintenanceEndDate,
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

const onClientSelect = async (customer: Customer) => {
  formData.value.client_name = customer.name
  formData.value.address = customer.address || ''
  formData.value.client_contact = ''
  formData.value.client_contact_info = ''
  formData.value.client_contact_position = ''
  showClientPicker.value = false
  searchKeyword.value = ''

  if (customer.name) {
    await fetchContacts(customer.name)
  }
}

const fetchContacts = async (customerName: string) => {
  contactLoading.value = true
  try {
    const response = await customerService.getContactsByName(customerName)
    if (response.code === 200 && response.data) {
      contactList.value = response.data
    }
  } catch (error) {
    console.error('Failed to fetch contacts:', error)
  } finally {
    contactLoading.value = false
  }
}

const onContactSelect = (contact: CustomerContact) => {
  formData.value.client_contact = contact.contact_person
  formData.value.client_contact_info = contact.phone || ''
  formData.value.client_contact_position = contact.contact_position || ''
  showContactPicker.value = false
  contactSearchKeyword.value = ''
}

const openContactPicker = () => {
  if (!formData.value.client_name) {
    showToast('请先选择客户单位')
    return
  }
  customContactName.value = formData.value.client_contact || ''
  customContactPhone.value = formData.value.client_contact_info || ''
  customContactPosition.value = formData.value.client_contact_position || ''
  showContactPicker.value = true
}

const onCustomContactConfirm = () => {
  if (!customContactName.value.trim()) {
    showToast('请输入联系人姓名')
    return
  }
  formData.value.client_contact = customContactName.value.trim()
  formData.value.client_contact_info = customContactPhone.value.trim()
  formData.value.client_contact_position = customContactPosition.value.trim()
  showContactPicker.value = false
  contactSearchKeyword.value = ''
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
  if (!formData.value?.project_id?.trim()) {
    showToast('请输入项目编号')
    return false
  }
  if (!formData.value?.project_name?.trim()) {
    showToast('请输入项目名称')
    return false
  }
  if (!formData.value?.completion_date) {
    showToast('请选择开始日期')
    return false
  }
  if (!formData.value?.maintenance_end_date) {
    showToast('请选择结束日期')
    return false
  }
  if (!formData.value?.maintenance_period) {
    showToast('请选择维保频率')
    return false
  }
  if (!formData.value?.client_name?.trim()) {
    showToast('请选择客户单位')
    return false
  }
  if (!formData.value?.address?.trim()) {
    showToast('请输入客户地址')
    return false
  }
  return true
}

const handleSubmit = async () => {
  if (!validateForm()) return

  if (!formData.value.project_id || !formData.value.project_name) {
    showToast('请填写项目编号和项目名称')
    return
  }

  try {
    const submitData = {
      project_id: formData.value.project_id,
      project_name: formData.value.project_name,
      completion_date: formData.value.completion_date + 'T00:00:00',
      maintenance_end_date: formData.value.maintenance_end_date + 'T00:00:00',
      maintenance_period: formData.value.maintenance_period,
      client_name: formData.value.client_name,
      address: formData.value.address,
      project_abbr: formData.value.project_abbr,
      project_manager: formData.value.project_manager,
      client_contact: formData.value.client_contact,
      client_contact_position: formData.value.client_contact_position,
      client_contact_info: formData.value.client_contact_info,
    }

    let response
    if (isEdit.value && projectId.value) {
      response = await projectInfoService.update(projectId.value, submitData)
    } else {
      response = await projectInfoService.create(submitData)
    }

    if (response.code === 200) {
      showSuccessToast(isEdit.value ? '更新成功' : '创建成功')
      goBack()
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
      message: '请确认是否要删除该项目？',
    })

    const response = await projectInfoService.delete(projectId.value)
    if (response.code === 200) {
      showSuccessToast('删除成功')
      goBack()
    } else if (response.code === 400 && response.message && response.message.includes('级联删除')) {
      try {
        await showConfirmDialog({
          title: '级联删除',
          message: response.message + '\n是否确认删除项目及其所有关联数据？',
        })
        const cascadeResponse = await projectInfoService.delete(projectId.value, true)
        if (cascadeResponse.code === 200) {
          showSuccessToast('删除成功')
          goBack()
        } else {
          showToast(cascadeResponse.message || '删除失败')
        }
      } catch {
        // 用户取消级联删除
      }
    } else {
      showToast(response.message || '删除失败')
    }
  } catch (error: any) {
    if (error !== 'cancel') {
      console.error('Failed to delete project:', error)
      if (error.status === 404) {
        showToast('该项目已被删除')
        goBack()
      } else {
        showToast(error.message || '删除失败')
      }
    }
  }
}

const handleBack = () => {
  goBack()
}

/**
 * 保持会话活跃，定期刷新token
 */
const keepSessionAlive = async () => {
  const token = userStore.token
  if (!token) {
    return
  }

  try {
    const response = await authService.refreshToken()
    if (response.code === 200 && response.data?.access_token) {
      userStore.setToken(response.data.access_token)
    }
  } catch (error) {
    console.error('Session refresh failed:', error)
  }
}

onMounted(() => {
  fetchCustomers()

  const id = route.query.id
  if (id) {
    isEdit.value = true
    projectId.value = Number(id)
    fetchProjectInfo(projectId.value)
  }

  sessionCheckInterval = setInterval(keepSessionAlive, 5 * 60 * 1000)
})

onUnmounted(() => {
  if (sessionCheckInterval) {
    clearInterval(sessionCheckInterval)
    sessionCheckInterval = null
  }
})
</script>

<template>
  <div class="project-info-page">
    <van-nav-bar fixed placeholder @click-left="handleBack">
      <template #left>
        <div class="nav-left">
          <van-icon name="arrow-left" />
          <span>返回</span>
        </div>
      </template>
      <template #right>
        <van-icon v-if="isEdit" name="delete-o" @click="handleDelete" />
      </template>
    </van-nav-bar>

    <van-loading v-if="loading" class="loading-overlay" />

    <div class="form-container">
      <van-cell-group inset>
        <van-field name="project_id"
          v-model="formData.project_id"
          label="项目编号"
          placeholder="请输入项目编号"
          required
          :rules="[{ required: true, message: '请输入项目编号' }]"
        />

        <van-field name="project_name"
          v-model="formData.project_name"
          label="项目名称"
          placeholder="请输入项目名称"
          required
          :rules="[{ required: true, message: '请输入项目名称' }]"
        />

        <van-field name="project_abbr" v-model="formData.project_abbr" label="项目简称" placeholder="请输入项目简称" />

        <van-field name="completion_date"
          v-model="formData.completion_date"
          is-link
          readonly
          label="开始日期"
          placeholder="请选择开始日期"
          required
          @click="showStartDatePicker = true"
        />

        <van-field name="maintenance_end_date"
          v-model="formData.maintenance_end_date"
          is-link
          readonly
          label="结束日期"
          placeholder="请选择结束日期"
          required
          @click="showEndDatePicker = true"
        />

        <van-field name="maintenance_period"
          v-model="formData.maintenance_period"
          is-link
          readonly
          label="维保频率"
          placeholder="请选择维保频率"
          required
          @click="showPeriodPicker = true"
        />

        <van-field name="client_name"
          v-model="formData.client_name"
          is-link
          readonly
          label="客户单位"
          placeholder="请选择客户单位"
          required
          @click="showClientPicker = true"
        />

        <van-field name="address"
          v-model="formData.address"
          label="客户地址"
          placeholder="请输入客户地址"
          required
        />

        <van-field name="project_manager"
          v-model="formData.project_manager"
          label="运维人员"
          placeholder="请输入运维人员"
        />

        <van-field name="client_contact"
          v-model="formData.client_contact"
          is-link
          readonly
          label="客户联系人"
          placeholder="请选择或输入客户联系人"
          @click="openContactPicker"
        />

        <van-field name="client_contact_position"
          v-model="formData.client_contact_position"
          label="联系人职位"
          placeholder="请输入联系人职位"
        />

        <van-field name="client_contact_info"
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

    <van-popup v-model:show="showClientPicker" position="bottom" round :style="{ height: '60%' }">
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

        <div v-else class="client-list">
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
      </div>
    </van-popup>

    <van-popup v-model:show="showContactPicker" position="bottom" round :style="{ height: '60%' }">
      <div class="client-picker">
        <div class="picker-header">
          <span class="picker-title">选择客户联系人</span>
          <van-icon name="cross" @click="showContactPicker = false" />
        </div>

        <div class="custom-input-section">
          <van-field name="custom_contact_name"
            v-model="customContactName"
            placeholder="手动输入联系人姓名"
            class="custom-input-field"
          />
          <van-field name="custom_contact_phone"
            v-model="customContactPhone"
            placeholder="联系方式"
            class="custom-input-field"
          />
          <van-field name="custom_contact_position"
            v-model="customContactPosition"
            placeholder="职位"
            class="custom-input-field"
          />
          <van-button type="primary" size="small" @click="onCustomContactConfirm">确定</van-button>
        </div>

        <div class="picker-divider">
          <span>或从已有联系人中选择</span>
        </div>

        <SearchInput
          v-model="contactSearchKeyword"
          field-key="ProjectInfoPage_contact"
          placeholder="搜索联系人"
          @input="contactSearchKeyword = $event"
        />

        <van-loading v-if="contactLoading" class="picker-loading" />

        <div v-else class="client-list">
          <van-cell
            v-for="contact in filteredContacts"
            :key="contact.id"
            :title="contact.contact_person"
            :label="contact.phone || '暂无联系方式'"
            is-link
            @click="onContactSelect(contact)"
          >
            <template #value>
              <span v-if="contact.contact_position" class="contact-position">{{
                contact.contact_position
              }}</span>
            </template>
          </van-cell>

          <van-empty v-if="filteredContacts.length === 0" description="暂无联系人数据" />
        </div>
      </div>
    </van-popup>

    <van-popup v-model:show="showPeriodPicker" position="bottom" round>
      <van-picker name="picker"
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
  background-color: var(--color-bg-page);
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
  border-bottom: 1px solid var(--color-border-light);
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
  border-top: 1px solid var(--color-border-light);
  gap: 8px;
  flex-wrap: wrap;
}

.custom-input-section .van-field {
  flex: 1;
  min-width: 80px;
}

.custom-input-field {
  padding: 5px 8px;
  background: var(--color-bg-page);
  border-radius: 4px;
}

.picker-divider {
  padding: 8px 16px;
  background: var(--color-bg-page);
  text-align: center;
  color: var(--color-text-secondary);
  font-size: 12px;
}

:deep(.van-cell-group--inset) {
  margin: 0;
}

:deep(.van-field__label) {
  width: 90px;
}

.contact-position {
  font-size: 12px;
  color: var(--color-text-secondary);
}
</style>
