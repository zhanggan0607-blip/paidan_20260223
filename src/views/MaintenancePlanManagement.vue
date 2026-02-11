<template>
  <div class="maintenance-plan-management">
    <LoadingSpinner :visible="loading" text="加载中..." />
    <Toast :visible="toast.visible" :message="toast.message" :type="toast.type" />

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
        <button class="btn btn-add" @click="openModal">
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
          <tr v-for="(item, index) in planData" :key="item.id" :class="{ 'even-row': index % 2 === 0 }">
            <td>{{ startIndex + index + 1 }}</td>
            <td>{{ item.project_id }}</td>
            <td>{{ item.plan_name }}</td>
            <td>{{ formatDate(item.plan_start_date) }}</td>
            <td>{{ formatDate(item.plan_end_date) }}</td>
            <td>{{ 1 }}</td>
            <td>{{ item.responsible_department || '-' }}</td>
            <td>{{ item.equipment_location || '-' }}</td>
            <td class="action-cell">
              <a href="#" class="action-link action-view" @click.prevent="handleView(item)">查看</a>
              <a href="#" class="action-link action-edit" @click.prevent="handleEdit(item)">编辑计划</a>
              <a href="#" class="action-link action-maintenance" @click.prevent="handleMaintenance(item)">事项维护</a>
              <a href="#" class="action-link action-delete" @click.prevent="handleDelete(item)">删除</a>
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
          v-for="page in totalPages"
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

    <div v-if="isModalOpen" class="modal-overlay" @click.self="closeModal">
      <div class="modal-container modal-large">
        <div class="modal-header">
          <h3 class="modal-title">新增维保计划</h3>
          <button class="modal-close" @click="closeModal">×</button>
        </div>
        <div class="modal-body">
          <div class="section-title">基础信息</div>
          <div class="form-grid">
            <div class="form-column">
              <div class="form-item">
                <label class="form-label">
                  <span class="required">*</span> 项目名称
                </label>
                <select class="form-input" v-model="formData.selectedProjectId" @change="handleProjectChange">
                  <option value="">请选择项目</option>
                  <option v-for="project in projectList" :key="project.id" :value="project.id">
                    {{ project.project_name }}
                  </option>
                </select>
              </div>
              <div class="form-item">
                <label class="form-label">维保周期</label>
                <input type="text" class="form-input form-input-readonly" v-model="formData.maintenance_period" readonly />
              </div>
              <div class="form-item">
                <label class="form-label">项目地址</label>
                <input type="text" class="form-input form-input-readonly" v-model="formData.address" readonly />
              </div>
            </div>
            <div class="form-column">
              <div class="form-item">
                <label class="form-label">项目编号</label>
                <input type="text" class="form-input form-input-readonly" v-model="formData.project_id" readonly />
              </div>
              <div class="form-item">
                <label class="form-label">项目结束日期</label>
                <input type="text" class="form-input form-input-readonly" v-model="formData.maintenance_end_date" readonly />
              </div>
              <div class="form-item">
                <label class="form-label">客户单位</label>
                <input type="text" class="form-input form-input-readonly" v-model="formData.client_name" readonly />
              </div>
            </div>
          </div>

          <div class="section-divider"></div>

          <div class="section-title">维保计划</div>
          <div class="table-section-inner">
            <table class="inner-table">
              <thead>
                <tr>
                  <th>计划编号</th>
                  <th>计划开始日期</th>
                  <th>计划结束日期</th>
                  <th>维保人员</th>
                  <th>备注</th>
                  <th>操作</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="(plan, index) in formData.planList" :key="index">
                  <td>
                    <input type="text" class="table-input" v-model="plan.plan_id" placeholder="请输入" />
                  </td>
                  <td>
                    <input type="date" class="table-input" v-model="plan.plan_start_date" />
                  </td>
                  <td>
                    <input type="date" class="table-input" v-model="plan.plan_end_date" />
                  </td>
                  <td>
                    <select class="table-input" v-model="plan.responsible_person">
                      <option value="">请选择</option>
                      <option v-for="person in personnelList" :key="person" :value="person">
                        {{ person }}
                      </option>
                    </select>
                  </td>
                  <td>
                    <input type="text" class="table-input" v-model="plan.remarks" placeholder="请输入" />
                  </td>
                  <td class="action-cell">
                    <a href="#" class="action-link action-delete" @click.prevent="removePlan(index)">删除</a>
                  </td>
                </tr>
              </tbody>
            </table>
            <div class="table-actions">
              <button class="btn btn-add-small" @click="addPlan">添加</button>
            </div>
          </div>

          <div class="section-divider"></div>

          <div class="section-title">维保事项</div>
          <div class="table-section-inner">
            <table class="inner-table">
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
                <tr v-for="(item, index) in formData.itemList" :key="index">
                  <td>
                    <input type="text" class="table-input" v-model="item.item_id" placeholder="请输入" />
                  </td>
                  <td>
                    <input type="text" class="table-input" v-model="item.inspection_item" placeholder="请输入" />
                  </td>
                  <td>
                    <input type="text" class="table-input" v-model="item.inspection_content" placeholder="请输入" />
                  </td>
                  <td>
                    <input type="text" class="table-input" v-model="item.check_requirements" placeholder="请输入" />
                  </td>
                  <td>
                    <input type="text" class="table-input" v-model="item.brief_description" placeholder="请输入" />
                  </td>
                  <td class="action-cell">
                    <a href="#" class="action-link action-delete" @click.prevent="removeItem(index)">删除</a>
                  </td>
                </tr>
              </tbody>
            </table>
            <div class="table-actions">
              <button class="btn btn-add-small" @click="addItem">添加行</button>
              <button class="btn btn-add-small" @click="importItems">导入事项</button>
            </div>
          </div>
        </div>
        <div class="modal-footer">
          <button class="btn btn-cancel" @click="closeModal">取消</button>
          <button class="btn btn-save" @click="handleSave" :disabled="saving">
            {{ saving ? '保存中...' : '保存' }}
          </button>
        </div>
      </div>
    </div>

    <div v-if="isViewModalOpen" class="modal-overlay" @click.self="closeViewModal">
      <div class="modal-container">
        <div class="modal-header">
          <h3 class="modal-title">查看维保计划</h3>
          <button class="modal-close" @click="closeViewModal">×</button>
        </div>
        <div class="modal-body">
          <div class="form-grid">
            <div class="form-column">
              <div class="form-item">
                <label class="form-label">计划名称</label>
                <div class="form-value">{{ viewData.plan_name || '-' }}</div>
              </div>
              <div class="form-item">
                <label class="form-label">计划编号</label>
                <div class="form-value">{{ viewData.plan_id || '-' }}</div>
              </div>
              <div class="form-item">
                <label class="form-label">项目编号</label>
                <div class="form-value">{{ viewData.project_id || '-' }}</div>
              </div>
              <div class="form-item">
                <label class="form-label">计划类型</label>
                <div class="form-value">{{ viewData.plan_type || '-' }}</div>
              </div>
              <div class="form-item">
                <label class="form-label">设备编号</label>
                <div class="form-value">{{ viewData.equipment_id || '-' }}</div>
              </div>
              <div class="form-item">
                <label class="form-label">设备名称</label>
                <div class="form-value">{{ viewData.equipment_name || '-' }}</div>
              </div>
              <div class="form-item">
                <label class="form-label">设备型号</label>
                <div class="form-value">{{ viewData.equipment_model || '-' }}</div>
              </div>
              <div class="form-item">
                <label class="form-label">设备位置</label>
                <div class="form-value">{{ viewData.equipment_location || '-' }}</div>
              </div>
            </div>
            <div class="form-column">
              <div class="form-item">
                <label class="form-label">开始日期</label>
                <div class="form-value">{{ formatDate(viewData.plan_start_date) || '-' }}</div>
              </div>
              <div class="form-item">
                <label class="form-label">结束日期</label>
                <div class="form-value">{{ formatDate(viewData.plan_end_date) || '-' }}</div>
              </div>
              <div class="form-item">
                <label class="form-label">执行日期</label>
                <div class="form-value">{{ formatDate(viewData.execution_date) || '-' }}</div>
              </div>
              <div class="form-item">
                <label class="form-label">下次维保日期</label>
                <div class="form-value">{{ formatDate(viewData.next_maintenance_date) || '-' }}</div>
              </div>
              <div class="form-item">
                <label class="form-label">负责人</label>
                <div class="form-value">{{ viewData.responsible_person || '-' }}</div>
              </div>
              <div class="form-item">
                <label class="form-label">负责部门</label>
                <div class="form-value">{{ viewData.responsible_department || '-' }}</div>
              </div>
              <div class="form-item">
                <label class="form-label">联系方式</label>
                <div class="form-value">{{ viewData.contact_info || '-' }}</div>
              </div>
              <div class="form-item">
                <label class="form-label">计划状态</label>
                <div class="form-value">{{ viewData.plan_status || '-' }}</div>
              </div>
              <div class="form-item">
                <label class="form-label">执行状态</label>
                <div class="form-value">{{ viewData.execution_status || '-' }}</div>
              </div>
              <div class="form-item">
                <label class="form-label">完成率</label>
                <div class="form-value">{{ viewData.completion_rate || 0 }}%</div>
              </div>
            </div>
          </div>
          <div class="form-item-full">
            <label class="form-label">维保内容</label>
            <div class="form-value form-value-textarea">{{ viewData.maintenance_content || '-' }}</div>
          </div>
          <div class="form-item-full">
            <label class="form-label">维保要求</label>
            <div class="form-value form-value-textarea">{{ viewData.maintenance_requirements || '-' }}</div>
          </div>
          <div class="form-item-full">
            <label class="form-label">维保标准</label>
            <div class="form-value form-value-textarea">{{ viewData.maintenance_standard || '-' }}</div>
          </div>
          <div class="form-item-full">
            <label class="form-label">备注</label>
            <div class="form-value form-value-textarea">{{ viewData.remarks || '-' }}</div>
          </div>
        </div>
        <div class="modal-footer">
          <button class="btn btn-cancel" @click="closeViewModal">关闭</button>
        </div>
      </div>
    </div>

    <div v-if="isEditModalOpen" class="modal-overlay" @click.self="closeEditModal">
      <div class="modal-container">
        <div class="modal-header">
          <h3 class="modal-title">编辑维保计划</h3>
          <button class="modal-close" @click="closeEditModal">×</button>
        </div>
        <div class="modal-body">
          <div class="form-grid">
            <div class="form-column">
              <div class="form-item">
                <label class="form-label">
                  <span class="required">*</span> 计划名称
                </label>
                <input type="text" class="form-input" placeholder="请输入" v-model="editData.plan_name" maxlength="200" />
              </div>
              <div class="form-item">
                <label class="form-label">
                  <span class="required">*</span> 计划编号
                </label>
                <input type="text" class="form-input" placeholder="请输入" v-model="editData.plan_id" maxlength="50" />
              </div>
              <div class="form-item">
                <label class="form-label">
                  <span class="required">*</span> 项目编号
                </label>
                <input type="text" class="form-input" placeholder="请输入" v-model="editData.project_id" maxlength="50" />
              </div>
              <div class="form-item">
                <label class="form-label">
                  <span class="required">*</span> 计划类型
                </label>
                <select class="form-input" v-model="editData.plan_type">
                  <option value="">请选择</option>
                  <option value="定期维保">定期维保</option>
                  <option value="预防性维保">预防性维保</option>
                  <option value="故障维修">故障维修</option>
                  <option value="巡检">巡检</option>
                  <option value="其他">其他</option>
                </select>
              </div>
              <div class="form-item">
                <label class="form-label">
                  <span class="required">*</span> 设备编号
                </label>
                <input type="text" class="form-input" placeholder="请输入" v-model="editData.equipment_id" maxlength="50" />
              </div>
              <div class="form-item">
                <label class="form-label">
                  <span class="required">*</span> 设备名称
                </label>
                <input type="text" class="form-input" placeholder="请输入" v-model="editData.equipment_name" maxlength="200" />
              </div>
              <div class="form-item">
                <label class="form-label">设备型号</label>
                <input type="text" class="form-input" placeholder="请输入" v-model="editData.equipment_model" maxlength="100" />
              </div>
              <div class="form-item">
                <label class="form-label">设备位置</label>
                <input type="text" class="form-input" placeholder="请输入" v-model="editData.equipment_location" maxlength="200" />
              </div>
            </div>
            <div class="form-column">
              <div class="form-item">
                <label class="form-label">
                  <span class="required">*</span> 开始日期
                </label>
                <input type="date" class="form-input" v-model="editData.plan_start_date" />
              </div>
              <div class="form-item">
                <label class="form-label">
                  <span class="required">*</span> 结束日期
                </label>
                <input type="date" class="form-input" v-model="editData.plan_end_date" />
              </div>
              <div class="form-item">
                <label class="form-label">执行日期</label>
                <input type="date" class="form-input" v-model="editData.execution_date" />
              </div>
              <div class="form-item">
                <label class="form-label">下次维保日期</label>
                <input type="date" class="form-input" v-model="editData.next_maintenance_date" />
              </div>
              <div class="form-item">
                <label class="form-label">
                  <span class="required">*</span> 负责人
                </label>
                <input type="text" class="form-input" placeholder="请输入" v-model="editData.responsible_person" maxlength="50" />
              </div>
              <div class="form-item">
                <label class="form-label">负责部门</label>
                <input type="text" class="form-input" placeholder="请输入" v-model="editData.responsible_department" maxlength="100" />
              </div>
              <div class="form-item">
                <label class="form-label">联系方式</label>
                <input type="text" class="form-input" placeholder="请输入" v-model="editData.contact_info" maxlength="50" />
              </div>
              <div class="form-item">
                <label class="form-label">
                  <span class="required">*</span> 计划状态
                </label>
                <select class="form-input" v-model="editData.plan_status">
                  <option value="">请选择</option>
                  <option value="待执行">待执行</option>
                  <option value="执行中">执行中</option>
                  <option value="已完成">已完成</option>
                  <option value="已取消">已取消</option>
                  <option value="已延期">已延期</option>
                </select>
              </div>
              <div class="form-item">
                <label class="form-label">
                  <span class="required">*</span> 执行状态
                </label>
                <select class="form-input" v-model="editData.execution_status">
                  <option value="">请选择</option>
                  <option value="未开始">未开始</option>
                  <option value="进行中">进行中</option>
                  <option value="已完成">已完成</option>
                  <option value="已取消">已取消</option>
                  <option value="异常">异常</option>
                </select>
              </div>
              <div class="form-item">
                <label class="form-label">完成率</label>
                <input type="number" class="form-input" placeholder="0-100" v-model="editData.completion_rate" min="0" max="100" />
              </div>
            </div>
          </div>
          <div class="form-item-full">
            <label class="form-label">
              <span class="required">*</span> 维保内容
            </label>
            <textarea class="form-textarea" placeholder="请输入" v-model="editData.maintenance_content" rows="3"></textarea>
          </div>
          <div class="form-item-full">
            <label class="form-label">维保要求</label>
            <textarea class="form-textarea" placeholder="请输入" v-model="editData.maintenance_requirements" rows="2"></textarea>
          </div>
          <div class="form-item-full">
            <label class="form-label">维保标准</label>
            <textarea class="form-textarea" placeholder="请输入" v-model="editData.maintenance_standard" rows="2"></textarea>
          </div>
          <div class="form-item-full">
            <label class="form-label">备注</label>
            <textarea class="form-textarea" placeholder="请输入" v-model="editData.remarks" rows="2"></textarea>
          </div>
        </div>
        <div class="modal-footer">
          <button class="btn btn-cancel" @click="closeEditModal">取消</button>
          <button class="btn btn-save" @click="handleUpdate" :disabled="saving">
            {{ saving ? '保存中...' : '保存' }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script lang="ts">
import { defineComponent, reactive, ref, computed, watch, onMounted } from 'vue'
import { maintenancePlanService, type MaintenancePlan, type MaintenancePlanCreate, type MaintenancePlanUpdate } from '../services/maintenancePlan'
import { projectInfoService, type ProjectInfo } from '../services/projectInfo'
import { personnelService } from '../services/personnel'
import LoadingSpinner from '../components/LoadingSpinner.vue'
import Toast from '../components/Toast.vue'

export default defineComponent({
  name: 'MaintenancePlanManagement',
  components: {
    LoadingSpinner,
    Toast
  },
  setup() {
    const searchForm = reactive({
      projectName: '',
      clientName: ''
    })

    const currentPage = ref(0)
    const pageSize = ref(10)
    const jumpPage = ref(1)
    const loading = ref(false)
    const saving = ref(false)
    const isModalOpen = ref(false)
    const isViewModalOpen = ref(false)
    const isEditModalOpen = ref(false)
    const editingId = ref<number | null>(null)
    
    const planData = ref<MaintenancePlan[]>([])
    const totalElements = ref(0)
    const totalPages = ref(0)
    const projectList = ref<ProjectInfo[]>([])
    const personnelList = ref<string[]>([])

    const toast = reactive({
      visible: false,
      message: '',
      type: 'success' as 'success' | 'error' | 'warning' | 'info'
    })

    const loadPersonnel = async () => {
      try {
        const response = await personnelService.getAll()
        if (response.code === 200 && response.data) {
          personnelList.value = response.data.map(p => p.name)
        }
      } catch (error) {
        console.error('加载人员选项失败:', error)
      }
    }

    interface PlanItem {
      plan_id: string
      plan_start_date: string
      plan_end_date: string
      responsible_person: string
      remarks: string
    }

    interface InspectionItem {
      item_id: string
      inspection_item: string
      inspection_content: string
      check_requirements: string
      brief_description: string
    }

    const formData = reactive({
      selectedProjectId: 0,
      project_id: '',
      address: '',
      maintenance_period: '',
      maintenance_end_date: '',
      client_name: '',
      planList: [] as PlanItem[],
      itemList: [] as InspectionItem[]
    })

    const viewData = reactive({
      id: 0,
      plan_id: '',
      plan_name: '',
      project_id: '',
      plan_type: '',
      equipment_id: '',
      equipment_name: '',
      equipment_model: '',
      equipment_location: '',
      plan_start_date: '',
      plan_end_date: '',
      execution_date: '',
      next_maintenance_date: '',
      responsible_person: '',
      responsible_department: '',
      contact_info: '',
      maintenance_content: '',
      maintenance_requirements: '',
      maintenance_standard: '',
      plan_status: '',
      execution_status: '',
      completion_rate: 0,
      remarks: ''
    })

    const editData = reactive({
      id: 0,
      plan_id: '',
      plan_name: '',
      project_id: '',
      plan_type: '',
      equipment_id: '',
      equipment_name: '',
      equipment_model: '',
      equipment_location: '',
      plan_start_date: '',
      plan_end_date: '',
      execution_date: '',
      next_maintenance_date: '',
      responsible_person: '',
      responsible_department: '',
      contact_info: '',
      maintenance_content: '',
      maintenance_requirements: '',
      maintenance_standard: '',
      plan_status: '',
      execution_status: '',
      completion_rate: 0,
      remarks: ''
    })

    const startIndex = computed(() => currentPage.value * pageSize.value)

    const showToast = (message: string, type: 'success' | 'error' | 'warning' | 'info' = 'success') => {
      toast.message = message
      toast.type = type
      toast.visible = true
    }

    const formatDate = (dateStr: string) => {
      if (!dateStr) return '-'
      const date = new Date(dateStr)
      return date.toLocaleDateString('zh-CN', {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit'
      })
    }

    const formatDateForAPI = (dateStr: string) => {
      if (!dateStr) return ''
      const date = new Date(dateStr)
      const year = date.getFullYear()
      const month = String(date.getMonth() + 1).padStart(2, '0')
      const day = String(date.getDate()).padStart(2, '0')
      return `${year}-${month}-${day}T00:00:00`
    }

    const loadProjectList = async () => {
      try {
        const response = await projectInfoService.getAll()
        if (response.code === 200) {
          projectList.value = response.data
        }
      } catch (error) {
        console.error('加载项目列表失败:', error)
      }
    }

    const handleProjectChange = () => {
      const selectedProject = projectList.value.find(p => p.id === formData.selectedProjectId)
      if (selectedProject) {
        formData.project_id = selectedProject.project_id
        formData.address = selectedProject.address
        formData.maintenance_period = selectedProject.maintenance_period
        formData.maintenance_end_date = formatDate(selectedProject.maintenance_end_date)
        formData.client_name = selectedProject.client_name
      }
    }

    const addPlan = () => {
      formData.planList.push({
        plan_id: '',
        plan_start_date: '',
        plan_end_date: '',
        responsible_person: '',
        remarks: ''
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
        brief_description: ''
      })
    }

    const removeItem = (index: number) => {
      formData.itemList.splice(index, 1)
    }

    const importItems = () => {
      showToast('导入事项功能开发中', 'info')
    }

    const loadData = async () => {
      console.log('🔄 [前端] 开始加载数据...')
      loading.value = true
      try {
        console.log('📤 [前端] 请求参数:', {
          page: currentPage.value,
          size: pageSize.value,
          project_name: searchForm.projectName || undefined,
          client_name: searchForm.clientName || undefined
        })
        
        const response = await maintenancePlanService.getList({
          page: currentPage.value,
          size: pageSize.value,
          project_name: searchForm.projectName || undefined,
          client_name: searchForm.clientName || undefined
        })
        
        console.log('📥 [前端] 响应数据:', response)
        
        if (response.code === 200) {
          console.log('✅ [前端] 数据加载成功，记录数:', response.data.content.length)
          planData.value = response.data.content
          totalElements.value = response.data.totalElements
          totalPages.value = response.data.totalPages
          console.log('📋 [前端] 当前列表:', planData.value)
        } else {
          console.error('❌ [前端] 数据加载失败:', response.message)
          showToast(response.message || '加载数据失败', 'error')
        }
      } catch (error: any) {
        console.error('❌ [前端] 加载数据异常:', error)
        showToast(error.message || '加载数据失败，请检查网络连接', 'error')
      } finally {
        loading.value = false
      }
    }

    const handleSearch = () => {
      currentPage.value = 0
      loadData()
    }

    const checkFormValid = (): boolean => {
      if (!formData.selectedProjectId) {
        showToast('请选择项目', 'warning')
        return false
      }
      if (formData.planList.length === 0) {
        showToast('请至少添加一条维保计划', 'warning')
        return false
      }
      return true
    }

    const openModal = () => {
      resetForm()
      loadProjectList()
      isModalOpen.value = true
    }

    const closeModal = () => {
      isModalOpen.value = false
    }

    const resetForm = () => {
      formData.selectedProjectId = 0
      formData.project_id = ''
      formData.address = ''
      formData.maintenance_period = ''
      formData.maintenance_end_date = ''
      formData.client_name = ''
      formData.planList = []
      formData.itemList = []
    }

    const handleSave = async () => {
      console.log('🔄 [前端] 开始保存维保计划...')
      if (!checkFormValid()) {
        console.log('❌ [前端] 表单验证失败')
        return
      }

      saving.value = true
      try {
        const selectedProject = projectList.value.find(p => p.id === formData.selectedProjectId)
        if (!selectedProject) {
          showToast('请选择项目', 'error')
          return
        }

        const createData: MaintenancePlanCreate = {
          plan_id: formData.planList[0]?.plan_id || '',
          plan_name: selectedProject.project_name,
          project_id: formData.project_id,
          plan_type: '定期维保',
          equipment_id: 'EQ001',
          equipment_name: '默认设备',
          equipment_model: undefined,
          equipment_location: formData.address,
          plan_start_date: formData.planList[0]?.plan_start_date || '',
          plan_end_date: formData.planList[0]?.plan_end_date || '',
          execution_date: undefined,
          next_maintenance_date: undefined,
          responsible_person: formData.planList[0]?.responsible_person || '',
          responsible_department: formData.client_name,
          contact_info: undefined,
          maintenance_content: formData.itemList.map(item => item.inspection_content).join('; '),
          maintenance_requirements: formData.itemList.map(item => item.check_requirements).join('; '),
          maintenance_standard: undefined,
          plan_status: '待执行',
          execution_status: '未开始',
          completion_rate: 0,
          remarks: formData.planList[0]?.remarks
        }

        console.log('📤 [前端] 创建数据:', createData)
        const response = await maintenancePlanService.create(createData)
        console.log('📥 [前端] 创建响应:', response)
        
        if (response.code === 200) {
          console.log('✅ [前端] 创建成功')
          showToast('创建成功', 'success')
          closeModal()
          resetForm()
          
          console.log('🔄 [前端] 重置到第一页并刷新数据...')
          currentPage.value = 0
          await loadData()
        } else {
          console.error('❌ [前端] 创建失败:', response.message)
          showToast(response.message || '创建失败', 'error')
        }
      } catch (error: any) {
        console.error('❌ [前端] 创建异常:', error)
        showToast(error.message || '创建失败，请检查网络连接', 'error')
      } finally {
        saving.value = false
      }
    }

    const handleView = async (item: MaintenancePlan) => {
      viewData.id = item.id
      viewData.plan_id = item.plan_id
      viewData.plan_name = item.plan_name
      viewData.project_id = item.project_id
      viewData.plan_type = item.plan_type
      viewData.equipment_id = item.equipment_id
      viewData.equipment_name = item.equipment_name
      viewData.equipment_model = item.equipment_model || ''
      viewData.equipment_location = item.equipment_location || ''
      viewData.plan_start_date = item.plan_start_date
      viewData.plan_end_date = item.plan_end_date
      viewData.execution_date = item.execution_date || ''
      viewData.next_maintenance_date = item.next_maintenance_date || ''
      viewData.responsible_person = item.responsible_person
      viewData.responsible_department = item.responsible_department || ''
      viewData.contact_info = item.contact_info || ''
      viewData.maintenance_content = item.maintenance_content
      viewData.maintenance_requirements = item.maintenance_requirements || ''
      viewData.maintenance_standard = item.maintenance_standard || ''
      viewData.plan_status = item.plan_status
      viewData.execution_status = item.execution_status
      viewData.completion_rate = item.completion_rate || 0
      viewData.remarks = item.remarks || ''
      isViewModalOpen.value = true
    }

    const handleEdit = (item: MaintenancePlan) => {
      editingId.value = item.id
      editData.id = item.id
      editData.plan_id = item.plan_id
      editData.plan_name = item.plan_name
      editData.project_id = item.project_id
      editData.plan_type = item.plan_type
      editData.equipment_id = item.equipment_id
      editData.equipment_name = item.equipment_name
      editData.equipment_model = item.equipment_model || ''
      editData.equipment_location = item.equipment_location || ''
      editData.plan_start_date = item.plan_start_date
      editData.plan_end_date = item.plan_end_date
      editData.execution_date = item.execution_date || ''
      editData.next_maintenance_date = item.next_maintenance_date || ''
      editData.responsible_person = item.responsible_person
      editData.responsible_department = item.responsible_department || ''
      editData.contact_info = item.contact_info || ''
      editData.maintenance_content = item.maintenance_content
      editData.maintenance_requirements = item.maintenance_requirements || ''
      editData.maintenance_standard = item.maintenance_standard || ''
      editData.plan_status = item.plan_status
      editData.execution_status = item.execution_status
      editData.completion_rate = item.completion_rate || 0
      editData.remarks = item.remarks || ''
      isEditModalOpen.value = true
    }

    const closeViewModal = () => {
      isViewModalOpen.value = false
    }

    const closeEditModal = () => {
      isEditModalOpen.value = false
      editingId.value = null
    }

    const checkEditFormValid = (): boolean => {
      if (!editData.plan_name?.trim()) {
        showToast('请填写计划名称', 'warning')
        return false
      }
      if (!editData.plan_id?.trim()) {
        showToast('请填写计划编号', 'warning')
        return false
      }
      if (!editData.project_id?.trim()) {
        showToast('请填写项目编号', 'warning')
        return false
      }
      if (!editData.plan_type?.trim()) {
        showToast('请选择计划类型', 'warning')
        return false
      }
      if (!editData.equipment_id?.trim()) {
        showToast('请填写设备编号', 'warning')
        return false
      }
      if (!editData.equipment_name?.trim()) {
        showToast('请填写设备名称', 'warning')
        return false
      }
      if (!editData.plan_start_date) {
        showToast('请填写开始日期', 'warning')
        return false
      }
      if (!editData.plan_end_date) {
        showToast('请填写结束日期', 'warning')
        return false
      }
      if (!editData.responsible_person?.trim()) {
        showToast('请填写负责人', 'warning')
        return false
      }
      if (!editData.plan_status?.trim()) {
        showToast('请选择计划状态', 'warning')
        return false
      }
      if (!editData.execution_status?.trim()) {
        showToast('请选择执行状态', 'warning')
        return false
      }
      if (!editData.maintenance_content?.trim()) {
        showToast('请填写维保内容', 'warning')
        return false
      }
      return true
    }

    const handleUpdate = async () => {
      if (!checkEditFormValid() || editingId.value === null) {
        return
      }

      saving.value = true
      try {
        const updateData: MaintenancePlanUpdate = {
          plan_id: editData.plan_id,
          plan_name: editData.plan_name,
          project_id: editData.project_id,
          plan_type: editData.plan_type,
          equipment_id: editData.equipment_id,
          equipment_name: editData.equipment_name,
          equipment_model: editData.equipment_model || undefined,
          equipment_location: editData.equipment_location || undefined,
          plan_start_date: formatDateForAPI(editData.plan_start_date),
          plan_end_date: formatDateForAPI(editData.plan_end_date),
          execution_date: editData.execution_date ? formatDateForAPI(editData.execution_date) : undefined,
          next_maintenance_date: editData.next_maintenance_date ? formatDateForAPI(editData.next_maintenance_date) : undefined,
          responsible_person: editData.responsible_person,
          responsible_department: editData.responsible_department || undefined,
          contact_info: editData.contact_info || undefined,
          maintenance_content: editData.maintenance_content,
          maintenance_requirements: editData.maintenance_requirements || undefined,
          maintenance_standard: editData.maintenance_standard || undefined,
          plan_status: editData.plan_status,
          execution_status: editData.execution_status,
          completion_rate: editData.completion_rate || 0,
          remarks: editData.remarks || undefined
        }

        const response = await maintenancePlanService.update(editingId.value, updateData)
        
        if (response.code === 200) {
          showToast('更新成功', 'success')
          closeEditModal()
          await loadData()
        } else {
          showToast(response.message || '更新失败', 'error')
        }
      } catch (error: any) {
        console.error('更新失败:', error)
        showToast(error.message || '更新失败，请检查网络连接', 'error')
      } finally {
        saving.value = false
      }
    }

    const handleDelete = async (item: MaintenancePlan) => {
      if (!confirm('确定要删除该维保计划吗？')) {
        return
      }

      loading.value = true
      try {
        const response = await maintenancePlanService.delete(item.id)
        
        if (response.code === 200) {
          showToast('删除成功', 'success')
          await loadData()
        } else {
          showToast(response.message || '删除失败', 'error')
        }
      } catch (error: any) {
        console.error('删除失败:', error)
        showToast(error.message || '删除失败，请检查网络连接', 'error')
      } finally {
        loading.value = false
      }
    }

    const handleMaintenance = (item: MaintenancePlan) => {
      showToast('事项维护功能开发中', 'info')
    }

    const handleJump = () => {
      const page = jumpPage.value
      if (page >= 1 && page <= totalPages.value) {
        currentPage.value = page - 1
      }
    }

    const handlePageSizeChange = () => {
      currentPage.value = 0
      loadData()
    }

    watch(currentPage, () => {
      loadData()
    })

    onMounted(() => {
      loadData()
      loadPersonnel()
    })

    return {
      searchForm,
      planData,
      currentPage,
      pageSize,
      totalPages,
      jumpPage,
      totalElements,
      startIndex,
      isModalOpen,
      loading,
      saving,
      isViewModalOpen,
      isEditModalOpen,
      viewData,
      editData,
      formData,
      toast,
      projectList,
      personnelList,
      openModal,
      closeModal,
      handleSave,
      handleView,
      handleEdit,
      handleDelete,
      handleMaintenance,
      handleSearch,
      handleUpdate,
      handleJump,
      handlePageSizeChange,
      closeViewModal,
      closeEditModal,
      formatDate,
      handleProjectChange,
      addPlan,
      removePlan,
      addItem,
      removeItem,
      importItems
    }
  }
})
</script>

<style scoped>
.maintenance-plan-management {
  background: #fff;
  border-radius: 4px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  padding: 20px;
  position: relative;
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
  flex-wrap: wrap;
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
  opacity: 0.6;
  cursor: not-allowed;
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

.btn-search:hover {
  background: #1976D2;
}

.table-section {
  margin-bottom: 20px;
  border: 1px solid #e0e0e0;
  border-radius: 4px;
  overflow-x: auto;
}

.data-table {
  width: 100%;
  border-collapse: collapse;
  min-width: 1200px;
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
  white-space: nowrap;
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

.action-maintenance {
  color: #FF9800;
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
  width: 1000px;
  max-width: 95vw;
  max-height: 90vh;
  overflow-y: auto;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
}

.modal-large {
  width: 1200px;
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
  min-height: 90px;
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

.form-textarea {
  padding: 8px 12px;
  border: 1px solid #e0e0e0;
  border-radius: 3px;
  font-size: 14px;
  color: #333;
  background: #fff;
  transition: border-color 0.15s;
  resize: vertical;
  font-family: inherit;
}

.form-textarea:focus {
  outline: none;
  border-color: #1976d2;
  box-shadow: 0 0 0 2px rgba(25, 118, 210, 0.1);
}

.form-textarea::placeholder {
  color: #999;
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
  background: #2196F3;
  color: #fff;
}

.btn-save:hover:not(:disabled) {
  background: #1976D2;
}

.section-title {
  font-size: 16px;
  font-weight: 600;
  color: #333;
  margin-bottom: 16px;
  padding-bottom: 8px;
  border-bottom: 2px solid #2196F3;
}

.section-divider {
  height: 1px;
  background: #e0e0e0;
  margin: 24px 0;
}

.table-section-inner {
  margin-top: 16px;
}

.inner-table {
  width: 100%;
  border-collapse: collapse;
  margin-bottom: 12px;
}

.inner-table thead {
  background: #E0E0E0;
}

.inner-table th {
  padding: 10px 12px;
  text-align: left;
  font-size: 13px;
  font-weight: 600;
  color: #333;
  border-bottom: 1px solid #d0d0d0;
  white-space: nowrap;
}

.inner-table td {
  padding: 8px 12px;
  border-bottom: 1px solid #f0f0f0;
}

.table-input {
  width: 100%;
  padding: 6px 8px;
  border: 1px solid #e0e0e0;
  border-radius: 3px;
  font-size: 13px;
  color: #333;
  background: #fff;
  transition: border-color 0.15s;
}

.table-input:focus {
  outline: none;
  border-color: #1976d2;
  box-shadow: 0 0 0 2px rgba(25, 118, 210, 0.1);
}

.table-input::placeholder {
  color: #999;
}

.table-actions {
  display: flex;
  gap: 8px;
  justify-content: flex-start;
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
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.1);
}

.btn-add-small:hover {
  background: #1B5E20;
}

.form-input-readonly {
  background: #f5f5f5;
  cursor: not-allowed;
}
</style>
