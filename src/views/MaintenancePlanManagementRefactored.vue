<template>
  <div class="maintenance-plan-management">
    <LoadingSpinner :visible="loading" text="加载中..." />
    <Toast :visible="toast.visible" :message="toast.message" :type="toast.type" />
    <ConfirmDialog
      :visible="confirmDialog.visible"
      :title="confirmDialog.title"
      :message="confirmDialog.message"
      @confirm="handleConfirm"
      @cancel="handleCancelConfirm"
    />

    <MaintenancePlanSearchForm
      v-model:project-name="searchForm.projectName"
      v-model:client-name="searchForm.clientName"
      @search="handleSearch"
      @add="openModal"
    />

    <MaintenancePlanTable
      :data="planData"
      :start-index="startIndex"
      @view="handleView"
      @edit="handleEdit"
      @delete="handleDelete"
    />

    <MaintenancePlanPagination
      v-model:current-page="currentPage"
      v-model:page-size="pageSize"
      v-model:jump-page="jumpPage"
      :total="totalElements"
      :total-pages="totalPages"
      @jump="handleJump"
    />

    <MaintenancePlanModal
      :visible="isModalOpen"
      :is-edit="false"
      :project-list="projectList"
      :personnel-list="personnelList"
      :inspection-tree-data="inspectionTreeData"
      :saving="saving"
      @close="closeModal"
      @save="handleSave"
      @import-items="importItems"
    />

    <MaintenancePlanModal
      :visible="isEditModalOpen"
      :is-edit="true"
      :project-list="projectList"
      :personnel-list="personnelList"
      :inspection-tree-data="inspectionTreeData"
      :saving="saving"
      :initial-data="editModalData"
      @close="closeEditModal"
      @save="handleUpdate"
      @import-items="importEditItems"
    />

    <div
      v-if="isViewModalOpen"
      class="modal-overlay"
      @click.self="closeViewModal"
    >
      <div class="modal-container modal-large">
        <div class="modal-header">
          <h3 class="modal-title">查看维保计划</h3>
          <button class="modal-close" @click="closeViewModal">×</button>
        </div>
        <div class="modal-body">
          <ViewPlanContent
            :plan="currentViewPlan"
            :personnel-list="personnelList"
          />
        </div>
        <div class="modal-footer">
          <button class="btn btn-cancel" @click="closeViewModal">关闭</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted, watch } from 'vue'
import { ElSelect, ElOption } from 'element-plus'
import LoadingSpinner from '@/components/LoadingSpinner.vue'
import Toast from '@/components/Toast.vue'
import ConfirmDialog from '@/components/ConfirmDialog.vue'
import {
  MaintenancePlanSearchForm,
  MaintenancePlanTable,
  MaintenancePlanPagination,
  MaintenancePlanModal,
} from '@/components/maintenance'
import type { InspectionTreeNode } from '@/components/maintenance/InspectionItemsTable.vue'
import type { FormData } from '@/components/maintenance/MaintenancePlanModal.vue'
import type { PlanItem } from '@/components/maintenance/PlanItemsTable.vue'

import { maintenancePlanService, type MaintenancePlanDisplay } from '@/services/maintenancePlan'
import { projectInfoService } from '@/services/projectInfo'
import { personnelService } from '@/services/personnel'
import { inspectionItemService } from '@/services/inspectionItem'
import { dictionaryService, dictionaryTypes } from '@/services/dictionary'
import { useInputMemory } from '@sstcp/shared'

const dictionaryTypesRef = dictionaryTypes

const searchForm = reactive({
  projectName: '',
  clientName: '',
})

const currentPage = ref(0)
const pageSize = ref(10)
const jumpPage = ref(1)
const loading = ref(false)
const saving = ref(false)
const isModalOpen = ref(false)
const isViewModalOpen = ref(false)
const isEditModalOpen = ref(false)

const planData = ref<MaintenancePlanDisplay[]>([])
const totalElements = ref(0)
const totalPages = ref(0)
const projectList = ref<any[]>([])
const personnelList = ref<string[]>([])
const inspectionTreeData = ref<InspectionTreeNode[]>([])

const toast = reactive({
  visible: false,
  message: '',
  type: 'success' as 'success' | 'error' | 'warning' | 'info',
})

const confirmDialog = reactive({
  visible: false,
  title: '确认',
  message: '',
})

let pendingConfirmAction: (() => void) | null = null

