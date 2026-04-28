﻿﻿﻿﻿﻿﻿﻿﻿﻿﻿﻿﻿﻿﻿﻿﻿<template>
  <div class="temporary-repair-page">
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
              <label for="search_projectName" class="search-label">项目名称：</label>
              <SearchInput
              input-id="search_projectName"
                v-model="searchForm.project_name"
                field-key="TemporaryRepairQuery_project_name"
                placeholder="请输入项目名称"
                @input="handleSearch"
              />
            </div>
            <div class="search-item">
              <label for="search_workOrderId" class="search-label">工单编号：</label>
              <SearchInput
              input-id="search_workOrderId"
                v-model="searchForm.repair_id"
                field-key="TemporaryRepairQuery_repair_id"
                placeholder="请输入工单编号"
                @input="handleSearch"
              />
            </div>
          </div>
        </div>
        <div class="action-buttons">
          <button
            class="btn btn-add"
            @click="handleAdd"
          >
            新增临时工单
          </button>
        </div>
      </div>

      <div class="table-section">
        <table class="data-table">
          <thead>
            <tr>
              <th>序号</th>
              <th>项目编号</th>
              <th>项目名称</th>
              <th>工单编号</th>
              <th>计划开始日期</th>
              <th>计划结束日期</th>
              <th>客户单位</th>
              <th>运维人员</th>
              <th>维修内容</th>
              <th>操作</th>
            </tr>
          </thead>
          <tbody>
            <tr v-if="loading">
              <td
                colspan="10"
                style="text-align: center; padding: 20px"
              >
                加载中...
              </td>
            </tr>
            <tr v-else-if="repairData.length === 0">
              <td
                colspan="10"
                style="text-align: center; padding: 20px"
              >
                暂无数据
              </td>
            </tr>
            <tr
              v-for="(item, index) in repairData"
              v-else
              :key="item.id"
              :class="{ 'even-row': index % 2 === 0 }"
            >
              <td>{{ (currentPage - 1) * pageSize + index + 1 }}</td>
              <td>{{ item.project_id }}</td>
              <td>{{ item.project_name }}</td>
              <td>{{ item.repair_id }}</td>
              <td>{{ formatDate(item.plan_start_date) }}</td>
              <td>{{ formatDate(item.plan_end_date) }}</td>
              <td>{{ item.client_name || '-' }}</td>
              <td>{{ item.maintenance_personnel || '-' }}</td>
              <td>{{ item.remarks || '-' }}</td>
              <td class="action-cell">
                <a
                  href="#"
                  class="action-link action-view"
                  @click.prevent="handleView(item)"
                >查看</a>
                <a
                  v-if="canEditWork(item)"
                  href="#"
                  class="action-link action-edit"
                  @click.prevent="handleEdit(item)"
                >编辑</a>
                <a
                  v-if="isAdmin && item.status === WORK_STATUS.PENDING_CONFIRM"
                  href="#"
                  class="action-link action-reject"
                  @click.prevent="handleReject(item)"
                >退回</a>
                <a
                  v-if="canRecallWork(item)"
                  href="#"
                  class="action-link action-recall"
                  @click.prevent="handleRecall(item)"
                >撤回</a>
                <a
                  v-if="item.status === WORK_STATUS.COMPLETED"
                  href="#"
                  class="action-link action-export"
                  @click.prevent="handleExport(item)"
                >导出</a>
                <a
                  v-if="canDelete"
                  href="#"
                  class="action-link action-delete"
                  @click.prevent="handleDelete(item)"
                >删除</a>
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
            :disabled="currentPage === 1"
            @click="currentPage--"
          >
            &lt;
          </button>
          <button
            v-for="page in totalPages"
            :key="page"
            class="page-btn page-num"
            :class="{ active: page === currentPage }"
            @click="currentPage = page"
          >
            {{ page }}
          </button>
          <button
            class="page-btn page-nav"
            :disabled="currentPage === totalPages"
            @click="currentPage++"
          >
            &gt;
          </button>
          <select
            id="pageSize"
            name="pageSize"
            v-model="pageSize"
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
    </div>

    <div
      v-if="isAddModalOpen"
      class="modal-overlay"
      @click.self="closeAddModal"
    >
      <div class="modal-container">
        <div class="modal-header">
          <h3 class="modal-title">
            新增临时工单
          </h3>
          <button
            class="modal-close"
            @click="closeAddModal"
          >
            ×
          </button>
        </div>
        <div class="modal-body">
          <div class="form-grid">
            <div class="form-column">
              <div class="form-item">
                <label for="projectName" class="form-label"> <span class="required">*</span> 项目名称 </label>
                <select id="projectName" name="projectName"
                  v-model="formData.project_name"
                  class="form-input"
                  @change="handleProjectChange"
                >
                  <option value="">
                    请选择项目
                  </option>
                  <option
                    v-for="project in projectList"
                    :key="project.id"
                    :value="project.project_name"
                  >
                    {{ project.project_name }}
                  </option>
                </select>
              </div>
              <div class="form-item">
                <label for="planStartDate" class="form-label"> <span class="required">*</span> 计划开始日期 </label>
                <input id="planStartDate" name="planStartDate"
                  v-model="formData.plan_start_date"
                  type="date"
                  class="form-input"
                >
              </div>
              <div class="form-item">
                <label for="clientContact" class="form-label"> <span class="required">*</span> 客户联系人 </label>
                <input id="clientContact" name="clientContact"
                  v-model="formData.client_contact"
                  type="text"
                  class="form-input form-input-readonly"
                  placeholder="请输入客户联系人"
                  readonly
                >
              </div>
            </div>
            <div class="form-column">
              <div class="form-item">
                <label for="maintenancePersonnel" class="form-label"> <span class="required">*</span> 运维人员 </label>
                <select id="maintenancePersonnel" name="maintenancePersonnel"
                  v-model="formData.maintenance_personnel"
                  class="form-input"
                >
                  <option value="">
                    请选择
                  </option>
                  <option
                    v-for="person in personnelList"
                    :key="person.id"
                    :value="person.name"
                  >
                    {{ person.name }}
                  </option>
                </select>
              </div>
              <div class="form-item">
                <label for="planEndDate" class="form-label"> <span class="required">*</span> 计划结束日期 </label>
                <input id="planEndDate" name="planEndDate"
                  v-model="formData.plan_end_date"
                  type="date"
                  class="form-input"
                >
              </div>
              <div class="form-item">
                <label for="clientContactInfo" class="form-label"> <span class="required">*</span> 客户联系方式 </label>
                <input id="clientContactInfo" name="clientContactInfo"
                  v-model="formData.client_contact_info"
                  type="text"
                  class="form-input form-input-readonly"
                  placeholder="请输入客户联系方式"
                  readonly
                >
              </div>
            </div>
          </div>
          <div class="form-item-full">
            <label for="repairContent" class="form-label"> <span class="required">*</span> 报修内容 </label>
            <textarea id="repairContent" name="repairContent"
              v-model="formData.remarks"
              class="form-input form-textarea"
              placeholder="请输入报修内容"
              maxlength="500"
            />
          </div>
        </div>
        <div class="modal-footer">
          <button
            class="btn btn-cancel"
            @click="closeAddModal"
          >
            取消
          </button>
          <button
            class="btn btn-save"
            :disabled="saving"
            @click="handleSave"
          >
            {{ saving ? '保存中...' : '保存' }}
          </button>
        </div>
      </div>
    </div>

    <div
      v-if="showRejectModal"
      class="modal-overlay"
      @click.self="closeRejectModal"
    >
      <div class="modal-container modal-small">
        <div class="modal-header">
          <h3 class="modal-title">
            退回确认
          </h3>
          <button
            class="modal-close"
            @click="closeRejectModal"
          >
            ×
          </button>
        </div>
        <div class="modal-body">
          <div class="form-item-full">
            <label for="rejectReason" class="form-label">退回原因 <span class="required">*</span></label>
            <textarea id="rejectReason" name="rejectReason"
              v-model="rejectReason"
              class="form-input form-textarea"
              placeholder="请输入退回原因（10-500字符）"
              maxlength="500"
              rows="4"
            />
            <div class="char-count">
              {{ rejectReason.length }}/500
            </div>
          </div>
        </div>
        <div class="modal-footer">
          <button
            class="btn btn-cancel"
            @click="closeRejectModal"
          >
            取消
          </button>
          <button
            class="btn btn-reject"
            :disabled="saving"
            @click="confirmReject"
          >
            {{ saving ? '处理中...' : '确认退回' }}
          </button>
        </div>
      </div>
    </div>

    <PdfPreviewModal
      :visible="isPdfPreviewOpen"
      :data="pdfPreviewData"
      :photos="pdfPreviewPhotos"
      :operation-logs="pdfPreviewLogs"
      order-type="repair"
      @close="closePdfPreview"
      @export="confirmExport"
    />

    <ConfirmDialog
      :visible="isDeleteConfirmOpen"
      title="确认删除"
      :message="deleteConfirmMessage"
      confirm-text="删除"
      cancel-text="取消"
      @confirm="confirmDelete"
      @cancel="closeDeleteConfirm"
    />
  </div>
