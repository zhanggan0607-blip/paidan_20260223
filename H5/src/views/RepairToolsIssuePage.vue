<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { showLoadingToast, closeToast, showSuccessToast, showFailToast, showConfirmDialog } from 'vant'
import api from '../utils/api'
import type { ApiResponse } from '../types'
import { formatDate } from '../config/constants'
import UserSelector from '../components/UserSelector.vue'
import { userStore } from '../stores/userStore'

interface RepairToolsIssueItem {
  id: number
  tool_id: string
  tool_name: string
  specification: string
  quantity: number
  user_name: string
  issue_time: string
  project_name: string
  status: string
}

interface ToolStockItem {
  id: number
  tool_id: string
  tool_name: string
  category: string
  specification: string
  stock: number
  unit: string
}

interface ProjectItem {
  project_id: string
  project_name: string
}

const router = useRouter()
const loading = ref(false)
const issueList = ref<RepairToolsIssueItem[]>([])
const toolStockList = ref<ToolStockItem[]>([])
const projectList = ref<ProjectItem[]>([])

const showIssuePopup = ref(false)
const selectedTool = ref<ToolStockItem | null>(null)
const issueForm = ref({
  projectId: '',
  projectName: '',
  quantity: 1 as number,
  remark: ''
})

const filteredToolList = computed(() => {
  return toolStockList.value.filter(item => item.stock > 0)
})

const maxQuantity = computed(() => {
  return selectedTool.value?.stock || 1
})

/**
 * 获取领用记录
 */
const fetchIssueList = async () => {
  loading.value = true
  showLoadingToast({ message: '加载中...', forbidClick: true })
  try {
    const response = await api.get<unknown, ApiResponse<{ items: RepairToolsIssueItem[], total: number }>>('/repair-tools/issue', {
      params: { page: 0, size: 100 }
    })
    if (response.code === 200) {
      issueList.value = response.data?.items || []
    }
  } catch (error) {
    console.error('Failed to fetch issue list:', error)
  } finally {
    loading.value = false
    closeToast()
  }
}

/**
 * 获取工具库存列表
 */
const fetchToolStockList = async () => {
  try {
    const response = await api.get<unknown, ApiResponse<{ items: ToolStockItem[], total: number }>>('/repair-tools/stock', {
      params: { page: 0, size: 500 }
    })
    if (response.code === 200) {
      toolStockList.value = response.data?.items || []
    }
  } catch (error) {
    console.error('Failed to fetch tool stock list:', error)
  }
}

/**
 * 获取项目列表（根据用户权限自动过滤）
 */
const fetchProjectList = async () => {
  try {
    const response = await api.get<unknown, ApiResponse<ProjectItem[]>>('/project-info/all/list')
    if (response.code === 200) {
      projectList.value = response.data || []
    }
  } catch (error) {
    console.error('Failed to fetch project list:', error)
  }
}

/**
 * 选择工具
 */
const handleSelectTool = (item: ToolStockItem) => {
  selectedTool.value = item
  issueForm.value.quantity = 1
}

/**
 * 提交领用
 */
const handleSubmitIssue = async () => {
  if (!selectedTool.value) {
    showFailToast('请选择工具')
    return
  }
  if (!issueForm.value.projectId) {
    showFailToast('请选择项目')
    return
  }
  if (issueForm.value.quantity <= 0) {
    showFailToast('请选择领用数量')
    return
  }

  try {
    await showConfirmDialog({
      title: '确认领用',
      message: `确认领用 ${selectedTool.value.tool_name} ${issueForm.value.quantity}件?`
    })
  } catch {
    return
  }

  loading.value = true
  showLoadingToast({ message: '提交中...', forbidClick: true })
  
  try {
    const response = await api.post<unknown, ApiResponse<null>>('/repair-tools/issue', {
      tool_id: selectedTool.value.tool_id || String(selectedTool.value.id),
      tool_name: selectedTool.value.tool_name,
      specification: selectedTool.value.specification || null,
      quantity: issueForm.value.quantity,
      user_name: userStore.getUser()?.name,
      project_id: issueForm.value.projectId || null,
      project_name: issueForm.value.projectName || null,
      remark: issueForm.value.remark || null
    })
    
    if (response.code === 200) {
      showSuccessToast('领用成功')
      showIssuePopup.value = false
      selectedTool.value = null
      issueForm.value = {
        projectId: '',
        projectName: '',
        quantity: 1,
        remark: ''
      }
      fetchIssueList()
      fetchToolStockList()
    } else {
      showFailToast(response.message || '领用失败')
    }
  } catch (error) {
    console.error('Failed to submit:', error)
    showFailToast('领用失败，请重试')
  } finally {
    loading.value = false
    closeToast()
  }
}

