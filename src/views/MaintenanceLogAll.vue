<template>
  <div class="maintenance-log-page">
    <div class="content">
      <div class="search-section">
        <div class="search-form">
          <div class="search-row">
            <div class="search-item">
              <label class="search-label">项目名称：</label>
              <SearchInput
                v-model="filters.project"
                field-key="MaintenanceLogAll_project"
                placeholder="请输入项目名称"
                @input="handleSearch"
              />
            </div>
            <div class="search-item">
              <label class="search-label">日志日期：</label>
              <input v-model="filters.logDate" type="date" class="search-input" @change="handleSearch" />
            </div>
            <div class="search-item">
              <label class="search-label">提交人：</label>
              <SearchInput
                v-model="filters.createdBy"
                field-key="MaintenanceLogAll_created_by"
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
                    <span class="log-type-tag" :class="item.log_type">
                      {{ getLogTypeName(item.log_type) }}
                    </span>
                  </td>
                  <td class="content-cell">
                    <span class="content-text" :title="item.work_content">
                      {{ truncateContent(item.work_content) }}
                    </span>
                  </td>
                  <td>{{ item.created_by || '-' }}</td>
                  <td>{{ formatDateTime(item.created_at) }}</td>
                  <td class="action-cell">
                    <a href="#" class="action-link action-view" @click.prevent="handleView(item)">查看</a>
                    <a 
                      href="#" 
                      v-if="!item.status || item.status === 'submitted'" 
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
          <h3>日志详情</h3>
          <button class="close-btn" @click="closeDetailModal">&times;</button>
        </div>
        <div class="modal-body" v-if="detailData">
          <div class="detail-section">
            <div class="detail-row">
              <div class="detail-item">
                <label class="detail-label">日志类型</label>
                <div class="detail-value">
                  <span class="log-type-tag" :class="detailData.log_type">
                    {{ getLogTypeName(detailData.log_type) }}
                  </span>
                </div>
              </div>
              <div class="detail-item">
                <label class="detail-label">项目名称</label>
                <div class="detail-value">{{ detailData.project_name }}</div>
              </div>
            </div>
            <div class="detail-row">
              <div class="detail-item">
                <label class="detail-label">项目编号</label>
                <div class="detail-value">{{ detailData.project_id }}</div>
              </div>
              <div class="detail-item">
                <label class="detail-label">日志日期</label>
                <div class="detail-value">{{ formatDate(detailData.log_date) }}</div>
              </div>
            </div>
            <div class="detail-row">
              <div class="detail-item">
                <label class="detail-label">提交人</label>
                <div class="detail-value">{{ detailData.created_by || '-' }}</div>
              </div>
              <div class="detail-item">
                <label class="detail-label">提交时间</label>
                <div class="detail-value">{{ formatDateTime(detailData.created_at) }}</div>
              </div>
            </div>
            <div class="detail-row full-width">
              <div class="detail-item">
                <label class="detail-label">工作内容</label>
                <div class="detail-value content-full">{{ detailData.work_content || '-' }}</div>
              </div>
            </div>
            <div class="detail-row full-width">
              <div class="detail-item">
                <label class="detail-label">备注</label>
                <div class="detail-value content-full">{{ detailData.remark || '-' }}</div>
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

          <div class="operation-log-section" v-if="maintenanceLogOperationLogs.length > 0">
            <div class="section-title">内部确认区</div>
            <div class="timeline">
              <div 
                v-for="(log, index) in maintenanceLogOperationLogs" 
                :key="log.id" 
                class="timeline-item"
                :class="{ 'last': index === maintenanceLogOperationLogs.length - 1 }"
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
      <div class="modal-content modal-content-small">
        <div class="modal-header">
          <h3>退回确认</h3>
          <button class="close-btn" @click="closeRejectModal">&times;</button>
        </div>
        <div class="modal-body">
          <div class="form-group">
            <label class="form-label">退回原因 <span class="required">*</span></label>
            <textarea 
              v-model="rejectReason" 
              class="form-textarea" 
              placeholder="请输入退回原因"
              rows="4"
            ></textarea>
          </div>
        </div>
        <div class="modal-footer">
          <button class="cancel-btn" @click="closeRejectModal">取消</button>
          <button class="confirm-btn reject" @click="confirmReject" :disabled="submitting">
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
import SearchInput from '@/components/SearchInput.vue'

