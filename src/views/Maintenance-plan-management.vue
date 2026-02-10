<template>
  <div class="maintenance-plan-management">
    <div class="search-section">
      <div class="search-form">
        <div class="search-item">
          <label class="search-label">项目名称：</label>
          <input type="text" class="search-input" placeholder="请输入" v-model="searchForm.projectName" />
        </div>
        <div class="search-item">
          <label class="search-label">客户名称：</label>
          <input type="text" class="search-input" placeholder="请输入" v-model="searchForm.clientName" />
        </div>
      </div>
      <div class="search-actions">
        <button class="btn btn-add" @click="handleAdd">
          + 新增维保计划
        </button>
        <button class="btn btn-search" @click="handleSearch">
          搜索
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
            <th>开始日期</th>
            <th>结束日期</th>
            <th>维保计划数</th>
            <th>客户单位</th>
            <th>地址</th>
            <th>操作</th>
          </tr>
        </thead>
        <tbody>
          <tr v-if="loading">
            <td colspan="9" style="text-align: center; padding: 20px;">加载中...</td>
          </tr>
          <tr v-else-if="planData.length === 0">
            <td colspan="9" style="text-align: center; padding: 20px;">暂无数据</td>
          </tr>
          <tr v-else v-for="(item, index) in planData" :key="item.id" :class="{ 'even-row': index % 2 === 0 }">
            <td>{{ (currentPage - 1) * pageSize + index + 1 }}</td>
            <td>{{ item.planId }}</td>
            <td>{{ item.projectName }}</td>
            <td>{{ item.startDate }}</td>
            <td>{{ item.endDate }}</td>
            <td>{{ item.planCount }}</td>
            <td>{{ item.clientName }}</td>
            <td>{{ item.address }}</td>
            <td class="action-cell">
              <a href="#" class="action-link action-view" @click="handleView(item)">查看</a>
              <a href="#" class="action-link action-edit" @click="handleEdit(item)">编辑</a>
              <a href="#" class="action-link action-delete" @click="handleDelete(item)">删除</a>
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
        <button class="page-btn page-nav" :disabled="currentPage === 1" @click="currentPage--">
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
        <button class="page-btn page-nav" :disabled="currentPage === totalPages" @click="currentPage++">
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

    <div v-if="isAddModalOpen" class="modal-overlay" @click.self="closeAddModal">
      <div class="modal-container modal-large">
        <div class="modal-header">
          <h3 class="modal-title">添加维保计划</h3>
          <button class="modal-close" @click="closeAddModal">×</button>
        </div>
        <div class="modal-body">
          <div class="project-info-section">
            <div class="project-info-title">项目信息</div>
            <div class="form-grid-half">
              <div class="form-column">
                <div class="form-item">
                  <label class="form-label">
                    <span class="required">*</span> 项目名称
                  </label>
                  <select class="form-input" v-model="addForm.projectName" @change="handleProjectChange">
                    <option value="">选择项目，支持搜索选择</option>
                    <option v-for="project in projectOptions" :key="project.id" :value="project.name">
                      {{ project.name }}
                    </option>
                  </select>
                </div>
                <div class="form-item">
                  <label class="form-label">项目地址</label>
                  <input type="text" class="form-input readonly-input" v-model="addForm.projectAddress" readonly />
                </div>
                <div class="form-item">
                  <label class="form-label">结束日期</label>
                  <input type="text" class="form-input readonly-input" v-model="addForm.endDate" readonly />
                </div>
              </div>
              <div class="form-column">
                <div class="form-item">
                  <label class="form-label">项目编号</label>
                  <input type="text" class="form-input readonly-input" v-model="addForm.projectId" readonly />
                </div>
                <div class="form-item">
                  <label class="form-label">维保周期</label>
                  <input type="text" class="form-input readonly-input" v-model="addForm.maintenanceDays" readonly />
                </div>
                <div class="form-item">
                  <label class="form-label">客户单位</label>
                  <input type="text" class="form-input readonly-input" v-model="addForm.clientUnit" readonly />
                </div>
              </div>
            </div>
          </div>

          <div class="plan-table-section">
            <div class="section-header">
              <div class="section-title">维保计划</div>
              <button class="btn btn-add-small" @click="addPlanRow">添加</button>
            </div>
            <div class="table-wrapper">
              <table class="edit-table">
                <thead>
                  <tr>
                    <th>计划编号</th>
                    <th>开始日期</th>
                    <th>结束日期</th>
                    <th>维保人员</th>
                    <th>备注</th>
                    <th>操作</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="(row, index) in addForm.planRows" :key="row.id">
                    <td>{{ row.planNo }}</td>
                    <td><input type="date" class="table-input" v-model="row.startDate" /></td>
                    <td><input type="date" class="table-input" v-model="row.endDate" /></td>
                    <td>
                      <select class="table-select" v-model="row.maintenancePerson">
                        <option value="">请选择</option>
                        <option v-for="person in maintenancePersons" :key="person" :value="person">
                          {{ person }}
                        </option>
                      </select>
                    </td>
                    <td><input type="text" class="table-input" v-model="row.remark" placeholder="备注" /></td>
                    <td>
                      <a href="#" class="action-link action-delete" @click="deletePlanRow(index)">删除</a>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>

          <div class="item-table-section">
            <div class="section-header">
              <div class="section-title">维保事项</div>
              <button class="btn btn-add-small" @click="addItemRow">添加事项</button>
            </div>
            <div class="table-wrapper">
              <table class="edit-table">
                <thead>
                  <tr>
                    <th>事项编号</th>
                    <th>巡检项</th>
                    <th>巡检内容</th>
                    <th>检查要求</th>
                    <th>简要说明</th>
                    <th>操作</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="(row, index) in addForm.itemRows" :key="row.id">
                    <td>{{ index + 1 }}</td>
                    <td><input type="text" class="table-input" v-model="row.inspectionItem" placeholder="xxx系统" /></td>
                    <td><input type="text" class="table-input" v-model="row.inspectionContent" placeholder="巡检内容" /></td>
                    <td><input type="text" class="table-input" v-model="row.inspectionRequirement" placeholder="检查要求" /></td>
                    <td><input type="text" class="table-input" v-model="row.briefDescription" placeholder="简要说明" /></td>
                    <td>
                      <a href="#" class="action-link action-delete" @click="deleteItemRow(index)">删除</a>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>
        <div class="modal-footer">
          <button class="btn btn-cancel" @click="closeAddModal">取消</button>
          <button class="btn btn-save" @click="handleSaveAdd">保存</button>
        </div>
      </div>
    </div>

    <div v-if="isEditModalOpen" class="modal-overlay" @click.self="closeEditModal">
      <div class="modal-container modal-large">
        <div class="modal-header">
          <h3 class="modal-title">编辑维保计划</h3>
          <button class="modal-close" @click="closeEditModal">×</button>
        </div>
        <div class="modal-body">
          <div class="project-info-section">
            <div class="project-info-title">项目信息</div>
            <div class="form-grid-half">
              <div class="form-column">
                <div class="form-item">
                  <label class="form-label">
                    <span class="required">*</span> 项目名称
                  </label>
                  <select class="form-input" v-model="editForm.projectName" @change="handleProjectChange">
                    <option value="">选择项目，支持搜索选择</option>
                    <option v-for="project in projectOptions" :key="project.id" :value="project.name">
                      {{ project.name }}
                    </option>
                  </select>
                </div>
                <div class="form-item">
                  <label class="form-label">项目地址</label>
                  <input type="text" class="form-input readonly-input" v-model="editForm.projectAddress" readonly />
                </div>
                <div class="form-item">
                  <label class="form-label">结束日期</label>
                  <input type="text" class="form-input readonly-input" v-model="editForm.endDate" readonly />
                </div>
              </div>
              <div class="form-column">
                <div class="form-item">
                  <label class="form-label">项目编号</label>
                  <input type="text" class="form-input readonly-input" v-model="editForm.projectId" readonly />
                </div>
                <div class="form-item">
                  <label class="form-label">维保周期</label>
                  <input type="text" class="form-input readonly-input" v-model="editForm.maintenanceDays" readonly />
                </div>
                <div class="form-item">
                  <label class="form-label">客户单位</label>
                  <input type="text" class="form-input readonly-input" v-model="editForm.clientUnit" readonly />
                </div>
              </div>
            </div>
          </div>

          <div class="plan-table-section">
            <div class="section-header">
              <div class="section-title">维保计划</div>
              <button class="btn btn-add-small" @click="addEditPlanRow">添加</button>
            </div>
            <div class="table-wrapper">
              <table class="edit-table">
                <thead>
                  <tr>
                    <th>计划编号</th>
                    <th>开始日期</th>
                    <th>结束日期</th>
                    <th>维保人员</th>
                    <th>备注</th>
                    <th>操作</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="(row, index) in editForm.planRows" :key="row.id">
                    <td>{{ row.planNo }}</td>
                    <td><input type="date" class="table-input" v-model="row.startDate" /></td>
                    <td><input type="date" class="table-input" v-model="row.endDate" /></td>
                    <td>
                      <select class="table-select" v-model="row.maintenancePerson">
                        <option value="">请选择</option>
                        <option v-for="person in maintenancePersons" :key="person" :value="person">
                          {{ person }}
                        </option>
                      </select>
                    </td>
                    <td><input type="text" class="table-input" v-model="row.remark" placeholder="备注" /></td>
                    <td>
                      <a href="#" class="action-link action-delete" @click="deleteEditPlanRow(index)">删除</a>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>

          <div class="item-table-section">
            <div class="section-header">
              <div class="section-title">维保事项</div>
              <button class="btn btn-add-small" @click="addEditItemRow">添加事项</button>
            </div>
            <div class="table-wrapper">
              <table class="edit-table">
                <thead>
                  <tr>
                    <th>事项编号</th>
                    <th>巡检项</th>
                    <th>巡检内容</th>
                    <th>检查要求</th>
                    <th>简要说明</th>
                    <th>操作</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="(row, index) in editForm.itemRows" :key="row.id">
                    <td>{{ index + 1 }}</td>
                    <td><input type="text" class="table-input" v-model="row.inspectionItem" placeholder="xxx系统" /></td>
                    <td><input type="text" class="table-input" v-model="row.inspectionContent" placeholder="巡检内容" /></td>
                    <td><input type="text" class="table-input" v-model="row.inspectionRequirement" placeholder="检查要求" /></td>
                    <td><input type="text" class="table-input" v-model="row.briefDescription" placeholder="简要说明" /></td>
                    <td>
                      <a href="#" class="action-link action-delete" @click="deleteEditItemRow(index)">删除</a>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>
        <div class="modal-footer">
          <button class="btn btn-cancel" @click="closeEditModal">取消</button>
          <button class="btn btn-save" @click="handleUpdateEdit">保存</button>
        </div>
      </div>
    </div>

    <div v-if="isViewModalOpen" class="modal-overlay" @click.self="closeViewModal">
      <div class="modal-container modal-large">
        <div class="modal-header">
          <h3 class="modal-title">查看维保计划</h3>
          <button class="modal-close" @click="closeViewModal">×</button>
        </div>
        <div class="modal-body">
          <div class="project-info-section">
            <div class="project-info-title">项目信息</div>
            <div class="form-grid-half">
              <div class="form-column">
                <div class="form-item">
                  <label class="form-label">项目编号</label>
                  <div class="form-value">{{ viewData.id || '-' }}</div>
                </div>
                <div class="form-item">
                  <label class="form-label">项目名称</label>
                  <div class="form-value">{{ viewData.projectName || '-' }}</div>
                </div>
                <div class="form-item">
                  <label class="form-label">开始日期</label>
                  <div class="form-value">{{ viewData.startDate || '-' }}</div>
                </div>
                <div class="form-item">
                  <label class="form-label">客户单位</label>
                  <div class="form-value">{{ viewData.clientName || '-' }}</div>
                </div>
              </div>
              <div class="form-column">
                <div class="form-item">
                  <label class="form-label">维保计划数</label>
                  <div class="form-value">{{ viewData.planCount || '-' }}</div>
                </div>
                <div class="form-item">
                  <label class="form-label">结束日期</label>
                  <div class="form-value">{{ viewData.endDate || '-' }}</div>
                </div>
                <div class="form-item">
                  <label class="form-label">地址</label>
                  <div class="form-value">{{ viewData.address || '-' }}</div>
                </div>
              </div>
            </div>
          </div>

          <div class="plan-table-section">
            <div class="section-header">
              <div class="section-title">维保计划</div>
            </div>
            <div class="table-wrapper">
              <table class="edit-table">
                <thead>
                  <tr>
                    <th>计划编号</th>
                    <th>开始日期</th>
                    <th>结束日期</th>
                    <th>维保人员</th>
                    <th>备注</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="(row, index) in viewData.planRows" :key="row.id">
                    <td>{{ row.planNo }}</td>
                    <td>{{ row.startDate }}</td>
                    <td>{{ row.endDate }}</td>
                    <td>{{ row.maintenancePerson || '-' }}</td>
                    <td>{{ row.remark || '-' }}</td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>

          <div class="item-table-section">
            <div class="section-header">
              <div class="section-title">维保事项</div>
            </div>
            <div class="table-wrapper">
              <table class="edit-table">
                <thead>
                  <tr>
                    <th>事项编号</th>
                    <th>巡检项</th>
                    <th>巡检内容</th>
                    <th>检查要求</th>
                    <th>简要说明</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="(row, index) in viewData.itemRows" :key="row.id">
                    <td>{{ index + 1 }}</td>
                    <td>{{ row.inspectionItem }}</td>
                    <td>{{ row.inspectionContent }}</td>
                    <td>{{ row.inspectionRequirement }}</td>
                    <td>{{ row.briefDescription || '-' }}</td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>
        <div class="modal-footer">
          <button class="btn btn-cancel" @click="closeViewModal">关闭</button>
        </div>
      </div>
    </div>

    <Toast :visible="toast.visible" :message="toast.message" :type="toast.type" />
    <ConfirmDialog 
      :visible="confirmDialog.visible" 
      :title="confirmDialog.title" 
      :message="confirmDialog.message"
      @confirm="confirmDialog.onConfirm"
      @cancel="confirmDialog.visible = false"
    />
  </div>
