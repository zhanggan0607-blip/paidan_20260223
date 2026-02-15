<template>
  <div class="personnel-management">
    <LoadingSpinner :visible="loading" text="加载中..." />
    <Toast :visible="toast.visible" :message="toast.message" :type="toast.type" />

    <div class="search-section">
      <div class="search-form">
        <div class="search-item">
          <label class="search-label">姓名：</label>
          <SearchInput
            v-model="searchForm.name"
            field-key="PersonnelManagement_name"
            placeholder="请输入"
            @input="handleSearch"
          />
        </div>
        <div class="search-item">
          <label class="search-label">部门：</label>
          <SearchInput
            v-model="searchForm.department"
            field-key="PersonnelManagement_department"
            placeholder="请输入"
            @input="handleSearch"
          />
        </div>
      </div>
      <div class="search-actions">
        <button class="btn btn-add" @click="openModal">
          + 新增人员
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
            <th>姓名</th>
            <th>性别</th>
            <th>部门</th>
            <th>角色</th>
            <th>联系电话</th>
            <th>操作</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="(item, index) in personnelData" :key="item.id" :class="{ 'even-row': index % 2 === 0 }">
            <td>{{ startIndex + index + 1 }}</td>
            <td>{{ item.name }}</td>
            <td>{{ item.gender }}</td>
            <td>{{ item.department || '-' }}</td>
            <td :class="getRoleClass(item.role)">{{ item.role }}</td>
            <td>{{ item.phone || '-' }}</td>
            <td class="action-cell">
              <a href="#" class="action-link action-view" @click.prevent="handleView(item)">查看</a>
              <a href="#" class="action-link action-edit" @click.prevent="handleEdit(item)" v-if="canEdit(item)">编辑</a>
              <a href="#" class="action-link action-delete" @click.prevent="handleDelete(item)" v-if="canDelete(item)">删除</a>
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
          <h3 class="modal-title">{{ isEditMode ? '编辑人员' : '新增人员' }}</h3>
          <button class="modal-close" @click="closeModal">×</button>
        </div>
        <div class="modal-body">
          <div class="form-grid">
            <div class="form-column">
              <div class="form-item">
                <label class="form-label">
                  <span class="required">*</span> 姓名
                </label>
                <input type="text" class="form-input" placeholder="请输入" v-model="formData.name" maxlength="50" />
              </div>
              <div class="form-item">
                <label class="form-label">
                  <span class="required">*</span> 性别
                </label>
                <select class="form-input" v-model="formData.gender">
                  <option value="">请选择</option>
                  <option value="男">男</option>
                  <option value="女">女</option>
                  <option value="其他">其他</option>
                </select>
              </div>
              <div class="form-item">
                <label class="form-label">联系电话</label>
                <input type="text" class="form-input" placeholder="请输入手机号码" v-model="formData.phone" maxlength="11" />
              </div>
            </div>
            <div class="form-column">
              <div class="form-item">
                <label class="form-label">所属部门</label>
                <input type="text" class="form-input" placeholder="请输入" v-model="formData.department" maxlength="100" />
              </div>
              <div class="form-item">
                <label class="form-label">
                  <span class="required">*</span> 角色
                </label>
                <select class="form-input" v-model="formData.role" :disabled="!canEditRole()">
                  <option value="">请选择</option>
                  <option value="管理员">管理员</option>
                  <option value="部门经理">部门经理</option>
                  <option value="材料员">材料员</option>
                  <option value="员工">员工</option>
                </select>
              </div>
              <div class="form-item">
                <label class="form-label">地址</label>
                <input type="text" class="form-input" placeholder="请输入" v-model="formData.address" maxlength="200" />
              </div>
            </div>
          </div>
          <div class="form-item-full">
            <label class="form-label">备注</label>
            <textarea class="form-textarea" placeholder="请输入" v-model="formData.remarks" rows="3" maxlength="500"></textarea>
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
          <h3 class="modal-title">查看人员</h3>
          <button class="modal-close" @click="closeViewModal">×</button>
        </div>
        <div class="modal-body">
          <div class="form-grid">
            <div class="form-column">
              <div class="form-item">
                <label class="form-label">姓名</label>
                <div class="form-value">{{ viewData.name || '-' }}</div>
              </div>
              <div class="form-item">
                <label class="form-label">性别</label>
                <div class="form-value">{{ viewData.gender || '-' }}</div>
              </div>
              <div class="form-item">
                <label class="form-label">联系电话</label>
                <div class="form-value">{{ viewData.phone || '-' }}</div>
              </div>
            </div>
            <div class="form-column">
              <div class="form-item">
                <label class="form-label">所属部门</label>
                <div class="form-value">{{ viewData.department || '-' }}</div>
              </div>
              <div class="form-item">
                <label class="form-label">角色</label>
                <div class="form-value" :class="getRoleClass(viewData.role)">{{ viewData.role || '-' }}</div>
              </div>
              <div class="form-item">
                <label class="form-label">地址</label>
                <div class="form-value">{{ viewData.address || '-' }}</div>
              </div>
              <div class="form-item">
                <label class="form-label">备注</label>
                <div class="form-value form-value-textarea">{{ viewData.remarks || '-' }}</div>
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
import { defineComponent, reactive, ref, computed, watch, onMounted, onUnmounted, watchEffect } from 'vue'
import { ElMessageBox } from 'element-plus'
import { personnelService, type Personnel, type PersonnelCreate, type PersonnelUpdate } from '../services/personnel'
import LoadingSpinner from '../components/LoadingSpinner.vue'
import Toast from '../components/Toast.vue'
import SearchInput from '../components/SearchInput.vue'
import { useInputMemory } from '../utils/inputMemory'
import { USER_ROLES, GENDER_LIST, formatDate } from '../config/constants'

