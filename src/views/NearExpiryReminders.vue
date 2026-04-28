﻿﻿﻿﻿﻿﻿﻿﻿﻿﻿﻿﻿﻿﻿<template>
  <div class="near-expiry-page">
    <LoadingSpinner
      :visible="loading"
      text="加载中..."
    />
    <Toast
      :visible="toast.visible"
      :message="toast.message"
      :type="toast.type"
    />

    <div class="search-section">
      <div class="search-form">
        <div class="search-row">
          <div class="search-item">
            <label for="search_projectName" class="search-label">项目名称：</label>
            <SearchInput
              input-id="search_projectName"
              v-model="searchForm.projectName"
              field-key="NearExpiryReminders_projectName"
              placeholder="请输入项目名称"
              @input="handleSearch"
            />
          </div>
          <div class="search-item">
            <label for="search_clientName" class="search-label">客户名称：</label>
            <SearchInput
              input-id="search_clientName"
              v-model="searchForm.clientName"
              field-key="NearExpiryReminders_clientName"
              placeholder="请输入客户名称"
              @input="handleSearch"
            />
          </div>
        </div>
      </div>
    </div>

    <div class="table-section">
      <table class="data-table">
        <thead>
          <tr>
            <th>序号</th>
            <th>工单编号</th>
            <th>项目编号</th>
            <th>项目名称</th>
            <th>工单类型</th>
            <th>计划开始日期</th>
            <th class="th-days-warning">
              距今日数
            </th>
            <th>运维人员</th>
            <th>操作</th>
          </tr>
        </thead>
        <tbody>
          <tr v-if="filteredData.length === 0">
            <td
              colspan="9"
              class="empty-cell"
            >
              暂无数据
            </td>
          </tr>
          <tr
            v-for="(item, index) in paginatedData"
            :key="item.id + '-' + item.workOrderType"
            :class="{ 'even-row': index % 2 === 0 }"
          >
            <td>{{ startIndex + index + 1 }}</td>
            <td>{{ item.workOrderId }}</td>
            <td>{{ item.projectId }}</td>
            <td>{{ item.projectName }}</td>
            <td>{{ item.workOrderType }}</td>
            <td>{{ formatDate(item.planStartDate) }}</td>
            <td :class="getDaysClass(item.daysFromToday)">
              {{ item.daysFromToday }} 天
            </td>
            <td>{{ item.executor || '-' }}</td>
            <td class="action-cell">
              <a
                href="#"
                class="action-link action-view"
                @click.prevent="handleView(item)"
              >查看</a>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <div class="pagination-section">
      <div class="pagination-info">
        共 {{ totalElements }} 条记录
      </div>
      <div class="pagination-controls">
        <button
          class="page-btn page-nav"
          :disabled="currentPage === 0"
          @click="currentPage--"
        >
          &lt;
        </button>
        <button
          v-for="page in displayedPages"
          :key="page"
          class="page-btn page-num"
          :class="{ active: page === currentPage + 1 }"
          @click="currentPage = page - 1"
        >
          {{ page }}
        </button>
        <button
          class="page-btn page-nav"
          :disabled="currentPage >= totalPages - 1"
          @click="currentPage++"
        >
          &gt;
        </button>
        <select
          id="pageSize"
          name="pageSize"
          v-model="pageSize"
          class="page-select"
          @change="handlePageSizeChange"
        >
          <option value="10">
            10 条 / 页
          </option>
          <option value="20">
            20 条 / 页
          </option>
          <option value="50">
            50 条 / 页
          </option>
        </select>
        <div class="page-jump">
          <span>跳至</span>
          <input
            id="jumpPage"
            v-model="jumpPage"
            name="jumpPage"
            type="number"
            class="page-input"
            min="1"
            :max="totalPages"
            aria-label="跳转页码"
          >
          <span>页</span>
          <button
            class="page-btn page-go"
            @click="handleJump"
          >
            Go
          </button>
        </div>
      </div>
    </div>

    <div
      v-if="isViewModalOpen"
      class="modal-overlay"
      @click.self="closeViewModal"
    >
      <div class="modal-container">
        <div class="modal-header">
          <h3 class="modal-title">
            查看临期提醒
          </h3>
          <button
            class="modal-close"
            @click="closeViewModal"
          >
            ×
          </button>
        </div>
        <div class="modal-body">
          <div class="form-grid">
            <div class="form-column">
              <div class="form-item">
                <span class="form-label">工单编号</span>
                <div class="form-value">
                  {{ viewData.workOrderId || '-' }}
                </div>
              </div>
              <div class="form-item">
                <span class="form-label">项目编号</span>
                <div class="form-value">
                  {{ viewData.projectId || '-' }}
                </div>
              </div>
              <div class="form-item">
                <span class="form-label">项目名称</span>
                <div class="form-value">
                  {{ viewData.projectName || '-' }}
                </div>
              </div>
              <div class="form-item">
                <span class="form-label">工单类型</span>
                <div class="form-value">
                  {{ viewData.workOrderType || '-' }}
                </div>
              </div>
              <div class="form-item">
                <span class="form-label">客户单位</span>
                <div class="form-value">
                  {{ viewData.clientName || '-' }}
                </div>
              </div>
              <div class="form-item">
                <span class="form-label">客户联系人</span>
                <div class="form-value">
                  {{ viewData.clientContact || '-' }}
                </div>
              </div>
              <div class="form-item">
                <span class="form-label">联系人职位</span>
                <div class="form-value">
                  {{ viewData.clientContactPosition || '-' }}
                </div>
              </div>
            </div>
            <div class="form-column">
              <div class="form-item">
                <span class="form-label">计划开始日期</span>
                <div class="form-value">
                  {{ formatDate(viewData.planStartDate) || '-' }}
                </div>
              </div>
              <div class="form-item">
                <span class="form-label">运维人员</span>
                <div class="form-value">
                  {{ viewData.executor || '-' }}
                </div>
              </div>
              <div class="form-item">
                <span class="form-label">客户联系方式</span>
                <div class="form-value">
                  {{ viewData.clientContactInfo || '-' }}
                </div>
              </div>
              <div class="form-item">
                <span class="form-label">客户地址</span>
                <div class="form-value">
                  {{ viewData.address || '-' }}
                </div>
              </div>
              <div class="form-item">
                <span class="form-label">距今日数</span>
                <div class="form-value days-warning">
                  {{ viewData.daysFromToday }} 天
                </div>
              </div>
              <div class="form-item">
                <span class="form-label">合同剩余时间</span>
                <div
                  class="form-value"
                  :class="getRemainingTimeClass()"
                >
                  {{ viewData.remainingTime || '-' }}
                </div>
              </div>
              <div class="form-item">
                <span class="form-label">状态</span>
                <div
                  class="form-value"
                  :class="getStatusClass(viewData.status)"
                >
                  {{ viewData.status || '-' }}
                </div>
              </div>
            </div>
          </div>
        </div>
        <div class="modal-footer">
          <button
            class="btn btn-cancel"
            @click="closeViewModal"
          >
            关闭
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script lang="ts">
import { defineComponent, ref, reactive, computed, onMounted, onUnmounted } from 'vue'
import { request } from '@/api/request'
import { projectInfoService, type ProjectInfo } from '../services/projectInfo'
import { userStore } from '../stores/userStore'
import { LoadingSpinner, Toast, SearchInput } from '@sstcp/shared'
import { USER_ROLES, WORK_STATUS } from '../config/constants'
import type { ApiResponse as ApiResponseType } from '../types/api'