</template>

<script lang="ts">
import { defineComponent, reactive, ref, computed, watch, onMounted } from 'vue'
import type { ProjectInfo } from '@/types'
import { maintenancePlanService, type MaintenancePlan, type MaintenancePlanDisplay } from '../services/maintenancePlan'
import { projectInfoService } from '../services/projectInfo'
import Toast from '../components/Toast.vue'
import ConfirmDialog from '../components/ConfirmDialog.vue'

export interface PlanRow {
  id: string
  planNo: string
  startDate: string
  endDate: string
  maintenancePerson: string
  remark: string
}

export interface ItemRow {
  id: string
  inspectionItem: string
  inspectionContent: string
  inspectionRequirement: string
  briefDescription: string
}

export default defineComponent({
  name: 'MaintenancePlanManagement',
  setup() {
    const searchForm = reactive({
      projectName: '',
      clientName: ''
    })

    const currentPage = ref(1)
    const pageSize = ref(10)
    const jumpPage = ref(1)
    const isAddModalOpen = ref(false)
    const isEditModalOpen = ref(false)
    const isViewModalOpen = ref(false)
    const editingId = ref('')

    const toast = reactive({
      visible: false,
      message: '',
      type: 'info' as 'success' | 'error' | 'warning' | 'info'
    })

    const confirmDialog = reactive({
      visible: false,
      title: '确认',
      message: '',
      onConfirm: () => {},
      onCancel: () => {}
    })

    const showToast = (message: string, type: 'success' | 'error' | 'warning' | 'info' = 'info') => {
      toast.message = message
      toast.type = type
      toast.visible = true
      setTimeout(() => {
        toast.visible = false
      }, 3000)
    }

    const showConfirm = (message: string, onConfirm: () => void) => {
      confirmDialog.message = message
      confirmDialog.onConfirm = onConfirm
      confirmDialog.visible = true
    }

    const viewData = reactive({
      id: '',
      projectName: '',
      startDate: '',
      endDate: '',
      planCount: 0,
      clientName: '',
      address: '',
      planRows: [] as PlanRow[],
      itemRows: [] as ItemRow[]
    })

    const projectOptions = ref<ProjectInfo[]>([])

    const loadProjectOptions = async () => {
      try {
        const response = await projectInfoService.getAll()
        if (response.code === 200) {
          projectOptions.value = response.data.map((project: any) => ({
            id: String(project.id),
            name: project.project_name,
            completionDate: project.completion_date,
            maintenanceEndDate: project.maintenance_end_date,
            maintenancePeriod: project.maintenance_period,
            clientName: project.client_name,
            address: project.address
          }))
        }
      } catch (error) {
        console.error('加载项目选项失败:', error)
      }
    }

    const maintenancePersons = ref(['刘园智', '晋海龙', '张伟', '李明', '王芳', '赵强'])

    const addForm = reactive({
      projectName: '',
      projectId: '',
      projectAddress: '',
      maintenanceDays: '',
      endDate: '',
      clientUnit: '',
      planRows: [] as PlanRow[],
      itemRows: [] as ItemRow[]
    })

    const editForm = reactive({
      projectName: '',
      projectId: '',
      projectAddress: '',
      maintenanceDays: '',
      endDate: '',
      clientUnit: '',
      planRows: [] as PlanRow[],
      itemRows: [] as ItemRow[]
    })

    const planData = ref<MaintenancePlanDisplay[]>([])
    const totalElements = ref(0)
    const totalPages = ref(0)
    const loading = ref(false)

    const formatDate = (dateStr: string) => {
      if (!dateStr) return ''
      const date = new Date(dateStr)
      const year = date.getFullYear()
      const month = String(date.getMonth() + 1).padStart(2, '0')
      const day = String(date.getDate()).padStart(2, '0')
      return `${year}-${month}-${day}`
    }

    const loadData = async () => {
      loading.value = true
      try {
        const params: any = {
          page: currentPage.value - 1,
          size: pageSize.value
        }
        
        if (searchForm.projectName.trim()) {
          params.plan_name = searchForm.projectName.trim()
        }
        
        if (searchForm.clientName.trim()) {
          params.responsible_department = searchForm.clientName.trim()
        }

        const response = await maintenancePlanService.getList(params)
        
        if (response.code === 200) {
          planData.value = response.data.content.map((item: MaintenancePlan) => ({
            id: String(item.id),
            planId: item.plan_id,
            projectName: item.plan_name,
            startDate: formatDate(item.plan_start_date),
            endDate: formatDate(item.plan_end_date),
            planCount: 1,
            clientName: item.responsible_department || '',
            address: item.equipment_location || '',
            originalData: item
          }))
          totalElements.value = response.data.totalElements
          totalPages.value = response.data.totalPages
        }
      } catch (error) {
        console.error('加载维保计划失败:', error)
        showToast('加载维保计划失败，请稍后重试', 'error')
      } finally {
        loading.value = false
      }
    }

    const handleSearch = () => {
      currentPage.value = 1
      loadData()
    }

    const debounce = (fn: Function, delay: number) => {
      let timeoutId: any
      return (...args: any[]) => {
        clearTimeout(timeoutId)
        timeoutId = setTimeout(() => fn(...args), delay)
      }
    }

    const debouncedSearch = debounce(handleSearch, 300)

    watch(
      () => [searchForm.projectName, searchForm.clientName],
      () => {
        debouncedSearch()
      }
    )

    const handleAdd = () => {
      resetAddForm()
      isAddModalOpen.value = true
    }

    const closeAddModal = () => {
      isAddModalOpen.value = false
    }

    const resetAddForm = () => {
      addForm.projectName = ''
      addForm.projectId = ''
      addForm.projectAddress = ''
      addForm.maintenanceDays = ''
      addForm.endDate = ''
      addForm.clientUnit = ''
      addForm.planRows = []
      addForm.itemRows = []
    }

    const handleProjectChange = () => {
      const selectedProject = projectOptions.value.find(p => p.name === addForm.projectName)
      if (selectedProject) {
        addForm.projectId = selectedProject.id
        addForm.projectAddress = selectedProject.address
        addForm.endDate = selectedProject.maintenanceEndDate
        addForm.clientUnit = selectedProject.clientName

        const start = new Date(selectedProject.completionDate)
        const end = new Date(selectedProject.maintenanceEndDate)
        const diffTime = Math.abs(end.getTime() - start.getTime())
        const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24))
        addForm.maintenanceDays = `${diffDays} 天`

        addForm.planRows = Array.from({ length: 6 }, (_, i) => ({
          id: `plan-${Date.now()}-${i}`,
          planNo: `ZFDY-CY0M-20251101`,
          startDate: '',
          endDate: '',
          maintenancePerson: '',
          remark: ''
        }))

        addForm.itemRows = Array.from({ length: 2 }, (_, i) => ({
          id: `item-${Date.now()}-${i}`,
          inspectionItem: 'xxx系统',
          inspectionContent: '巡检内容巡检内容巡检内容',
          inspectionRequirement: '检查要求检查要求检查要求',
          briefDescription: ''
        }))
      }
    }

    const addPlanRow = () => {
      const lastRow = addForm.planRows[addForm.planRows.length - 1]
      const lastPlanNo = lastRow ? lastRow.planNo : 'ZFDY-CY0M-20251101'
      const parts = lastPlanNo.split('-')
      const lastNum = parseInt(parts[2])
      const newNum = lastNum + 1
      addForm.planRows.push({
        id: `plan-${Date.now()}`,
        planNo: `ZFDY-CY0M-${newNum}`,
        startDate: '',
        endDate: '',
        maintenancePerson: '',
        remark: ''
      })
    }

    const deletePlanRow = (index: number) => {
      showConfirm('确定要删除该计划吗？', () => {
        addForm.planRows.splice(index, 1)
      })
    }

    const addItemRow = () => {
      addForm.itemRows.push({
        id: `item-${Date.now()}`,
        inspectionItem: '',
        inspectionContent: '',
        inspectionRequirement: '',
        briefDescription: ''
      })
    }

    const deleteItemRow = (index: number) => {
      showConfirm('确定要删除该事项吗？', () => {
        addForm.itemRows.splice(index, 1)
      })
    }

    const handleSaveAdd = () => {
      if (!addForm.projectName) {
        showToast('请选择项目名称', 'warning')
        return
      }

      const newPlan: MaintenancePlanDisplay = {
        id: `PLAN-2025-${String(planData.value.length + 1).padStart(3, '0')}`,
        planId: `MP-2025-${String(planData.value.length + 1).padStart(3, '0')}`,
        projectName: addForm.projectName,
        startDate: addForm.endDate,
        endDate: addForm.endDate,
        planCount: addForm.planRows.length,
        clientName: addForm.clientUnit,
        address: addForm.projectAddress,
        originalData: {} as MaintenancePlan
      }

      planData.value = [newPlan, ...planData.value]
      showToast('添加成功', 'success')
      closeAddModal()
    }

    const handleView = (item: MaintenancePlanDisplay) => {
      viewData.id = item.id
      viewData.projectName = item.projectName
      viewData.startDate = item.startDate
      viewData.endDate = item.endDate
      viewData.planCount = item.planCount
      viewData.clientName = item.clientName
      viewData.address = item.address
      viewData.planRows = Array.from({ length: 6 }, (_, i) => ({
        id: `plan-${Date.now()}-${i}`,
        planNo: `ZFDY-CY0M-20251101`,
        startDate: item.startDate,
        endDate: item.endDate,
        maintenancePerson: i === 0 ? '刘园智' : i === 1 ? '晋海龙' : '',
        remark: i === 0 ? '需要跟客户现场演示' : ''
      }))
      viewData.itemRows = Array.from({ length: 2 }, (_, i) => ({
        id: `item-${Date.now()}-${i}`,
        inspectionItem: 'xxx系统',
        inspectionContent: '巡检内容巡检内容巡检内容',
        inspectionRequirement: '检查要求检查要求检查要求',
        briefDescription: ''
      }))
      isViewModalOpen.value = true
    }

    const closeViewModal = () => {
      isViewModalOpen.value = false
    }

    const handleEdit = (item: MaintenancePlanDisplay) => {
      editingId.value = item.id
      editForm.projectName = item.projectName
      editForm.projectId = item.planId
      editForm.projectAddress = item.address
      editForm.endDate = item.endDate
      editForm.clientUnit = item.clientName
      editForm.planRows = Array.from({ length: 6 }, (_, i) => ({
        id: `plan-${Date.now()}-${i}`,
        planNo: `ZFDY-CY0M-20251101`,
        startDate: item.startDate,
        endDate: item.endDate,
        maintenancePerson: '',
        remark: ''
      }))
      editForm.itemRows = Array.from({ length: 2 }, (_, i) => ({
        id: `item-${Date.now()}-${i}`,
        inspectionItem: 'xxx系统',
        inspectionContent: '巡检内容巡检内容巡检内容',
        inspectionRequirement: '检查要求检查要求检查要求',
        briefDescription: ''
      }))
      isEditModalOpen.value = true
    }

    const closeEditModal = () => {
      isEditModalOpen.value = false
      editingId.value = ''
    }

    const handleUpdateEdit = () => {
      if (!editForm.projectName) {
        showToast('请选择项目名称', 'warning')
        return
      }

      const index = planData.value.findIndex(p => p.id === editingId.value)
      if (index > -1) {
        planData.value[index] = {
          id: editingId.value,
          planId: planData.value[index].planId,
          projectName: editForm.projectName,
          startDate: editForm.planRows[0]?.startDate || editForm.endDate,
          endDate: editForm.endDate,
          planCount: editForm.planRows.length,
          clientName: editForm.clientUnit,
          address: editForm.projectAddress,
          originalData: {} as MaintenancePlan
        }
      }
      showToast('更新成功', 'success')
      closeEditModal()
    }

    const addEditPlanRow = () => {
      const lastRow = editForm.planRows[editForm.planRows.length - 1]
      const lastPlanNo = lastRow ? lastRow.planNo : 'ZFDY-CY0M-20251101'
      const parts = lastPlanNo.split('-')
      const lastNum = parseInt(parts[2])
      const newNum = lastNum + 1
      editForm.planRows.push({
        id: `plan-${Date.now()}`,
        planNo: `ZFDY-CY0M-${newNum}`,
        startDate: '',
        endDate: '',
        maintenancePerson: '',
        remark: ''
      })
    }

    const deleteEditPlanRow = (index: number) => {
      showConfirm('确定要删除该计划吗？', () => {
        editForm.planRows.splice(index, 1)
      })
    }

    const addEditItemRow = () => {
      editForm.itemRows.push({
        id: `item-${Date.now()}`,
        inspectionItem: '',
        inspectionContent: '',
        inspectionRequirement: '',
        briefDescription: ''
      })
    }

    const deleteEditItemRow = (index: number) => {
      showConfirm('确定要删除该事项吗？', () => {
        editForm.itemRows.splice(index, 1)
      })
    }

    const handleDelete = async (item: MaintenancePlanDisplay) => {
      showConfirm('确定要删除该维保计划吗？', async () => {
        try {
          const response = await maintenancePlanService.delete(Number(item.id))
          
          if (response.code === 200) {
            showToast('删除成功', 'success')
            loadData()
          } else {
            showToast(response.message || '删除失败', 'error')
          }
        } catch (error) {
          console.error('删除失败:', error)
          showToast('删除失败，请稍后重试', 'error')
        }
      })
    }

    const handleJump = () => {
      const page = jumpPage.value
      if (page >= 1 && page <= totalPages.value) {
        currentPage.value = page
      }
    }

    return {
      searchForm,
      planData,
      loading,
      currentPage,
      pageSize,
      totalPages,
      totalElements,
      jumpPage,
      isAddModalOpen,
      isEditModalOpen,
      isViewModalOpen,
      projectOptions,
      maintenancePersons,
      addForm,
      editForm,
      viewData,
      toast,
      confirmDialog,
      formatDate,
      handleSearch,
      handleAdd,
      closeAddModal,
      handleProjectChange,
      addPlanRow,
      deletePlanRow,
      addItemRow,
      deleteItemRow,
      handleSaveAdd,
      handleView,
      closeViewModal,
      handleEdit,
      closeEditModal,
      handleUpdateEdit,
      addEditPlanRow,
      deleteEditPlanRow,
      addEditItemRow,
      deleteEditItemRow,
      handleDelete,
      handleJump
    }

    onMounted(() => {
      loadData()
      loadProjectOptions()
    })
  }
})
</script>