</template>

<script lang="ts">
import { defineComponent, ref, onMounted, onUnmounted, reactive, watch } from 'vue'
import { useRouter } from 'vue-router'
import { projectInfoService, type ProjectInfo } from '@/services/projectInfo'
import { personnelService, type Personnel } from '@/services/personnel'
import { temporaryRepairService, type TemporaryRepair } from '@/services/temporaryRepair'
import { operationLogService } from '@/services/operationLog'
import Toast from '@/components/Toast.vue'
import SearchInput from '@/components/SearchInput.vue'
import PdfPreviewModal from '@/components/PdfPreviewModal.vue'
import ConfirmDialog from '@/components/ConfirmDialog.vue'
import { WORK_STATUS, formatDate as formatDateUtil } from '@/config/constants'
import { userStore } from '@/stores/userStore'
import { sortByTimestampDesc } from '@/utils'

interface RepairItem {
  id: number
  repair_id: string
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
  name: 'TemporaryRepairQuery',
  components: {
    Toast,
    SearchInput,
    PdfPreviewModal,
    ConfirmDialog,
  },
  setup() {
    const router = useRouter()
    const currentPage = ref(1)
    const pageSize = ref(10)
    const jumpPage = ref(1)
    const loading = ref(false)
    const saving = ref(false)
    const totalElements = ref(0)
    const totalPages = ref(1)
    const isAddModalOpen = ref(false)

    const isAdmin = ref(userStore.isAdmin())
    const isDepartmentManager = ref(userStore.isDepartmentManager?.() || false)
    const currentUserName = ref(userStore.getUser()?.name || '')
    const canDelete = userStore.canDeleteWorkOrder()

    const canEditWork = (item: RepairItem): boolean => {
      if (isAdmin.value) return true
      if (item.status === WORK_STATUS.COMPLETED) return false
      const isOwner = item.maintenance_personnel === currentUserName.value
      const isEditableStatus = item.status === WORK_STATUS.PENDING_CONFIRM ||
                               item.status === WORK_STATUS.IN_PROGRESS ||
                               item.status === WORK_STATUS.RETURNED
      return isOwner && isEditableStatus
    }

    const canRecallWork = (item: RepairItem): boolean => {
      if (item.status !== WORK_STATUS.PENDING_CONFIRM) return false
      if (isAdmin.value) return true
      return item.maintenance_personnel === currentUserName.value
    }

    const toast = reactive({
      visible: false,
      message: '',
      type: 'success' as 'success' | 'error' | 'warning' | 'info',
    })

    const searchForm = ref({
      project_name: '',
      repair_id: '',
      plan_start_date: '',
      plan_end_date: '',
    })

    const projectList = ref<ProjectInfo[]>([])
    const personnelList = ref<Personnel[]>([])

    const formData = ref({
      project_name: '',
      project_id: '',
      repair_id: '',
      client_name: '',
      client_contact: '',
      client_contact_info: '',
      plan_start_date: '',
      plan_end_date: '',
      maintenance_personnel: '',
      status: WORK_STATUS.IN_PROGRESS,
      remarks: '',
    })

    const repairData = ref<RepairItem[]>([])

    const isPdfPreviewOpen = ref(false)
    const pdfPreviewData = ref<any>({})
    const pdfPreviewPhotos = ref<string[]>([])
    const pdfPreviewLogs = ref<any[]>([])
    const currentExportItem = ref<RepairItem | null>(null)

    const showToast = (
      message: string,
      type: 'success' | 'error' | 'warning' | 'info' = 'success'
    ) => {
      toast.message = message
      toast.type = type
      toast.visible = true
    }

    const loadData = async () => {
      loading.value = true
      try {
        const response = await temporaryRepairService.getList({
          page: currentPage.value - 1,
          size: pageSize.value,
          project_name: searchForm.value.project_name || undefined,
          repair_id: searchForm.value.repair_id || undefined,
        })

        if (response.code === 200 && response.data) {
          const rawData = response.data.content || []
          // 使用统一的排序函数，按时间戳降序排列
          const sortedData = sortByTimestampDesc(rawData, {
            secondarySortKey: 'id'
          })
          
          repairData.value = sortedData.map((item: TemporaryRepair) => ({
            id: item.id,
            repair_id: item.repair_id,
            project_id: item.project_id,
            project_name: item.project_name,
            plan_start_date: item.plan_start_date,
            plan_end_date: item.plan_end_date,
            client_name: item.client_name || '',
            maintenance_personnel: item.maintenance_personnel || '',
            status: item.status || '执行中',
            remarks: item.remarks || '',
          }))
          totalElements.value = response.data.totalElements || 0
          totalPages.value = response.data.totalPages || 1
        } else {
          showToast(response.message || '加载数据失败', 'error')
        }
      } catch (error: any) {
        showToast(error.message || '加载数据失败，请检查网络连接', 'error')
      } finally {
        loading.value = false
      }
    }

    const formatDate = (dateStr: string) => {
      return formatDateUtil(dateStr)
    }

    const handleSearch = () => {
      currentPage.value = 1
      loadData()
    }

    const handleReset = () => {
      searchForm.value = {
        project_name: '',
        repair_id: '',
        plan_start_date: '',
        plan_end_date: '',
      }
      currentPage.value = 1
      loadData()
    }

    const loadProjects = async () => {
      try {
        const response = await projectInfoService.getAll()
        if (response.code === 200 && response.data) {
          projectList.value = response.data
        }
      } catch (error) {
        console.error('加载项目列表失败:', error)
      }
    }

    const loadPersonnel = async () => {
      try {
        const response = await personnelService.getAll()
        if (response.code === 200 && response.data) {
          personnelList.value = response.data
        }
      } catch (error) {
        console.error('加载人员列表失败:', error)
      }
    }

    const handleProjectChange = async () => {
      const selectedProject = projectList.value.find(
        (p: ProjectInfo) => p.project_name === formData.value.project_name
      )
      if (selectedProject) {
        formData.value.project_id = selectedProject.project_id
        formData.value.client_name = selectedProject.client_name
        formData.value.client_contact = selectedProject.client_contact || ''
        formData.value.client_contact_info = selectedProject.client_contact_info || ''
        formData.value.maintenance_personnel = selectedProject.project_manager || ''
        await generateRepairId()
      }
    }

    const generateRepairId = async () => {
      if (!formData.value.project_id) return

      try {
        const response = await temporaryRepairService.generateId(formData.value.project_id)
        if (response.code === 200 && response.data) {
          formData.value.repair_id = response.data.repair_id
        }
      } catch (error) {
        console.error('生成维修单编号失败:', error)
        const today = new Date()
        const year = today.getFullYear()
        const month = String(today.getMonth() + 1).padStart(2, '0')
        const day = String(today.getDate()).padStart(2, '0')
        const dateStr = `${year}${month}${day}`
        formData.value.repair_id = `WX-${formData.value.project_id}-${dateStr}-01`
      }
    }

    const handleProjectInfoChanged = () => {
      loadProjects()
    }

    onMounted(() => {
      loadData()
      window.addEventListener('user-changed', handleUserChanged)
      window.addEventListener('project-info-changed', handleProjectInfoChanged)
    })

    onUnmounted(() => {
      window.removeEventListener('user-changed', handleUserChanged)
      window.removeEventListener('project-info-changed', handleProjectInfoChanged)
    })

    const handleUserChanged = () => {
      loadData()
    }

    watch([currentPage, pageSize], () => {
      loadData()
    })

    const getTodayDate = () => {
      const today = new Date()
      const year = today.getFullYear()
      const month = String(today.getMonth() + 1).padStart(2, '0')
      const day = String(today.getDate()).padStart(2, '0')
      return `${year}-${month}-${day}`
    }

    const handleAdd = async () => {
      await Promise.all([loadProjects(), loadPersonnel()])
      isAddModalOpen.value = true
    }

    const closeAddModal = () => {
      isAddModalOpen.value = false
      resetForm()
    }

    const resetForm = () => {
      const today = getTodayDate()
      formData.value = {
        project_name: '',
        project_id: '',
        repair_id: '',
        client_name: '',
        client_contact: '',
        client_contact_info: '',
        plan_start_date: today,
        plan_end_date: today,
        maintenance_personnel: '',
        status: WORK_STATUS.IN_PROGRESS,
        remarks: '',
      }
    }

    const handleSave = async () => {
      if (!formData.value.project_name) {
        showToast('请选择项目名称', 'error')
        return
      }
      if (!formData.value.maintenance_personnel) {
        showToast('请选择运维人员', 'error')
        return
      }
      if (!formData.value.plan_start_date) {
        showToast('请选择计划开始日期', 'error')
        return
      }
      if (!formData.value.plan_end_date) {
        showToast('请选择计划结束日期', 'error')
        return
      }
      if (!formData.value.remarks) {
        showToast('请输入报修内容', 'error')
        return
      }

      saving.value = true

      try {
        const response = await temporaryRepairService.create({
          repair_id: formData.value.repair_id,
          project_id: formData.value.project_id,
          project_name: formData.value.project_name,
          plan_start_date: formData.value.plan_start_date,
          plan_end_date: formData.value.plan_end_date,
          client_name: formData.value.client_name,
          maintenance_personnel: formData.value.maintenance_personnel,
          status: '执行中',
          remarks: formData.value.remarks || '',
        })

        if (response.code === 200) {
          showToast('保存成功', 'success')
          await loadData()
          closeAddModal()
        } else {
          showToast(response.message || '保存失败', 'error')
        }
      } catch (error: any) {
        console.error('保存失败:', error)
        showToast('保存失败，请检查网络连接', 'error')
      } finally {
        saving.value = false
      }
    }

    const handleView = (item: RepairItem) => {
      router.push({
        name: 'TemporaryRepairDetail',
        query: { id: item.id },
      })
    }

    const handleEdit = (item: RepairItem) => {
      router.push({
        name: 'TemporaryRepairDetail',
        query: { id: item.id, type: 'edit' },
      })
    }

    const handleExport = async (item: RepairItem) => {
      if (item.status !== WORK_STATUS.COMPLETED) {
        showToast('只能导出已完成的工单', 'warning')
        return
      }

      currentExportItem.value = item
      
      try {
        const response = await temporaryRepairService.getById(item.id)
        const detail = response.data
        
        pdfPreviewData.value = {
          id: detail.id,
          repair_id: detail.repair_id,
          project_id: detail.project_id,
          project_name: detail.project_name,
          plan_start_date: detail.plan_start_date,
          plan_end_date: detail.plan_end_date,
          client_name: detail.client_name,
          client_contact: detail.client_contact || '',
          client_contact_info: detail.client_contact_info || '',
          client_contact_position: '',
          address: detail.address || '',
          maintenance_personnel: detail.maintenance_personnel,
          status: detail.status,
          execution_result: detail.fault_description || detail.solution || '',
          remarks: detail.remarks || '',
          signature: detail.signature || '',
          remainingTime: '',
        }
        
        pdfPreviewPhotos.value = detail.photos || []
        
        const logResult = await operationLogService.getByWorkOrder({
          work_order_type: 'temporary_repair',
          work_order_id: item.id,
        })
        pdfPreviewLogs.value = logResult.data || []
        
        isPdfPreviewOpen.value = true
      } catch (error) {
        console.error('获取详情失败:', error)
        showToast('获取详情失败', 'error')
      }
    }

    const closePdfPreview = () => {
      isPdfPreviewOpen.value = false
      currentExportItem.value = null
    }

    const confirmExport = async () => {
      if (!currentExportItem.value) return
      
      const item = currentExportItem.value
      const defaultFilename = `临时维修单_${item.repair_id}.pdf`
      
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
      
      try {
        const token = localStorage.getItem('token')
        const exportUrl = `/api/v1/export/temporary-repair/${item.id}`

        const response = await fetch(exportUrl, {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        })

        if (!response.ok) {
          const error = await response.json()
          showToast(error.message || error.detail || '导出失败', 'error')
          return
        }

        const blob = await response.blob()

        if (fileHandle) {
          const writable = await fileHandle.createWritable()
          await writable.write(blob)
          await writable.close()
          showToast('导出成功', 'success')
          closePdfPreview()
        } else {
          fallbackDownload(blob, defaultFilename)
        }
      } catch (error) {
        console.error('导出失败:', error)
        showToast('导出失败，请检查网络连接', 'error')
      }
    }

    const fallbackDownload = (blob: Blob, filename: string) => {
      const url = window.URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = filename
      document.body.appendChild(a)
      a.click()
      document.body.removeChild(a)
      setTimeout(() => window.URL.revokeObjectURL(url), 100)
      showToast('导出成功', 'success')
      closePdfPreview()
    }

    const showRejectModal = ref(false)
    const rejectReason = ref('')
    const pendingRejectItem = ref<RepairItem | null>(null)

    const handleReject = (item: RepairItem) => {
      pendingRejectItem.value = item
      rejectReason.value = ''
      showRejectModal.value = true
    }

    const handleRecall = async (item: RepairItem) => {
      if (!confirm('确认撤回此工单？撤回后可继续编辑。')) return
      try {
        const response = await temporaryRepairService.recall(item.id)
        if (response.code === 200) {
          showToast('撤回成功', 'success')
          await loadData()
        } else {
          showToast(response.message || '撤回失败', 'error')
        }
      } catch (error) {
        console.error('撤回失败:', error)
        showToast('撤回失败', 'error')
      }
    }

    const closeRejectModal = () => {
      showRejectModal.value = false
      pendingRejectItem.value = null
      rejectReason.value = ''
    }

    const confirmReject = async () => {
      if (!pendingRejectItem.value) return

      const reason = rejectReason.value.trim()
      if (!reason) {
        showToast('请输入退回原因', 'error')
        return
      }
      if (reason.length < 10) {
        showToast('退回原因至少需要10个字符', 'error')
        return
      }
      if (reason.length > 500) {
        showToast('退回原因不能超过500个字符', 'error')
        return
      }

      saving.value = true
      try {
        const response = await temporaryRepairService.patch(pendingRejectItem.value.id, {
          status: '已退回',
          reject_reason: reason,
        })

        if (response.code === 200) {
          showToast('已退回', 'success')
          closeRejectModal()
          await loadData()
        } else {
          showToast(response.message || '退回失败', 'error')
        }
      } catch (error: any) {
        console.error('退回失败:', error)
        showToast(error.response?.data?.detail || '退回失败，请检查网络连接', 'error')
      } finally {
        saving.value = false
      }
    }

    const handleJump = () => {
      const page = parseInt(String(jumpPage.value))
      if (page >= 1 && page <= totalPages.value) {
        currentPage.value = page
      }
    }

    const toggleSidebar = () => {
    }

    const isDeleteConfirmOpen = ref(false)
    const deleteConfirmMessage = ref('')
    const deleteTargetItem = ref<RepairItem | null>(null)

    const handleDelete = (item: RepairItem) => {
      deleteTargetItem.value = item
      deleteConfirmMessage.value = `确定要删除工单「${item.repair_id}」吗？此操作不可恢复。`
      isDeleteConfirmOpen.value = true
    }

    const closeDeleteConfirm = () => {
      isDeleteConfirmOpen.value = false
      deleteTargetItem.value = null
    }

    const confirmDelete = async () => {
      if (!deleteTargetItem.value) return

      const item = deleteTargetItem.value
      try {
        await temporaryRepairService.delete(item.id)
        showToast('删除成功', 'success')
        closeDeleteConfirm()
        await loadData()
      } catch (error) {
        console.error('删除失败:', error)
        showToast('删除失败，请稍后重试', 'error')
      }
    }

    return {
      currentPage,
      pageSize,
      jumpPage,
      loading,
      saving,
      totalElements,
      totalPages,
      isAddModalOpen,
      showRejectModal,
      rejectReason,
      pendingRejectItem,
      toast,
      searchForm,
      formData,
      projectList,
      personnelList,
      repairData,
      formatDate,
      WORK_STATUS,
      handleSearch,
      handleReset,
      handleProjectChange,
      handleAdd,
      closeAddModal,
      handleSave,
      handleView,
      handleEdit,
      handleExport,
      handleReject,
      handleRecall,
      canRecallWork,
      closeRejectModal,
      confirmReject,
      handleJump,
      toggleSidebar,
      showToast,
      isAdmin,
      isDepartmentManager,
      currentUserName,
      canEditWork,
      isPdfPreviewOpen,
      pdfPreviewData,
      pdfPreviewPhotos,
      pdfPreviewLogs,
      closePdfPreview,
      confirmExport,
      canDelete,
      handleDelete,
      isDeleteConfirmOpen,
      deleteConfirmMessage,
      confirmDelete,
      closeDeleteConfirm,
    }
  },
})
</script>

