<template>
  <div class="project-info-management">
    <LoadingSpinner :visible="loading" text="加载中..." />
    <Toast :visible="toast.visible" :message="toast.message" :type="toast.type" />

    <div class="search-section">
      <div class="search-form">
        <div class="search-item">
          <label class="search-label">项目名称：</label>
          <input type="text" class="search-input" placeholder="请输入" v-model="searchForm.projectName" @input="handleSearch" />
        </div>
        <div class="search-item">
          <label class="search-label">客户名称：</label>
          <input type="text" class="search-input" placeholder="请输入" v-model="searchForm.clientName" @input="handleSearch" />
        </div>
      </div>
      <div class="search-actions">
        <button class="btn btn-add" @click="openModal">
          + 新增项目信息
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
            <th>项目开始日期</th>
            <th>项目结束日期</th>
            <th>维保周期</th>
            <th>客户单位</th>
            <th>地址</th>
            <th>操作</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="(item, index) in projectData" :key="item.id" :class="{ 'even-row': index % 2 === 0 }">
            <td>{{ startIndex + index + 1 }}</td>
            <td>{{ item.project_id }}</td>
            <td>{{ item.project_name }}</td>
            <td>{{ formatDate(item.completion_date) }}</td>
            <td>{{ formatDate(item.maintenance_end_date) }}</td>
            <td>{{ item.maintenance_period }}</td>
            <td>{{ item.client_name }}</td>
            <td>{{ item.address }}</td>
            <td class="action-cell">
              <a href="#" class="action-link action-view" @click.prevent="handleView(item)">查看</a>
              <a href="#" class="action-link action-edit" @click.prevent="handleEdit(item)">编辑</a>
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
      <div class="modal-container">
        <div class="modal-header">
          <h3 class="modal-title">添加项目信息</h3>
          <button class="modal-close" @click="closeModal">×</button>
        </div>
        <div class="modal-body">
          <div class="form-grid">
            <div class="form-column">
              <div class="form-item">
                <label class="form-label">
                  <span class="required">*</span> 项目名称
                </label>
                <input type="text" class="form-input" placeholder="请输入" v-model="formData.project_name" maxlength="200" />
              </div>
              <div class="form-item">
                <label class="form-label">
                  <span class="required">*</span> 项目编号
                </label>
                <input type="text" class="form-input" placeholder="请输入" v-model="formData.project_id" maxlength="50" />
              </div>
              <div class="form-item">
                <label class="form-label">
                  <span class="required">*</span> 项目开始日期
                </label>
                <input type="date" class="form-input" v-model="formData.completion_date" />
              </div>
              <div class="form-item">
                <label class="form-label">
                  <span class="required">*</span> 客户单位
                </label>
                <input type="text" class="form-input" placeholder="请输入" v-model="formData.client_name" maxlength="100" />
              </div>
              <div class="form-item">
                <label class="form-label">
                  <span class="required">*</span> 客户联系人
                </label>
                <input type="text" class="form-input" placeholder="请输入" v-model="formData.client_contact" maxlength="50" />
              </div>
              <div class="form-item">
                <label class="form-label">客户联系人职位</label>
                <input type="text" class="form-input" placeholder="请输入" v-model="formData.client_contact_position" maxlength="20" />
              </div>
            </div>
            <div class="form-column">
              <div class="form-item">
                <label class="form-label">
                  <span class="required">*</span> 维保周期
                </label>
                <select class="form-input" v-model="formData.maintenance_period">
                  <option value="">请选择</option>
                  <option value="每天">每天</option>
                  <option value="每周">每周</option>
                  <option value="每月">每月</option>
                  <option value="每季度">每季度</option>
                  <option value="每半年">每半年</option>
                </select>
              </div>
              <div class="form-item">
                <label class="form-label">
                  <span class="required">*</span> 项目目前简称
                </label>
                <input type="text" class="form-input" placeholder="请输入" v-model="formData.project_abbr" maxlength="10" />
              </div>
              <div class="form-item">
                <label class="form-label">
                  <span class="required">*</span> 项目结束日期
                </label>
                <input type="date" class="form-input" v-model="formData.maintenance_end_date" />
                <span class="form-hint">截止日期指的是当日 23:59:59</span>
              </div>
              <div class="form-item">
                <label class="form-label">
                  <span class="required">*</span> 客户地址
                </label>
                <input type="text" class="form-input" placeholder="请输入" v-model="formData.address" maxlength="200" />
              </div>
              <div class="form-item">
                <label class="form-label">
                  <span class="required">*</span> 客户联系方式
                </label>
                <input type="text" class="form-input" placeholder="请输入" v-model="formData.client_contact_info" maxlength="50" />
              </div>
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
          <h3 class="modal-title">查看项目信息</h3>
          <button class="modal-close" @click="closeViewModal">×</button>
        </div>
        <div class="modal-body">
          <div class="form-grid">
            <div class="form-column">
              <div class="form-item">
                <label class="form-label">项目名称</label>
                <div class="form-value">{{ viewData.project_name || '-' }}</div>
              </div>
              <div class="form-item">
                <label class="form-label">项目编号</label>
                <div class="form-value">{{ viewData.project_id || '-' }}</div>
              </div>
              <div class="form-item">
                <label class="form-label">项目开始日期</label>
                <div class="form-value">{{ formatDate(viewData.completion_date) || '-' }}</div>
              </div>
              <div class="form-item">
                <label class="form-label">客户单位</label>
                <div class="form-value">{{ viewData.client_name || '-' }}</div>
              </div>
              <div class="form-item">
                <label class="form-label">客户联系人</label>
                <div class="form-value">{{ viewData.client_contact || '-' }}</div>
              </div>
              <div class="form-item">
                <label class="form-label">客户联系人职位</label>
                <div class="form-value">{{ viewData.client_contact_position || '-' }}</div>
              </div>
            </div>
            <div class="form-column">
              <div class="form-item">
                <label class="form-label">维保周期</label>
                <div class="form-value">{{ viewData.maintenance_period || '-' }}</div>
              </div>
              <div class="form-item">
                <label class="form-label">项目目前简称</label>
                <div class="form-value">{{ viewData.project_abbr || '-' }}</div>
              </div>
              <div class="form-item">
                <label class="form-label">项目结束日期</label>
                <div class="form-value">{{ formatDate(viewData.maintenance_end_date) || '-' }}</div>
              </div>
              <div class="form-item">
                <label class="form-label">客户地址</label>
                <div class="form-value">{{ viewData.address || '-' }}</div>
              </div>
              <div class="form-item">
                <label class="form-label">客户联系方式</label>
                <div class="form-value">{{ viewData.client_contact_info || '-' }}</div>
              </div>
            </div>
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
          <h3 class="modal-title">编辑项目信息</h3>
          <button class="modal-close" @click="closeEditModal">×</button>
        </div>
        <div class="modal-body">
          <div class="form-grid">
            <div class="form-column">
              <div class="form-item">
                <label class="form-label">
                  <span class="required">*</span> 项目名称
                </label>
                <input type="text" class="form-input" placeholder="请输入" v-model="editData.project_name" maxlength="200" />
              </div>
              <div class="form-item">
                <label class="form-label">
                  <span class="required">*</span> 项目编号
                </label>
                <input type="text" class="form-input" placeholder="请输入" v-model="editData.project_id" maxlength="50" />
              </div>
              <div class="form-item">
                <label class="form-label">
                  <span class="required">*</span> 项目开始日期
                </label>
                <input type="date" class="form-input" v-model="editData.completion_date" />
              </div>
              <div class="form-item">
                <label class="form-label">
                  <span class="required">*</span> 客户单位
                </label>
                <input type="text" class="form-input" placeholder="请输入" v-model="editData.client_name" maxlength="100" />
              </div>
              <div class="form-item">
                <label class="form-label">
                  <span class="required">*</span> 客户联系人
                </label>
                <input type="text" class="form-input" placeholder="请输入" v-model="editData.client_contact" maxlength="50" />
              </div>
              <div class="form-item">
                <label class="form-label">客户联系人职位</label>
                <input type="text" class="form-input" placeholder="请输入" v-model="editData.client_contact_position" maxlength="20" />
              </div>
            </div>
            <div class="form-column">
              <div class="form-item">
                <label class="form-label">
                  <span class="required">*</span> 维保周期
                </label>
                <select class="form-input" v-model="editData.maintenance_period">
                  <option value="">请选择</option>
                  <option value="每天">每天</option>
                  <option value="每周">每周</option>
                  <option value="每月">每月</option>
                  <option value="每季度">每季度</option>
                  <option value="每半年">每半年</option>
                </select>
              </div>
              <div class="form-item">
                <label class="form-label">
                  <span class="required">*</span> 项目结束日期
                </label>
                <input type="date" class="form-input" v-model="editData.maintenance_end_date" />
                <span class="form-hint">截止日期指的是当日 23:59:59</span>
              </div>
              <div class="form-item">
                <label class="form-label">
                  <span class="required">*</span> 客户地址
                </label>
                <input type="text" class="form-input" placeholder="请输入" v-model="editData.address" maxlength="200" />
              </div>
              <div class="form-item">
                <label class="form-label">
                  <span class="required">*</span> 客户联系方式
                </label>
                <input type="text" class="form-input" placeholder="请输入" v-model="editData.client_contact_info" maxlength="50" />
              </div>
            </div>
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
import { defineComponent, reactive, ref, computed, watch, onMounted, onUnmounted } from 'vue'
import { projectInfoService, type ProjectInfo, type ProjectInfoCreate, type ProjectInfoUpdate } from '../services/projectInfo'
import LoadingSpinner from '../components/LoadingSpinner.vue'
import Toast from '../components/Toast.vue'

