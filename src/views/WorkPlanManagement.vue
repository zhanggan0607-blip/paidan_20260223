<template>
  <div class="work-plan-page">
    <Toast :visible="toast.visible" :message="toast.message" :type="toast.type" />
    <div class="content">
      <div class="search-section">
        <div class="search-form">
          <div class="search-row">
            <div class="search-item">
              <label class="search-label">计划类型：</label>
              <select class="search-input" v-model="searchForm.plan_type">
                <option value="">全部</option>
                <option v-for="type in planTypes" :key="type" :value="type">{{ type }}</option>
              </select>
            </div>
            <div class="search-item">
              <label class="search-label">项目名称：</label>
              <input type="text" class="search-input" placeholder="请输入项目名称" v-model="searchForm.project_name" />
            </div>
            <div class="search-item">
              <label class="search-label">客户名称：</label>
              <input type="text" class="search-input" placeholder="请输入客户名称" v-model="searchForm.client_name" />
            </div>
          </div>
        </div>
        <div class="action-buttons">
          <button class="btn btn-reset" @click="handleReset">
            重置
          </button>
          <button class="btn btn-add" @click="handleAdd">
            新增工作计划
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
              <th>工单编号</th>
              <th>计划类型</th>
              <th>项目编号</th>
              <th>项目名称</th>
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
                <span :class="getPlanTypeClass(item.plan_type)" class="type-badge">{{ item.plan_type }}</span>
              </td>
              <td>{{ item.project_id }}</td>
              <td>{{ item.project_name }}</td>
              <td>{{ formatDate(item.plan_start_date) }}</td>
              <td>{{ formatDate(item.plan_end_date) }}</td>
              <td>{{ item.client_name || '-' }}</td>
              <td>{{ item.maintenance_personnel || '-' }}</td>
              <td>
                <span :class="getStatusClass(item.status)" class="status-badge">{{ item.status }}</span>
              </td>
              <td class="action-cell">
                <a href="#" class="action-link action-view" @click.prevent="handleView(item)">查看</a>
                <a href="#" v-if="item.status === '待执行' || item.status === '未进行'" class="action-link action-edit" @click.prevent="handleEdit(item)">编辑</a>
                <a href="#" v-if="item.status === '待执行' || item.status === '未进行'" class="action-link action-delete" @click.prevent="handleDelete(item)">删除</a>
                <a href="#" v-if="item.status === '待确认'" class="action-link action-confirm" @click.prevent="handleConfirm(item)">确认</a>
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

    <div v-if="isAddModalOpen" class="modal-overlay" @click.self="closeAddModal">
      <div class="modal-container">
        <div class="modal-header">
          <h3 class="modal-title">{{ isEditMode ? '编辑工作计划' : '新增工作计划' }}</h3>
          <button class="modal-close" @click="closeAddModal">×</button>
        </div>
        <div class="modal-body">
          <div class="form-grid">
            <div class="form-column">
              <div class="form-item">
                <label class="form-label">
                  <span class="required">*</span> 计划类型
                </label>
                <select class="form-input" v-model="formData.plan_type">
                  <option value="">请选择计划类型</option>
                  <option v-for="type in planTypes" :key="type" :value="type">{{ type }}</option>
                </select>
              </div>
              <div class="form-item">
                <label class="form-label">
                  <span class="required">*</span> 项目名称
                </label>
                <select class="form-input" v-model="formData.project_name" @change="handleProjectChange">
                  <option value="">请选择项目</option>
                  <option v-for="project in projectList" :key="project.id" :value="project.project_name">
                    {{ project.project_name }}
                  </option>
                </select>
              </div>
              <div class="form-item">
                <label class="form-label">
                  <span class="required">*</span> 项目编号
                </label>
                <input type="text" class="form-input form-input-readonly" placeholder="选择项目后自动填充" v-model="formData.project_id" readonly />
              </div>
              <div class="form-item">
                <label class="form-label">
                  <span class="required">*</span> 工单编号
                </label>
                <input type="text" class="form-input form-input-readonly" placeholder="选择项目后自动生成" v-model="formData.plan_id" readonly />
              </div>
              <div class="form-item">
                <label class="form-label">
                  <span class="required">*</span> 客户单位
                </label>
                <input type="text" class="form-input form-input-readonly" placeholder="选择项目后自动填充" v-model="formData.client_name" readonly />
              </div>
            </div>
            <div class="form-column">
              <div class="form-item">
                <label class="form-label">
                  <span class="required">*</span> 计划开始日期
                </label>
                <input type="date" class="form-input" v-model="formData.plan_start_date" />
              </div>
              <div class="form-item">
                <label class="form-label">
                  <span class="required">*</span> 计划结束日期
                </label>
                <input type="date" class="form-input" v-model="formData.plan_end_date" />
              </div>
              <div class="form-item">
                <label class="form-label">
                  <span class="required">*</span> 运维人员
                </label>
                <select class="form-input" v-model="formData.maintenance_personnel">
                  <option value="">请选择</option>
                  <option v-for="person in personnelList" :key="person.id" :value="person.name">
                    {{ person.name }}
                  </option>
                </select>
              </div>
              <div class="form-item">
                <label class="form-label">状态</label>
                <select class="form-input" v-model="formData.status">
                  <option value="未进行">未进行</option>
                  <option value="待确认">待确认</option>
                  <option value="进行中">进行中</option>
                  <option value="已完成">已完成</option>
                </select>
              </div>
              <div class="form-item">
                <label class="form-label">备注</label>
                <input type="text" class="form-input" placeholder="请输入备注" v-model="formData.remarks" />
              </div>
            </div>
          </div>
        </div>
        <div class="modal-footer">
          <button class="btn btn-cancel" @click="closeAddModal">取消</button>
          <button class="btn btn-save" @click="handleSave" :disabled="saving">
            {{ saving ? '保存中...' : '保存' }}
          </button>
        </div>
      </div>
    </div>

    <div v-if="isViewModalOpen" class="modal-overlay" @click.self="closeViewModal">
      <div class="modal-container">
        <div class="modal-header">
          <h3 class="modal-title">查看工作计划</h3>
          <button class="modal-close" @click="closeViewModal">×</button>
        </div>
        <div class="modal-body">
          <div class="form-grid">
            <div class="form-column">
              <div class="form-item">
                <label class="form-label">工单编号</label>
                <div class="form-value">{{ viewData.plan_id || '-' }}</div>
              </div>
              <div class="form-item">
                <label class="form-label">计划类型</label>
                <div class="form-value">{{ viewData.plan_type || '-' }}</div>
              </div>
              <div class="form-item">
                <label class="form-label">项目编号</label>
                <div class="form-value">{{ viewData.project_id || '-' }}</div>
              </div>
              <div class="form-item">
                <label class="form-label">项目名称</label>
                <div class="form-value">{{ viewData.project_name || '-' }}</div>
              </div>
              <div class="form-item">
                <label class="form-label">客户单位</label>
                <div class="form-value">{{ viewData.client_name || '-' }}</div>
              </div>
            </div>
            <div class="form-column">
              <div class="form-item">
                <label class="form-label">计划开始日期</label>
                <div class="form-value">{{ formatDate(viewData.plan_start_date) || '-' }}</div>
              </div>
              <div class="form-item">
                <label class="form-label">计划结束日期</label>
                <div class="form-value">{{ formatDate(viewData.plan_end_date) || '-' }}</div>
              </div>
              <div class="form-item">
                <label class="form-label">运维人员</label>
                <div class="form-value">{{ viewData.maintenance_personnel || '-' }}</div>
              </div>
              <div class="form-item">
                <label class="form-label">状态</label>
                <div class="form-value">{{ viewData.status || '-' }}</div>
              </div>
              <div class="form-item">
                <label class="form-label">创建时间</label>
                <div class="form-value">{{ formatDateTime(viewData.created_at) || '-' }}</div>
              </div>
            </div>
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
  </div>