<style scoped>
.maintenance-plan-management {
  background: #fff;
  border-radius: 4px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  padding: 20px;
}

.search-section {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding: 20px;
  background: #f8f9fa;
  border-radius: 4px;
}

.search-form {
  display: flex;
  gap: 24px;
  align-items: center;
}

.search-item {
  display: flex;
  align-items: center;
  gap: 8px;
}

.search-label {
  font-size: 14px;
  font-weight: 500;
  color: #424242;
  white-space: nowrap;
}

.search-input {
  width: 200px;
  padding: 8px 12px;
  border: 1px solid #e0e0e0;
  border-radius: 3px;
  font-size: 14px;
  color: #333;
  background: #fff;
  transition: border-color 0.15s;
}

.search-input:focus {
  outline: none;
  border-color: #1976d2;
  box-shadow: 0 0 0 2px rgba(25, 118, 210, 0.1);
}

.search-input::placeholder {
  color: #999;
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

.btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
  box-shadow: none;
}

.btn-add {
  background: #2E7D32;
  color: #fff;
}

.btn-add:hover:not(:disabled) {
  background: #1B5E20;
}

.btn-search {
  background: #2196F3;
  color: #fff;
}

.btn-search:hover:not(:disabled) {
  background: #1976D2;
}

.table-section {
  margin-bottom: 20px;
  border: 1px solid #e0e0e0;
  border-radius: 4px;
  overflow: hidden;
}