/**
 * 获取状态样式
 */
const getStatusClass = (status: string) => {
  if (status === '已领用' || status === '待归还') return 'status-issued'
  return 'status-returned'
}

const handleBack = () => {
  router.push('/')
}

const handleUserChanged = () => {
  fetchIssueList()
  fetchProjectList()
}

onMounted(() => {
  fetchIssueList()
  fetchProjectList()
})
</script>

<template>
  <div class="repair-tools-issue-page">
    <van-nav-bar 
      title="维修工具领用" 
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
        <UserSelector @userChanged="handleUserChanged" />
      </template>
    </van-nav-bar>
    
    <div class="action-bar">
      <van-button type="primary" size="small" @click="showIssuePopup = true">
        新增领用
      </van-button>
    </div>
    
    <van-pull-refresh v-model="loading" @refresh="fetchIssueList">
      <van-list :loading="loading" :finished="true">
        <div class="issue-list">
          <div 
            v-for="item in issueList" 
            :key="item.id"
            class="issue-card"
          >
            <div class="card-header">
              <span class="tool-name">{{ item.tool_name }}</span>
              <span :class="['status-badge', getStatusClass(item.status)]">
                {{ item.status }}
              </span>
            </div>
            <div class="card-body">
              <div class="info-row">
                <span class="label">工具编号</span>
                <span class="value">{{ item.tool_id }}</span>
              </div>
              <div class="info-row">
                <span class="label">规格型号</span>
                <span class="value">{{ item.specification || '-' }}</span>
              </div>
              <div class="info-row">
                <span class="label">领用数量</span>
                <span class="value">{{ item.quantity }}</span>
              </div>
              <div class="info-row">
                <span class="label">运维人员</span>
                <span class="value">{{ item.user_name }}</span>
              </div>
              <div class="info-row">
                <span class="label">领用时间</span>
                <span class="value">{{ formatDate(item.issue_time) }}</span>
              </div>
              <div class="info-row">
                <span class="label">所属项目</span>
                <span class="value">{{ item.project_name || '-' }}</span>
              </div>
            </div>
          </div>
        </div>
        <van-empty v-if="!loading && issueList.length === 0" description="暂无领用记录" />
      </van-list>
    </van-pull-refresh>

    <van-popup v-model:show="showIssuePopup" position="bottom" round :style="{ height: '85%' }">
      <div class="popup-content">
        <div class="popup-header">
          <span class="popup-title">新增维修工具领用</span>
          <van-icon name="cross" @click="showIssuePopup = false" />
        </div>
        
        <div class="popup-body">
          <div class="section-title">选择工具</div>
          <div class="tool-list">
            <div 
              v-for="item in filteredToolList" 
              :key="item.id"
              class="tool-item"
              :class="{ selected: selectedTool?.id === item.id }"
              @click="handleSelectTool(item)"
            >
              <div class="tool-name">{{ item.tool_name }}</div>
              <div class="tool-info">
                <span v-if="item.tool_id">{{ item.tool_id }}</span>
                <span v-if="item.specification">{{ item.specification }}</span>
                <span class="tool-stock">库存: {{ item.stock }}</span>
              </div>
            </div>
            <van-empty v-if="filteredToolList.length === 0" description="暂无库存" />
          </div>
          
          <div class="section-title">领用信息</div>
          <van-cell-group inset>
            <van-field 
              :model-value="selectedTool?.tool_name || ''"
              label="工具名称"
              placeholder="请选择工具"
              readonly
              required
            />
            <van-field 
              :model-value="selectedTool?.tool_id || ''"
              label="工具编号"
              readonly
            />
            <van-field 
              :model-value="selectedTool?.specification || ''"
              label="规格型号"
              readonly
            />
            <van-field 
              :model-value="selectedTool?.stock || 0"
              label="库存数量"
              readonly
            />
            <van-field label="领用数量" required>
              <template #input>
                <van-stepper 
                  v-model="issueForm.quantity" 
                  :min="1" 
                  :max="maxQuantity"
                  theme="round"
                  button-size="22"
                />
              </template>
            </van-field>
            <van-field 
              v-model="issueForm.projectName"
              label="所属项目"
              placeholder="请选择项目"
              required
            >
              <template #input>
                <select v-model="issueForm.projectId" class="project-select" @change="() => {
                  const project = projectList.find(p => p.project_id === issueForm.projectId)
                  issueForm.projectName = project ? project.project_name : ''
                }">
                  <option value="">请选择项目</option>
                  <option v-for="project in projectList" :key="project.project_id" :value="project.project_id">
                    {{ project.project_name }}
                  </option>
                </select>
              </template>
            </van-field>
            <van-field 
              v-model="issueForm.remark"
              label="备注"
              placeholder="请输入备注"
              type="textarea"
              rows="2"
            />
          </van-cell-group>
        </div>
        
        <div class="popup-footer">
          <van-button type="primary" block :loading="loading" @click="handleSubmitIssue">
            确认领用
          </van-button>
        </div>
      </div>
    </van-popup>
  </div>
