<template>
  <div class="weekly-report-page">
    <div class="content">
      <div class="search-section">
        <div class="search-form">
          <div class="search-row">
            <div class="search-item">
              <label class="search-label">周报单号：</label>
              <SearchInput
                v-model="filters.reportId"
                field-key="WeeklyReport_report_id"
                placeholder="请输入周报单号"
                @input="handleSearch"
              />
            </div>
            <div class="search-item">
              <label class="search-label">填报时间：</label>
              <input v-model="filters.reportDate" type="date" class="search-input" @change="handleSearch" />
            </div>
            <div class="search-item">
              <label class="search-label">周报内容：</label>
              <SearchInput
                v-model="filters.workSummary"
                field-key="WeeklyReport_work_summary"
                placeholder="请输入周报内容"
                @input="handleSearch"
              />
            </div>
            <div class="search-item" v-if="canViewAll">
              <label class="search-label">提交人：</label>
              <SearchInput
                v-model="filters.createdBy"
                field-key="WeeklyReport_created_by"
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
                  <th>部门周报编号</th>
                  <th>项目名称</th>
                  <th>项目编号</th>
                  <th>周开始日期</th>
                  <th>周结束日期</th>
                  <th>填报日期</th>
                  <th>本周工作总结</th>
                  <th>状态</th>
                  <th>提交人</th>
                  <th>提交时间</th>
                  <th>操作</th>
                </tr>
              </thead>
              <tbody>
                <tr v-if="loading">
                  <td colspan="12" class="loading-cell">
                    <div class="loading-spinner"></div>
                    <span>加载中...</span>
                  </td>
                </tr>
                <tr v-else-if="dataList.length === 0">
                  <td colspan="12" class="empty-cell">暂无数据</td>
                </tr>
                <tr v-else v-for="(item, index) in dataList" :key="item.id">
                  <td>{{ (currentPage - 1) * pageSize + index + 1 }}</td>
                  <td class="report-id-cell">{{ item.report_id }}</td>
                  <td>{{ item.project_name }}</td>
                  <td>{{ item.project_id }}</td>
                  <td>{{ formatDate(item.week_start_date) }}</td>
                  <td>{{ formatDate(item.week_end_date) }}</td>
                  <td>{{ formatDate(item.report_date) }}</td>
                  <td class="content-cell">
                    <span class="content-text" :title="item.work_summary">
                      {{ truncateContent(item.work_summary) }}
                    </span>
                  </td>
                  <td>
                    <span class="status-tag" :class="item.status">
                      {{ getStatusName(item.status) }}
                    </span>
                  </td>
                  <td>{{ item.created_by || '-' }}</td>
                  <td>{{ formatDateTime(item.created_at) }}</td>
                  <td class="action-cell">
                    <a href="#" class="action-link action-view" @click.prevent="handleView(item)">查看</a>
                    <a 
                      v-if="canEdit(item)" 
                      href="#" 
                      class="action-link action-edit" 
                      @click.prevent="handleEdit(item)"
                    >编辑</a>
                    <a 
                      v-if="canReject(item)" 
                      href="#" 
                      class="action-link action-reject" 
                      @click.prevent="handleReject(item)"
                    >退回</a>
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

    <div v-if="showDetailModal" class="modal-overlay" @click.self="closeDetailModal">
      <div class="modal-content modal-content-large">
        <div class="modal-header">
          <h3>部门周报详情</h3>
          <button class="close-btn" @click="closeDetailModal">&times;</button>
        </div>
        <div class="modal-body" v-if="detailData">
          <div class="detail-section">
            <div class="detail-row">
              <div class="detail-item">
                <label class="detail-label">部门周报编号</label>
                <div class="detail-value">{{ detailData.report_id }}</div>
              </div>
              <div class="detail-item">
                <label class="detail-label">状态</label>
                <div class="detail-value">
                  <span class="status-tag" :class="detailData.status">
                    {{ getStatusName(detailData.status) }}
                  </span>
                </div>
              </div>
            </div>
            <div class="detail-row">
              <div class="detail-item">
                <label class="detail-label">项目名称</label>
                <div class="detail-value">{{ detailData.project_name }}</div>
              </div>
              <div class="detail-item">
                <label class="detail-label">项目编号</label>
                <div class="detail-value">{{ detailData.project_id }}</div>
              </div>
            </div>
            <div class="detail-row">
              <div class="detail-item">
                <label class="detail-label">周开始日期</label>
                <div class="detail-value">{{ formatDate(detailData.week_start_date) }}</div>
              </div>
              <div class="detail-item">
                <label class="detail-label">周结束日期</label>
                <div class="detail-value">{{ formatDate(detailData.week_end_date) }}</div>
              </div>
            </div>
            <div class="detail-row">
              <div class="detail-item">
                <label class="detail-label">填报日期</label>
                <div class="detail-value">{{ formatDate(detailData.report_date) }}</div>
              </div>
              <div class="detail-item">
                <label class="detail-label">提交人</label>
                <div class="detail-value">{{ detailData.created_by || '-' }}</div>
              </div>
            </div>
            <div class="detail-row">
              <div class="detail-item">
                <label class="detail-label">提交时间</label>
                <div class="detail-value">{{ formatDateTime(detailData.created_at) }}</div>
              </div>
              <div class="detail-item" v-if="detailData.approved_by">
                <label class="detail-label">审核人</label>
                <div class="detail-value">{{ detailData.approved_by }}</div>
              </div>
            </div>
            <div class="detail-row full-width">
              <div class="detail-item">
                <label class="detail-label">本周工作总结</label>
                <div class="detail-value content-full">{{ detailData.work_summary || '-' }}</div>
              </div>
            </div>
            <div class="detail-row full-width">
              <div class="detail-item">
                <label class="detail-label">下周工作计划</label>
                <div class="detail-value content-full">{{ detailData.next_week_plan || '-' }}</div>
              </div>
            </div>
            <div class="detail-row full-width">
              <div class="detail-item">
                <label class="detail-label">存在问题</label>
                <div class="detail-value content-full">{{ detailData.issues || '-' }}</div>
              </div>
            </div>
            <div class="detail-row full-width">
              <div class="detail-item">
                <label class="detail-label">建议措施</label>
                <div class="detail-value content-full">{{ detailData.suggestions || '-' }}</div>
              </div>
            </div>
            <div class="detail-row full-width" v-if="detailData.reject_reason">
              <div class="detail-item">
                <label class="detail-label">退回原因</label>
                <div class="detail-value content-full reject-reason">{{ detailData.reject_reason }}</div>
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

          <div class="operation-log-section" v-if="operationLogs.length > 0">
            <div class="section-title">操作日志</div>
            <div class="timeline">
              <div 
                v-for="(log, index) in operationLogs" 
                :key="log.id" 
                class="timeline-item"
                :class="{ 'last': index === operationLogs.length - 1 }"
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
import { useRouter } from 'vue-router'
import apiClient from '@/utils/api'
import type { ApiResponse, PaginatedResponse } from '@/types/api'
import { userStore } from '@/stores/userStore'
import { formatDate, formatDateTime } from '@/config/constants'
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
  name: 'WeeklyReportList',
  components: {
    SearchInput
  },
  setup() {
    const router = useRouter()
    const loading = ref(false)
    const submitting = ref(false)
    const dataList = ref<WeeklyReportItem[]>([])
    const total = ref(0)
    const currentPage = ref(1)
    const pageSize = ref(10)
    const showDetailModal = ref(false)
    const detailData = ref<WeeklyReportItem | null>(null)
    const showImagePreview = ref(false)
    const previewImageUrl = ref('')
    const showRejectModal = ref(false)
    const rejectReason = ref('')
    const pendingRejectItem = ref<WeeklyReportItem | null>(null)
    const operationLogs = ref<OperationLogItem[]>([])

    const canViewAll = computed(() => {
      return userStore.isAdmin() || userStore.isDepartmentManager()
    })

    const filters = ref({
      reportId: '',
      reportDate: '',
      workSummary: '',
      createdBy: ''
    })

    const totalPages = computed(() => {
      return Math.ceil(total.value / pageSize.value) || 1
    })

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
     * 判断是否可以编辑
     */
    const canEdit = (item: WeeklyReportItem) => {
      const user = userStore.getUser()
      if (!user) return false
      const isOwner = item.created_by === user.name
      const isEditableStatus = item.status === 'draft' || item.status === 'rejected'
      return isOwner && isEditableStatus
    }

    /**
     * 判断是否可以退回
     */
    const canReject = (item: WeeklyReportItem) => {
      if (!canViewAll.value) return false
      return item.status === 'submitted'
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
        if (filters.value.reportId) params.report_id = filters.value.reportId
        if (filters.value.reportDate) params.report_date = filters.value.reportDate
        if (filters.value.workSummary) params.work_summary = filters.value.workSummary
        
        if (!canViewAll.value) {
          const user = userStore.getUser()
          if (user && user.name) {
            params.created_by = user.name
          }
        } else if (filters.value.createdBy) {
          params.created_by = filters.value.createdBy
        }

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
     * 获取操作日志
     */
    const fetchOperationLogs = async (reportId: number) => {
      try {
        const response = await apiClient.get(`/weekly-report/${reportId}/operation-logs`) as unknown as ApiResponse<OperationLogItem[]>
        if (response.code === 200) {
          operationLogs.value = response.data || []
        }
      } catch (error) {
        console.error('获取操作日志失败:', error)
        operationLogs.value = []
      }
    }

    /**
     * 查看详情
     */
    const handleView = async (item: WeeklyReportItem) => {
      detailData.value = item
      showDetailModal.value = true
      operationLogs.value = []
      await fetchOperationLogs(item.id)
    }

    /**
     * 关闭详情弹窗
     */
    const closeDetailModal = () => {
      showDetailModal.value = false
      detailData.value = null
      operationLogs.value = []
    }

    /**
     * 编辑
     */
    const handleEdit = (item: WeeklyReportItem) => {
      router.push(`/weekly-report/edit/${item.id}`)
    }

    /**
     * 退回
     */
    const handleReject = (item: WeeklyReportItem) => {
      pendingRejectItem.value = item
      rejectReason.value = ''
      showRejectModal.value = true
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
      submitting,
      dataList,
      total,
      currentPage,
      pageSize,
      totalPages,
      filters,
      canViewAll,
      currentUser: userStore.readonlyCurrentUser,
      showDetailModal,
      detailData,
      showImagePreview,
      previewImageUrl,
      showRejectModal,
      rejectReason,
      operationLogs,
      getStatusName,
      truncateContent,
      parseImages,
      formatOperationTime,
      canEdit,
      canReject,
      formatDate,
      formatDateTime,
      handleSearch,
      handleView,
      handleEdit,
      handleReject,
      closeDetailModal,
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
.weekly-report-page {
  background: #fff;
  min-height: 100vh;
}

.content {
  padding: 20px;
}

.search-section {
  display: flex;
  gap: 16px;
  margin-bottom: 20px;
  align-items: flex-start;
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

.search-input {
  padding: 8px 12px;
  border: 1px solid #d0d7de;
  border-radius: 4px;
  font-size: 14px;
  outline: none;
  min-width: 180px;
}

.search-input:focus {
  border-color: #1976d2;
  box-shadow: 0 0 0 2px rgba(25, 118, 210, 0.1);
}

.table-section {
  background: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
  overflow-x: auto;
}

.data-table {
  width: 100%;
  border-collapse: collapse;
  min-width: 1200px;
}

.data-table thead {
  background: #f5f5f5;
}

.data-table th {
  padding: 12px 8px;
  text-align: left;
  font-size: 14px;
  font-weight: 600;
  color: #333;
  border-bottom: 2px solid #e0e0e0;
  white-space: nowrap;
}

.data-table tbody tr {
  transition: background 0.15s;
}

.data-table tbody tr:hover {
  background: #f9f9f9;
}

.data-table td {
  padding: 12px 8px;
  border-bottom: 1px solid #e0e0e0;
  font-size: 14px;
  color: #666;
}

.report-id-cell {
  font-family: monospace;
  font-size: 13px;
  white-space: nowrap;
}

.status-tag {
  display: inline-block;
  padding: 4px 8px;
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
  white-space: nowrap;
}

.action-link {
  font-size: 14px;
  font-weight: 500;
  text-decoration: none;
  transition: color 0.2s;
}

.action-view {
  color: #1976d2;
}

.action-view:hover {
  color: #1565c0;
}

.action-edit {
  color: #388e3c;
}

.action-edit:hover {
  color: #2e7d32;
}

.action-reject {
  color: #d32f2f;
}

.action-reject:hover {
  color: #c62828;
}

.pagination-section {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 0;
  border-top: 1px solid #e0e0e0;
}

.pagination-info {
  font-size: 14px;
  color: #666;
}

.pagination-controls {
  display: flex;
  gap: 8px;
  align-items: center;
}

.pagination-button {
  min-width: 32px;
  padding: 6px 12px;
  border: 1px solid #d0d7de;
  border-radius: 4px;
  background: #fff;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.2s;
}

.pagination-button:hover:not(:disabled) {
  background: #f5f5f5;
  border-color: #1976d2;
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
  border: 1px solid #d0d7de;
  border-radius: 4px;
  font-size: 14px;
  text-align: center;
  outline: none;
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
  border: 1px solid #d0d7de;
  border-radius: 4px;
  font-size: 14px;
  background: #fff;
  cursor: pointer;
  outline: none;
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

.reject-reason {
  color: #d32f2f;
  background: #ffebee;
  padding: 8px 12px;
  border-radius: 4px;
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