.data-table {
  width: 100%;
  border-collapse: collapse;
}

.data-table thead {
  background: #E0E0E0;
}

.data-table th {
  padding: 12px 16px;
  text-align: left;
  font-size: 14px;
  font-weight: 600;
  color: #333;
  border-bottom: 1px solid #d0d0d0;
}

.data-table td {
  padding: 12px 16px;
  text-align: left;
  font-size: 14px;
  color: #616161;
  border-bottom: 1px solid #f0f0f0;
}

.data-table tbody tr:hover {
  background: #f5f5f5;
}

.even-row {
  background: #fafafa;
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
  writing-mode: horizontal-tb;
  white-space: nowrap;
}

.action-link:hover {
  opacity: 0.8;
}

.action-view {
  color: #2E7D32;
}

.action-edit {
  color: #2196F3;
}

.action-delete {
  color: #D32F2F;
}

.pagination-section {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 0;
}

.pagination-info {
  font-size: 14px;
  color: #666;
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
  border: 1px solid #e0e0e0;
  border-radius: 3px;
  background: #fff;
  font-size: 14px;
  color: #333;
  cursor: pointer;
  transition: all 0.15s;
  display: flex;
  align-items: center;
  justify-content: center;
}

.page-btn:hover:not(:disabled) {
  border-color: #2196F3;
  color: #2196F3;
}