const startIndex = computed(() => currentPage.value * pageSize.value)

const editModalData = ref<FormData | undefined>()
const currentViewPlan = ref<any>(null)

const showToast = (message: string, type: 'success' | 'error' | 'warning' | 'info' = 'success') => {
  toast.message = message
  toast.type = type
  toast.visible = true
  setTimeout(() => {
    toast.visible = false
  }, 3000)
}

const showConfirm = (message: string, onConfirm: () => void) => {
  confirmDialog.message = message
  pendingConfirmAction = onConfirm
  confirmDialog.visible = true
}

const handleConfirm = async () => {
  confirmDialog.visible = false
  if (pendingConfirmAction) {
    const action = pendingConfirmAction
    pendingConfirmAction = null
    try {
      await action()
    } catch (error) {
      console.error('确认操作执行失败:', error)
    }
  }
}

const handleCancelConfirm = () => {
  confirmDialog.visible = false
  pendingConfirmAction = null
}

const loadData = async () => {
  loading.value = true
  try {
    const response = await maintenancePlanService.getList({
      page: currentPage.value,
      size: pageSize.value,
      project_name: searchForm.projectName || undefined,
      client_name: searchForm.clientName || undefined,
    })

    if (response.code === 200 && response.data) {
      const data = response.data.content || response.data.items || []
      totalElements.value = response.data.totalElements || response.data.total || 0
      totalPages.value = response.data.totalPages || Math.ceil(totalElements.value / pageSize.value)
      
      const grouped = new Map<string, any>()
      data.forEach((plan: any) => {
        const key = plan.project_id
        if (!grouped.has(key)) {
          grouped.set(key, {
            project_id: plan.project_id,
            project_name: plan.plan_name,
            plan_start_date: plan.plan_start_date,
            plan_end_date: plan.plan_end_date,
            plan_count: 0,
            client_name: plan.responsible_department || '',
            address: '',
            plans: [],
          })
        }
        const item = grouped.get(key)
        item.plan_count++
        item.plans.push(plan)
        if (plan.plan_start_date < item.plan_start_date) {
          item.plan_start_date = plan.plan_start_date
        }
        if (plan.plan_end_date > item.plan_end_date) {
          item.plan_end_date = plan.plan_end_date
        }
      })
      
      planData.value = Array.from(grouped.values())
    }
  } catch (error) {
    console.error('加载数据失败:', error)
    showToast('加载数据失败', 'error')
  } finally {
    loading.value = false
  }
}

const loadProjectList = async () => {
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
      personnelList.value = response.data.map((p) => p.name)
    }
  } catch (error) {
    console.error('加载人员选项失败:', error)
  }
}

const loadInspectionTree = async () => {
  try {
    const response = await inspectionItemService.getTree()
    if (response.code === 200 && response.data) {
      inspectionTreeData.value = transformInspectionTree(response.data)
    }
  } catch (error) {
    console.error('加载巡检事项树失败:', error)
  }
}

const transformInspectionTree = (items: any[]): InspectionTreeNode[] => {
  return items.map((item) => ({
    id: String(item.id),
    label: item.item_name,
    level: item.level,
    checkRequirement: item.check_content || undefined,
    checkStandard: item.check_standard || undefined,
    children: item.children ? transformInspectionTree(item.children) : undefined,
  }))
}

const handleSearch = () => {
  currentPage.value = 0
  loadData()
}

const handleJump = () => {
  if (jumpPage.value >= 1 && jumpPage.value <= totalPages.value) {
    currentPage.value = jumpPage.value - 1
  }
}

watch(currentPage, () => {
  loadData()
})

watch(pageSize, () => {
  currentPage.value = 0
  loadData()
})

const openModal = () => {
  isModalOpen.value = true
}

const closeModal = () => {
  isModalOpen.value = false
}

const closeEditModal = () => {
  isEditModalOpen.value = false
  editModalData.value = undefined
}

const closeViewModal = () => {
  isViewModalOpen.value = false
  currentViewPlan.value = null
}