interface MaintenanceLogItem {
  id: number
  log_id: string
  project_id: string
  project_name: string
  log_type: string
  log_date: string
  work_content: string
  images: string
  remark: string
  status: string
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
  name: 'MaintenanceLogAll',
  components: {
    SearchInput
  },
  setup() {
    const loading = ref(false)
    const dataList = ref<MaintenanceLogItem[]>([])
    const total = ref(0)
    const currentPage = ref(1)
    const pageSize = ref(10)
    const currentUser = ref(authService.getCurrentUser())
    const showDetailModal = ref(false)
    const detailData = ref<MaintenanceLogItem | null>(null)
    const showImagePreview = ref(false)
    const previewImageUrl = ref('')
    const showRejectModal = ref(false)
    const rejectReason = ref('')
    const pendingRejectItem = ref<MaintenanceLogItem | null>(null)
    const submitting = ref(false)
    const maintenanceLogOperationLogs = ref<OperationLogItem[]>([])

    const filters = ref({
      project: '',
      logDate: '',
      createdBy: ''
    })

    const isAdmin = computed(() => {
      return authService.isAdmin(currentUser.value)
    })

    const totalPages = computed(() => {
      return Math.ceil(total.value / pageSize.value) || 1
    })

    /**
     * 获取日志类型名称
     */
    const getLogTypeName = (logType: string) => {
      const typeMap: Record<string, string> = {
        'maintenance': '维修日志',
        'spot': '维修日志',
        'repair': '维修日志'
      }
      return typeMap[logType] || '维修日志'
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
        if (filters.value.logDate) params.log_date = filters.value.logDate
        if (filters.value.createdBy) params.created_by = filters.value.createdBy

        const response = await apiClient.get('/maintenance-log', { params }) as unknown as ApiResponse<PaginatedResponse<MaintenanceLogItem>>
        
        if (response && response.code === 200 && response.data) {
          dataList.value = response.data.items || response.data.content || []
          total.value = response.data.total || response.data.totalElements || 0
        }
      } catch (error) {
        console.error('加载维保日志数据失败:', error)
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
     * 获取维保日志操作日志
     */
    const fetchMaintenanceLogOperationLogs = async (logId: number) => {
      try {
        const response = await apiClient.get(`/maintenance-log/${logId}/operation-logs`) as unknown as ApiResponse<OperationLogItem[]>
        if (response.code === 200) {
          maintenanceLogOperationLogs.value = response.data || []
        }
      } catch (error) {
        console.error('获取操作日志失败:', error)
        maintenanceLogOperationLogs.value = []
      }
    }

    /**
     * 查看详情
     */
    const handleView = async (item: MaintenanceLogItem) => {
      detailData.value = item
      showDetailModal.value = true
      maintenanceLogOperationLogs.value = []
      await fetchMaintenanceLogOperationLogs(item.id)
    }

    /**
     * 关闭详情弹窗
     */
    const closeDetailModal = () => {
      showDetailModal.value = false
      detailData.value = null
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
     * 打开退回弹窗
     */
    const handleReject = (item: MaintenanceLogItem) => {
      pendingRejectItem.value = item
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
        const response = await apiClient.post(`/maintenance-log/${pendingRejectItem.value.id}/reject`, {
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
      currentUser,
      isAdmin,
      showDetailModal,
      detailData,
      showImagePreview,
      previewImageUrl,
      showRejectModal,
      rejectReason,
      pendingRejectItem,
      maintenanceLogOperationLogs,
      getLogTypeName,
      truncateContent,
      parseImages,
      formatDate,
      formatDateTime,
      formatOperationTime,
      handleSearch,
      handleView,
      closeDetailModal,
      previewImage,
      closeImagePreview,
      handleReject,
      confirmReject,
      closeRejectModal,
      handlePageChange,
      handlePageSizeChange
    }
  }
})
</script>

<style scoped>
.maintenance-log-page {
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
  min-width: 1000px;
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

.log-id-cell {
  font-family: monospace;
  font-size: 13px;
  white-space: nowrap;
}

.log-type-tag {
  display: inline-block;
  padding: 2px 8px;
  border-radius: 4px;
  font-size: 12px;
  font-weight: 500;
}

.log-type-tag.maintenance {
  background: #e3f2fd;
  color: #1976d2;
}

.log-type-tag.spot {
  background: #e3f2fd;
  color: #1976d2;
}

.log-type-tag.repair {
  background: #fff3e0;
  color: #f57c00;
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

.cancel-btn {
  padding: 10px 24px;
  border: none;
  border-radius: 4px;
  font-size: 14px;
  cursor: pointer;
  background: #f5f5f5;
  color: #666;
}

.cancel-btn:hover {
  background: #e0e0e0;
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

.modal-content-small {
  width: 400px;
  max-width: 90%;
}

.form-group {
  margin-bottom: 16px;
}

.form-label {
  display: block;
  margin-bottom: 6px;
  font-size: 14px;
  font-weight: 500;
  color: #333;
}

.required {
  color: #d32f2f;
}

.form-textarea {
  width: 100%;
  padding: 10px 12px;
  border: 1px solid #e0e0e0;
  border-radius: 4px;
  font-size: 14px;
  resize: vertical;
  min-height: 80px;
}

.form-textarea:focus {
  outline: none;
  border-color: #1976d2;
  box-shadow: 0 0 0 3px rgba(25, 118, 210, 0.1);
}

.confirm-btn {
  padding: 10px 24px;
  border: none;
  border-radius: 4px;
  font-size: 14px;
  cursor: pointer;
  background: #1976d2;
  color: #fff;
}

.confirm-btn:hover {
  background: #1565c0;
}

.confirm-btn:disabled {
  background: #ccc;
  cursor: not-allowed;
}

.confirm-btn.reject {
  background: #d32f2f;
}

.confirm-btn.reject:hover {
  background: #c62828;
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