.page-btn:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}

.page-btn.active {
  background: #2196F3;
  color: #fff;
  border-color: #2196F3;
}

.page-nav {
  font-size: 16px;
}

.page-select {
  padding: 6px 12px;
  border: 1px solid #e0e0e0;
  border-radius: 3px;
  font-size: 14px;
  color: #333;
  background: #fff;
  cursor: pointer;
}

.page-jump {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
  color: #666;
}

.page-input {
  width: 48px;
  padding: 6px 8px;
  border: 1px solid #e0e0e0;
  border-radius: 3px;
  font-size: 14px;
  color: #333;
  text-align: center;
  background: #fff;
}

.page-input:focus {
  outline: none;
  border-color: #2196F3;
}

.page-go {
  min-width: 40px;
  height: 28px;
  padding: 0 8px;
  background: #2196F3;
  color: #fff;
  border: none;
  border-radius: 3px;
  font-size: 12px;
  cursor: pointer;
  transition: background 0.15s;
}

.page-go:hover {
  background: #1976D2;
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
  display: flex;
  flex-direction: column;
}

.modal-large {
  width: 900px;
  max-width: 95vw;
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
  overflow-y: auto;
  flex: 1;
}

.project-info-section {
  margin-bottom: 24px;
  padding: 16px;
  background: #f8f9fa;
  border-radius: 4px;
}

