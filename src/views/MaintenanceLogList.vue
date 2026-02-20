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
                field-key="MaintenanceLogList_project"
                placeholder="请输入项目名称"
                @input="handleSearch"
              />
            </div>
            <div class="search-item">
              <label class="search-label">日志日期：</label>
              <input v-model="filters.logDate" type="date" class="search-input" @change="handleSearch" />
            </div>
          </div>
        </div>
      </div>

      <div class="table-section">
        <table class="data-table">
          <thead>
            <tr>
              <th>序号</th>
              <th>日志编号</th>
              <th>项目名称</th>
              <th>项目编号</th>
              <th>日志类型</th>
              <th>日志日期</th>
              <th>工作内容</th>
              <th>提交时间</th>
              <th>操作</th>
            </tr>
          </thead>
          <tbody>
            <tr v-if="loading">
              <td colspan="9" style="text-align: center; padding: 20px;">加载中...</td>
            </tr>
            <tr v-else-if="dataList.length === 0">
              <td colspan="9" style="text-align: center; padding: 20px;">暂无数据</td>
            </tr>
            <tr v-else v-for="(item, index) in dataList" :key="item.id" :class="{ 'even-row': index % 2 === 0 }">
              <td>{{ (currentPage - 1) * pageSize + index + 1 }}</td>
              <td class="log-id-cell">{{ item.log_id }}</td>
              <td>{{ item.project_name }}</td>
              <td>{{ item.project_id }}</td>
              <td>
                <span class="log-type-tag" :class="item.log_type">
                  {{ getLogTypeName(item.log_type) }}
                </span>
              </td>
              <td>{{ formatDate(item.log_date) }}</td>
              <td class="content-cell">
                <span class="content-text" :title="item.work_content">
                  {{ truncateContent(item.work_content) }}
                </span>
              </td>
              <td>{{ formatDateTime(item.created_at) }}</td>
              <td class="action-cell">
                <a href="#" class="action-link action-view" @click.prevent="handleView(item)">查看</a>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <div class="pagination-section">
        <div class="pagination-info">
          共 {{ total }} 条记录
        </div>
        <div class="pagination-controls">
          <button class="page-btn page-nav" :disabled="currentPage === 1" @click="handlePageChange(currentPage - 1)">
            &lt;
          </button>
          <button
            v-for="page in displayedPages"
            :key="page"
            class="page-btn page-num"
            :class="{ active: page === currentPage }"
            @click="handlePageChange(page)"
          >
            {{ page }}
          </button>
          <button class="page-btn page-nav" :disabled="currentPage >= totalPages" @click="handlePageChange(currentPage + 1)">
            &gt;
          </button>
          <select class="page-select" v-model="pageSize" @change="handlePageSizeChange">
            <option value="10">10 条 / 页</option>
            <option value="20">20 条 / 页</option>
            <option value="50">50 条 / 页</option>
          </select>
          <div class="page-jump">
            <span>跳至</span>
            <input type="number" class="page-input" v-model="jumpPage" min="1" :max="totalPages" />
            <span>页</span>
            <button class="page-btn page-go" @click="handleJump">Go</button>
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
                <label class="detail-label">日志编号</label>
                <div class="detail-value">{{ detailData.log_id }}</div>
              </div>
              <div class="detail-item">
                <label class="detail-label">日志类型</label>
                <div class="detail-value">
                  <span class="log-type-tag" :class="detailData.log_type">
                    {{ getLogTypeName(detailData.log_type) }}
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
                <label class="detail-label">日志日期</label>
                <div class="detail-value">{{ formatDate(detailData.log_date) }}</div>
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
            <div class="detail-row full-width" v-if="detailData.images && detailData.images.length > 0">
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
            <div class="section-title">内部确认区</div>
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
          <div class="operation-log-section" v-else-if="!loadingLogs">
            <div class="section-title">内部确认区</div>
            <div class="no-logs">暂无操作记录</div>
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
  </div>
</template>

<script lang="ts">
import { defineComponent, ref, computed, onMounted, onUnmounted } from 'vue'
import apiClient from '@/utils/api'
import type { ApiResponse, PaginatedResponse } from '@/types/api'
import { authService } from '@/services/auth'
import { formatDate, formatDateTime } from '@/config/constants'
import SearchInput from '@/components/SearchInput.vue'

/**
 * 维保日志项接口定义
 */
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
  created_by: string
  created_at: string
  updated_at: string
}