</template>

<style scoped>
.repair-tools-issue-page {
  min-height: 100vh;
  background-color: #f5f7fa;
}

.action-bar {
  padding: 12px 16px;
  background: #fff;
  border-bottom: 1px solid #ebedf0;
}

.issue-list {
  padding: 12px;
}

.issue-card {
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
}

.tool-name {
  font-weight: 600;
  color: #323233;
}

.status-badge {
  padding: 4px 12px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 500;
}

.status-issued {
  background: #fff3e0;
  color: #e65100;
}

.status-returned {
  background: #e8f5e9;
  color: #2e7d32;
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

.nav-left {
  display: flex;
  align-items: center;
  gap: 4px;
  color: #323233;
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
  border-bottom: 1px solid #ebedf0;
  flex-shrink: 0;
}

.popup-title {
  font-size: 16px;
  font-weight: 500;
}

.popup-body {
  flex: 1;
  overflow-y: auto;
}

.section-title {
  padding: 12px 16px 8px;
  font-size: 14px;
  font-weight: 500;
  color: #323233;
  background: #f7f8fa;
}

.tool-list {
  max-height: 250px;
  overflow-y: auto;
  padding: 0 12px;
  background: #fff;
}

.tool-item {
  padding: 12px;
  border-bottom: 1px solid #ebedf0;
  cursor: pointer;
}

.tool-item.selected {
  background: #e8f4ff;
  border-left: 3px solid #1989fa;
}

.tool-item:last-child {
  border-bottom: none;
}

.tool-item .tool-name {
  font-weight: 500;
  color: #323233;
  margin-bottom: 4px;
}

.tool-info {
  font-size: 12px;
  color: #969799;
  display: flex;
  gap: 8px;
}

.tool-stock {
  color: #1989fa;
  font-weight: 500;
}

.popup-footer {
  padding: 16px;
  flex-shrink: 0;
  border-top: 1px solid #ebedf0;
}

.project-select {
  width: 100%;
  padding: 8px 0;
  border: none;
  font-size: 14px;
  background: transparent;
}

:deep(.van-pull-refresh) {
  min-height: calc(100vh - 92px);
}

:deep(.van-cell-group--inset) {
  margin: 12px;
}
</style>
