<template>
  <div class="work-plan-page">
    <Toast
      :visible="toast.visible"
      :message="toast.message"
      :type="toast.type"
    />
    <div class="content">
      <div class="search-section">
        <div class="search-form">
          <div class="search-row">
            <div class="search-item">
              <label
                for="search_projectName"
                class="search-label"
              >项目名称：</label>
              <SearchInput
                v-model="searchForm.project_name"
                input-id="search_projectName"
                field-key="WorkPlanManagement_project_name"
                placeholder="请输入项目名称"
                @input="handleSearch"
              />
            </div>
            <div class="search-item">
              <label
                for="search_workOrderId"
                class="search-label"
              >工单编号：</label>
              <SearchInput
                v-model="searchForm.order_id"
                input-id="search_workOrderId"
                field-key="WorkPlanManagement_order_id"
                placeholder="请输入工单编号"
                @input="handleSearch"
              />
            </div>
            <div class="search-item">
              <label
                for="search_planType"
                class="search-label"
              >工单类型：</label>
              <select
                id="search_planType"
                v-model="searchForm.plan_type"
                class="search-select"
                @change="handleSearch"
              >
                <option value="">
                  全部类型
                </option>
                <option
                  v-for="pt in planTypeOptions"
                  :key="pt.value"
                  :value="pt.value"
                >
                  {{ pt.label }}
                </option>
              </select>
            </div>
          </div>
        </div>
        <div class="action-buttons" />
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
              <td
                colspan="11"
                style="text-align: center; padding: 20px"
              >
                加载中...
              </td>
            </tr>
            <tr v-else-if="planData.length === 0">
              <td
                colspan="11"
                style="text-align: center; padding: 20px"
              >
                暂无数据
              </td>
            </tr>
            <tr
              v-for="(item, index) in planData"
              v-else
              :key="item.id"
              :class="{ 'even-row': index % 2 === 0 }"
            >
              <td>{{ currentPage * pageSize + index + 1 }}</td>
              <td>{{ item.plan_id }}</td>
              <td>
                <span
                  :class="getOrderTypeClass(item.order_type_code)"
                  class="type-badge"
                >{{
                  item.plan_type
                }}</span>
              </td>
              <td>{{ item.project_name }}</td>
              <td>{{ item.project_id }}</td>
              <td>{{ formatDate(item.plan_start_date) }}</td>
              <td>{{ formatDate(item.plan_end_date) }}</td>
              <td>{{ item.client_name || '暂无数据' }}</td>
              <td>{{ item.maintenance_personnel || '暂无数据' }}</td>
              <td>
                <span
                  :class="getStatusClass(item.status)"
                  class="status-badge"
                >{{
                  item.status
                }}</span>
              </td>
              <td class="action-cell">
                <a
                  href="#"
                  class="action-link action-view"
                  @click.prevent="handleView(item)"
                >查看</a>
                <a
                  v-if="item.status === WORK_STATUS.COMPLETED"
                  href="#"
                  class="action-link action-export"
                  @click.prevent="handleExport(item)"
                >导出</a>
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
            v-model="pageSize"
            name="pageSize"
            class="page-select"
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
    </div>

    <div
      v-if="isViewModalOpen"
      class="modal-overlay"
      @click.self="closeViewModal"
    >
      <div class="modal-container modal-container-large">
        <div class="modal-header">
          <h3 class="modal-title">
            {{ viewData.plan_type || '工单' }}详情
          </h3>
          <button
            class="modal-close"
            @click="closeViewModal"
          >
            ×
          </button>
        </div>
        <div class="modal-body">
          <div class="detail-section">
            <div class="detail-grid detail-grid-3">
              <div class="detail-item">
                <span class="detail-label">项目名称</span>
                <div class="detail-value">
                  {{ viewData.project_name || '暂无数据' }}
                </div>
              </div>
              <div class="detail-item">
                <span class="detail-label">项目编号</span>
                <div class="detail-value">
                  {{ viewData.project_id || '暂无数据' }}
                </div>
              </div>
              <div class="detail-item">
                <span class="detail-label">合同剩余时间</span>
                <div
                  class="detail-value"
                  :class="getRemainingTimeClass()"
                >
                  {{ viewData.remainingTime || '暂无数据' }}
                </div>
              </div>
              <div class="detail-item">
                <span class="detail-label">客户单位</span>
                <div class="detail-value">
                  {{ viewData.client_name || '暂无数据' }}
                </div>
              </div>
              <div class="detail-item">
                <span class="detail-label">客户联系人</span>
                <div class="detail-value">
                  {{ viewData.client_contact || '暂无数据' }}
                </div>
              </div>
              <div class="detail-item">
                <span class="detail-label">客户联系方式</span>
                <div class="detail-value">
                  {{ viewData.client_contact_info || '暂无数据' }}
                </div>
              </div>
              <div class="detail-item">
                <span class="detail-label">运维人员</span>
                <div class="detail-value">
                  {{ viewData.maintenance_personnel || '暂无数据' }}
                </div>
              </div>
              <div class="detail-item">
                <span class="detail-label">计划开始日期</span>
                <div class="detail-value">
                  {{ formatDate(viewData.plan_start_date) || '暂无数据' }}
                </div>
              </div>
              <div class="detail-item">
                <span class="detail-label">计划结束日期</span>
                <div class="detail-value">
                  {{ formatDate(viewData.plan_end_date) || '暂无数据' }}
                </div>
              </div>
            </div>
          </div>

          <div class="detail-section">
            <h4 class="section-title">
              巡检内容:
            </h4>
            <table class="inspection-table">
              <thead>
                <tr>
                  <th style="width: 60px">
                    序号
                  </th>
                  <th style="width: 150px">
                    巡查项
                  </th>
                  <th style="width: 200px">
                    巡查内容
                  </th>
                  <th style="width: 200px">
                    检查要求
                  </th>
                  <th style="width: 200px">
                    简要说明
                  </th>
                </tr>
              </thead>
              <tbody>
                <tr
                  v-for="(item, index) in viewInspectionItems"
                  :key="index"
                >
                  <td>{{ index + 1 }}</td>
                  <td>{{ item.inspection_item || '暂无数据' }}</td>
                  <td>{{ item.inspection_content || '暂无数据' }}</td>
                  <td>{{ item.check_requirement || '暂无数据' }}</td>
                  <td>{{ item.brief_description || '暂无数据' }}</td>
                </tr>
                <tr v-if="viewInspectionItems.length === 0">
                  <td
                    colspan="5"
                    style="text-align: center; padding: 20px; color: #999"
                  >
                    暂无数据
                  </td>
                </tr>
              </tbody>
            </table>
          </div>

          <div class="detail-section">
            <h4 class="section-title">
              现场处理内容
            </h4>
            <table class="inspection-table">
              <thead>
                <tr>
                  <th style="width: 300px">
                    实际现场故障情况
                  </th>
                  <th style="width: 300px">
                    故障解决方案
                  </th>
                  <th style="width: 80px">
                    是否解决
                  </th>
                </tr>
              </thead>
              <tbody>
                <tr
                  v-for="(item, index) in viewFieldHandling"
                  :key="index"
                >
                  <td>{{ item.fault_situation || '暂无数据' }}</td>
                  <td>{{ item.solution || '暂无数据' }}</td>
                  <td>
                    <span :class="item.is_resolved ? 'status-resolved' : 'status-unresolved'">
                      {{ item.is_resolved ? '已解决' : '未解决' }}
                    </span>
                  </td>
                </tr>
                <tr v-if="viewFieldHandling.length === 0">
                  <td
                    colspan="3"
                    style="text-align: center; padding: 20px; color: #999"
                  >
                    暂无数据
                  </td>
                </tr>
              </tbody>
            </table>
          </div>

          <div class="detail-section">
            <h4 class="section-title">
              图片附件
            </h4>
            <div class="image-attachment-section">
              <div class="image-group">
                <span class="image-label">巡检组相关图片</span>
                <div class="image-list">
                  <div
                    v-for="(img, index) in viewInspectionImages"
                    :key="'insp-' + index"
                    class="image-item"
                  >
                    <img
                      :src="img"
                      alt="巡检图片"
                      loading="lazy"
                      @click="previewImage(img)"
                    >
                  </div>
                  <div
                    v-if="viewInspectionImages.length === 0"
                    class="no-image"
                  >
                    暂无数据
                  </div>
                </div>
              </div>
            </div>
          </div>

          <div class="detail-section">
            <h4 class="section-title">
              用户电子签名
            </h4>
            <div class="signature-area">
              <div
                v-if="viewSignature"
                class="signature-image"
                @click="previewImage(viewSignature)"
              >
                <img
                  :src="viewSignature"
                  alt="电子签名"
                  loading="lazy"
                >
              </div>
              <div
                v-else
                class="no-signature"
              >
                暂无数据
              </div>
            </div>
          </div>

          <div class="detail-section">
            <h4 class="section-title">
              内部确认
            </h4>
            <div class="confirmation-list">
              <div
                v-for="(record, index) in viewConfirmationRecords"
                :key="index"
                class="confirmation-item"
              >
                <span class="confirmation-time">{{ record.time }}</span>
                <span class="confirmation-user">{{ record.user }}</span>
                <span
                  :class="[
                    'confirmation-status',
                    record.status === '已完成'
                      ? 'status-confirmed'
                      : record.status === '已退回'
                        ? 'status-returned'
                        : 'status-submitted',
                  ]"
                >
                  {{ record.status }}
                </span>
                <span
                  v-if="record.reason"
                  class="confirmation-reason"
                >{{ record.reason }}</span>
              </div>
              <div
                v-if="viewConfirmationRecords.length === 0"
                class="no-confirmation"
              >
                暂无数据
              </div>
            </div>
          </div>
        </div>
        <div class="modal-footer">
          <button
            class="btn btn-cancel"
            @click="closeViewModal"
          >
            取消
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script lang="ts">
import { defineComponent, ref, onMounted, reactive, watch, computed } from 'vue'
import { periodicInspectionService } from '@/services/periodicInspection'
import { temporaryRepairService } from '@/services/temporaryRepair'
import { spotWorkService } from '@/services/spotWork'
import { maintenancePlanService } from '@/services/maintenancePlan'
import { workPlanService, type PlanType } from '@/services/workPlan'
import { projectInfoService, type ProjectInfo } from '@/services/projectInfo'
import { operationLogService } from '@/services/operationLog'
import request from '@/api/request'
import { API_ENDPOINTS } from '@/api/endpoints'
import type { OperationLog } from '@/types/api'
import { Toast, SearchInput } from '@sstcp/shared'
import {
  PLAN_TYPES,
  WORK_STATUS,
  formatDate as formatDateUtil,
  formatDateTime as formatDateTimeUtil,
} from '@/config/constants'