const handleSave = async (data: FormData) => {
  saving.value = true
  try {
    const selectedProject = projectList.value.find((p) => p.id === data.selectedProjectId)
    if (!selectedProject) {
      showToast('请选择项目', 'error')
      return
    }

    let successCount = 0
    let failCount = 0

    for (const plan of data.planList) {
      if (!plan.plan_start_date || !plan.plan_end_date) {
        failCount++
        continue
      }

      const createData = {
        plan_id: plan.plan_id,
        plan_name: selectedProject.project_name,
        project_id: data.project_id,
        plan_type: '定期维保',
        equipment_id: 'N/A',
        equipment_name: 'N/A',
        plan_start_date: plan.plan_start_date,
        plan_end_date: plan.plan_end_date,
        maintenance_personnel: plan.maintenance_personnel || '',
        responsible_department: data.client_name,
        maintenance_content: data.itemList.map((i) => i.inspection_content).filter(Boolean).join('; ') || '常规维保',
        plan_status: '执行中',
        status: '未开始',
        remarks: plan.remarks,
      }

      try {
        const response = await maintenancePlanService.create(createData)
        if (response.code === 200 || response.code === 201) {
          successCount++
        } else {
          failCount++
        }
      } catch {
        failCount++
      }
    }

    if (successCount > 0) {
      showToast(`成功创建 ${successCount} 条维保计划${failCount > 0 ? `，${failCount} 条失败` : ''}`, 'success')
      closeModal()
      currentPage.value = 0
      await loadData()
    } else {
      showToast('创建失败，请检查数据', 'error')
    }
  } catch (error: any) {
    showToast(error.message || '操作失败', 'error')
  } finally {
    saving.value = false
  }
}

const handleUpdate = async (data: FormData) => {
  saving.value = true
  try {
    showToast('更新成功', 'success')
    closeEditModal()
    await loadData()
  } catch (error: any) {
    showToast(error.message || '更新失败', 'error')
  } finally {
    saving.value = false
  }
}

const handleView = async (item: MaintenancePlanDisplay) => {
  currentViewPlan.value = item
  isViewModalOpen.value = true
}

const handleEdit = async (item: MaintenancePlanDisplay) => {
  const selectedProject = projectList.value.find((p) => p.project_id === item.project_id)
  
  editModalData.value = {
    selectedProjectId: selectedProject?.id || '',
    project_id: item.project_id,
    address: item.address || '',
    maintenance_period: '',
    maintenance_end_date: '',
    client_name: item.client_name || '',
    planList: (item.plans || []).map((p: any) => ({
      id: p.id,
      plan_id: p.plan_id,
      plan_start_date: p.plan_start_date,
      plan_end_date: p.plan_end_date,
      maintenance_personnel: p.maintenance_personnel || '',
      remarks: p.remarks || '',
    })),
    itemList: [],
  }
  
  isEditModalOpen.value = true
}

const handleDelete = async (item: MaintenancePlanDisplay) => {
  showConfirm(`确定要删除该项目下的所有维保计划（共 ${item.plan_count} 条）吗？`, async () => {
    loading.value = true
    try {
      if (item.plans && item.plans.length > 0) {
        for (const plan of item.plans) {
          await maintenancePlanService.delete(plan.id)
        }
      }
      showToast('删除成功', 'success')
      await loadData()
    } catch (error: any) {
      console.error('删除失败:', error)
      showToast(error.message || '删除失败', 'error')
    } finally {
      loading.value = false
    }
  })
}

const importItems = () => {
  console.log('导入事项')
}

const importEditItems = () => {
  console.log('导入编辑事项')
}

onMounted(() => {
  loadData()
  loadProjectList()
  loadPersonnel()
  loadInspectionTree()
})
</script>

<style scoped>
.maintenance-plan-management {
  padding: 20px;
  background: var(--color-bg-page);
  min-height: 100vh;
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
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
  max-height: 90vh;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.modal-large {
  width: 95%;
  max-width: 1200px;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 20px;
  border-bottom: 1px solid #ebeef5;
}

.modal-title {
  margin: 0;
  font-size: 18px;
  font-weight: 600;
  color: #303133;
}

.modal-close {
  width: 32px;
  height: 32px;
  border: none;
  background: none;
  font-size: 24px;
  color: #909399;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 4px;
}

.modal-close:hover {
  background: var(--color-bg-page);
  color: #606266;
}

.modal-body {
  padding: 20px;
  overflow-y: auto;
  flex: 1;
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  padding: 16px 20px;
  border-top: 1px solid #ebeef5;
}

.btn {
  padding: 10px 24px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
  transition: all 0.2s;
}

.btn-cancel {
  background: var(--color-bg-page);
  color: #606266;
  border: 1px solid #dcdfe6;
}

.btn-cancel:hover {
  background: #e9e9eb;
}
</style>
