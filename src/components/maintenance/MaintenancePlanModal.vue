<template>
  <div
    v-if="visible"
    class="modal-overlay"
    @click.self="$emit('close')"
  >
    <div class="modal-container modal-large">
      <div class="modal-header">
        <h3 class="modal-title">
          {{ isEdit ? '编辑维保计划' : '新增维保计划' }}
        </h3>
        <button
          class="modal-close"
          @click="$emit('close')"
        >
          ×
        </button>
      </div>
      <div class="modal-body">
        <div class="section-title">
          基础信息
        </div>
        <div class="form-grid">
          <div class="form-column">
            <div class="form-item">
              <span class="form-label">
                <span class="required">*</span> 项目名称
              </span>
              <el-select
                v-model="formData.selectedProjectId"
                placeholder="请选择或搜索项目"
                filterable
                size="default"
                style="width: 100%"
                @change="handleProjectChange"
              >
                <el-option
                  v-for="project in projectList"
                  :key="project.id"
                  :label="project.project_name"
                  :value="project.id"
                />
              </el-select>
            </div>
            <div class="form-item">
              <label for="maintenancePeriod" class="form-label">维保频率</label>
              <input id="maintenancePeriod" name="maintenancePeriod"
                v-model="formData.maintenance_period"
                type="text"
                class="form-input form-input-readonly"
                readonly
              >
            </div>
            <div class="form-item">
              <label for="projectAddress" class="form-label">项目地址</label>
              <input id="projectAddress" name="projectAddress"
                v-model="formData.address"
                type="text"
                class="form-input form-input-readonly"
                readonly
              >
            </div>
          </div>
          <div class="form-column">
            <div class="form-item">
              <label for="projectId" class="form-label">项目编号</label>
              <input id="projectId" name="projectId"
                v-model="formData.project_id"
                type="text"
                class="form-input form-input-readonly"
                readonly
              >
            </div>
            <div class="form-item">
              <label for="projectEndDate" class="form-label">项目结束日期</label>
              <input id="projectEndDate" name="projectEndDate"
                v-model="formData.maintenance_end_date"
                type="text"
                class="form-input form-input-readonly"
                readonly
              >
            </div>
            <div class="form-item">
              <label for="clientName" class="form-label">客户单位</label>
              <input id="clientName" name="clientName"
                v-model="formData.client_name"
                type="text"
                class="form-input form-input-readonly"
                readonly
              >
            </div>
          </div>
        </div>

        <div class="section-divider" />

        <PlanItemsTable
          :items="formData.planList"
          :personnel-list="personnelList"
          @add="addPlan"
          @remove="removePlan"
        />

        <div class="section-divider" />

        <InspectionItemsTable
          :items="formData.itemList"
          :tree-data="inspectionTreeData"
          :show-import="true"
          @add="addItem"
          @remove="removeItem"
          @import="importItems"
        />
      </div>
      <div class="modal-footer">
        <button
          class="btn btn-cancel"
          @click="$emit('close')"
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
</template>

<script setup lang="ts">
import { reactive, watch } from 'vue'
import { ElSelect, ElOption } from 'element-plus'
import PlanItemsTable, { type PlanItem } from './PlanItemsTable.vue'
import InspectionItemsTable, { type InspectionItem, type InspectionTreeNode } from './InspectionItemsTable.vue'
import type { ProjectInfo } from '@sstcp/shared'

export interface FormData {
  selectedProjectId: number | string
  project_id: string
  address: string
  maintenance_period: string
  maintenance_end_date: string
  client_name: string
  planList: PlanItem[]
  itemList: InspectionItem[]
}

const props = defineProps<{
  visible: boolean
  isEdit: boolean
  projectList: ProjectInfo[]
  personnelList: string[]
  inspectionTreeData: InspectionTreeNode[]
  saving: boolean
  initialData?: FormData
}>()

const emit = defineEmits<{
  'close': []
  'save': [data: FormData]
  'import-items': []
}>()

const formData = reactive<FormData>({
  selectedProjectId: '',
  project_id: '',
  address: '',
  maintenance_period: '',
  maintenance_end_date: '',
  client_name: '',
  planList: [],
  itemList: [],
})

watch(() => props.visible, (visible) => {
  if (visible && props.initialData) {
    Object.assign(formData, props.initialData)
  } else if (visible) {
    resetForm()
  }
})

const resetForm = () => {
  formData.selectedProjectId = ''
  formData.project_id = ''
  formData.address = ''
  formData.maintenance_period = ''
  formData.maintenance_end_date = ''
  formData.client_name = ''
  formData.planList = []
  formData.itemList = []
}

const handleProjectChange = () => {
  const selectedProject = props.projectList.find((p) => p.id === formData.selectedProjectId)
  if (selectedProject) {
    formData.project_id = selectedProject.project_id
    formData.address = selectedProject.address || ''
    formData.maintenance_period = selectedProject.maintenance_period || ''
    formData.maintenance_end_date = formatDate(selectedProject.maintenance_end_date)
    formData.client_name = selectedProject.client_name || ''
  }
}

const formatDate = (date: string | undefined): string => {
  if (!date) return ''
  try {
    const d = new Date(date)
    return d.toLocaleDateString('zh-CN')
  } catch {
    return date
  }
}

const addPlan = () => {
  formData.planList.push({
    plan_id: '',
    plan_start_date: '',
    plan_end_date: '',
    maintenance_personnel: '',
    remarks: '',
  })
}

const removePlan = (index: number) => {
  formData.planList.splice(index, 1)
}

const addItem = () => {
  formData.itemList.push({
    item_id: '',
    inspection_item: '',
    inspection_content: '',
    check_requirements: '',
    brief_description: '',
    level1_id: '',
    level1_name: '',
    level2_id: '',
    level2_name: '',
    level3_id: '',
    level3_name: '',
  })
}

const removeItem = (index: number) => {
  formData.itemList.splice(index, 1)
}

const importItems = () => {
  emit('import-items')
}

const handleSave = () => {
  emit('save', { ...formData })
}
</script>

<style scoped>
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

.section-title {
  font-size: 15px;
  font-weight: 600;
  color: #303133;
  margin-bottom: 16px;
  padding-left: 10px;
  border-left: 3px solid #409eff;
}

.section-divider {
  height: 1px;
  background: #ebeef5;
  margin: 20px 0;
}

.form-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;
}

.form-column {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.form-item {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.form-label {
  font-size: 14px;
  color: #606266;
  font-weight: 500;
}

.required {
  color: #f56c6c;
  margin-right: 4px;
}

.form-input {
  padding: 10px 12px;
  border: 1px solid #dcdfe6;
  border-radius: 4px;
  font-size: 14px;
  transition: border-color 0.2s;
}

.form-input:focus {
  border-color: #409eff;
  outline: none;
}

.form-input-readonly {
  background: var(--color-bg-page);
  cursor: not-allowed;
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

.btn-save {
  background: linear-gradient(135deg, var(--color-primary) 0%, var(--color-primary) 100%);
  color: white;
}

.btn-save:hover:not(:disabled) {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
}

.btn-save:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}
</style>