export default defineComponent({
  name: 'ProjectInfoManagement',
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
    
    const projectData = ref<ProjectInfo[]>([])
    const totalElements = ref(0)
    const totalPages = ref(0)

    const toast = reactive({
      visible: false,
      message: '',
      type: 'success' as 'success' | 'error' | 'warning' | 'info'
    })

    const viewData = reactive({
      id: 0,
      project_id: '',
      project_name: '',
      completion_date: '',
      maintenance_end_date: '',
      maintenance_period: '',
      client_name: '',
      address: '',
      project_abbr: '',
      client_contact: '',
      client_contact_position: '',
      client_contact_info: ''
    })

    const editData = reactive({
      id: 0,
      project_id: '',
      project_name: '',
      completion_date: '',
      maintenance_end_date: '',
      maintenance_period: '',
      client_name: '',
      address: '',
      project_abbr: '',
      client_contact: '',
      client_contact_position: '',
      client_contact_info: ''
    })

    const formData = reactive({
      project_name: '',
      project_id: '',
      completion_date: '',
      client_name: '',
      client_contact: '',
      client_contact_position: '',
      maintenance_period: '',
      project_abbr: '',
      maintenance_end_date: '',
      address: '',
      client_contact_info: ''
    })

    let abortController: AbortController | null = null

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

    const loadData = async () => {
      if (abortController) {
        abortController.abort()
      }
      abortController = new AbortController()

      loading.value = true
      try {
        const response = await projectInfoService.getList({
          page: currentPage.value,
          size: pageSize.value,
          project_name: searchForm.projectName || undefined,
          client_name: searchForm.clientName || undefined
        })
        
        if (response.code === 200) {
          projectData.value = response.data.content
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
      if (!formData.project_name?.trim()) {
        showToast('请填写项目名称', 'warning')
        return false
      }
      if (!formData.project_id?.trim()) {
        showToast('请填写项目编号', 'warning')
        return false
      }
      if (!formData.completion_date) {
        showToast('请填写项目开始日期', 'warning')
        return false
      }
      if (!formData.maintenance_end_date) {
        showToast('请填写项目结束日期', 'warning')
        return false
      }
      if (!formData.maintenance_period?.trim()) {
        showToast('请填写维保周期', 'warning')
        return false
      }
      if (!formData.client_name?.trim()) {
        showToast('请填写客户单位', 'warning')
        return false
      }
      if (!formData.address?.trim()) {
        showToast('请填写客户地址', 'warning')
        return false
      }
      return true
    }

    const openModal = () => {
      resetForm()
      isModalOpen.value = true
    }

    const closeModal = () => {
      isModalOpen.value = false
    }

    const resetForm = () => {
      formData.project_name = ''
      formData.project_id = ''
      formData.completion_date = ''
      formData.client_name = ''
      formData.client_contact = ''
      formData.client_contact_position = ''
      formData.maintenance_period = ''
      formData.project_abbr = ''
      formData.maintenance_end_date = ''
      formData.address = ''
      formData.client_contact_info = ''
    }

    const handleSave = async () => {
      if (!checkFormValid()) {
        return
      }

      saving.value = true
      try {
        const createData: ProjectInfoCreate = {
          project_id: formData.project_id,
          project_name: formData.project_name,
          completion_date: formatDateForAPI(formData.completion_date),
          maintenance_end_date: formatDateForAPI(formData.maintenance_end_date),
          maintenance_period: formData.maintenance_period,
          client_name: formData.client_name,
          address: formData.address,
          project_abbr: formData.project_abbr || undefined,
          client_contact: formData.client_contact || undefined,
          client_contact_position: formData.client_contact_position || undefined,
          client_contact_info: formData.client_contact_info || undefined
        }

        const response = await projectInfoService.create(createData)
        
        if (response.code === 200) {
          showToast('创建成功', 'success')
          closeModal()
          resetForm()
          
          currentPage.value = 0
          await loadData()
        } else {
          showToast(response.message || '创建失败', 'error')
        }
      } catch (error: any) {
        showToast(error.message || '创建失败，请检查网络连接', 'error')
      } finally {
        saving.value = false
      }
    }

    const handleView = async (item: ProjectInfo) => {
      viewData.id = item.id
      viewData.project_id = item.project_id
      viewData.project_name = item.project_name
      viewData.completion_date = item.completion_date
      viewData.maintenance_end_date = item.maintenance_end_date
      viewData.maintenance_period = item.maintenance_period
      viewData.client_name = item.client_name
      viewData.address = item.address
      viewData.project_abbr = item.project_abbr || ''
      viewData.client_contact = item.client_contact || ''
      viewData.client_contact_position = item.client_contact_position || ''
      viewData.client_contact_info = item.client_contact_info || ''
      isViewModalOpen.value = true
    }

    const handleEdit = (item: ProjectInfo) => {
      editingId.value = item.id
      editData.id = item.id
      editData.project_id = item.project_id
      editData.project_name = item.project_name
      editData.completion_date = item.completion_date
      editData.maintenance_end_date = item.maintenance_end_date
      editData.maintenance_period = item.maintenance_period
      editData.client_name = item.client_name
      editData.address = item.address
      editData.project_abbr = item.project_abbr || ''
      editData.client_contact = item.client_contact || ''
      editData.client_contact_position = item.client_contact_position || ''
      editData.client_contact_info = item.client_contact_info || ''
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
      if (!editData.project_name?.trim()) {
        showToast('请填写项目名称', 'warning')
        return false
      }
      if (!editData.project_id?.trim()) {
        showToast('请填写项目编号', 'warning')
        return false
      }
      if (!editData.completion_date) {
        showToast('请填写项目开始日期', 'warning')
        return false
      }
      if (!editData.maintenance_end_date) {
        showToast('请填写项目结束日期', 'warning')
        return false
      }
      if (!editData.maintenance_period?.trim()) {
        showToast('请填写维保周期', 'warning')
        return false
      }
      if (!editData.client_name?.trim()) {
        showToast('请填写客户单位', 'warning')
        return false
      }
      if (!editData.address?.trim()) {
        showToast('请填写客户地址', 'warning')
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
        const updateData: ProjectInfoUpdate = {
          project_id: editData.project_id,
          project_name: editData.project_name,
          completion_date: formatDateForAPI(editData.completion_date),
          maintenance_end_date: formatDateForAPI(editData.maintenance_end_date),
          maintenance_period: editData.maintenance_period,
          client_name: editData.client_name,
          address: editData.address,
          project_abbr: editData.project_abbr || undefined,
          client_contact: editData.client_contact || undefined,
          client_contact_position: editData.client_contact_position || undefined,
          client_contact_info: editData.client_contact_info || undefined
        }

        const response = await projectInfoService.update(editingId.value, updateData)
        
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

    const handleDelete = async (item: ProjectInfo) => {
      if (!confirm('确定要删除该项目吗？')) {
        return
      }

      loading.value = true
      try {
        const response = await projectInfoService.delete(item.id)
        
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

    const handleJump = () => {
      const page = parseInt(jumpPage.value.toString())
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
    })

    onUnmounted(() => {
      if (abortController) {
        abortController.abort()
      }
    })

    return {
      searchForm,
      projectData,
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
      openModal,
      closeModal,
      handleSearch,
      handleSave,
      handleUpdate,
      handleView,
      handleEdit,
      handleDelete,
      handleJump,
      handlePageSizeChange,
      closeViewModal,
      closeEditModal,
      formatDate
    }
  }
})
</script>

<style scoped>
.project-info-management {
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
  min-height: 90px;
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

.form-hint {
  font-size: 12px;
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
</style>