interface NearExpiryItem {
  id: number
  workOrderId: string
  projectId: string
  projectName: string
  workOrderType: string
  planStartDate: string
  daysFromToday: number
  executor: string
}

export default defineComponent({
  name: 'NearExpiryReminders',
  components: {
    LoadingSpinner,
    Toast,
    SearchInput,
  },
  setup() {
    const loading = ref(false)
    const isViewModalOpen = ref(false)
    const searchForm = reactive({
      projectName: '',
      clientName: '',
    })

    const currentPage = ref(0)
    const pageSize = ref(10)
    const jumpPage = ref(1)
    const allData = ref<NearExpiryItem[]>([])

    const toast = reactive({
      visible: false,
      message: '',
      type: 'success' as 'success' | 'error' | 'warning' | 'info',
    })

    const viewData = reactive({
      id: 0,
      workOrderId: '',
      projectId: '',
      projectName: '',
      workOrderType: '',
      planStartDate: '',
      planEndDate: '',
      clientName: '',
      clientContact: '',
      clientContactInfo: '',
      clientContactPosition: '',
      address: '',
      executor: '',
      status: '',
      daysFromToday: 0,
      remainingTime: '',
    })

    const showToast = (
      message: string,
      type: 'success' | 'error' | 'warning' | 'info' = 'success'
    ) => {
      toast.message = message
      toast.type = type
      toast.visible = true
    }

    const formatDate = (dateStr: string) => {
      if (!dateStr) return '-'
      const date = new Date(dateStr)
      return date.toLocaleDateString('zh-CN', {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
      })
    }

    const getDaysClass = (_days: number): string => {
      return 'days-warning'
    }

    const loadData = async () => {
      loading.value = true
      try {
        const response = await request.get<{ items: any[]; total: number }>(
          '/expiring-soon',
          { params: { page: 0, size: 1000 } }
        )

        const items: NearExpiryItem[] = []

        if (response.code === 200 && response.data?.items) {
          response.data.items.forEach((item: any) => {
            items.push({
              id: parseInt(item.id),
              workOrderId: item.workOrderNo,
              projectId: item.project_id,
              projectName: item.projectName,
              workOrderType: item.workOrderType,
              planStartDate: item.planStartDate,
              daysFromToday: item.daysRemaining,
              executor: item.executor,
            })
          })
        }

        allData.value = items.sort((a, b) => a.daysFromToday - b.daysFromToday)
      } catch (error: any) {
        console.error('加载数据失败:', error)
        showToast(error.message || '加载数据失败，请检查网络连接', 'error')
      } finally {
        loading.value = false
      }
    }

    const filteredData = computed(() => {
      let result = allData.value

      const user = userStore.getUser()
      if (user && user.role === USER_ROLES.EMPLOYEE) {
        result = result.filter((item) => item.executor === user.name)
      }

      if (searchForm.projectName) {
        result = result.filter((item) =>
          item.projectName.toLowerCase().includes(searchForm.projectName.toLowerCase())
        )
      }

      if (searchForm.clientName) {
        result = result.filter((item) =>
          item.projectId.toLowerCase().includes(searchForm.clientName.toLowerCase())
        )
      }

      return result
    })

    const totalElements = computed(() => filteredData.value.length)

    const totalPages = computed(() => Math.ceil(totalElements.value / pageSize.value) || 1)

    const startIndex = computed(() => currentPage.value * pageSize.value)

    const paginatedData = computed(() => {
      const start = startIndex.value
      const end = start + pageSize.value
      return filteredData.value.slice(start, end)
    })

    const displayedPages = computed(() => {
      const pages: number[] = []
      const start = Math.max(1, currentPage.value - 1)
      const end = Math.min(totalPages.value, currentPage.value + 3)
      for (let i = start; i <= end; i++) {
        pages.push(i)
      }
      return pages
    })

    const handleSearch = () => {
      currentPage.value = 0
    }

    const handleReset = () => {
      searchForm.projectName = ''
      searchForm.clientName = ''
      currentPage.value = 0
    }

    const handlePageSizeChange = () => {
      currentPage.value = 0
    }

    const handleJump = () => {
      const page = jumpPage.value
      if (page >= 1 && page <= totalPages.value) {
        currentPage.value = page - 1
      }
    }

    const handleView = async (item: NearExpiryItem) => {
      viewData.id = item.id
      viewData.workOrderId = item.workOrderId
      viewData.projectId = item.projectId
      viewData.projectName = item.projectName
      viewData.workOrderType = item.workOrderType
      viewData.planStartDate = item.planStartDate
      viewData.planEndDate = ''
      viewData.clientName = ''
      viewData.clientContact = ''
      viewData.clientContactInfo = ''
      viewData.clientContactPosition = ''
      viewData.address = ''
      viewData.executor = item.executor || ''
      viewData.status = WORK_STATUS.IN_PROGRESS
      viewData.daysFromToday = item.daysFromToday
      viewData.remainingTime = '-'

      try {
        const projectResponse = await projectInfoService.getAll()
        if (projectResponse.code === 200 && projectResponse.data) {
          const project = projectResponse.data.find(
            (p: ProjectInfo) => p.project_id === item.projectId
          )
          if (project) {
            viewData.projectName = project.project_name || viewData.projectName
            viewData.clientName = project.client_name || ''
            viewData.clientContact = project.client_contact || ''
            viewData.clientContactInfo = project.client_contact_info || ''
            viewData.clientContactPosition = project.client_contact_position || ''
            viewData.address = project.address || ''
            viewData.remainingTime = calculateRemainingTime(project.maintenance_end_date)
          }
        }
      } catch (error) {
        console.error('获取项目信息失败:', error)
      }

      isViewModalOpen.value = true
    }

    const closeViewModal = () => {
      isViewModalOpen.value = false
    }

    const calculateRemainingTime = (endDate: string): string => {
      if (!endDate) return '-'

      const today = new Date()
      today.setHours(0, 0, 0, 0)

      const end = new Date(endDate)
      end.setHours(0, 0, 0, 0)

      const diffTime = end.getTime() - today.getTime()

      if (diffTime < 0) {
        return '已过期'
      }

      const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24))

      const years = Math.floor(diffDays / 365)
      const months = Math.floor((diffDays % 365) / 30)
      const days = diffDays % 30

      const parts: string[] = []
      if (years > 0) parts.push(`${years}年`)
      if (months > 0) parts.push(`${months}月`)
      if (days > 0 || parts.length === 0) parts.push(`${days}日`)

      return parts.join('')
    }

    const getRemainingTimeClass = () => {
      if (!viewData.remainingTime) return ''
      if (viewData.remainingTime === '已过期') return 'remaining-expired'
      return 'remaining-normal'
    }

    const getStatusClass = (status: string) => {
      if (status === '执行中') {
        return 'status-pending'
      }
      if (status === '待确认') {
        return 'status-confirmed'
      }
      if (status === '已完成') {
        return 'status-completed'
      }
      if (status === '已退回') {
        return 'status-returned'
      }
      return ''
    }

    const formatDateTime = (dateStr: string) => {
      if (!dateStr) return '-'
      const date = new Date(dateStr)
      return date.toLocaleString('zh-CN', {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit',
      })
    }

    const handleUserChanged = () => {
      loadData()
    }

    onMounted(() => {
      loadData()
      window.addEventListener('user-changed', handleUserChanged)
    })

    onUnmounted(() => {
      window.removeEventListener('user-changed', handleUserChanged)
    })

    return {
      loading,
      currentUser: userStore.readonlyCurrentUser,
      searchForm,
      currentPage,
      pageSize,
      jumpPage,
      filteredData,
      paginatedData,
      totalElements,
      totalPages,
      startIndex,
      displayedPages,
      toast,
      isViewModalOpen,
      viewData,
      formatDate,
      formatDateTime,
      getDaysClass,
      getRemainingTimeClass,
      getStatusClass,
      handleSearch,
      handleReset,
      handlePageSizeChange,
      handleJump,
      handleView,
      closeViewModal,
    }
  },
})
</script>