<style scoped>
.temporary-repair-page {
  background: var(--color-bg-card);
  min-height: 100vh;
}

.top-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 20px;
  background: var(--color-bg-page);
  border-bottom: 1px solid var(--color-border);
}

.menu-toggle {
  cursor: pointer;
  padding: 8px;
  border-radius: 4px;
  transition: background 0.2s;
}

.menu-toggle:hover {
  background: rgba(0, 0, 0, 0.05);
}

.breadcrumb {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
  color: var(--color-text-secondary);
  font-weight: 500;
}

.breadcrumb-level1 {
  color: var(--color-primary);
  font-weight: 500;
}

.breadcrumb-separator {
  color: var(--color-text-placeholder);
}

.breadcrumb-level2 {
  color: var(--color-text-primary);
  font-weight: 600;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 6px 12px;
  background: var(--color-bg-card);
  border-radius: 20px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.user-avatar {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background: linear-gradient(135deg, var(--color-primary) 0%, #42a5f5 100%);
  color: var(--color-bg-card);
  font-size: 12px;
  font-weight: 600;
  display: flex;
  align-items: center;
  justify-content: center;
}

.user-name {
  font-size: 14px;
  color: var(--color-text-primary);
  font-weight: 500;
}

.content {
  padding: 20px;
}

.search-section {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding: 20px;
  background: var(--color-bg-card);
  border-radius: 4px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.search-form {
  display: flex;
  gap: 16px;
  align-items: center;
  flex: 1;
}

.search-row {
  display: flex;
  gap: 16px;
  align-items: center;
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
  min-width: 200px;
}

.search-input:focus {
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
}

.data-table {
  width: 100%;
  border-collapse: collapse;
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

.action-export {
  color: var(--color-primary);
}

.action-export:hover {
  color: var(--color-primary-dark);
}

.action-delete {
  color: var(--color-danger);
}

.action-delete:hover {
  color: var(--color-danger);
}

.status-tag {
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
  color: var(--color-bg-card);
}

.status-completed {
  background: var(--color-success);
  color: var(--color-bg-card);
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

.page-btn.page-nav {
  background: var(--color-bg-page);
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

.page-select:focus {
  border-color: var(--color-primary);
  box-shadow: 0 0 0 2px rgba(25, 118, 210, 0.1);
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

.page-input:focus {
  border-color: var(--color-primary);
  box-shadow: 0 0 0 2px rgba(25, 118, 210, 0.1);
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
  min-height: 90px;
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

.form-item-full {
  display: flex;
  flex-direction: column;
  gap: 8px;
  margin-top: 16px;
}

.form-textarea {
  min-height: 100px;
  resize: vertical;
  line-height: 1.5;
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
</style>
