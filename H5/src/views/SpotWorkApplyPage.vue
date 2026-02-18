<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { showLoadingToast, closeToast, showToast, showSuccessToast, showFailToast } from 'vant'
import api from '../utils/api'
import type { ApiResponse } from '../types'
import { formatDate, formatDateTime } from '../config/constants'
import UserSelector from '../components/UserSelector.vue'
import { authService, type User } from '../services/auth'

interface ProjectInfo {
  id: number
  project_id: string
  project_name: string
  client_name: string
}

const router = useRouter()
const route = useRoute()

const activeTab = ref(0)
const loading = ref(false)
const workList = ref<any[]>([])
const userReady = ref(false)
const currentUser = ref<User | null>(null)

const canApprove = computed(() => authService.canApproveSpotWork(currentUser.value))

const applyFormData = ref({
  projectId: '',
  projectIdDisplay: '',
  projectName: '',
  workDateStart: formatDate(new Date()),
  workDateEnd: formatDate(new Date()),
  workContent: '',
  remark: ''
})

const projectList = ref<ProjectInfo[]>([])
const showProjectPicker = ref(false)
const showDateRangePicker = ref(false)
const selectedProjectName = ref('')
const submitLoading = ref(false)
const workerCount = ref(0)
const generatedWorkId = ref('')

const minDate = new Date(2020, 0, 1)
const maxDate = new Date(2030, 11, 31)

const dateDisplayText = computed(() => {
  if (applyFormData.value.workDateStart === applyFormData.value.workDateEnd) {
    return applyFormData.value.workDateStart
  }
  return `${applyFormData.value.workDateStart} 至 ${applyFormData.value.workDateEnd}`
})

const workDays = computed(() => {
  if (!applyFormData.value.workDateStart || !applyFormData.value.workDateEnd) return 0
  const start = new Date(applyFormData.value.workDateStart)
  const end = new Date(applyFormData.value.workDateEnd)
  const diffTime = Math.abs(end.getTime() - start.getTime())
  const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24)) + 1
  return diffDays
})

const baseTabs = [
  { key: '申报用工', title: '申报用工', statuses: [], color: '#07c160' },
  { key: '待确认', title: '待确认', statuses: ['待确认'], color: '#ff976a' },
  { key: '已完成', title: '已完成', statuses: ['已确认', '已完成'], color: '#1989fa' }
]

const approvalTab = { key: '审批', title: '审批', statuses: ['待确认'], color: '#1989fa' }

const tabs = computed(() => {
  if (canApprove.value) {
    return [approvalTab, ...baseTabs]
  }
  return baseTabs
})

const currentTab = computed(() => tabs.value[activeTab.value])
const currentTabColor = computed(() => tabs.value[activeTab.value]?.color || '#1989fa')

const getStatusType = (status: string) => {
  switch (status) {
    case '已完成':
    case '已确认':
      return 'success'
    case '待确认':
      return 'warning'
    default:
      return 'default'
  }
}

const getDisplayStatus = (status: string) => {
  if (status === '已确认' || status === '已完成') return '已完成'
  if (status === '待确认') return '待确认'
  return status
}

/**
 * 根据工单编号长度计算字体大小
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

/**
 * 复制工单编号到剪贴板
 */
const copyOrderId = async (orderId: string) => {
  try {
    await navigator.clipboard.writeText(orderId)
    showToast('工单编号已复制')
  } catch {
    showToast('复制失败')
  }
}

/**
 * 获取项目列表
 */
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

/**
 * 获取工单列表
 */