<style scoped>
.near-expiry-page {
  background: var(--color-bg-card);
  border-radius: 4px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  padding: 20px;
  position: relative;
}

.search-section {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding: 20px;
  background: var(--color-bg-page);
  border-radius: 4px;
}

.search-form {
  display: flex;
  flex-direction: column;
  gap: 16px;
  align-items: flex-start;
  flex-wrap: wrap;
}

.search-row {
  display: flex;
  gap: 16px;
  align-items: center;
  flex-wrap: wrap;
}

.search-item {
  display: flex;
  align-items: center;
  gap: 8px;
}

.search-label {
  font-size: 14px;
  font-weight: 500;
  color: var(--color-text-regular);
  white-space: nowrap;
}

.search-input,
.search-select {
  width: 200px;
  padding: 8px 12px;
  border: 1px solid var(--color-border);
  border-radius: 3px;
  font-size: 14px;
  color: var(--color-text-primary);
  background: var(--color-bg-card);
  transition: border-color 0.15s;
}

.search-input:focus,
.search-select:focus {
  outline: none;
  border-color: var(--color-primary);
  box-shadow: 0 0 0 2px rgba(25, 118, 210, 0.1);
}

.search-input::placeholder {
  color: var(--color-text-placeholder);
}

.search-actions {
  display: flex;
  flex-wrap: nowrap;
  gap: 10px;
  overflow-x: auto;
  white-space: nowrap;
  min-width: max-content;
  align-items: center;
}