// TODO: 工单管理页面 - 考虑加入批量操作功能
// FIXME: 导出功能目前只支持单个工单，需要支持批量导出
// TODO: 工单状态流转逻辑需要更清晰的状态机
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
  execution_result?: string
  signature?: string
}

export default defineComponent({
  name: 'WorkPlanManagement',
  components: {
    Toast,
    SearchInput,
  },
  setup() {
    const parseInspectionItems = (raw: any): any[] => {
      if (Array.isArray(raw)) return raw
      if (typeof raw === 'string') {
        try { return JSON.parse(raw) } catch { return [] }
      }
      if (raw && typeof raw === 'object') {
        try { return Array.isArray(raw) ? raw : [raw] } catch { return [] }
      }
      return []
    }

    const planTypes = [
      PLAN_TYPES.PERIODIC_MAINTENANCE,
      PLAN_TYPES.TEMPORARY_REPAIR,
      PLAN_TYPES.SPOT_WORK,
    ]
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
      type: 'success' as 'success' | 'error' | 'warning' | 'info',
    })

    const searchForm = ref({
      project_name: '',
      order_id: '',
      plan_type: PLAN_TYPES.PERIODIC_INSPECTION,
    })

    const planTypeOptions = [
      { value: PLAN_TYPES.PERIODIC_INSPECTION, label: '定期巡检单' },
      { value: PLAN_TYPES.PERIODIC_MAINTENANCE, label: '定期维保单' },
    ]

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
      remainingTime: '',
    })

    const viewInspectionItems = ref<
      Array<{
        inspection_item: string
        inspection_content: string
        check_requirement: string
        brief_description: string
        is_normal: boolean
      }>
    >([])

    const viewFieldHandling = ref<
      Array<{
        fault_situation: string
        solution: string
        is_resolved: boolean
      }>
    >([])

    const viewInspectionImages = ref<string[]>([])
    const viewSignature = ref('')
    const viewConfirmationRecords = ref<
      Array<{
        time: string
        user: string
        status: string
        reason?: string
      }>
    >([])

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

    const showToast = (
      message: string,
      type: 'success' | 'error' | 'warning' | 'info' = 'success'
    ) => {
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
        case PLAN_TYPES.PERIODIC_INSPECTION:
          return 'type-inspection'
        case PLAN_TYPES.PERIODIC_MAINTENANCE:
          return 'type-maintenance'
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
        case 'maintenance':
          return 'type-maintenance'
        case 'repair':
          return 'type-repair'
        case 'spotwork':
          return 'type-spot'
        default:
          return ''
      }
    }

    const getStatusClass = (status: string) => {
      if (status === '执行中') {
        return 'status-in-progress'
      }
      if (status === '待确认') {
        return 'status-waiting'
      }
      if (status === '已完成') {
        return 'status-completed'
      }
      if (status === '已退回') {
        return 'status-returned'
      }
      return ''
    }

    const loadData = async () => {
      loading.value = true
      try {
        const planType = searchForm.value.plan_type

        if (planType === PLAN_TYPES.PERIODIC_INSPECTION) {
          const response = await periodicInspectionService.getList({
            page: currentPage.value,
            size: pageSize.value,
            project_name: searchForm.value.project_name || undefined,
            inspection_id: searchForm.value.order_id || undefined,
          })

          if (response.code === 200 && response.data) {
            planData.value = (response.data.items || response.data.content || []).map((item: any) => {
              return {
                id: item.id,
                plan_id: item.inspection_id,
                plan_type: '定期巡检单',
                order_type_code: 'inspection',
                project_id: item.project_id,
                project_name: item.project_name,
                plan_start_date: item.plan_start_date,
                plan_end_date: item.plan_end_date,
                client_name: item.client_name || '',
                maintenance_personnel: item.maintenance_personnel || '',
                status: item.status || '执行中',
                remarks: item.remarks || '',
                execution_result: '',
                signature: '',
              }
            })
            totalElements.value = response.data.total ?? response.data.totalElements ?? 0
            totalPages.value = response.data.totalPages ?? 0
          } else {
            showToast(response.message || '加载数据失败', 'error')
          }
        } else if (planType === PLAN_TYPES.PERIODIC_MAINTENANCE) {
          const response = await maintenancePlanService.getList({
            page: currentPage.value,
            size: pageSize.value,
            project_name: searchForm.value.project_name || undefined,
          })

          if (response.code === 200 && response.data) {
            const content = response.data.items || response.data.content || []
            planData.value = content.map((item: any) => {
              return {
                id: item.id,
                plan_id: item.plan_id,
                plan_type: '定期维保单',
                order_type_code: 'maintenance',
                project_id: item.project_id,
                project_name: item.project_name,
                plan_start_date: item.plan_start_date,
                plan_end_date: item.plan_end_date,
                client_name: item.client_name || '',
                maintenance_personnel: item.maintenance_personnel || '',
                status: item.status || item.plan_status || '执行中',
                remarks: item.remarks || '',
                execution_result: '',
                signature: '',
              }
            })
            totalElements.value = response.data.total ?? response.data.totalElements ?? 0
            totalPages.value = response.data.totalPages ?? 0
          } else {
            showToast(response.message || '加载数据失败', 'error')
          }
        } else {
          const response = await workPlanService.getList({
            page: currentPage.value,
            size: pageSize.value,
            project_name: searchForm.value.project_name || undefined,
            plan_id: searchForm.value.order_id || undefined,
            plan_type: (searchForm.value.plan_type as PlanType) || undefined,
          })

          if (response.code === 200 && response.data) {
            planData.value = (response.data.items || response.data.content || []).map((item: any) => {
              return {
                id: item.source_id || item.id,
                plan_id: item.plan_id,
                plan_type: item.plan_type + '单',
                order_type_code: item.order_type_code || (item.plan_type === '定期维保' ? 'maintenance' : 'inspection'),
                project_id: item.project_id,
                project_name: item.project_name,
                plan_start_date: item.plan_start_date,
                plan_end_date: item.plan_end_date,
                client_name: item.client_name || '',
                maintenance_personnel: item.maintenance_personnel || '',
                status: item.status || '执行中',
                remarks: item.remarks || '',
                execution_result: '',
                signature: '',
              }
            })
            totalElements.value = response.data.total ?? response.data.totalElements ?? 0
            totalPages.value = response.data.totalPages ?? 0
          } else {
            showToast(response.message || '加载数据失败', 'error')
          }
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
        order_id: '',
        plan_type: PLAN_TYPES.PERIODIC_INSPECTION,
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
        let detailResponse: any = null
        if (item.order_type_code === 'repair') {
          detailResponse = await temporaryRepairService.getById(item.id)
        } else if (item.order_type_code === 'spotwork') {
          detailResponse = await spotWorkService.getById(item.id)
        } else if (item.order_type_code === 'maintenance') {
          detailResponse = await maintenancePlanService.getById(item.id)
        } else {
          detailResponse = await periodicInspectionService.getById(item.id)
        }
        if (detailResponse.code === 200 && detailResponse.data) {
          const detail = detailResponse.data
          viewData.remarks = detail.remarks || ''
          viewSignature.value = detail.signature || ''

          if (item.order_type_code === 'repair') {
            if (detail.fault_description || detail.solution) {
              viewFieldHandling.value.push({
                fault_situation: detail.fault_description || '',
                solution: detail.solution || '',
                is_resolved: detail.status === '已完成',
              })
            }
            if (detail.photos && Array.isArray(detail.photos)) {
              viewInspectionImages.value = detail.photos
            }
          } else if (item.order_type_code === 'spotwork') {
            if (detail.work_content) {
              viewFieldHandling.value.push({
                fault_situation: detail.work_content || '',
                solution: '',
                is_resolved: detail.status === '已完成',
              })
            }
            if (detail.photos && Array.isArray(detail.photos)) {
              viewInspectionImages.value = detail.photos
            }
          } else if (item.order_type_code === 'maintenance') {
            if (detail.plan_name || detail.remarks) {
              viewFieldHandling.value.push({
                fault_situation: detail.plan_name || '',
                solution: detail.remarks || '',
                is_resolved: detail.plan_status === '已完成',
              })
            }
          } else {
            if (detail.execution_result || detail.remarks) {
              viewFieldHandling.value.push({
                fault_situation: detail.execution_result || '',
                solution: detail.remarks || '',
                is_resolved: true,
              })
            }
          }
        }
      } catch (error: any) {
        console.error('获取工单详情失败:', error)
        if (error?.status === 404) {
          showToast('工单不存在或已被删除', 'error')
        }
      }

      try {
        if (item.order_type_code === 'inspection' || item.order_type_code === 'maintenance') {
          const recordsResponse = await request.get<Array<{ photos?: string[] }>>(
            API_ENDPOINTS.PERIODIC_INSPECTION.INSPECTION_RECORDS(item.plan_id)
          )
          if (recordsResponse.code === 200 && recordsResponse.data) {
            const allPhotos: string[] = []
            recordsResponse.data.forEach((record: { photos?: string[] }) => {
              if (record.photos && Array.isArray(record.photos)) {
                allPhotos.push(...record.photos)
              }
            })
            viewInspectionImages.value = allPhotos
          }
        }
      } catch (error) {
        console.error('获取巡检记录失败:', error)
      }

      try {
        const projectResponse = await projectInfoService.getAll()
        if (projectResponse.code === 200 && projectResponse.data) {
          const project = projectResponse.data.find(
            (p: ProjectInfo) => p.project_id === item.project_id
          )
          if (project) {
            viewData.project_name = project.project_name || viewData.project_name
            viewData.client_name = project.client_name || viewData.client_name
            viewData.client_contact = project.client_contact || ''
            viewData.client_contact_info = project.client_contact_info || ''
            viewData.client_contact_position = project.client_contact_position || ''
            viewData.address = project.address || ''
            viewData.remainingTime = calculateRemainingTime(project.maintenance_end_date ?? '')
          }
        }
      } catch (error) {
        console.error('获取项目信息失败:', error)
      }

      try {
        if (item.order_type_code === 'inspection' || item.order_type_code === 'maintenance') {
          const response = await maintenancePlanService.getByProjectId(item.project_id)
        if (response.code === 200 && response.data) {
          const orderStartDate = item.plan_start_date ? new Date(item.plan_start_date) : null
          const orderEndDate = item.plan_end_date ? new Date(item.plan_end_date) : null
          if (orderStartDate) orderStartDate.setHours(0, 0, 0, 0)
          if (orderEndDate) orderEndDate.setHours(0, 0, 0, 0)

          const filteredPlans = response.data.filter((plan: any) => {
            if (!plan.plan_start_date || !plan.plan_end_date) return false
            const planStartDate = new Date(plan.plan_start_date)
            planStartDate.setHours(0, 0, 0, 0)
            const planEndDate = new Date(plan.plan_end_date)
            planEndDate.setHours(0, 0, 0, 0)
            if (orderStartDate && orderEndDate) {
              return orderStartDate <= planEndDate && orderEndDate >= planStartDate
            }
            return false
          })

          const allItems: any[] = []
          filteredPlans.forEach((plan: any) => {
            if (plan.inspection_items) {
              try {
                const items = parseInspectionItems(plan.inspection_items)
                items.forEach((item: any) => {
                  allItems.push({
                    inspection_item: item.inspection_item || '',
                    inspection_content: item.inspection_content || '',
                    check_requirement: item.check_requirements || '',
                    brief_description: item.brief_description || '',
                    is_normal: plan.execution_status === WORK_STATUS.COMPLETED,
                  })
                })
              } catch (e) {
                console.error('解析巡查项数据失败:', e)
              }
            }
          })

          viewInspectionItems.value = allItems
        }
        }
      } catch (error) {
        console.error('获取巡检内容失败:', error)
      }

      try {
        const workOrderTypeMap: Record<string, string> = {
          inspection: 'periodic_inspection',
          maintenance: 'periodic_maintenance',
          repair: 'temporary_repair',
          spotwork: 'spot_work',
        }
        const logResponse = await operationLogService.getByWorkOrder({
          work_order_type: workOrderTypeMap[item.order_type_code] || 'periodic_inspection',
          work_order_id: item.id,
        })
        if (logResponse.code === 200 && logResponse.data) {
          viewConfirmationRecords.value = logResponse.data.map((log: OperationLog) => ({
            time: formatDateTime(log.created_at),
            user: log.operator_name || '暂无数据',
            status: log.operation_type_name || '暂无数据',
            reason: log.operation_remark || undefined,
          }))
        }
      } catch (error) {
        console.error('获取操作日志失败:', error)
      }

      isViewModalOpen.value = true
    }

    const closeViewModal = () => {
      isViewModalOpen.value = false
    }

    const handleExport = async (item: PlanItem) => {
      let defaultFilename = ''
      let exportUrl = ''
      
      switch (item.order_type_code) {
        case 'inspection':
          exportUrl = `/api/v1/export/periodic-inspection/${item.id}`
          defaultFilename = `定期巡检单_${item.plan_id}.pdf`
          break
        case 'maintenance':
          exportUrl = `/api/v1/export/periodic-maintenance/${item.id}`
          defaultFilename = `定期维保单_${item.plan_id}.pdf`
          break
        case 'repair':
          exportUrl = `/api/v1/export/temporary-repair/${item.id}`
          defaultFilename = `临时维修单_${item.plan_id}.pdf`
          break
        case 'spotwork':
          exportUrl = `/api/v1/export/spot-work/${item.id}`
          defaultFilename = `零星用工单_${item.plan_id}.pdf`
          break
        default:
          showToast('不支持的工单类型', 'error')
          return
      }

      try {
        const token = localStorage.getItem('token')

        const response = await fetch(exportUrl, {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        })

        if (!response.ok) {
          let errorMsg = '导出失败'
          try {
            const error = await response.json()
            errorMsg = error.detail || error.message || errorMsg
          } catch {
            errorMsg = `导出失败 (${response.status})`
          }
          showToast(errorMsg, 'error')
          return
        }

        const contentType = response.headers.get('content-type') || ''
        if (!contentType.includes('application/pdf') && !contentType.includes('octet-stream')) {
          showToast('服务器返回了非PDF文件', 'error')
          return
        }

        const blob = await response.blob()

        if (blob.size === 0) {
          showToast('导出的PDF文件为空', 'error')
          return
        }

        let fileHandle: any = null

        if ('showSaveFilePicker' in window && window.isSecureContext) {
          try {
            fileHandle = await (window as any).showSaveFilePicker({
              suggestedName: defaultFilename,
              types: [{
                description: 'PDF文件',
                accept: { 'application/pdf': ['.pdf'] },
              }],
            })
          } catch (err: any) {
            if (err.name === 'AbortError') {
              return
            }
          }
        }

        if (fileHandle) {
          const writable = await fileHandle.createWritable()
          await writable.write(blob)
          await writable.close()
          showToast('导出成功', 'success')
        } else {
          const url = window.URL.createObjectURL(blob)
          const a = document.createElement('a')
          a.href = url
          a.download = defaultFilename
          document.body.appendChild(a)
          a.click()
          document.body.removeChild(a)
          setTimeout(() => window.URL.revokeObjectURL(url), 100)
          showToast('导出成功', 'success')
        }
      } catch (error) {
        console.error('导出失败:', error)
        showToast('导出失败，请检查网络连接', 'error')
      }
    }

    const handleJump = () => {
      const page = parseInt(String(jumpPage.value))
      if (page >= 1 && page <= totalPages.value) {
        currentPage.value = page - 1
      }
    }

    const previewImage = (img: string) => {
      if (!img) return
      if (img.startsWith('data:')) {
        const newWindow = window.open('', '_blank')
        if (newWindow) {
          newWindow.document.write(`
            <!DOCTYPE html>
            <html>
            <head><title>图片预览</title></head>
            <body style="margin:0;display:flex;justify-content:center;align-items:center;min-height:100vh;background:#f5f5f5;">
              <img src="${img}" style="max-width:100%;max-height:100vh;object-fit:contain;" />
            </body>
            </html>
          `)
          newWindow.document.close()
        }
      } else {
        window.open(img, '_blank')
      }
    }

    return {
      planTypes,
      planTypeOptions,
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
      previewImage,
    }
  },
})
</script>

