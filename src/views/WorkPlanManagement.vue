<template>
  <div class="work-plan-page">
    <Toast :visible="toast.visible" :message="toast.message" :type="toast.type" />
    <div class="content">
      <div class="search-section">
        <div class="search-form">
          <div class="search-row">
            <div class="search-item">
              <label class="search-label">项目名称：</label>
              <SearchInput
                v-model="searchForm.project_name"
                field-key="WorkPlanManagement_project_name"
                placeholder="请输入项目名称"
                @input="handleSearch"
              />
            </div>
            <div class="search-item">
              <label class="search-label">客户名称：</label>
              <SearchInput
                v-model="searchForm.client_name"
                field-key="WorkPlanManagement_client_name"
                placeholder="请输入客户名称"
                @input="handleSearch"
              />
            </div>
          </div>
        </div>
        <div class="action-buttons">
        </div>
      </div>

      <div class="table-section">
        <table class="data-table">
          <thead>
            <tr>
              <th>序号</th>
              <th>工单编号</th>
              <th>工单类型</th>
              <th>项目名称</th>
              <th>项目编号</th>
              <th>计划开始日期</th>
              <th>计划结束日期</th>
              <th>客户单位</th>
              <th>运维人员</th>
              <th>状态</th>
              <th>操作</th>
            </tr>
          </thead>
          <tbody>
            <tr v-if="loading">
              <td colspan="11" style="text-align: center; padding: 20px;">加载中...</td>
            </tr>
            <tr v-else-if="planData.length === 0">
              <td colspan="11" style="text-align: center; padding: 20px;">暂无数据</td>
            </tr>
            <tr v-else v-for="(item, index) in planData" :key="item.id" :class="{ 'even-row': index % 2 === 0 }">
              <td>{{ currentPage * pageSize + index + 1 }}</td>
              <td>{{ item.plan_id }}</td>
              <td>
                <span :class="getOrderTypeClass(item.order_type_code)" class="type-badge">{{ item.plan_type }}</span>
              </td>
              <td>{{ item.project_name }}</td>
              <td>{{ item.project_id }}</td>
              <td>{{ formatDate(item.plan_start_date) }}</td>
              <td>{{ formatDate(item.plan_end_date) }}</td>
              <td>{{ item.client_name || '-' }}</td>
              <td>{{ item.maintenance_personnel || '-' }}</td>
              <td>
                <span :class="getStatusClass(item.status)" class="status-badge">{{ item.status }}</span>
              </td>
              <td class="action-cell">
                <a href="#" class="action-link action-view" @click.prevent="handleView(item)">查看</a>
                <a href="#" v-if="item.status === WORK_STATUS.COMPLETED" class="action-link action-export" @click.prevent="handleExport(item)">导出</a>
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
          <button class="page-btn page-nav" :disabled="currentPage === 0" @click="currentPage--">
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
          <button class="page-btn page-nav" :disabled="currentPage >= totalPages - 1" @click="currentPage++">
            &gt;
          </button>
          <select class="page-select" v-model="pageSize">
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

    <div v-if="isViewModalOpen" class="modal-overlay" @click.self="closeViewModal">
      <div class="modal-container modal-container-large">
        <div class="modal-header">
          <h3 class="modal-title">定期巡检单详情</h3>
          <button class="modal-close" @click="closeViewModal">×</button>
        </div>
        <div class="modal-body">
          <div class="detail-section">
            <div class="detail-grid detail-grid-3">
              <div class="detail-item">
                <label class="detail-label">项目名称</label>
                <div class="detail-value">{{ viewData.project_name || '-' }}</div>
              </div>
              <div class="detail-item">
                <label class="detail-label">客户单位</label>
                <div class="detail-value">{{ viewData.client_name || '-' }}</div>
              </div>
              <div class="detail-item">
                <label class="detail-label">客户联系人</label>
                <div class="detail-value">{{ viewData.client_contact || '-' }}</div>
              </div>
              <div class="detail-item">
                <label class="detail-label">联系人职位</label>
                <div class="detail-value">{{ viewData.client_contact_position || '-' }}</div>
              </div>
              <div class="detail-item">
                <label class="detail-label">客户联系方式</label>
                <div class="detail-value">{{ viewData.client_contact_info || '-' }}</div>
              </div>
              <div class="detail-item">
                <label class="detail-label">客户地址</label>
                <div class="detail-value">{{ viewData.address || '-' }}</div>
              </div>
              <div class="detail-item">
                <label class="detail-label">合同剩余时间</label>
                <div class="detail-value" :class="getRemainingTimeClass()">{{ viewData.remainingTime || '-' }}</div>
              </div>
              <div class="detail-item">
                <label class="detail-label">计划开始日期</label>
                <div class="detail-value">{{ formatDate(viewData.plan_start_date) || '-' }}</div>
              </div>
              <div class="detail-item">
                <label class="detail-label">计划结束日期</label>
                <div class="detail-value">{{ formatDate(viewData.plan_end_date) || '-' }}</div>
              </div>
              <div class="detail-item">
                <label class="detail-label">运维人员</label>
                <div class="detail-value">{{ viewData.maintenance_personnel || '-' }}</div>
              </div>
            </div>
          </div>

          <div class="detail-section">
            <h4 class="section-title">巡检内容:</h4>
            <table class="inspection-table">
              <thead>
                <tr>
                  <th style="width: 60px;">序号</th>
                  <th style="width: 120px;">巡检项</th>
                  <th style="width: 150px;">巡检内容</th>
                  <th style="width: 150px;">检查要求</th>
                  <th style="width: 150px;">简要说明</th>
                  <th style="width: 80px;">是否正常</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="(item, index) in viewInspectionItems" :key="index">
                  <td>{{ index + 1 }}</td>
                  <td>{{ item.inspection_item || '-' }}</td>
                  <td>{{ item.inspection_content || '-' }}</td>
                  <td>{{ item.check_requirement || '-' }}</td>
                  <td>{{ item.brief_description || '-' }}</td>
                  <td>
                    <span :class="item.is_normal ? 'status-normal' : 'status-abnormal'">
                      {{ item.is_normal ? '正常' : '异常' }}
                    </span>
                  </td>
                </tr>
                <tr v-if="viewInspectionItems.length === 0">
                  <td colspan="6" style="text-align: center; padding: 20px; color: #999;">暂无巡检内容</td>
                </tr>
              </tbody>
            </table>
          </div>

          <div class="detail-section">
            <h4 class="section-title">现场处理内容</h4>
            <table class="inspection-table">
              <thead>
                <tr>
                  <th style="width: 300px;">实际现场故障情况</th>
                  <th style="width: 300px;">故障解决方案</th>
                  <th style="width: 80px;">是否解决</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="(item, index) in viewFieldHandling" :key="index">
                  <td>{{ item.fault_situation || '-' }}</td>
                  <td>{{ item.solution || '-' }}</td>
                  <td>
                    <span :class="item.is_resolved ? 'status-resolved' : 'status-unresolved'">
                      {{ item.is_resolved ? '已解决' : '未解决' }}
                    </span>
                  </td>
                </tr>
                <tr v-if="viewFieldHandling.length === 0">
                  <td colspan="3" style="text-align: center; padding: 20px; color: #999;">暂无现场处理内容</td>
                </tr>
              </tbody>
            </table>
          </div>

          <div class="detail-section">
            <h4 class="section-title">图片附件</h4>
            <div class="image-attachment-section">
              <div class="image-group">
                <label class="image-label">巡检组相关图片</label>
                <div class="image-list">
                  <div v-for="(img, index) in viewInspectionImages" :key="'insp-' + index" class="image-item">
                    <img :src="img" alt="巡检图片" @click="previewImage(img)" />
                  </div>
                  <div v-if="viewInspectionImages.length === 0" class="no-image">暂无图片</div>
                </div>
              </div>
            </div>
          </div>

          <div class="detail-section">
            <h4 class="section-title">用户电子签名</h4>
            <div class="signature-area">
              <div v-if="viewSignature" class="signature-image">
                <img :src="viewSignature" alt="电子签名" />
              </div>
              <div v-else class="no-signature">暂无签名</div>
            </div>
          </div>

          <div class="detail-section">
            <h4 class="section-title">内部确认</h4>
            <div class="confirmation-list">
              <div v-for="(record, index) in viewConfirmationRecords" :key="index" class="confirmation-item">
                <span class="confirmation-time">{{ record.time }}</span>
                <span class="confirmation-user">{{ record.user }}</span>
                <span :class="['confirmation-status', record.status === '已确认' ? 'status-confirmed' : record.status === '已退回' ? 'status-returned' : 'status-submitted']">
                  {{ record.status }}
                </span>
                <span v-if="record.reason" class="confirmation-reason">{{ record.reason }}</span>
              </div>
              <div v-if="viewConfirmationRecords.length === 0" class="no-confirmation">暂无确认记录</div>
            </div>
          </div>
        </div>
        <div class="modal-footer">
          <button class="btn btn-cancel" @click="closeViewModal">取消</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script lang="ts">