/**
 * 操作日志项接口定义
 */
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
  name: 'MaintenanceLogList',
  components: {
    SearchInput
  },
  setup() {
    const loading = ref(false)
    const dataList = ref<MaintenanceLogItem[]>([])
    const total = ref(0)
    const currentPage = ref(1)
    const pageSize = ref(10)
    const jumpPage = ref(1)
    const currentUser = ref(authService.getCurrentUser())
    const showDetailModal = ref(false)
    const detailData = ref<MaintenanceLogItem | null>(null)
    const showImagePreview = ref(false)
    const previewImageUrl = ref('')
    const operationLogs = ref<OperationLogItem[]>([])
    const loadingLogs = ref(false)

    const filters = ref({
      project: '',
      logDate: ''
    })

    const isAdmin = computed(() => {
      return authService.isAdmin(currentUser.value)
    })

    const isDepartmentManager = computed(() => {
      return authService.isDepartmentManager(currentUser.value)
    })

    const totalPages = computed(() => {
      return Math.ceil(total.value / pageSize.value) || 1
    })

    /**
     * 计算显示的页码
     */
    const displayedPages = computed(() => {
      const pages: number[] = []
      const start = Math.max(1, currentPage.value - 2)
      const end = Math.min(totalPages.value, start + 4)
      for (let i = start; i <= end; i++) {
        pages.push(i)
      }
      return pages
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

        // 管理员和部门经理能看到所有数据，普通员工只能看到自己的数据
        if (currentUser.value && currentUser.value.name && !isAdmin.value && !isDepartmentManager.value) {
          params.created_by = currentUser.value.name
        }

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
     * 查看详情
     */
    const handleView = async (item: MaintenanceLogItem) => {
      detailData.value = item
      showDetailModal.value = true
      // 获取操作日志
      await fetchOperationLogs(item.id)
    }

    /**
     * 获取操作日志
     */
    const fetchOperationLogs = async (logId: number) => {
      loadingLogs.value = true
      try {
        const response = await apiClient.get(`/maintenance-log/${logId}/operation-logs`) as unknown as ApiResponse<OperationLogItem[]>
        if (response.code === 200) {
          operationLogs.value = response.data || []
        }
      } catch (error) {
        console.error('获取操作日志失败:', error)
        operationLogs.value = []
      } finally {
        loadingLogs.value = false
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
     * 关闭详情弹窗
     */
    const closeDetailModal = () => {
      showDetailModal.value = false
      detailData.value = null
      operationLogs.value = []
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

    /**
     * 跳转到指定页
     */
    const handleJump = () => {
      const page = parseInt(String(jumpPage.value))
      if (page >= 1 && page <= totalPages.value) {
        handlePageChange(page)
      }
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
      dataList,
      total,
      currentPage,
      pageSize,
      totalPages,
      jumpPage,
      displayedPages,
      filters,
      currentUser,
      isAdmin,
      isDepartmentManager,
      showDetailModal,
      detailData,
      showImagePreview,
      previewImageUrl,
      operationLogs,
      loadingLogs,
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
      handlePageChange,
      handlePageSizeChange,
      handleJump
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

.data-table tbody tr.even-row {
  background: #fafafa;
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
  padding: 4px 8px;
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
  -webkit-box-orient: vertical;
  overflow: hidden;
  text-overflow: ellipsis;
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

.page-btn {
  min-width: 32px;
  padding: 6px 12px;
  border: 1px solid #d0d7de;
  border-radius: 4px;
  background: #fff;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.2s;
}

.page-btn:hover:not(:disabled) {
  background: #f5f5f5;
  border-color: #1976d2;
}

.page-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.page-btn.page-num {
  min-width: 36px;
}

.page-btn.active {
  background: #1976d2;
  color: #fff;
  border-color: #1976d2;
}

.page-select {
  padding: 6px 8px;
  border: 1px solid #d0d7de;
  border-radius: 4px;
  font-size: 14px;
  background: #fff;
  cursor: pointer;
  outline: none;
}

.page-jump {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
  color: #666;
}

.page-input {
  width: 60px;
  padding: 6px 8px;
  border: 1px solid #d0d7de;
  border-radius: 4px;
  font-size: 14px;
  text-align: center;
  outline: none;
}

.page-btn.page-go {
  background: #1976d2;
  color: #fff;
}

.page-btn.page-go:hover {
  background: #1565c0;
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

.timeline-item.last::before {
  display: none;
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

.no-logs {
  text-align: center;
  color: #999;
  font-size: 14px;
  padding: 20px 0;
}
</style>
