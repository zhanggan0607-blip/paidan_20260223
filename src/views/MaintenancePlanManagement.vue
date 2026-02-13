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
          <h3 class="modal-title">{{ editingId !== null ? '编辑维保计划' : '新增维保计划' }}</h3>
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
                <label class="form-label">维保频率</label>
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
                  <th>工单编号</th>
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
                  <th style="width: 60px;">事项编号</th>
                  <th>巡查类</th>
                  <th>巡查项</th>
                  <th>巡查内容</th>
                  <th>检查要求</th>
                  <th>简要说明</th>
                  <th>操作</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="(item, index) in formData.itemList" :key="index">
                  <td>
                    <input type="text" class="table-input table-input-readonly" :value="index + 1" readonly />
                  </td>
                  <td>
                    <el-select 
                      v-model="item.level1_id" 
                      placeholder="选择巡查类" 
                      size="small"
                      style="width: 100%;"
                      @change="handleLevel1Change(index)"
                    >
                      <el-option
                        v-for="node in level1Nodes"
                        :key="node.id"
                        :label="node.label"
                        :value="node.id"
                      />
                    </el-select>
                  </td>
                  <td>
                    <el-select 
                      v-model="item.level2_id" 
                      placeholder="选择巡查项" 
                      size="small"
                      style="width: 100%;"
                      :disabled="!item.level1_id"
                      @change="handleLevel2Change(index)"
                    >
                      <el-option
                        v-for="node in getLevel2Nodes(item.level1_id)"
                        :key="node.id"
                        :label="node.label"
                        :value="node.id"
                      />
                    </el-select>
                  </td>
                  <td>
                    <el-select 
                      v-model="item.level3_id" 
                      placeholder="选择巡查内容" 
                      size="small"
                      style="width: 100%;"
                      :disabled="!item.level2_id"
                      @change="handleLevel3Change(index)"
                    >
                      <el-option
                        v-for="node in getLevel3Nodes(item.level1_id, item.level2_id)"
                        :key="node.id"
                        :label="node.label"
                        :value="node.id"
                      />
                    </el-select>
                  </td>
                  <td>
                    <el-input 
                      v-model="item.check_requirements" 
                      placeholder="自动带出"
                      size="small"
                      readonly
                    />
                  </td>
                  <td>
                    <input type="text" class="table-input table-input-readonly" v-model="item.brief_description" placeholder="自动带出" readonly />
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
                <label class="form-label">工单编号</label>
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
                  <span class="required">*</span> 工单编号
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
                  <option v-for="option in planTypeOptions" :key="option.dict_key" :value="option.dict_value">
                    {{ option.dict_label }}
                  </option>
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
                  <option v-for="option in planStatusOptions" :key="option.dict_key" :value="option.dict_value">
                    {{ option.dict_label }}
                  </option>
                </select>
              </div>
              <div class="form-item">
                <label class="form-label">
                  <span class="required">*</span> 执行状态
                </label>
                <select class="form-input" v-model="editData.execution_status">
                  <option value="">请选择</option>
                  <option v-for="option in executionStatusOptions" :key="option.dict_key" :value="option.dict_value">
                    {{ option.dict_label }}
                  </option>
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

    <Toast :visible="toast.visible" :message="toast.message" :type="toast.type" />
    <ConfirmDialog 
      :visible="confirmDialog.visible" 
      :title="confirmDialog.title" 
      :message="confirmDialog.message"
      @confirm="handleConfirm"
      @cancel="handleCancelConfirm"
    />
  </div>
</template>

<script lang="ts">
import { defineComponent, reactive, ref, computed, watch, onMounted, onUnmounted, watchEffect } from 'vue'
import { ElSelect, ElOption, ElInput } from 'element-plus'
import { maintenancePlanService, type MaintenancePlan, type MaintenancePlanCreate, type MaintenancePlanUpdate } from '../services/maintenancePlan'
import { projectInfoService, type ProjectInfo } from '../services/projectInfo'
import { personnelService } from '../services/personnel'
import { dictionaryService, dictionaryTypes, type Dictionary } from '../services/dictionary'
import { inspectionItemService, type InspectionItem as ApiInspectionItem } from '../services/inspectionItem'
import LoadingSpinner from '../components/LoadingSpinner.vue'
import Toast from '../components/Toast.vue'
import ConfirmDialog from '../components/ConfirmDialog.vue'