<style scoped>
.work-plan-page {
  background: var(--color-bg-card);
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
  color: var(--color-text-secondary);
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
  border-color: var(--color-primary);
  box-shadow: 0 0 0 2px rgba(25, 118, 210, 0.1);
}

.search-select {
  padding: 8px 12px;
  border: 1px solid #d0d7de;
  border-radius: 4px;
  font-size: 14px;
  outline: none;
  min-width: 140px;
  background-color: #fff;
  cursor: pointer;
  appearance: auto;
}

.search-select:focus {
  border-color: var(--color-primary);
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
  background: var(--color-success);
  color: var(--color-bg-card);
}

.btn-add:hover {
  background: #45a049;
}

.btn-reset {
  background: var(--color-bg-page);
  color: var(--color-text-secondary);
  border: 1px solid #d0d7de;
}

.btn-reset:hover {
  background: var(--color-border);
}

.btn-search {
  background: var(--color-primary);
  color: var(--color-bg-card);
}

.btn-search:hover {
  background: var(--color-primary-dark);
}

.table-section {
  background: var(--color-bg-card);
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
  background: var(--color-bg-page);
}

.data-table th {
  padding: 12px 8px;
  text-align: left;
  font-size: 14px;
  font-weight: 600;
  color: var(--color-text-primary);
  border-bottom: 2px solid var(--color-border);
  white-space: nowrap;
}