.btn {
  padding: 8px 16px;
  border: none;
  border-radius: 3px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.15s;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.1);
}

.btn-search {
  background: var(--color-primary);
  color: var(--color-bg-card);
}

.btn-search:hover {
  background: var(--color-primary);
}

.btn-reset {
  background: var(--color-bg-card);
  color: var(--color-text-secondary);
  border: 1px solid var(--color-border);
}

.btn-reset:hover {
  background: var(--color-bg-page);
}

.table-section {
  margin-bottom: 20px;
  border: 1px solid var(--color-border);
  border-radius: 4px;
  overflow-x: auto;
}

.data-table {
  width: 100%;
  border-collapse: collapse;
  min-width: 1200px;
}

.data-table thead {
  background: var(--color-border);
}

.data-table th {
  padding: 12px 16px;
  text-align: left;
  font-size: 14px;
  font-weight: 600;
  color: var(--color-text-primary);
  border-bottom: 1px solid var(--color-border);
  white-space: nowrap;
}

.data-table .th-days-warning {
  color: var(--color-warning);
}

.data-table td {
  padding: 12px 16px;
  text-align: left;
  font-size: 14px;
  color: var(--color-text-regular);
  border-bottom: 1px solid var(--color-border-light);
}

.data-table tbody tr:hover {
  background: var(--color-bg-page);
}