interface InspectionTreeNode {
  id: string
  label: string
  level: number
  checkRequirement?: string
  checkStandard?: string
  children?: InspectionTreeNode[]
}

export default defineComponent({
  name: 'MaintenancePlanManagement',
  components: {
    LoadingSpinner,
    Toast,
    ConfirmDialog,
    ElSelect,
    ElOption,
    ElInput
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
    const planTypeOptions = ref<Dictionary[]>([])
    const planStatusOptions = ref<Dictionary[]>([])
    const executionStatusOptions = ref<Dictionary[]>([])

    const toast = reactive({
      visible: false,
      message: '',
      type: 'success' as 'success' | 'error' | 'warning' | 'info'
    })

    const confirmDialog = reactive({
      visible: false,
      title: '确认',
      message: ''
    })

    let pendingConfirmAction: (() => void) | null = null

    const showConfirm = (message: string, onConfirm: () => void) => {
      confirmDialog.message = message
      pendingConfirmAction = onConfirm
      confirmDialog.visible = true
    }

    const handleConfirm = () => {
      confirmDialog.visible = false
      if (pendingConfirmAction) {
        pendingConfirmAction()
        pendingConfirmAction = null
      }
    }

    const handleCancelConfirm = () => {
      confirmDialog.visible = false
      pendingConfirmAction = null
    }

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

    const loadDictionary = async () => {
      try {
        const [planTypeRes, planStatusRes, executionStatusRes] = await Promise.all([
          dictionaryService.getByType(dictionaryTypes.MAINTENANCE_PLAN_TYPE),
          dictionaryService.getByType(dictionaryTypes.MAINTENANCE_PLAN_STATUS),
          dictionaryService.getByType(dictionaryTypes.MAINTENANCE_EXECUTION_STATUS)
        ])
        
        if (planTypeRes.code === 200 && planTypeRes.data) {
          planTypeOptions.value = planTypeRes.data
        }
        if (planStatusRes.code === 200 && planStatusRes.data) {
          planStatusOptions.value = planStatusRes.data
        }
        if (executionStatusRes.code === 200 && executionStatusRes.data) {
          executionStatusOptions.value = executionStatusRes.data
        }
      } catch (error) {
        console.error('加载字典数据失败:', error)
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
      level1_id: string
      level2_id: string
      level3_id: string
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

    const inspectionTreeData = ref<InspectionTreeNode[]>([])

    const transformInspectionTree = (items: ApiInspectionItem[]): InspectionTreeNode[] => {
      return items.map(item => ({
        id: String(item.id),
        label: item.item_name,
        level: item.level,
        checkRequirement: item.check_content || undefined,
        checkStandard: item.check_standard || undefined,
        children: item.children ? transformInspectionTree(item.children) : undefined
      }))
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

    const level1Nodes = computed(() => {
      return inspectionTreeData.value.filter(node => node.level === 1)
    })

    const getLevel2Nodes = (level1Id: string) => {
      const level1Node = inspectionTreeData.value.find(node => node.id === level1Id)
      return level1Node?.children || []
    }

    const getLevel3Nodes = (level1Id: string, level2Id: string) => {
      const level2Nodes = getLevel2Nodes(level1Id)
      const level2Node = level2Nodes.find(node => node.id === level2Id)
      return level2Node?.children || []
    }

    const handleLevel1Change = (index: number) => {
      const item = formData.itemList[index]
      item.level2_id = ''
      item.level3_id = ''
      item.check_requirements = ''
      item.brief_description = ''
      item.inspection_item = ''
      item.inspection_content = ''
      
      if (item.level1_id) {
        const level1Node = inspectionTreeData.value.find(node => node.id === item.level1_id)
        if (level1Node) {
          item.inspection_item = level1Node.label
        }
      }
    }

    const handleLevel2Change = (index: number) => {
      const item = formData.itemList[index]
      item.level3_id = ''
      item.check_requirements = ''
      item.brief_description = ''
      item.inspection_content = ''
      
      if (item.level1_id && item.level2_id) {
        const level2Nodes = getLevel2Nodes(item.level1_id)
        const level2Node = level2Nodes.find(node => node.id === item.level2_id)
        if (level2Node) {
          item.inspection_content = level2Node.label
        }
      }
    }

    const handleLevel3Change = (index: number) => {
      const item = formData.itemList[index]
      item.check_requirements = ''
      item.brief_description = ''
      
      if (item.level1_id && item.level2_id && item.level3_id) {
        const level3Nodes = getLevel3Nodes(item.level1_id, item.level2_id)
        const level3Node = level3Nodes.find(node => node.id === item.level3_id)
        if (level3Node) {
          item.check_requirements = level3Node.checkRequirement || ''
          item.brief_description = level3Node.checkStandard || ''
        }
      }
    }

    let abortController: AbortController | null = null

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

        const projectManager = (selectedProject as any).project_manager || ''
        formData.planList = generatePlanList(
          selectedProject.project_id,
          new Date(selectedProject.completion_date),
          new Date(selectedProject.maintenance_end_date),
          selectedProject.maintenance_period,
          projectManager
        )
      }
    }

    const generatePlanList = (projectId: string, startDate: Date, endDate: Date, period: string, projectManager: string = ''): PlanItem[] => {
      const list: PlanItem[] = []
      const planPeriods = generateMaintenancePeriods(startDate, endDate, period)
      
      planPeriods.forEach((periodInfo, index) => {
        const planId = `${projectId}-${String(index + 1).padStart(3, '0')}`
        list.push({
          plan_id: planId,
          plan_start_date: formatDateToString(periodInfo.start),
          plan_end_date: formatDateToString(periodInfo.end),
          responsible_person: projectManager,
          remarks: ''
        })
      })
      
      return list
    }

    interface PeriodInfo {
      start: Date
      end: Date
    }

    const generateMaintenancePeriods = (projStart: Date, projEnd: Date, period: string): PeriodInfo[] => {
      const periods: PeriodInfo[] = []
      
      if (period === '每天') {
        return generateDailyPeriods(projStart, projEnd)
      } else if (period === '每周') {
        return generateWeeklyPeriods(projStart, projEnd)
      } else if (period === '每月') {
        return generateMonthlyPeriods(projStart, projEnd)
      } else if (period === '每季度') {
        return generateQuarterlyPeriods(projStart, projEnd)
      } else if (period === '每半年') {
        return generateHalfYearlyPeriods(projStart, projEnd)
      }
      
      return generateMonthlyPeriods(projStart, projEnd)
    }

    const generateDailyPeriods = (projStart: Date, projEnd: Date): PeriodInfo[] => {
      const periods: PeriodInfo[] = []
      let currentDate = new Date(projStart)
      
      while (currentDate <= projEnd) {
        periods.push({
          start: new Date(currentDate),
          end: new Date(currentDate)
        })
        currentDate.setDate(currentDate.getDate() + 1)
      }
      
      return periods
    }

    const generateWeeklyPeriods = (projStart: Date, projEnd: Date): PeriodInfo[] => {
      const periods: PeriodInfo[] = []
      let currentStart = new Date(projStart)
      
      while (currentStart <= projEnd) {
        const dayOfWeek = currentStart.getDay()
        const daysToMonday = dayOfWeek === 0 ? -6 : 1 - dayOfWeek
        const daysToSunday = dayOfWeek === 0 ? 0 : 7 - dayOfWeek
        
        const weekStart = new Date(currentStart)
        weekStart.setDate(weekStart.getDate() + daysToMonday)
        if (weekStart < projStart) {
          weekStart.setTime(projStart.getTime())
        }
        
        const weekEnd = new Date(currentStart)
        weekEnd.setDate(weekEnd.getDate() + daysToSunday)
        if (weekEnd > projEnd) {
          weekEnd.setTime(projEnd.getTime())
        }
        
        periods.push({
          start: new Date(weekStart),
          end: new Date(weekEnd)
        })
        
        const nextWeekStart = new Date(currentStart)
        nextWeekStart.setDate(nextWeekStart.getDate() + (7 - dayOfWeek) + 1)
        currentStart = nextWeekStart
      }
      
      return periods
    }

    const generateMonthlyPeriods = (projStart: Date, projEnd: Date): PeriodInfo[] => {
      const periods: PeriodInfo[] = []
      let currentStart = new Date(projStart)
      
      while (currentStart <= projEnd) {
        const year = currentStart.getFullYear()
        const month = currentStart.getMonth()
        
        const monthStart = new Date(year, month, 1)
        if (monthStart < projStart) {
          monthStart.setTime(projStart.getTime())
        }
        
        const monthEnd = new Date(year, month + 1, 0)
        if (monthEnd > projEnd) {
          monthEnd.setTime(projEnd.getTime())
        }
        
        periods.push({
          start: new Date(monthStart),
          end: new Date(monthEnd)
        })
        
        currentStart = new Date(year, month + 1, 1)
      }
      
      return periods
    }

    const generateQuarterlyPeriods = (projStart: Date, projEnd: Date): PeriodInfo[] => {
      const periods: PeriodInfo[] = []
      let currentStart = new Date(projStart)
      
      while (currentStart <= projEnd) {
        const year = currentStart.getFullYear()
        const month = currentStart.getMonth()
        const quarter = Math.floor(month / 3)
        
        const quarterStartMonth = quarter * 3
        const quarterEndMonth = quarterStartMonth + 2
        
        const quarterStart = new Date(year, quarterStartMonth, 1)
        if (quarterStart < projStart) {
          quarterStart.setTime(projStart.getTime())
        }
        
        const quarterEnd = new Date(year, quarterEndMonth + 1, 0)
        if (quarterEnd > projEnd) {
          quarterEnd.setTime(projEnd.getTime())
        }
        
        periods.push({
          start: new Date(quarterStart),
          end: new Date(quarterEnd)
        })
        
        currentStart = new Date(year, quarterEndMonth + 1, 1)
      }
      
      return periods
    }

    const generateHalfYearlyPeriods = (projStart: Date, projEnd: Date): PeriodInfo[] => {
      const periods: PeriodInfo[] = []
      let currentStart = new Date(projStart)
      
      while (currentStart <= projEnd) {
        const year = currentStart.getFullYear()
        const month = currentStart.getMonth()
        const half = month < 6 ? 0 : 1
        
        let halfStart: Date, halfEnd: Date
        
        if (half === 0) {
          halfStart = new Date(year, 0, 1)
          halfEnd = new Date(year, 6, 0)
        } else {
          halfStart = new Date(year, 6, 1)
          halfEnd = new Date(year, 12, 0)
        }
        
        if (halfStart < projStart) {
          halfStart.setTime(projStart.getTime())
        }
        if (halfEnd > projEnd) {
          halfEnd.setTime(projEnd.getTime())
        }
        
        periods.push({
          start: new Date(halfStart),
          end: new Date(halfEnd)
        })
        
        if (half === 0) {
          currentStart = new Date(year, 6, 1)
        } else {
          currentStart = new Date(year + 1, 0, 1)
        }
      }
      
      return periods
    }

    const formatDateToString = (date: Date): string => {
      const year = date.getFullYear()
      const month = String(date.getMonth() + 1).padStart(2, '0')
      const day = String(date.getDate()).padStart(2, '0')
      return `${year}-${month}-${day}`
    }

    const addPlan = () => {
      const projectId = formData.project_id || 'PRJ'
      let newNum = 1
      
      if (formData.planList.length > 0) {
        const lastPlan = formData.planList[formData.planList.length - 1]
        if (lastPlan && lastPlan.plan_id) {
          const parts = lastPlan.plan_id.split('-')
          const lastNum = parseInt(parts[parts.length - 1])
          if (!isNaN(lastNum)) {
            newNum = lastNum + 1
          }
        }
      }
      
      formData.planList.push({
        plan_id: `${projectId}-${String(newNum).padStart(3, '0')}`,
        plan_start_date: '',
        plan_end_date: '',
        responsible_person: '',
        remarks: ''
      })
    }

    const removePlan = (index: number) => {
      showConfirm('确定要删除该计划吗？', () => {
        formData.planList.splice(index, 1)
      })
    }

    const addItem = () => {
      formData.itemList.push({
        item_id: '',
        inspection_item: '',
        inspection_content: '',
        check_requirements: '',
        brief_description: '',
        level1_id: '',
        level2_id: '',
        level3_id: ''
      })
    }

    const removeItem = (index: number) => {
      showConfirm('确定要删除该事项吗？', () => {
        formData.itemList.splice(index, 1)
      })
    }

    const importItems = () => {
      showToast('导入事项功能开发中', 'info')
    }

    const loadData = async () => {
      if (abortController) {
        abortController.abort()
      }
      abortController = new AbortController()

      loading.value = true
      try {
        const response = await maintenancePlanService.getList({
          page: currentPage.value,
          size: pageSize.value,
          project_name: searchForm.projectName || undefined,
          client_name: searchForm.clientName || undefined
        })
        
        if (response.code === 200) {
          planData.value = response.data.content
          totalElements.value = response.data.totalElements
          totalPages.value = response.data.totalPages
        } else {
          showToast(response.message || '加载数据失败', 'error')
        }
      } catch (error: any) {
        if (error instanceof Error && error.name === 'AbortError') {
          return
        }
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
      editingId.value = null
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
      if (!checkFormValid()) {
        return
      }

      saving.value = true
      try {
        const selectedProject = projectList.value.find(p => p.id === formData.selectedProjectId)
        if (!selectedProject) {
          showToast('请选择项目', 'error')
          return
        }

        const planData: MaintenancePlanCreate = {
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

        let response
        if (editingId.value !== null) {
          response = await maintenancePlanService.update(editingId.value, planData)
        } else {
          response = await maintenancePlanService.create(planData)
        }
        
        if (response.code === 200) {
          showToast(editingId.value !== null ? '更新成功' : '创建成功', 'success')
          closeModal()
          resetForm()
          editingId.value = null
          
          currentPage.value = 0
          await loadData()
        } else {
          showToast(response.message || (editingId.value !== null ? '更新失败' : '创建失败'), 'error')
        }
      } catch (error: any) {
        showToast(error.message || '操作失败，请检查网络连接', 'error')
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

    const handleEdit = async (item: MaintenancePlan) => {
      editingId.value = item.id
      
      if (projectList.value.length === 0) {
        await loadProjectList()
      }
      
      console.log('项目列表:', projectList.value.map(p => ({ id: p.id, project_id: p.project_id, project_name: p.project_name })))
      console.log('当前维保计划 project_id:', item.project_id)
      
      const project = projectList.value.find(p => p.project_id === item.project_id)
      console.log('匹配到的项目:', project)
      
      if (project) {
        formData.selectedProjectId = project.id
        formData.project_id = item.project_id
        formData.address = project.address
        formData.maintenance_period = project.maintenance_period
        formData.maintenance_end_date = formatDate(project.maintenance_end_date)
        formData.client_name = project.client_name
      } else {
        formData.selectedProjectId = 0
        formData.project_id = item.project_id
        formData.address = item.equipment_location || ''
        formData.maintenance_period = ''
        formData.maintenance_end_date = ''
        formData.client_name = item.responsible_department || ''
      }

      formData.planList = [{
        plan_id: item.plan_id,
        plan_start_date: formatDateForInput(item.plan_start_date),
        plan_end_date: formatDateForInput(item.plan_end_date),
        responsible_person: item.responsible_person,
        remarks: item.remarks || ''
      }]

      formData.itemList = []
      if (item.maintenance_content) {
        const contents = item.maintenance_content.split('; ')
        const requirements = item.maintenance_requirements ? item.maintenance_requirements.split('; ') : []
        contents.forEach((content, index) => {
          formData.itemList.push({
            item_id: '',
            inspection_item: '',
            inspection_content: content,
            check_requirements: requirements[index] || '',
            brief_description: '',
            level1_id: '',
            level2_id: '',
            level3_id: ''
          })
        })
      }

      isModalOpen.value = true
    }

    const formatDateForInput = (dateStr: string) => {
      if (!dateStr) return ''
      const date = new Date(dateStr)
      const year = date.getFullYear()
      const month = String(date.getMonth() + 1).padStart(2, '0')
      const day = String(date.getDate()).padStart(2, '0')
      return `${year}-${month}-${day}`
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
      showConfirm('确定要删除该维保计划吗？', async () => {
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
      })
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

    watchEffect((onCleanup) => {
      const unwatch = watch(currentPage, () => {
        loadData()
      })
      onCleanup(() => {
        unwatch()
      })
    })

    onMounted(() => {
      loadData()
      loadPersonnel()
      loadDictionary()
      loadProjectList()
      loadInspectionTree()
    })

    onUnmounted(() => {
      if (abortController) {
        abortController.abort()
      }
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
      confirmDialog,
      editingId,
      projectList,
      personnelList,
      planTypeOptions,
      planStatusOptions,
      executionStatusOptions,
      openModal,
      closeModal,
      handleSave,
      handleView,
      handleEdit,
      handleDelete,
      handleConfirm,
      handleCancelConfirm,
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
      importItems,
      level1Nodes,
      getLevel2Nodes,
      getLevel3Nodes,
      handleLevel1Change,
      handleLevel2Change,
      handleLevel3Change
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
  table-layout: auto;
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
  width: auto;
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

.table-input-readonly {
  background: #f5f5f5;
  color: #666;
  cursor: not-allowed;
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