.data-table tbody tr {
  transition: background 0.15s;
}

.data-table tbody tr:hover {
  background: #f9f9f9;
}

.data-table tbody tr.even-row {
  background: var(--color-bg-page);
}

.data-table td {
  padding: 12px 8px;
  border-bottom: 1px solid var(--color-border);
  font-size: 14px;
  color: var(--color-text-secondary);
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
  color: var(--color-primary);
}

.action-view:hover {
  color: var(--color-primary-dark);
}

.action-edit {
  color: var(--color-primary);
}

.action-edit:hover {
  color: var(--color-primary-dark);
}

.action-confirm {
  color: var(--color-success);
}

.action-confirm:hover {
  color: #45a049;
}

.action-export {
  color: var(--color-warning);
}

.action-export:hover {
  color: var(--color-warning);
}

.action-delete {
  color: var(--color-danger);
}

.action-delete:hover {
  color: var(--color-danger);
}

.type-badge {
  display: inline-block;
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 12px;
  font-weight: 500;
}

.type-inspection {
  background: var(--color-primary-subtle);
  color: var(--color-primary);
}

.type-repair {
  background: var(--color-warning-subtle);
  color: var(--color-warning);
}

.type-spot {
  background: var(--color-success-subtle);
  color: var(--color-success);
}