</template>

<script lang="ts">
import { defineComponent, ref, onMounted, reactive, watch, computed } from 'vue'
import { projectInfoService, type ProjectInfo } from '@/services/projectInfo'
import { personnelService, type Personnel } from '@/services/personnel'
import { maintenancePlanService, type MaintenancePlan } from '@/services/maintenancePlan'
import Toast from '@/components/Toast.vue'

interface PlanItem {
  id: number
  plan_id: string
  plan_type: string
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
    Toast
  },
  setup() {
    const planTypes = ['定期维保', '临时维修', '零星用工']
    const currentPage = ref(0)
    const pageSize = ref(10)
    const jumpPage = ref(1)
    const loading = ref(false)
    const saving = ref(false)
    const totalElements = ref(0)
    const totalPages = ref(0)
    const isAddModalOpen = ref(false)
    const isViewModalOpen = ref(false)
    const isEditMode = ref(false)
    const editingId = ref<number | null>(null)

    const toast = reactive({
      visible: false,
      message: '',
      type: 'success' as 'success' | 'error' | 'warning' | 'info'
    })

    const searchForm = ref({
      plan_type: '',
      project_name: '',
      client_name: ''
    })

    const projectList = ref<ProjectInfo[]>([])
    const personnelList = ref<Personnel[]>([])

    const formData = ref({
      plan_id: '',
      plan_type: '',
      project_name: '',
      project_id: '',
      client_name: '',
      plan_start_date: '',
      plan_end_date: '',
      maintenance_personnel: '',
      status: '待执行',
      remarks: ''
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
      maintenance_personnel: '',
      status: '',
      remarks: '',
      created_at: '',
      updated_at: ''
    })

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
      if (!dateStr) return '-'
      const date = new Date(dateStr)
      return `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}-${String(date.getDate()).padStart(2, '0')}`
    }

    const formatDateTime = (dateStr: string) => {
      if (!dateStr) return '-'
      const date = new Date(dateStr)
      return `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}-${String(date.getDate()).padStart(2, '0')} ${String(date.getHours()).padStart(2, '0')}:${String(date.getMinutes()).padStart(2, '0')}`
    }

    const getPlanTypeClass = (planType: string) => {
      switch (planType) {
        case '定期维保':
        case '定期巡检':
          return 'type-inspection'
        case '临时维修':
          return 'type-repair'
        case '零星用工':
          return 'type-spot'
        default:
          return ''
      }
    }

    const getStatusClass = (status: string) => {
      switch (status) {
        case '未进行':
        case '待执行':
          return 'status-pending'
        case '待确认':
          return 'status-waiting'
        case '进行中':
          return 'status-in-progress'
        case '已完成':
          return 'status-completed'
        case '已取消':
          return 'status-cancelled'
        default:
          return ''
      }
    }

    const loadData = async () => {
      loading.value = true
      try {
        const response = await maintenancePlanService.getList({
          page: currentPage.value,
          size: pageSize.value,
          project_name: searchForm.value.project_name || undefined,
          client_name: searchForm.value.client_name || undefined
        })
        
        if (response.code === 200) {
          planData.value = response.data.content.map((item: MaintenancePlan) => ({
            id: item.id,
            plan_id: item.plan_id,
            plan_type: item.plan_type || '定期维保',
            project_id: item.project_id,
            project_name: item.plan_name,
            plan_start_date: item.plan_start_date,
            plan_end_date: item.plan_end_date,
            client_name: item.responsible_department || '',
            maintenance_personnel: item.responsible_person || '',
            status: item.plan_status || '待执行',
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
        plan_type: '',
        project_name: '',
        client_name: ''
      }
      currentPage.value = 0
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
      const selectedProject = projectList.value.find(p => p.project_name === formData.value.project_name)
      if (selectedProject) {
        formData.value.project_id = selectedProject.project_id
        formData.value.client_name = selectedProject.client_name
        
        if (!isEditMode.value) {
          await generateWorkOrderId(selectedProject.project_id)
        }
      }
    }

    const generateWorkOrderId = async (projectId: string) => {
      try {
        const response = await maintenancePlanService.getByProjectId(projectId)
        if (response.code === 200 && response.data) {
          const count = response.data.length
          const nextNumber = count + 1
          const paddedNumber = String(nextNumber).padStart(3, '0')
          formData.value.plan_id = `${projectId}${paddedNumber}`
        } else {
          formData.value.plan_id = `${projectId}001`
        }
      } catch (error) {
        console.error('生成工单编号失败:', error)
        formData.value.plan_id = `${projectId}001`
      }
    }

    onMounted(() => {
      loadProjects()
      loadPersonnel()
      loadData()
    })

    watch([currentPage, pageSize], () => {
      loadData()
    })

    const handleAdd = () => {
      isEditMode.value = false
      editingId.value = null
      resetForm()
      isAddModalOpen.value = true
    }

    const handleEdit = (item: PlanItem) => {
      isEditMode.value = true
      editingId.value = item.id
      formData.value = {
        plan_id: item.plan_id,
        plan_type: item.plan_type,
        project_name: item.project_name,
        project_id: item.project_id,
        client_name: item.client_name || '',
        plan_start_date: item.plan_start_date ? item.plan_start_date.split('T')[0] : '',
        plan_end_date: item.plan_end_date ? item.plan_end_date.split('T')[0] : '',
        maintenance_personnel: item.maintenance_personnel || '',
        status: item.status,
        remarks: item.remarks || ''
      }
      isAddModalOpen.value = true
    }

    const closeAddModal = () => {
      isAddModalOpen.value = false
      resetForm()
    }

    const resetForm = () => {
      formData.value = {
        plan_id: '',
        plan_type: '',
        project_name: '',
        project_id: '',
        client_name: '',
        plan_start_date: '',
        plan_end_date: '',
        maintenance_personnel: '',
        status: '未进行',
        remarks: ''
      }
    }

    const handleSave = async () => {
      if (!formData.value.plan_type || !formData.value.project_id || 
          !formData.value.project_name || !formData.value.plan_start_date || !formData.value.plan_end_date) {
        showToast('请填写所有必填项', 'warning')
        return
      }

      if (!formData.value.plan_id) {
        showToast('请先选择项目以生成工单编号', 'warning')
        return
      }

      saving.value = true
      
      try {
        if (isEditMode.value && editingId.value) {
          const response = await maintenancePlanService.update(editingId.value, {
            plan_id: formData.value.plan_id,
            plan_type: formData.value.plan_type,
            project_id: formData.value.project_id,
            plan_name: formData.value.project_name,
            plan_start_date: formData.value.plan_start_date,
            plan_end_date: formData.value.plan_end_date,
            responsible_department: formData.value.client_name,
            responsible_person: formData.value.maintenance_personnel || '未指定',
            plan_status: formData.value.status,
            remarks: formData.value.remarks,
            equipment_id: 'EQ001',
            equipment_name: '默认设备',
            maintenance_content: '无',
            execution_status: '未开始'
          })
          
          if (response.code === 200) {
            showToast('更新成功', 'success')
            await loadData()
            closeAddModal()
          } else {
            showToast(response.message || '更新失败', 'error')
          }
        } else {
          const response = await maintenancePlanService.create({
            plan_id: formData.value.plan_id,
            plan_type: formData.value.plan_type,
            project_id: formData.value.project_id,
            plan_name: formData.value.project_name,
            plan_start_date: formData.value.plan_start_date,
            plan_end_date: formData.value.plan_end_date,
            responsible_department: formData.value.client_name,
            responsible_person: formData.value.maintenance_personnel || '未指定',
            plan_status: formData.value.status,
            remarks: formData.value.remarks,
            equipment_id: 'EQ001',
            equipment_name: '默认设备',
            maintenance_content: '无',
            execution_status: '未开始'
          })
          
          if (response.code === 200) {
            showToast('保存成功', 'success')
            await loadData()
            closeAddModal()
          } else {
            showToast(response.message || '保存失败', 'error')
          }
        }
      } catch (error: any) {
        console.error('保存失败:', error)
        showToast('保存失败，请检查网络连接', 'error')
      } finally {
        saving.value = false
      }
    }

    const handleView = (item: PlanItem) => {
      viewData.id = item.id
      viewData.plan_id = item.plan_id
      viewData.plan_type = item.plan_type
      viewData.project_id = item.project_id
      viewData.project_name = item.project_name
      viewData.plan_start_date = item.plan_start_date
      viewData.plan_end_date = item.plan_end_date
      viewData.client_name = item.client_name || ''
      viewData.maintenance_personnel = item.maintenance_personnel || ''
      viewData.status = item.status
      viewData.remarks = item.remarks || ''
      viewData.created_at = ''
      viewData.updated_at = ''
      isViewModalOpen.value = true
    }

    const closeViewModal = () => {
      isViewModalOpen.value = false
    }

    const handleDelete = async (item: PlanItem) => {
      if (confirm(`确定要删除计划 ${item.plan_id} 吗？`)) {
        try {
          await maintenancePlanService.delete(item.id)
          showToast('删除成功', 'success')
          loadData()
        } catch (error) {
          console.error('删除失败:', error)
          showToast('删除失败', 'error')
        }
      }
    }

    const handleConfirm = async (item: PlanItem) => {
      try {
        await maintenancePlanService.update(item.id, { 
          plan_id: item.plan_id,
          plan_type: item.plan_type,
          project_id: item.project_id,
          plan_name: item.project_name,
          plan_start_date: item.plan_start_date,
          plan_end_date: item.plan_end_date,
          responsible_department: item.client_name,
          responsible_person: item.maintenance_personnel || '未指定',
          plan_status: '进行中',
          equipment_id: 'EQ001',
          equipment_name: '默认设备',
          maintenance_content: '无',
          execution_status: '进行中'
        })
        showToast('确认成功', 'success')
        loadData()
      } catch (error) {
        console.error('确认失败:', error)
        showToast('确认失败', 'error')
      }
    }

    const handleJump = () => {
      const page = parseInt(String(jumpPage.value))
      if (page >= 1 && page <= totalPages.value) {
        currentPage.value = page - 1
      }
    }

    return {
      planTypes,
      currentPage,
      pageSize,
      jumpPage,
      loading,
      saving,
      totalElements,
      totalPages,
      displayedPages,
      isAddModalOpen,
      isViewModalOpen,
      isEditMode,
      toast,
      searchForm,
      formData,
      projectList,
      personnelList,
      planData,
      viewData,
      formatDate,
      formatDateTime,
      getPlanTypeClass,
      getStatusClass,
      handleSearch,
      handleReset,
      handleProjectChange,
      handleAdd,
      handleEdit,
      closeAddModal,
      handleSave,
      handleView,
      closeViewModal,
      handleDelete,
      handleConfirm,
      handleJump,
      showToast
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
</style>