.even-row {
  background: var(--color-bg-page);
}

.data-table .empty-cell {
  text-align: center;
  color: var(--color-text-placeholder);
  padding: 40px;
}

.days-critical {
  color: var(--color-danger);
  font-weight: 600;
}

.data-table .days-warning {
  color: var(--color-warning);
  font-weight: 600;
}

.days-normal {
  color: var(--color-success);
}

.action-cell {
  display: flex;
  flex-wrap: nowrap;
  gap: 16px;
  overflow-x: auto;
  white-space: nowrap;
  min-width: max-content;
  align-items: center;
}

.action-link {
  font-size: 14px;
  text-decoration: none;
  transition: opacity 0.15s;
}

.action-link:hover {
  opacity: 0.8;
}

.action-view {
  color: var(--color-success);
}

.pagination-section {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 0;
}

.pagination-info {
  font-size: 14px;
  color: var(--color-text-secondary);
}

.pagination-controls {
  display: flex;
  flex-wrap: nowrap;
  align-items: center;
  gap: 8px;
  overflow-x: auto;
  white-space: nowrap;
  min-width: max-content;
}

.page-btn {
  min-width: 32px;
  height: 32px;
  padding: 0 8px;
  border: 1px solid var(--color-border);
  border-radius: 3px;
  background: var(--color-bg-card);
  font-size: 14px;
  color: var(--color-text-primary);
  cursor: pointer;
  transition: all 0.15s;
  display: flex;
  align-items: center;
  justify-content: center;
}