.type-maintenance {
  background: #e8eaf6;
  color: #3949ab;
}

.status-badge {
  display: inline-block;
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 12px;
  font-weight: 500;
}

.status-pending {
  background: var(--color-bg-card)3cd;
  color: #856404;
}

.status-waiting {
  background: var(--color-bg-card)7e0;
  color: var(--color-warning);
}

.status-in-progress {
  background: var(--color-primary-subtle);
  color: var(--color-primary);
}

.status-completed {
  background: var(--color-success-subtle);
  color: var(--color-success);
}

.status-cancelled {
  background: var(--color-danger-subtle);
  color: var(--color-danger);
}

.status-returned {
  background: #fce4ec;
  color: #c2185b;
}

.remaining-normal {
  color: var(--color-success);
  font-weight: 500;
}

.remaining-expired {
  color: var(--color-danger);
  font-weight: 600;
}

.pagination-section {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 0;
  border-top: 1px solid var(--color-border);
}

.pagination-info {
  font-size: 14px;
  color: var(--color-text-secondary);
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
  background: var(--color-bg-card);
  font-size: 14px;
  cursor: pointer;
  transition: all 0.2s;
}

.page-btn:hover:not(:disabled) {
  background: var(--color-bg-page);
  border-color: var(--color-primary);
}