const fetchWorkList = async () => {
  if (!userReady.value) return
  if (currentTab.value?.key === '申报用工') return
  
  loading.value = true
  showLoadingToast({ message: '加载中...', forbidClick: true })
  try {
    const response = await api.get<unknown, ApiResponse<any>>('/spot-work', { 
      params: { 
        page: 0,
        size: 100
      } 
    })
    if (response.code === 200) {
      const allItems = response.data?.content || []
      const filteredItems = allItems.filter((item: any) => 
        currentTab.value?.statuses.includes(item.status)
      )
      workList.value = filteredItems.sort((a: any, b: any) => {
        const dateA = new Date(a.updated_at || a.created_at || 0).getTime()
        const dateB = new Date(b.updated_at || b.created_at || 0).getTime()
        return dateB - dateA
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
const handleProjectConfirm = ({ selectedOptions, selectedValues }: { selectedOptions: Array<{ text: string; value: string }>, selectedValues: string[] }) => {
  const selectedValue = selectedValues && selectedValues.length > 0 ? selectedValues[0] : null
  if (selectedValue) {
    const project = projectList.value.find(p => p.id.toString() === selectedValue)
    if (project) {
      applyFormData.value.projectId = project.project_id
      applyFormData.value.projectIdDisplay = project.project_id
      applyFormData.value.projectName = project.project_name
      selectedProjectName.value = project.project_name
    }
  } else if (selectedOptions && selectedOptions.length > 0) {
    const selected = selectedOptions[0]
    const project = projectList.value.find(p => p.id.toString() === selected.value)
    if (project) {
      applyFormData.value.projectId = project.project_id
      applyFormData.value.projectIdDisplay = project.project_id
      applyFormData.value.projectName = project.project_name
      selectedProjectName.value = project.project_name
    }
  }
  showProjectPicker.value = false
}

/**
 * 处理日期范围选择确认
 */
const handleDateRangeConfirm = (values: Date[]) => {
  if (values && values.length === 2) {
    applyFormData.value.workDateStart = formatDate(values[0])
    applyFormData.value.workDateEnd = formatDate(values[1])
  }
  showDateRangePicker.value = false
}

/**
 * 跳转到施工人员录入页面
 */
const handleWorkerEntry = () => {
  router.push({
    path: '/spot-work/worker-entry',
    query: {
      projectId: applyFormData.value.projectId,
      projectName: applyFormData.value.projectName,
      workDateStart: applyFormData.value.workDateStart,
      workDateEnd: applyFormData.value.workDateEnd
    }
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
  
  submitLoading.value = true
  showLoadingToast({ message: '提交中...', forbidClick: true })
  
  try {
    const response = await api.post<unknown, ApiResponse<{work_id: string}>>('/spot-work/quick-fill', {
      project_id: applyFormData.value.projectId,
      project_name: applyFormData.value.projectName,
      plan_start_date: applyFormData.value.workDateStart,
      plan_end_date: applyFormData.value.workDateEnd,
      work_content: applyFormData.value.workContent,
      remark: applyFormData.value.remark,
      worker_count: workerCount.value
    })
    if (response.code === 200) {
      generatedWorkId.value = response.data?.work_id || ''
      showSuccessToast({
        message: `提交成功\n工单号：${generatedWorkId.value}`,
        duration: 3000
      })
      applyFormData.value = {
        projectId: '',
        projectIdDisplay: '',
        projectName: '',
        workDateStart: formatDate(new Date()),
        workDateEnd: formatDate(new Date()),
        workContent: '',
        remark: ''
      }
      selectedProjectName.value = ''
      workerCount.value = 0
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
  router.push('/')
}

/**
 * 处理审批操作
 */
const handleApprove = (item: any) => {
  router.push(`/spot-work/${item.id}?tab=${activeTab.value}&mode=approve`)
}

const handleUserReady = (user: User) => {
  currentUser.value = user
  userReady.value = true
  fetchWorkList()
}

const handleUserChanged = (user: User) => {
  currentUser.value = user
  fetchWorkList()
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
  currentUser.value = authService.getCurrentUser()
  fetchProjectList()
  const tabParam = route.query.tab
  if (tabParam !== undefined && tabParam !== null) {
    const tabIndex = parseInt(tabParam as string, 10)
    if (!isNaN(tabIndex) && tabIndex >= 0 && tabIndex < tabs.value.length) {
      activeTab.value = tabIndex
    }
  }
})
</script>

<template>
  <div class="spot-work-apply-page">
    <van-nav-bar 
      title="申报用工" 
      fixed 
      placeholder 
      @click-left="handleBack" 
    >
      <template #left>
        <div class="nav-left" @click="handleBack">
          <van-icon name="arrow-left" />
          <span>返回</span>
        </div>
      </template>
      <template #right>
        <UserSelector @userChanged="handleUserChanged" @ready="handleUserReady" />
      </template>
    </van-nav-bar>
    
    <van-tabs v-model:active="activeTab" sticky @change="fetchWorkList" :color="currentTabColor">
      <van-tab v-for="tab in tabs" :key="tab.key" :title="tab.title">
        <template v-if="tab.key === '申报用工'">
          <van-cell-group inset title="基本信息" class="form-group">
            <div class="two-column-form">
              <div class="form-row">
                <van-cell 
                  :title="selectedProjectName || '选择项目'"
                  label="项目名称"
                  is-link
                  required
                  @click="showProjectPicker = true"
                  class="form-cell"
                />
                <van-cell 
                  v-if="applyFormData.projectIdDisplay"
                  :title="applyFormData.projectIdDisplay"
                  label="项目编号"
                  class="form-cell"
                />
              </div>
              <div class="form-row">
                <van-cell 
                  :title="dateDisplayText"
                  label="用工周期"
                  is-link
                  required
                  @click="showDateRangePicker = true"
                  class="form-cell"
                />
                <van-cell 
                  v-if="workDays > 0"
                  :title="workDays + ' 天'"
                  label="用工天数"
                  class="form-cell"
                />
              </div>
            </div>
            <van-field 
              v-model="applyFormData.workContent" 
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
            <van-cell 
              v-if="workerCount > 0"
              :title="workerCount + ' 人'"
              label="施工人数"
            />
            <van-field 
              v-model="applyFormData.remark" 
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
              color="#1989fa"
              background="#ecf9ff"
            />
          </div>
        </template>
        
        <template v-else>
          <van-pull-refresh v-model="loading" @refresh="fetchWorkList">
            <van-list :loading="loading" :finished="true">
              <div class="work-list">
                <div 
                  v-for="item in workList" 
                  :key="item.id"
                  class="work-card"
                >
                  <div class="card-header">
                    <van-tag :type="getStatusType(item.status)" size="medium">
                      {{ getDisplayStatus(item.status) }}
                    </van-tag>
                    <div class="work-id-wrapper">
                      <span class="work-id" :style="{ fontSize: getWorkIdFontSize(item.work_id) + 'px' }">{{ item.work_id }}</span>
                      <van-button size="mini" type="primary" plain class="copy-btn" @click.stop="copyOrderId(item.work_id)">复制单号</van-button>
                    </div>
                  </div>
                  <div class="card-body">
                    <div class="info-row">
                      <span class="label">项目名称</span>
                      <span class="value">{{ item.project_name }}</span>
                    </div>
                    <div class="info-row">
                      <span class="label">客户单位</span>
                      <span class="value">{{ item.client_name || '-' }}</span>
                    </div>
                    <div class="info-row">
                      <span class="label">运维时间</span>
                      <span class="value">{{ formatDate(item.plan_start_date) }} -- {{ formatDate(item.plan_end_date) }}</span>
                    </div>
                    <div class="info-row">
                      <span class="label">备注</span>
                      <span class="value">{{ item.remarks || '-' }}</span>
                    </div>
                    <div class="info-row" v-if="currentTab?.key === '待确认' || currentTab?.key === '审批'">
                      <span class="label">提交时间</span>
                      <span class="value">{{ formatDateTime(item.updated_at) }}</span>
                    </div>
                  </div>
                  <div class="card-footer">
                    <van-button 
                      v-if="currentTab?.key === '审批'"
                      type="success" 
                      size="small"
                      @click="handleApprove(item)"
                    >
                      审批
                    </van-button>
                    <van-button 
                      type="primary" 
                      size="small"
                      @click="handleView(item)"
                    >
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
        title="选择项目"
        :columns="projectColumns"
        @confirm="handleProjectConfirm"
        @cancel="showProjectPicker = false"
      />
    </van-popup>

    <van-calendar 
      v-model:show="showDateRangePicker" 
      type="range"
      title="选择用工周期"
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
.spot-work-apply-page {
  min-height: 100vh;
  background-color: #f5f7fa;
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
  background: #fff;
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
  background: #f7f8fa;
  border-bottom: 1px solid #ebedf0;
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
  color: #323233;
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

.card-body {
  padding: 12px 16px;
}

.info-row {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  padding: 6px 0;
  font-size: 13px;
}

.info-row .label {
  color: #969799;
  flex-shrink: 0;
  width: 70px;
}

.info-row .value {
  color: #323233;
  text-align: right;
  flex: 1;
  margin-left: 12px;
  word-break: break-all;
}

.card-footer {
  display: flex;
  justify-content: flex-end;
  gap: 8px;
  padding: 12px 16px;
  border-top: 1px solid #ebedf0;
}

.card-footer .van-button {
  min-width: 60px;
}

.nav-left {
  display: flex;
  align-items: center;
  gap: 4px;
  color: #323233;
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

.two-column-form {
  padding: 0;
}

.form-row {
  display: flex;
  border-bottom: 1px solid #ebedf0;
}

.form-row:last-child {
  border-bottom: none;
}

.form-cell {
  flex: 1;
  min-width: 0;
}

.form-cell :deep(.van-cell) {
  padding: 10px 12px;
}

.form-cell :deep(.van-cell__title) {
  font-size: 12px;
  color: #969799;
}

.form-cell :deep(.van-cell__value) {
  font-size: 14px;
  color: #323233;
}
</style>