.page-btn:hover:not(:disabled) {
  border-color: var(--color-primary);
  color: var(--color-primary);
}

.page-btn:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}

.page-btn.active {
  background: var(--color-primary);
  color: var(--color-bg-card);
  border-color: var(--color-primary);
}

.page-nav {
  font-size: 16px;
}

.page-select {
  padding: 6px 12px;
  border: 1px solid var(--color-border);
  border-radius: 3px;
  font-size: 14px;
  color: var(--color-text-primary);
  background: var(--color-bg-card);
  cursor: pointer;
}

.page-jump {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
  color: var(--color-text-secondary);
}

.page-input {
  width: 48px;
  padding: 6px 8px;
  border: 1px solid var(--color-border);
  border-radius: 3px;
  font-size: 14px;
  color: var(--color-text-primary);
  text-align: center;
  background: var(--color-bg-card);
}

.page-input:focus {
  outline: none;
  border-color: var(--color-primary);
}

.page-go {
  min-width: 40px;
  height: 28px;
  padding: 0 8px;
  background: var(--color-primary);
  color: var(--color-bg-card);
  border: none;
  border-radius: 3px;
  font-size: 12px;
  cursor: pointer;
  transition: background 0.15s;
}

.page-go:hover {
  background: var(--color-primary);
}

.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal-container {
  background: var(--color-bg-card);
  border-radius: 8px;
  width: 800px;
  max-width: 95vw;
  max-height: 90vh;
  overflow-y: auto;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px 24px;
  border-bottom: 1px solid var(--color-border);
}

.modal-title {
  font-size: 18px;
  font-weight: 600;
  color: var(--color-text-primary);
  margin: 0;
}

.modal-close {
  width: 32px;
  height: 32px;
  border: none;
  background: none;
  font-size: 24px;
  color: var(--color-text-placeholder);
  cursor: pointer;
  transition: color 0.15s;
  display: flex;
  align-items: center;
  justify-content: center;
}

.modal-close:hover {
  color: var(--color-text-primary);
}

.modal-body {
  padding: 24px;
}

.form-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 24px 40px;
  align-items: start;
}

.form-column {
  display: flex;
  flex-direction: column;
}

.form-item {
  display: flex;
  flex-direction: column;
  gap: 8px;
  min-height: 70px;
  padding: 4px 0;
}

.form-label {
  font-size: 14px;
  font-weight: 500;
  color: var(--color-text-regular);
}

.form-value {
  padding: 8px 12px;
  background: var(--color-bg-page);
  border: 1px solid var(--color-border);
  border-radius: 3px;
  font-size: 14px;
  color: var(--color-text-primary);
  min-height: 36px;
  display: flex;
  align-items: center;
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  padding: 20px 24px;
  border-top: 1px solid var(--color-border);
}

.btn-cancel {
  background: var(--color-bg-card);
  color: var(--color-text-secondary);
  border: 1px solid var(--color-border);
}

.btn-cancel:hover {
  background: var(--color-bg-page);
}

.remaining-normal {
  color: var(--color-success);
  font-weight: 500;
}

.remaining-expired {
  color: var(--color-danger);
  font-weight: 600;
}

.status-pending {
  color: var(--color-warning);
}

.status-confirmed {
  color: var(--color-success);
}

.status-in-progress {
  color: var(--color-success);
}

.status-completed {
  color: var(--color-success);
}

.status-cancelled {
  color: var(--color-danger);
}
</style>