.page-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.page-btn.page-num {
  min-width: 36px;
}

.page-btn.active {
  background: var(--color-primary);
  color: var(--color-bg-card);
  border-color: var(--color-primary);
}

.page-select {
  padding: 6px 8px;
  border: 1px solid #d0d7de;
  border-radius: 4px;
  font-size: 14px;
  background: var(--color-bg-card);
  cursor: pointer;
  outline: none;
}

.page-jump {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
  color: var(--color-text-secondary);
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
  background: var(--color-primary);
  color: var(--color-bg-card);
}

.page-btn.page-go:hover {
  background: var(--color-primary-dark);
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
  color: var(--color-text-regular);
}

.required {
  color: var(--color-danger);
  margin-right: 4px;
}

.form-input {
  padding: 8px 12px;
  border: 1px solid var(--color-border);
  border-radius: 3px;
  font-size: 14px;
  color: var(--color-text-primary);
  background: var(--color-bg-card);
  transition: border-color 0.15s;
}

.form-input:focus {
  outline: none;
  border-color: var(--color-primary);
  box-shadow: 0 0 0 2px rgba(25, 118, 210, 0.1);
}

.form-input::placeholder {
  color: var(--color-text-placeholder);
}

.form-input-readonly {
  background: var(--color-bg-page);
  color: var(--color-text-secondary);
  cursor: not-allowed;
}