import { defineComponent, ref, onMounted, reactive, watch, computed } from 'vue'
import { ElMessageBox } from 'element-plus'
import { workOrderService, type WorkOrder } from '@/services/workOrder'
import { projectInfoService, type ProjectInfo } from '@/services/projectInfo'
import Toast from '@/components/Toast.vue'
import SearchInput from '@/components/SearchInput.vue'
import { PLAN_TYPES, WORK_STATUS, formatDate as formatDateUtil, formatDateTime as formatDateTimeUtil } from '@/config/constants'

interface PlanItem {
  id: number
  plan_id: string
  plan_type: string
  order_type_code: string
  project_id: string
  project_name: string
  plan_start_date: string
  plan_end_date: string
  client_name: string
  maintenance_personnel: string
  status: string
  remarks?: string
}

export default defineComponent({
  name: 'WorkPlanManagement',
  components: {
    Toast,
    SearchInput
  },
  setup() {
    const planTypes = [PLAN_TYPES.PERIODIC_MAINTENANCE, PLAN_TYPES.TEMPORARY_REPAIR, PLAN_TYPES.SPOT_WORK]
    const currentPage = ref(0)
    const pageSize = ref(10)
    const jumpPage = ref(1)
    const loading = ref(false)
    const totalElements = ref(0)
    const totalPages = ref(0)
    const isViewModalOpen = ref(false)

    const toast = reactive({
      visible: false,
      message: '',
      type: 'success' as 'success' | 'error' | 'warning' | 'info'
    })

    const searchForm = ref({
      project_name: '',
      client_name: ''
    })

    const viewData = reactive({
      id: 0,
      plan_id: '',
      plan_type: '',
      project_id: '',
      project_name: '',
      plan_start_date: '',
      plan_end_date: '',
      client_name: '',
      client_contact: '',
      client_contact_info: '',
      client_contact_position: '',
      address: '',
      maintenance_personnel: '',
      status: '',
      remarks: '',
      created_at: '',
      updated_at: '',
      maintenance_cycle: '',
      project_start_date: '',
      project_end_date: '',
      remainingTime: ''
    })

    const viewInspectionItems = ref<Array<{
      inspection_item: string
      inspection_content: string
      check_requirement: string
      brief_description: string
      is_normal: boolean
    }>>([])

    const viewFieldHandling = ref<Array<{
      fault_situation: string
      solution: string
      is_resolved: boolean
    }>>([])

    const viewInspectionImages = ref<string[]>([])
    const viewSignature = ref('')
    const viewConfirmationRecords = ref<Array<{
      time: string
      user: string
      status: string
      reason?: string
    }>>([])

    const planData = ref<PlanItem[]>([])

    const displayedPages = computed(() => {
      const pages: number[] = []
      const start = Math.max(1, currentPage.value - 2)
      const end = Math.min(totalPages.value, start + 4)
      for (let i = start; i <= end; i++) {
        pages.push(i)
      }
      return pages
    })

    const showToast = (message: string, type: 'success' | 'error' | 'warning' | 'info' = 'success') => {
      toast.message = message
      toast.type = type
      toast.visible = true
    }

    const formatDate = (dateStr: string) => {
      return formatDateUtil(dateStr)
    }

    const formatDateTime = (dateStr: string) => {
      return formatDateTimeUtil(dateStr)
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

    const getPlanTypeClass = (planType: string) => {
      switch (planType) {
        case PLAN_TYPES.PERIODIC_MAINTENANCE:
        case PLAN_TYPES.PERIODIC_INSPECTION:
          return 'type-inspection'
        case PLAN_TYPES.TEMPORARY_REPAIR:
          return 'type-repair'
        case PLAN_TYPES.SPOT_WORK:
          return 'type-spot'
        default:
          return ''
      }
    }

    const getOrderTypeClass = (orderTypeCode: string) => {
      switch (orderTypeCode) {
        case 'inspection':
          return 'type-inspection'
        case 'repair':
          return 'type-repair'
        case 'spotwork':
          return 'type-spot'
        default:
          return ''
      }
    }

    const getStatusClass = (status: string) => {
      switch (status) {
        case WORK_STATUS.NOT_STARTED:
        case '待执行':
        case '未进行':
          return 'status-pending'
        case WORK_STATUS.PENDING_CONFIRM:
        case '待确认':
          return 'status-waiting'
        case WORK_STATUS.IN_PROGRESS:
          return 'status-in-progress'
        case WORK_STATUS.COMPLETED:
        case '已完成':
        case '已确认':
          return 'status-completed'
        case WORK_STATUS.CANCELLED:
          return 'status-cancelled'
        case '已退回':
          return 'status-returned'
        default:
          return ''
      }
    }

    const loadData = async () => {
      loading.value = true
      try {
        const response = await workOrderService.getList({
          page: currentPage.value,
          size: pageSize.value,
          project_name: searchForm.value.project_name || undefined,
          client_name: searchForm.value.client_name || undefined
        })
        
        if (response.code === 200) {
          planData.value = response.data.content.map((item: WorkOrder) => ({
            id: item.id,
            plan_id: item.order_id,
            plan_type: item.order_type || '定期巡检单',
            order_type_code: item.order_type_code || 'inspection',
            project_id: item.project_id,
            project_name: item.project_name,
            plan_start_date: item.plan_start_date,
            plan_end_date: item.plan_end_date,
            client_name: item.client_name || '',
            maintenance_personnel: item.maintenance_personnel || '',
            status: item.status || '未进行',
            remarks: item.remarks || ''
          }))
          totalElements.value = response.data.totalElements
          totalPages.value = response.data.totalPages
        } else {
          showToast(response.message || '加载数据失败', 'error')
        }
      } catch (error: any) {
        showToast(error.message || '加载数据失败，请检查网络连接', 'error')
      } finally {
        loading.value = false
      }
    }

    const handleSearch = () => {
      currentPage.value = 0
      loadData()
    }

    const handleReset = () => {
      searchForm.value = {
        project_name: '',
        client_name: ''
      }
      currentPage.value = 0
      loadData()
    }

    onMounted(() => {
      loadData()
      window.addEventListener('user-changed', handleUserChanged)
    })

    const handleUserChanged = () => {
      loadData()
    }

    watch([currentPage, pageSize], () => {
      loadData()
    })

    const handleView = async (item: PlanItem) => {
      viewData.id = item.id
      viewData.plan_id = item.plan_id
      viewData.plan_type = item.plan_type
      viewData.project_id = item.project_id
      viewData.project_name = item.project_name
      viewData.plan_start_date = item.plan_start_date
      viewData.plan_end_date = item.plan_end_date
      viewData.client_name = item.client_name || ''
      viewData.client_contact = ''
      viewData.client_contact_info = ''
      viewData.client_contact_position = ''
      viewData.address = ''
      viewData.maintenance_personnel = item.maintenance_personnel || ''
      viewData.status = item.status
      viewData.remarks = item.remarks || ''
      viewData.created_at = ''
      viewData.updated_at = ''
      viewData.project_start_date = item.plan_start_date
      viewData.project_end_date = item.plan_end_date
      viewData.maintenance_cycle = ''
      viewData.remainingTime = '-'
      
      viewInspectionItems.value = []
      viewFieldHandling.value = []
      viewInspectionImages.value = []
      viewSignature.value = ''
      viewConfirmationRecords.value = []
      
      try {
        const projectResponse = await projectInfoService.getAll()
        if (projectResponse.code === 200 && projectResponse.data) {
          const project = projectResponse.data.find((p: ProjectInfo) => p.project_id === item.project_id)
          if (project) {
            viewData.project_name = project.project_name || viewData.project_name
            viewData.client_name = project.client_name || viewData.client_name
            viewData.client_contact = project.client_contact || ''
            viewData.client_contact_info = project.client_contact_info || ''
            viewData.client_contact_position = project.client_contact_position || ''
            viewData.address = project.address || ''
            viewData.remainingTime = calculateRemainingTime(project.maintenance_end_date)
          }
        }
      } catch (error) {
        console.error('获取项目信息失败:', error)
      }
      
      try {
        const response = await maintenancePlanService.getByProjectId(item.project_id)
        if (response.code === 200 && response.data) {
          viewInspectionItems.value = response.data.map((plan: any) => ({
            inspection_item: plan.plan_id,
            inspection_content: plan.maintenance_content || '',
            check_requirement: plan.maintenance_requirements || '',
            brief_description: plan.remarks || '',
            is_normal: plan.execution_status === WORK_STATUS.COMPLETED
          }))
        }
      } catch (error) {
        console.error('获取巡检内容失败:', error)
      }
      
      isViewModalOpen.value = true
    }

    const closeViewModal = () => {
      isViewModalOpen.value = false
    }

    const handleExport = (item: PlanItem) => {
      showToast('导出功能开发中', 'info')
    }

    const handleJump = () => {
      const page = parseInt(String(jumpPage.value))
      if (page >= 1 && page <= totalPages.value) {
        currentPage.value = page - 1
      }
    }

    const previewImage = (img: string) => {
      window.open(img, '_blank')
    }

    return {
      planTypes,
      currentPage,
      pageSize,
      jumpPage,
      loading,
      totalElements,
      totalPages,
      displayedPages,
      isViewModalOpen,
      toast,
      searchForm,
      planData,
      viewData,
      viewInspectionItems,
      viewFieldHandling,
      viewInspectionImages,
      viewSignature,
      viewConfirmationRecords,
      formatDate,
      formatDateTime,
      getPlanTypeClass,
      getOrderTypeClass,
      getStatusClass,
      getRemainingTimeClass,
      WORK_STATUS,
      PLAN_TYPES,
      handleSearch,
      handleReset,
      handleView,
      closeViewModal,
      handleExport,
      handleJump,
      showToast,
      previewImage
    }
  }
})
</script>

<style scoped>
.work-plan-page {
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

.action-buttons {
  display: flex;
  gap: 12px;
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

.btn {
  padding: 8px 16px;
  border: none;
  border-radius: 4px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-add {
  background: #4caf50;
  color: #fff;
}

.btn-add:hover {
  background: #45a049;
}

.btn-reset {
  background: #f5f5f5;
  color: #666;
  border: 1px solid #d0d7de;
}

.btn-reset:hover {
  background: #e0e0e0;
}

.btn-search {
  background: #1976d2;
  color: #fff;
}

.btn-search:hover {
  background: #1565c0;
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
  color: #1976d2;
}

.action-edit:hover {
  color: #1565c0;
}

.action-confirm {
  color: #4caf50;
}

.action-confirm:hover {
  color: #45a049;
}

.action-export {
  color: #ff9800;
}

.action-export:hover {
  color: #f57c00;
}

.action-delete {
  color: #f44336;
}

.action-delete:hover {
  color: #d32f2f;
}

.type-badge {
  display: inline-block;
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 12px;
  font-weight: 500;
}

.type-inspection {
  background: #e3f2fd;
  color: #1976d2;
}

.type-repair {
  background: #fff3e0;
  color: #f57c00;
}

.type-spot {
  background: #e8f5e9;
  color: #388e3c;
}

.status-badge {
  display: inline-block;
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 12px;
  font-weight: 500;
}

.status-pending {
  background: #fff3cd;
  color: #856404;
}

.status-waiting {
  background: #fff7e0;
  color: #f57c00;
}

.status-in-progress {
  background: #e3f2fd;
  color: #1976d2;
}

.status-completed {
  background: #e8f5e9;
  color: #2e7d32;
}

.status-cancelled {
  background: #ffebee;
  color: #c62828;
}

.status-returned {
  background: #fce4ec;
  color: #c2185b;
}

.remaining-normal {
  color: #388E3C;
  font-weight: 500;
}

.remaining-expired {
  color: #D32F2F;
  font-weight: 600;
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

.modal-container {
  background: #fff;
  border-radius: 8px;
  width: 900px;
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
  border-bottom: 1px solid #e0e0e0;
}

.modal-title {
  font-size: 18px;
  font-weight: 600;
  color: #333;
  margin: 0;
}

.modal-close {
  width: 32px;
  height: 32px;
  border: none;
  background: none;
  font-size: 24px;
  color: #999;
  cursor: pointer;
  transition: color 0.15s;
  display: flex;
  align-items: center;
  justify-content: center;
}

.modal-close:hover {
  color: #333;
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
  min-height: 80px;
  padding: 4px 0;
}

.form-item-full {
  display: flex;
  flex-direction: column;
  gap: 8px;
  padding: 4px 0;
}

.form-label {
  font-size: 14px;
  font-weight: 500;
  color: #424242;
}

.required {
  color: #D32F2F;
  margin-right: 4px;
}

.form-input {
  padding: 8px 12px;
  border: 1px solid #e0e0e0;
  border-radius: 3px;
  font-size: 14px;
  color: #333;
  background: #fff;
  transition: border-color 0.15s;
}

.form-input:focus {
  outline: none;
  border-color: #1976d2;
  box-shadow: 0 0 0 2px rgba(25, 118, 210, 0.1);
}

.form-input::placeholder {
  color: #999;
}

.form-input-readonly {
  background: #f5f5f5;
  color: #666;
  cursor: not-allowed;
}

.form-input-readonly:focus {
  outline: none;
  border-color: #e0e0e0;
  box-shadow: none;
}

.form-value {
  padding: 8px 12px;
  background: #f5f5f5;
  border: 1px solid #e0e0e0;
  border-radius: 3px;
  font-size: 14px;
  color: #333;
  min-height: 36px;
  display: flex;
  align-items: center;
}

.form-value-textarea {
  min-height: 60px;
  align-items: flex-start;
  padding-top: 12px;
  padding-bottom: 12px;
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  padding: 20px 24px;
  border-top: 1px solid #e0e0e0;
}

.btn-cancel {
  background: #fff;
  color: #666;
  border: 1px solid #e0e0e0;
}

.btn-cancel:hover:not(:disabled) {
  background: #f5f5f5;
}

.btn-save {
  background: #1976d2;
  color: #fff;
}

.btn-save:hover:not(:disabled) {
  background: #1565c0;
}

.btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.modal-container-large {
  width: 1100px;
  max-width: 98vw;
}

.detail-section {
  margin-bottom: 24px;
  padding-bottom: 16px;
  border-bottom: 1px solid #e0e0e0;
}

.detail-section:last-child {
  border-bottom: none;
  margin-bottom: 0;
}

.section-title {
  font-size: 16px;
  font-weight: 600;
  color: #333;
  margin: 0 0 16px 0;
  padding-left: 8px;
  border-left: 3px solid #1976d2;
}

.detail-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 16px 24px;
}

.detail-item {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.detail-label {
  font-size: 13px;
  color: #666;
  font-weight: 500;
}

.detail-value {
  font-size: 14px;
  color: #333;
  padding: 8px 12px;
  background: #f9f9f9;
  border-radius: 4px;
  min-height: 20px;
}

.inspection-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 14px;
}

.inspection-table th {
  background: #f5f5f5;
  padding: 12px 10px;
  text-align: left;
  font-weight: 600;
  color: #333;
  border: 1px solid #e0e0e0;
}

.inspection-table td {
  padding: 10px;
  border: 1px solid #e0e0e0;
  color: #666;
}

.inspection-table tbody tr:hover {
  background: #f9f9f9;
}

.status-normal {
  color: #2e7d32;
  font-weight: 500;
}

.status-abnormal {
  color: #c62828;
  font-weight: 500;
}

.status-resolved {
  color: #2e7d32;
  font-weight: 500;
}

.status-unresolved {
  color: #c62828;
  font-weight: 500;
}

.image-attachment-section {
  display: flex;
  gap: 24px;
}

.image-group {
  flex: 1;
}

.image-label {
  font-size: 13px;
  color: #666;
  margin-bottom: 8px;
  display: block;
}

.image-list {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
}

.image-item {
  width: 100px;
  height: 100px;
  border: 1px solid #e0e0e0;
  border-radius: 4px;
  overflow: hidden;
  cursor: pointer;
  transition: transform 0.2s;
}

.image-item:hover {
  transform: scale(1.05);
}

.image-item img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.no-image, .no-signature, .no-confirmation {
  color: #999;
  font-size: 14px;
  padding: 20px;
  text-align: center;
  background: #f9f9f9;
  border-radius: 4px;
}

.signature-area {
  min-height: 80px;
}

.signature-image {
  max-width: 200px;
  max-height: 100px;
}

.signature-image img {
  max-width: 100%;
  max-height: 100px;
}

.confirmation-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.confirmation-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 10px 16px;
  background: #f9f9f9;
  border-radius: 4px;
  font-size: 14px;
}

.confirmation-time {
  color: #666;
  min-width: 120px;
}

.confirmation-user {
  color: #333;
  font-weight: 500;
  min-width: 80px;
}

.confirmation-status {
  padding: 2px 8px;
  border-radius: 4px;
  font-size: 12px;
  font-weight: 500;
}

.status-confirmed {
  background: #e8f5e9;
  color: #2e7d32;
}

.status-returned {
  background: #ffebee;
  color: #c62828;
}

.status-submitted {
  background: #e3f2fd;
  color: #1976d2;
}

.confirmation-reason {
  color: #666;
  margin-left: auto;
}
</style>