.project-info-title {
  font-size: 16px;
  font-weight: 600;
  color: #333;
  margin-bottom: 16px;
}

.form-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 24px 40px;
  align-items: start;
}

.form-grid-half {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 24px;
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

.readonly-input {
  background: #f5f5f5;
  cursor: not-allowed;
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

.plan-table-section,
.item-table-section {
  margin-bottom: 24px;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.section-title {
  font-size: 16px;
  font-weight: 600;
  color: #333;
}

.btn-add-small {
  padding: 6px 12px;
  background: #2E7D32;
  color: #fff;
  border: none;
  border-radius: 3px;
  font-size: 13px;
  font-weight: 500;
  cursor: pointer;
  transition: background 0.15s;
}

.btn-add-small:hover {
  background: #1B5E20;
}

.table-wrapper {
  border: 1px solid #e0e0e0;
  border-radius: 4px;
  overflow: hidden;
}

.edit-table {
  width: 100%;
  border-collapse: collapse;
}

.edit-table thead {
  background: #E0E0E0;
}

.edit-table th {
  padding: 10px 12px;
  text-align: left;
  font-size: 13px;
  font-weight: 600;
  color: #333;
  border-bottom: 1px solid #d0d0d0;
}

.edit-table td {
  padding: 8px 12px;
  text-align: left;
  font-size: 13px;
  border-bottom: 1px solid #f0f0f0;
}

.edit-table tbody tr:hover {
  background: #f5f5f5;
}

.table-input,
.table-select {
  width: 100%;
  padding: 6px 8px;
  border: 1px solid #e0e0e0;
  border-radius: 3px;
  font-size: 13px;
  color: #333;
  background: #fff;
  transition: border-color 0.15s;
}

.table-input:focus,
.table-select:focus {
  outline: none;
  border-color: #1976d2;
  box-shadow: 0 0 0 2px rgba(25, 118, 210, 0.1);
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

.btn-cancel:hover {
  background: #f5f5f5;
}

.btn-save {
  background: #2196F3;
  color: #fff;
}

.btn-save:hover {
  background: #1976D2;
}
</style>