export default defineComponent({
  name: 'PersonnelManagement',
  components: {
    LoadingSpinner,
    Toast,
    SearchInput
  },
  setup() {
    const searchForm = reactive({
      name: '',
      department: ''
    })

    const currentPage = ref(0)
    const pageSize = ref(10)
    const jumpPage = ref(1)
    const loading = ref(false)
    const saving = ref(false)
    const isModalOpen = ref(false)
    const isViewModalOpen = ref(false)
    const isEditMode = ref(false)
    const editingId = ref<number | null>(null)
    
    const personnelData = ref<Personnel[]>([])
    const totalElements = ref(0)
    const totalPages = ref(0)

    const toast = reactive({
      visible: false,
      message: '',
      type: 'success' as 'success' | 'error' | 'warning' | 'info'
    })

    const formData = reactive({
      name: '',
      gender: '',
      phone: '',
      department: '',
      role: '员工',
      address: '',
      remarks: ''
    })

    let abortController: AbortController | null = null

    const inputMemory = useInputMemory({
      pageName: 'PersonnelManagement',
      fields: ['name', 'gender', 'phone', 'department', 'role', 'address', 'remarks'],
      onRestore: (data) => {
        if (data.name) formData.name = data.name
        if (data.gender) formData.gender = data.gender
        if (data.phone) formData.phone = data.phone
        if (data.department) formData.department = data.department
        if (data.role) formData.role = data.role
        if (data.address) formData.address = data.address
        if (data.remarks) formData.remarks = data.remarks
      }
    })

    const currentUserRole = ref('管理员')
    const currentUserDepartment = ref('')

    const viewData = reactive({
      id: 0,
      name: '',
      gender: '',
      phone: '',
      department: '',
      role: '',
      address: '',
      remarks: ''
    })

    const startIndex = computed(() => currentPage.value * pageSize.value)

    const showToast = (message: string, type: 'success' | 'error' | 'warning' | 'info' = 'success') => {
      toast.message = message
      toast.type = type
      toast.visible = true
    }

    const getRoleClass = (role: string) => {
      switch (role) {
        case '管理员':
          return 'role-admin'
        case '部门经理':
          return 'role-manager'
        case '材料员':
          return 'role-material'
        case '员工':
          return 'role-employee'
        default:
          return ''
      }
    }

    const canEdit = (item: Personnel) => {
      if (currentUserRole.value === '管理员') {
        return true
      }
      if (currentUserRole.value === '部门经理' && item.department === currentUserDepartment.value) {
        return true
      }
      return false
    }

    const canDelete = (item: Personnel) => {
      if (currentUserRole.value === '管理员') {
        return true
      }
      return false
    }

    const canEditRole = () => {
      return currentUserRole.value === '管理员'
    }

    const loadData = async () => {
      if (abortController) {
        abortController.abort()
      }
      abortController = new AbortController()

      loading.value = true
      try {
        const response = await personnelService.getList({
          page: currentPage.value,
          size: pageSize.value,
          name: searchForm.name || undefined,
          department: searchForm.department || undefined,
          current_user_role: currentUserRole.value,
          current_user_department: currentUserDepartment.value || undefined
        })
        
        if (response.code === 200) {
          personnelData.value = response.data.content
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
      if (!formData.name?.trim()) {
        showToast('请填写姓名', 'warning')
        return false
      }
      if (!formData.gender?.trim()) {
        showToast('请选择性别', 'warning')
        return false
      }
      if (!formData.role?.trim()) {
        showToast('请选择角色', 'warning')
        return false
      }
      if (formData.phone && formData.phone.trim()) {
        const phonePattern = /^1[3-9]\d{9}$/
        if (!phonePattern.test(formData.phone.trim())) {
          showToast('请输入有效的手机号码', 'warning')
          return false
        }
      }
      return true
    }

    const openModal = () => {
      resetForm()
      isEditMode.value = false
      inputMemory.loadMemory()
      isModalOpen.value = true
    }

    const closeModal = () => {
      if (!isEditMode.value) {
        inputMemory.saveMemory(formData)
      }
      isModalOpen.value = false
    }

    const resetForm = () => {
      formData.name = ''
      formData.gender = ''
      formData.phone = ''
      formData.department = ''
      formData.role = '员工'
      formData.address = ''
      formData.remarks = ''
    }

    const handleSave = async () => {
      if (!checkFormValid()) {
        return
      }

      saving.value = true
      try {
        if (isEditMode.value && editingId.value !== null) {
          const updateData: PersonnelUpdate = {
            name: formData.name,
            gender: formData.gender,
            phone: formData.phone || undefined,
            department: formData.department || undefined,
            role: formData.role,
            address: formData.address || undefined,
            remarks: formData.remarks || undefined
          }

          const response = await personnelService.update(editingId.value, updateData)

          if (response.code === 200) {
            showToast('更新成功', 'success')
            closeModal()
            await loadData()
          } else {
            showToast(response.message || '更新失败', 'error')
          }
        } else {
          const createData: PersonnelCreate = {
            name: formData.name,
            gender: formData.gender,
            phone: formData.phone || undefined,
            department: formData.department || undefined,
            role: formData.role,
            address: formData.address || undefined,
            remarks: formData.remarks || undefined
          }

          const response = await personnelService.create(createData)

          if (response.code === 200) {
            showToast('创建成功', 'success')
            closeModal()
            await loadData()
          } else {
            showToast(response.message || '创建失败', 'error')
          }
        }
      } catch (error: any) {
        console.error('保存失败:', error)
        showToast(error.message || '保存失败，请检查网络连接', 'error')
      } finally {
        saving.value = false
      }
    }

    const handleView = (item: Personnel) => {
      viewData.id = item.id
      viewData.name = item.name
      viewData.gender = item.gender
      viewData.phone = item.phone || ''
      viewData.department = item.department || ''
      viewData.role = item.role
      viewData.address = item.address || ''
      viewData.remarks = item.remarks || ''
      isViewModalOpen.value = true
    }

    const handleEdit = (item: Personnel) => {
      editingId.value = item.id
      formData.name = item.name
      formData.gender = item.gender
      formData.phone = item.phone || ''
      formData.department = item.department || ''
      formData.role = item.role
      formData.address = item.address || ''
      formData.remarks = item.remarks || ''
      isEditMode.value = true
      isModalOpen.value = true
    }

    const closeViewModal = () => {
      isViewModalOpen.value = false
    }

    const handleDelete = async (item: Personnel) => {
      try {
        await ElMessageBox.confirm('确定要删除该人员吗？', '提示', {
          confirmButtonText: '确定',
          cancelButtonText: '取消',
          type: 'warning'
        })
        
        loading.value = true
        const response = await personnelService.delete(item.id)
        
        if (response.code === 200) {
          showToast('删除成功', 'success')
          await loadData()
        } else {
          showToast(response.message || '删除失败', 'error')
        }
      } catch (error: any) {
        if (error !== 'cancel') {
          console.error('删除失败:', error)
          showToast(error.message || '删除失败，请检查网络连接', 'error')
        }
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
    })

    onUnmounted(() => {
      if (abortController) {
        abortController.abort()
      }
    })

    return {
      searchForm,
      personnelData,
      currentPage,
      pageSize,
      totalPages,
      jumpPage,
      totalElements,
      startIndex,
      isModalOpen,
      isViewModalOpen,
      isEditMode,
      loading,
      saving,
      viewData,
      formData,
      toast,
      currentUserRole,
      currentUserDepartment,
      openModal,
      closeModal,
      handleSave,
      handleView,
      handleEdit,
      handleDelete,
      handleJump,
      handlePageSizeChange,
      closeViewModal,
      handleSearch,
      getRoleClass,
      canEdit,
      canDelete,
      canEditRole
    }
  }
})
</script>

<style scoped>
.personnel-management {
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

.role-admin {
  color: #D32F2F;
  font-weight: 600;
}

.role-manager {
  color: #1976D2;
  font-weight: 600;
}

.role-employee {
  color: #666;
  font-weight: 500;
}

.role-material {
  color: #FF9800;
  font-weight: 600;
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
</style>
