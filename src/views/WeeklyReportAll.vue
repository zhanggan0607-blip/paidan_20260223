<template>
  <div class="weekly-report-all-container">
    <div class="main-layout">
      <div class="content-area">
        <div class="content-wrapper">
          <div class="filter-section">
            <div class="search-form">
              <div class="search-row">
                <div class="search-item">
                  <label class="search-label">项目名称：</label>
                  <SearchInput
                    v-model="filters.project"
                    field-key="WeeklyReportAll_project"
                    placeholder="请输入项目名称"
                    @input="handleSearch"
                  />
                </div>
                <div class="search-item">
                  <label class="search-label">提交人：</label>
                  <SearchInput
                    v-model="filters.createdBy"
                    field-key="WeeklyReportAll_created_by"
                    placeholder="请输入提交人"
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
                  <th>项目名称</th>
                  <th>日志类型</th>
                  <th>工作内容</th>
                  <th>提交人</th>
                  <th>提交时间</th>
                  <th>操作</th>
                </tr>
              </thead>
              <tbody>
                <tr v-if="loading">
                  <td colspan="7" class="loading-cell">
                    <div class="loading-spinner"></div>
                    <span>加载中...</span>
                  </td>
                </tr>
                <tr v-else-if="dataList.length === 0">
                  <td colspan="7" class="empty-cell">暂无数据</td>
                </tr>
                <tr v-else v-for="(item, index) in dataList" :key="item.id">
                  <td>{{ (currentPage - 1) * pageSize + index + 1 }}</td>
                  <td>{{ item.project_name }}</td>
                  <td>
                    <span class="log-type-tag weekly">部门周报</span>
                  </td>
                  <td class="content-cell">
                    <span class="content-text" :title="item.work_summary">
                      {{ truncateContent(item.work_summary) }}
                    </span>
                  </td>
                  <td>{{ item.created_by || '-' }}</td>
                  <td>{{ formatDateTime(item.created_at) }}</td>
                  <td class="action-cell">
                    <button class="action-btn view-btn" @click="handleView(item)">查看</button>
                    <button 
                      v-if="!item.status || item.status === 'submitted'" 
                      class="action-btn reject-btn" 
                      @click="handleApprove(item, false)"
                    >退回</button>
                  </td>
                </tr>
              </tbody>
            </table>

            <div class="pagination-section">
              <div class="pagination-info">
                共 {{ total }} 条记录，第 {{ currentPage }} / {{ totalPages }} 页
              </div>
              <div class="pagination-controls">
                <button 
                  @click="handlePageChange(currentPage - 1)" 
                  :disabled="currentPage === 1"
                  class="pagination-button"
                >
                  上一页
                </button>
                <span class="pagination-pages">
                  <input 
                    v-model.number="currentPage" 
                    type="number" 
                    :min="1" 
                    :max="totalPages"
                    class="pagination-input"
                  />
                  <span class="pagination-slash">/</span>
                  <span>{{ totalPages }}</span>
                </span>
                <button 
                  @click="handlePageChange(currentPage + 1)" 
                  :disabled="currentPage === totalPages"
                  class="pagination-button"
                >
                  下一页
                </button>
              </div>
              <div class="page-size-selector">
                <span>每页</span>
                <select v-model="pageSize" @change="handlePageSizeChange" class="page-size-select">
                  <option :value="10">10</option>
                  <option :value="20">20</option>
                  <option :value="50">50</option>
                  <option :value="100">100</option>
                </select>
                <span>条</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <div v-if="showDetailModal" class="modal-overlay" @click.self="closeDetailModal">
      <div class="modal-content modal-content-large">
        <div class="modal-header">
          <h3>部门周报详情</h3>
          <button class="close-btn" @click="closeDetailModal">&times;</button>
        </div>
        <div class="modal-body" v-if="detailData">
          <div class="detail-section">
            <div class="detail-row">
              <div class="detail-column">
                <div class="detail-item">
                  <label class="detail-label">项目名称</label>
                  <div class="detail-value">{{ detailData.project_name }}</div>
                </div>
                <div class="detail-item">
                  <label class="detail-label">提交人</label>
                  <div class="detail-value">{{ detailData.created_by || '-' }}</div>
                </div>
                <div class="detail-item">
                  <label class="detail-label">日志类型</label>
                  <div class="detail-value">部门周报</div>
                </div>
              </div>
              <div class="detail-column">
                <div class="detail-item">
                  <label class="detail-label">项目编号</label>
                  <div class="detail-value">{{ detailData.project_id }}</div>
                </div>
                <div class="detail-item">
                  <label class="detail-label">提交时间</label>
                  <div class="detail-value">{{ formatDateTime(detailData.created_at) }}</div>
                </div>
              </div>
            </div>
            <div class="detail-row full-width">
              <div class="detail-item">
                <label class="detail-label">工作内容</label>
                <div class="detail-value content-full">{{ detailData.work_summary || '-' }}</div>
              </div>
            </div>
            <div class="detail-row full-width" v-if="parseImages(detailData.images).length > 0">
              <div class="detail-item">
                <label class="detail-label">现场照片</label>
                <div class="detail-images">
                  <img 
                    v-for="(img, index) in parseImages(detailData.images)" 
                    :key="index" 
                    :src="img" 
                    alt="现场照片"
                    class="detail-image"
                    loading="lazy"
                    @click="previewImage(img)"
                  />
                </div>
              </div>
            </div>
          </div>

          <div class="operation-log-section" v-if="weeklyReportOperationLogs.length > 0">
            <div class="section-title">内部确认区</div>
            <div class="timeline">
              <div 
                v-for="(log, index) in weeklyReportOperationLogs" 
                :key="log.id" 
                class="timeline-item"
                :class="{ 'last': index === weeklyReportOperationLogs.length - 1 }"
              >
                <div class="timeline-dot"></div>
                <div class="timeline-content">
                  <span class="timeline-time">{{ formatOperationTime(log.created_at) }}</span>
                  <span class="timeline-operator">{{ log.operator_name }}</span>
                  <span class="timeline-action">{{ log.operation_type_name }}</span>
                </div>
              </div>
            </div>
          </div>
        </div>
        <div class="modal-footer">
          <button class="cancel-btn" @click="closeDetailModal">关闭</button>
        </div>
      </div>
    </div>

    <div v-if="showImagePreview" class="image-preview-overlay" @click="closeImagePreview">
      <img :src="previewImageUrl" alt="预览图片" class="preview-image" loading="lazy" />
    </div>

    <div v-if="showRejectModal" class="modal-overlay" @click.self="closeRejectModal">
      <div class="modal-content">
        <div class="modal-header">
          <h3>退回部门周报</h3>
          <button class="close-btn" @click="closeRejectModal">&times;</button>
        </div>
        <div class="modal-body">
          <div class="form-item">
            <label class="form-label">退回原因</label>
            <textarea 
              v-model="rejectReason" 
              class="form-textarea" 
              placeholder="请输入退回原因"
              rows="3"
            ></textarea>
          </div>
        </div>
        <div class="modal-footer">
          <button class="cancel-btn" @click="closeRejectModal">取消</button>
          <button class="confirm-btn" @click="confirmReject" :disabled="submitting">
            {{ submitting ? '处理中...' : '确认退回' }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script lang="ts">
import { defineComponent, ref, computed, onMounted, onUnmounted } from 'vue'
import apiClient from '@/utils/api'
import type { ApiResponse, PaginatedResponse } from '@/types/api'
import { authService } from '@/services/auth'
import { formatDate, formatDateTime } from '@/config/constants'
import { USER_ROLES } from '@/config/constants'
import SearchInput from '@/components/SearchInput.vue'

interface WeeklyReportItem {
  id: number
  report_id: string
  project_id: string
  project_name: string
  week_start_date: string
  week_end_date: string
  report_date: string
  work_summary: string
  work_content: string
  next_week_plan: string
  issues: string
  suggestions: string
  images: string
  manager_signature: string
  status: string
  approved_by: string
  approved_at: string
  reject_reason: string
  created_by: string
  created_at: string
  updated_at: string
}

interface ProjectInfo {
  id: number
  project_id: string
  project_name: string
}

interface User {
  id: number
  name: string
  role: string
}

interface OperationLogItem {
  id: number
  work_order_type: string
  work_order_id: number
  work_order_no: string
  operator_name: string
  operator_id: number | null
  operation_type_code: string
  operation_type_name: string
  operation_remark: string | null
  created_at: string
}

export default defineComponent({
  name: 'WeeklyReportAll',
  components: {
    SearchInput
  },
  setup() {
    const loading = ref(false)
    const submitting = ref(false)
    const dataList = ref<WeeklyReportItem[]>([])
    const total = ref(0)
    const currentPage = ref(1)
    const pageSize = ref(10)
    const projectList = ref<ProjectInfo[]>([])
    const userList = ref<User[]>([])
    const currentUser = ref(authService.getCurrentUser())
    const showDetailModal = ref(false)
    const detailData = ref<WeeklyReportItem | null>(null)
    const showImagePreview = ref(false)
    const previewImageUrl = ref('')
    const showRejectModal = ref(false)
    const rejectReason = ref('')
    const pendingRejectItem = ref<WeeklyReportItem | null>(null)
    const weeklyReportOperationLogs = ref<OperationLogItem[]>([])

    const filters = ref({
      project: '',
      createdBy: ''
    })

    const totalPages = computed(() => {
      return Math.ceil(total.value / pageSize.value) || 1
    })

    /**
     * 格式化操作时间
     */
    const formatOperationTime = (dateStr: string) => {
      if (!dateStr) return '-'
      const date = new Date(dateStr)
      const year = date.getFullYear()
      const month = String(date.getMonth() + 1).padStart(2, '0')
      const day = String(date.getDate()).padStart(2, '0')
      const hours = String(date.getHours()).padStart(2, '0')
      const minutes = String(date.getMinutes()).padStart(2, '0')
      return `${year}-${month}-${day} ${hours}:${minutes}`
    }

    /**
     * 获取状态名称
     */
    const getStatusName = (status: string) => {
      const statusMap: Record<string, string> = {
        'draft': '草稿',
        'submitted': '已提交',
        'approved': '已审核',
        'rejected': '已退回'
      }
      return statusMap[status] || status
    }

    /**
     * 截断内容
     */
    const truncateContent = (content: string) => {
      if (!content) return '-'
      if (content.length > 30) {
        return content.substring(0, 30) + '...'
      }
      return content
    }

    /**
     * 解析图片URL列表
     */
    const parseImages = (images: string): string[] => {
      if (!images) return []
      try {
        const parsed = JSON.parse(images)
        return Array.isArray(parsed) ? parsed : []
      } catch {
        return images.split(',').filter((url: string) => url.trim())
      }
    }

    /**
     * 获取项目列表
     */
    const fetchProjectList = async () => {
      try {
        const response = await apiClient.get('/project-info/all/list') as unknown as ApiResponse<ProjectInfo[]>
        if (response.code === 200) {
          projectList.value = response.data || []
        }
      } catch (error) {
        console.error('Failed to fetch project list:', error)
      }
    }

    /**
     * 获取用户列表
     */
    const fetchUserList = async () => {
      try {
        const response = await apiClient.get('/personnel/all/list') as unknown as ApiResponse<User[]>
        if (response.code === 200 && response.data) {
          userList.value = (Array.isArray(response.data) ? response.data : []).filter(
            (user: User) => user && user.name && user.role === USER_ROLES.DEPARTMENT_MANAGER
          )
        }
      } catch (error) {
        console.error('Failed to fetch user list:', error)
      }
    }

    /**
     * 加载数据
     */
    const loadData = async () => {
      loading.value = true
      try {
        const params: Record<string, any> = {
          page: currentPage.value - 1,
          size: pageSize.value
        }
        if (filters.value.project) params.project_name = filters.value.project
        if (filters.value.createdBy) params.created_by = filters.value.createdBy

        const response = await apiClient.get('/weekly-report', { params }) as unknown as ApiResponse<PaginatedResponse<WeeklyReportItem>>
        
        if (response && response.code === 200 && response.data) {
          dataList.value = response.data.items || response.data.content || []
          total.value = response.data.total || response.data.totalElements || 0
        }
      } catch (error) {
        console.error('加载周报数据失败:', error)
      } finally {
        loading.value = false
      }
    }

    /**
     * 搜索
     */
    const handleSearch = () => {
      currentPage.value = 1
      loadData()
    }

    /**
     * 获取周报操作日志
     */
    const fetchWeeklyReportOperationLogs = async (reportId: number) => {
      try {
        const response = await apiClient.get(`/weekly-report/${reportId}/operation-logs`) as unknown as ApiResponse<OperationLogItem[]>
        if (response.code === 200) {
          weeklyReportOperationLogs.value = response.data || []
        }
      } catch (error) {
        console.error('获取操作日志失败:', error)
        weeklyReportOperationLogs.value = []
      }
    }

    /**
     * 查看详情
     */
    const handleView = async (item: WeeklyReportItem) => {
      detailData.value = item
      showDetailModal.value = true
      weeklyReportOperationLogs.value = []
      // 获取操作日志
      await fetchWeeklyReportOperationLogs(item.id)
    }

    /**
     * 关闭详情弹窗
     */
    const closeDetailModal = () => {
      showDetailModal.value = false
      detailData.value = null
    }

    /**
     * 审核
     */
    const handleApprove = async (item: WeeklyReportItem, approved: boolean) => {
      if (!approved) {
        pendingRejectItem.value = item
        rejectReason.value = ''
        showRejectModal.value = true
        return
      }

      if (!confirm('确定要通过该周报吗？')) {
        return
      }

      submitting.value = true
      try {
        const response = await apiClient.post(`/weekly-report/${item.id}/approve`, {
          approved: true
        }) as unknown as ApiResponse<null>
        
        if (response.code === 200) {
          alert('审核通过')
          loadData()
        } else {
          alert(response.message || '审核失败')
        }
      } catch (error) {
        console.error('Failed to approve:', error)
        alert('审核失败，请重试')
      } finally {
        submitting.value = false
      }
    }

    /**
     * 确认退回
     */
    const confirmReject = async () => {
      if (!rejectReason.value.trim()) {
        alert('请输入退回原因')
        return
      }

      if (!pendingRejectItem.value) return

      submitting.value = true
      try {
        const response = await apiClient.post(`/weekly-report/${pendingRejectItem.value.id}/approve`, {
          approved: false,
          reject_reason: rejectReason.value
        }) as unknown as ApiResponse<null>
        
        if (response.code === 200) {
          alert('已退回')
          closeRejectModal()
          loadData()
        } else {
          alert(response.message || '退回失败')
        }
      } catch (error) {
        console.error('Failed to reject:', error)
        alert('退回失败，请重试')
      } finally {
        submitting.value = false
      }
    }

    /**
     * 关闭退回弹窗
     */
    const closeRejectModal = () => {
      showRejectModal.value = false
      pendingRejectItem.value = null
      rejectReason.value = ''
    }

    /**
     * 预览图片
     */
    const previewImage = (url: string) => {
      previewImageUrl.value = url
      showImagePreview.value = true
    }

    /**
     * 关闭图片预览
     */
    const closeImagePreview = () => {
      showImagePreview.value = false
      previewImageUrl.value = ''
    }

    /**
     * 分页变更
     */
    const handlePageChange = (page: number) => {
      if (page < 1 || page > totalPages.value) return
      currentPage.value = page
      loadData()
    }

    /**
     * 每页数量变更
     */
    const handlePageSizeChange = () => {
      currentPage.value = 1
      loadData()
    }

    const handleUserChanged = () => {
      currentUser.value = authService.getCurrentUser()
      loadData()
    }

    onMounted(() => {
      fetchProjectList()
      fetchUserList()
      loadData()
      window.addEventListener('user-changed', handleUserChanged)
    })

    onUnmounted(() => {
      window.removeEventListener('user-changed', handleUserChanged)
    })

    return {
      loading,
      submitting,
      dataList,
      total,
      currentPage,
      pageSize,
      totalPages,
      filters,
      projectList,
      userList,
      currentUser,
      showDetailModal,
      detailData,
      showImagePreview,
      previewImageUrl,
      showRejectModal,
      rejectReason,
      weeklyReportOperationLogs,
      getStatusName,
      truncateContent,
      parseImages,
      formatDate,
      formatDateTime,
      formatOperationTime,
      handleSearch,
      handleView,
      closeDetailModal,
      handleApprove,
      confirmReject,
      closeRejectModal,
      previewImage,
      closeImagePreview,
      handlePageChange,
      handlePageSizeChange
    }
  }
})
</script>

<style scoped>
.weekly-report-all-container {
  min-height: 100vh;
  background: #f8f9fa;
}

.main-layout {
  display: flex;
  min-height: 100vh;
}

.content-area {
  flex: 1;
  display: flex;
  flex-direction: column;
  background: #f8f9fa;
}

.content-wrapper {
  display: flex;
  flex-direction: column;
  gap: 20px;
  padding: 20px;
  flex: 1;
  overflow-y: auto;
}

.filter-section {
  display: flex;
  gap: 16px;
  margin-bottom: 20px;
  align-items: flex-start;
  padding: 16px;
  background: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
}

.search-form {
  display: flex;
  flex-direction: column;
  gap: 16px;
  align-items: flex-start;
  flex: 1;
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
  color: #666;
  font-weight: 500;
  white-space: nowrap;
}

.filter-select,
.filter-input {
  padding: 8px 12px;
  border: 1px solid #e0e0e0;
  border-radius: 4px;
  font-size: 14px;
  min-width: 160px;
  transition: border-color 0.2s;
}

.filter-select:focus,
.filter-input:focus {
  outline: none;
  border-color: #1976d2;
  box-shadow: 0 0 0 3px rgba(25, 118, 210, 0.1);
}

.table-section {
  background: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
  overflow: hidden;
}

.data-table {
  width: 100%;
  border-collapse: collapse;
}

.data-table thead {
  background: #f5f7fa;
}

.data-table th {
  padding: 12px 16px;
  text-align: left;
  font-weight: 600;
  color: #333;
  border-bottom: 2px solid #e0e0e0;
  white-space: nowrap;
}

.data-table tbody tr {
  border-bottom: 1px solid #e0e0e0;
  transition: background 0.2s;
}

.data-table tbody tr:hover {
  background: #f8f9fa;
}

.data-table td {
  padding: 12px 16px;
  text-align: left;
  color: #555;
}

.report-id-cell {
  font-family: monospace;
  font-size: 13px;
  white-space: nowrap;
}

.status-tag {
  display: inline-block;
  padding: 2px 8px;
  border-radius: 4px;
  font-size: 12px;
  font-weight: 500;
}

.status-tag.draft {
  background: #f5f5f5;
  color: #666;
}

.status-tag.submitted {
  background: #e3f2fd;
  color: #1976d2;
}

.status-tag.approved {
  background: #e8f5e9;
  color: #388e3c;
}

.status-tag.rejected {
  background: #ffebee;
  color: #d32f2f;
}

.log-type-tag {
  display: inline-block;
  padding: 2px 8px;
  border-radius: 4px;
  font-size: 12px;
  font-weight: 500;
}

.log-type-tag.weekly {
  background: #e8f5e9;
  color: #388e3c;
}

.content-cell {
  max-width: 200px;
}

.content-text {
  display: -webkit-box;
  -webkit-line-clamp: 2;
  line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
  text-overflow: ellipsis;
}

.loading-cell,
.empty-cell {
  padding: 40px 16px;
  text-align: center;
  color: #999;
  font-size: 14px;
}

.loading-spinner {
  width: 24px;
  height: 24px;
  border: 3px solid #f3f3f3;
  border-top: 3px solid #1976d2;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin: 0 auto 12px;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.action-cell {
  display: flex;
  gap: 8px;
}

.action-btn {
  padding: 4px 12px;
  border: none;
  border-radius: 4px;
  font-size: 13px;
  cursor: pointer;
  transition: all 0.2s;
}

.view-btn {
  background: #e3f2fd;
  color: #1976d2;
}

.view-btn:hover {
  background: #1976d2;
  color: #fff;
}

.approve-btn {
  background: #e8f5e9;
  color: #388e3c;
}

.approve-btn:hover {
  background: #388e3c;
  color: #fff;
}

.reject-btn {
  background: #ffebee;
  color: #d32f2f;
}

.reject-btn:hover {
  background: #d32f2f;
  color: #fff;
}

.pagination-section {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px;
  background: #f5f7fa;
  border-top: 1px solid #e0e0e0;
  flex-wrap: wrap;
  gap: 12px;
}

.pagination-info {
  font-size: 14px;
  color: #666;
}

.pagination-controls {
  display: flex;
  align-items: center;
  gap: 8px;
}

.pagination-button {
  padding: 6px 16px;
  background: #fff;
  border: 1px solid #e0e0e0;
  border-radius: 4px;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.2s;
}

.pagination-button:hover:not(:disabled) {
  background: #1976d2;
  color: #fff;
}

.pagination-button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.pagination-pages {
  display: flex;
  align-items: center;
  gap: 4px;
}

.pagination-input {
  width: 60px;
  padding: 6px 8px;
  border: 1px solid #e0e0e0;
  border-radius: 4px;
  text-align: center;
  font-size: 14px;
}

.pagination-slash {
  color: #666;
}

.page-size-selector {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
  color: #666;
}

.page-size-select {
  padding: 6px 8px;
  border: 1px solid #e0e0e0;
  border-radius: 4px;
  font-size: 14px;
  cursor: pointer;
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

.modal-content {
  background: #fff;
  border-radius: 8px;
  width: 500px;
  max-width: 90%;
  max-height: 90vh;
  overflow-y: auto;
}

.modal-content-large {
  width: 700px;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 20px;
  border-bottom: 1px solid #e0e0e0;
}

.modal-header h3 {
  margin: 0;
  font-size: 18px;
  color: #333;
}

.close-btn {
  background: none;
  border: none;
  font-size: 24px;
  cursor: pointer;
  color: #999;
}

.modal-body {
  padding: 20px;
}

.detail-section {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.detail-row {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 16px;
}

.detail-column {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.detail-row.detail-row-five {
  grid-template-columns: repeat(5, 1fr);
}

.detail-row.full-width {
  grid-template-columns: 1fr;
}

.detail-item {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.detail-label {
  font-size: 13px;
  color: #999;
}

.detail-value {
  font-size: 14px;
  color: #333;
}

.content-full {
  white-space: pre-wrap;
  word-break: break-all;
  line-height: 1.6;
}

.detail-images {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
}

.detail-image {
  width: 100px;
  height: 100px;
  object-fit: cover;
  border-radius: 4px;
  cursor: pointer;
  transition: transform 0.2s;
}

.detail-image:hover {
  transform: scale(1.05);
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  padding: 16px 20px;
  border-top: 1px solid #e0e0e0;
}

.cancel-btn,
.confirm-btn {
  padding: 10px 24px;
  border: none;
  border-radius: 4px;
  font-size: 14px;
  cursor: pointer;
}

.cancel-btn {
  background: #f5f5f5;
  color: #666;
}

.cancel-btn:hover {
  background: #e0e0e0;
}

.confirm-btn {
  background: #d32f2f;
  color: #fff;
}

.confirm-btn:hover:not(:disabled) {
  background: #b71c1c;
}

.confirm-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.form-item {
  margin-bottom: 16px;
}

.form-label {
  display: block;
  margin-bottom: 6px;
  font-size: 14px;
  color: #333;
  font-weight: 500;
}

.form-textarea {
  width: 100%;
  padding: 10px 12px;
  border: 1px solid #e0e0e0;
  border-radius: 4px;
  font-size: 14px;
  box-sizing: border-box;
  min-height: 80px;
  resize: vertical;
}

.form-textarea:focus {
  outline: none;
  border-color: #1976d2;
}

.image-preview-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.9);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 2000;
  cursor: pointer;
}

.preview-image {
  max-width: 90%;
  max-height: 90%;
  object-fit: contain;
}

.operation-log-section {
  margin-top: 20px;
  padding-top: 20px;
  border-top: 1px solid #e0e0e0;
}

.section-title {
  font-size: 16px;
  font-weight: 600;
  color: #333;
  margin-bottom: 16px;
  padding-left: 12px;
  border-left: 3px solid #1976d2;
}

.timeline {
  position: relative;
  padding-left: 24px;
}

.timeline::before {
  content: '';
  position: absolute;
  left: 8px;
  top: 0;
  bottom: 0;
  width: 2px;
  background: #e0e0e0;
}

.timeline-item {
  position: relative;
  padding-bottom: 16px;
}

.timeline-item.last {
  padding-bottom: 0;
}

.timeline-dot {
  position: absolute;
  left: -20px;
  top: 4px;
  width: 12px;
  height: 12px;
  border-radius: 50%;
  background: #1976d2;
  border: 2px solid #fff;
  box-shadow: 0 0 0 2px #1976d2;
}

.timeline-content {
  display: flex;
  align-items: center;
  gap: 12px;
  flex-wrap: wrap;
}

.timeline-time {
  font-size: 14px;
  color: #666;
  font-family: monospace;
}

.timeline-operator {
  font-size: 14px;
  color: #333;
  font-weight: 500;
}

.timeline-action {
  font-size: 13px;
  color: #1976d2;
  background: #e3f2fd;
  padding: 2px 8px;
  border-radius: 4px;
}
</style>