.form-input-readonly:focus {
  outline: none;
  border-color: var(--color-border);
  box-shadow: none;
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
  border-top: 1px solid var(--color-border);
}

.btn-cancel {
  background: var(--color-bg-card);
  color: var(--color-text-secondary);
  border: 1px solid var(--color-border);
}

.btn-cancel:hover:not(:disabled) {
  background: var(--color-bg-page);
}

.btn-save {
  background: var(--color-primary);
  color: var(--color-bg-card);
}

.btn-save:hover:not(:disabled) {
  background: var(--color-primary-dark);
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
  border-bottom: 1px solid var(--color-border);
}

.detail-section:last-child {
  border-bottom: none;
  margin-bottom: 0;
}

.section-title {
  font-size: 16px;
  font-weight: 600;
  color: var(--color-text-primary);
  margin: 0 0 16px 0;
  padding-left: 8px;
  border-left: 3px solid var(--color-primary);
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
  color: var(--color-text-secondary);
  font-weight: 500;
}

.detail-value {
  font-size: 14px;
  color: var(--color-text-primary);
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
  background: var(--color-bg-page);
  padding: 12px 10px;
  text-align: left;
  font-weight: 600;
  color: var(--color-text-primary);
  border: 1px solid var(--color-border);
}

.inspection-table td {
  padding: 10px;
  border: 1px solid var(--color-border);
  color: var(--color-text-secondary);
}

.inspection-table tbody tr:hover {
  background: #f9f9f9;
}

.status-normal {
  color: var(--color-success);
  font-weight: 500;
}

.status-abnormal {
  color: var(--color-danger);
  font-weight: 500;
}

.status-resolved {
  color: var(--color-success);
  font-weight: 500;
}

.status-unresolved {
  color: var(--color-danger);
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
  color: var(--color-text-secondary);
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
  border: 1px solid var(--color-border);
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

.no-image,
.no-signature,
.no-confirmation {
  color: var(--color-text-placeholder);
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
  color: var(--color-text-secondary);
  min-width: 120px;
}

.confirmation-user {
  color: var(--color-text-primary);
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
  background: var(--color-success-subtle);
  color: var(--color-success);
}

.status-returned {
  background: var(--color-danger-subtle);
  color: var(--color-danger);
}

.status-submitted {
  background: var(--color-primary-subtle);
  color: var(--color-primary);
}

.confirmation-reason {
  color: var(--color-text-secondary);
  margin-left: auto;
}
</style>
