<template>
  <div class="personnel-management">
    <LoadingSpinner :visible="loading" text="加载中..." />
    <Toast :visible="toast.visible" :message="toast.message" :type="toast.type" />

    <div class="search-section">
      <div class="search-form">
        <div class="search-row">
          <div class="search-item">
            <label class="search-label">姓名：</label>
            <SearchInput
              v-model="searchForm.name"
              field-key="PersonnelManagement_name"
              placeholder="请输入姓名"
              @input="handleSearch"
            />
          </div>
          <div class="search-item">
            <label class="search-label">部门：</label>
            <SearchInput
              v-model="searchForm.department"
              field-key="PersonnelManagement_department"
              placeholder="请输入部门"
              @input="handleSearch"
            />
          </div>
        </div>
      </div>
      <div class="search-actions">
        <button class="btn btn-add" @click="handleOpenModal">+ 新增人员</button>
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
            <th>最后登录时间</th>
            <th>状态</th>
            <th>操作</th>
          </tr>
        </thead>
        <tbody>
          <tr
            v-for="(item, index) in personnelData"
            :key="item.id"
            :class="{ 'even-row': index % 2 === 0 }"
          >
            <td>{{ startIndex + index + 1 }}</td>
            <td>{{ item.name }}</td>
            <td>{{ item.gender }}</td>
            <td>{{ item.department || '-' }}</td>
            <td :class="getRoleClass(item.role)">{{ item.role }}</td>
            <td>{{ item.phone || '-' }}</td>
            <td>{{ item.last_login_at ? formatDate(item.last_login_at) : '-' }}</td>
            <td class="status-cell">
              <span
                class="status-badge"
                :class="{
                  'status-online': item.is_online,
                  'status-offline': !item.is_online,
                }"
              >
                <span class="status-dot"></span>
                <span class="status-text">{{ item.is_online ? '在线' : '离线' }}</span>
                <span v-if="item.is_online && item.device_type" class="device-type">
                  ({{ item.device_type === 'pc' ? '电脑端' : '手机端' }})
                </span>
              </span>
            </td>
            <td class="action-cell">
              <a href="#" class="action-link action-view" @click.prevent="handleView(item)">查看</a>
              <a
                v-if="canEdit(item)"
                href="#"
                class="action-link action-edit"
                @click.prevent="handleEdit(item)"
                >编辑</a
              >
              <a
                v-if="canDelete(item)"
                href="#"
                class="action-link action-delete"
                @click.prevent="handleDelete(item)"
                >删除</a
              >
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <div class="pagination-section">
      <div class="pagination-info">共 {{ totalElements }} 条记录</div>
      <div class="pagination-controls">
        <button class="page-btn page-nav" :disabled="currentPage === 0" @click="prevPage">
          &lt;
        </button>
        <button
          v-for="page in displayedPages"
          :key="page"
          class="page-btn page-num"
          :class="{ active: page === currentPage + 1 }"
          @click="goToPage(page - 1)"
        >
          {{ page }}
        </button>
        <button
          class="page-btn page-nav"
          :disabled="currentPage >= totalPages - 1"
          @click="nextPage"
        >
          &gt;
        </button>
        <select v-model.number="pageSize" class="page-select" @change="handlePageSizeChange">
          <option :value="10">10 条 / 页</option>
          <option :value="20">20 条 / 页</option>
          <option :value="50">50 条 / 页</option>
        </select>
        <div class="page-jump">
          <span>跳至</span>
          <input
            v-model.number="jumpPage"
            type="number"
            class="page-input"
            min="1"
            :max="totalPages"
          />
          <span>页</span>
          <button class="page-btn page-go" @click="handleJump">Go</button>
        </div>
      </div>
    </div>

    <div v-if="isModalOpen" class="modal-overlay" @click.self="handleCloseModal">
      <div class="modal-container">
        <div class="modal-header">
          <h3 class="modal-title">{{ isEditMode ? '编辑人员' : '新增人员' }}</h3>
          <button class="modal-close" @click="handleCloseModal">×</button>
        </div>
        <div class="modal-body">
          <div class="form-grid">
            <div class="form-column">
              <div class="form-item">
                <label class="form-label"> <span class="required">*</span> 姓名 </label>
                <input
                  v-model="formData.name"
                  type="text"
                  class="form-input"
                  placeholder="请输入"
                  maxlength="50"
                />
              </div>
              <div class="form-item">
                <label class="form-label"> <span class="required">*</span> 性别 </label>
                <select v-model="formData.gender" class="form-input">
                  <option value="">请选择</option>
                  <option value="男">男</option>
                  <option value="女">女</option>
                  <option value="其他">其他</option>
                </select>
              </div>
              <div class="form-item">
                <label class="form-label">联系电话</label>
                <input
                  v-model="formData.phone"
                  type="text"
                  class="form-input"
                  placeholder="请输入手机号码"
                  maxlength="11"
                />
              </div>
            </div>
            <div class="form-column">
              <div class="form-item">
                <label class="form-label">所属部门</label>
                <input
                  v-model="formData.department"
                  type="text"
                  class="form-input"
                  placeholder="请输入"
                  maxlength="100"
                />
              </div>
              <div class="form-item">
                <label class="form-label"> <span class="required">*</span> 角色 </label>
                <select v-model="formData.role" class="form-input" :disabled="!canEditRole()">
                  <option value="">请选择</option>
                  <option value="管理员">管理员</option>
                  <option value="部门经理">部门经理</option>
                  <option value="材料员">材料员</option>
                  <option value="运维人员">运维人员</option>
                </select>
              </div>
              <div class="form-item">
                <label class="form-label">地址</label>
                <input
                  v-model="formData.address"
                  type="text"
                  class="form-input"
                  placeholder="请输入"
                  maxlength="200"
                />
              </div>
            </div>
          </div>
          <div class="form-item-full">
            <label class="form-label">备注</label>
            <textarea
              v-model="formData.remarks"
              class="form-textarea"
              placeholder="请输入"
              rows="3"
              maxlength="500"
            ></textarea>
          </div>
        </div>
        <div class="modal-footer">
          <button class="btn btn-cancel" @click="handleCloseModal">取消</button>
          <button class="btn btn-save" :disabled="saving" @click="handleSave">
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
              <div class="form-item">
                <label class="form-label">最后登录时间</label>
                <div class="form-value">
                  {{ viewData.last_login_at ? formatDate(viewData.last_login_at) : '-' }}
                </div>
              </div>
            </div>
            <div class="form-column">
              <div class="form-item">
                <label class="form-label">所属部门</label>
                <div class="form-value">{{ viewData.department || '-' }}</div>
              </div>
              <div class="form-item">
                <label class="form-label">角色</label>
                <div class="form-value" :class="getRoleClass(viewData.role)">
                  {{ viewData.role || '-' }}
                </div>
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
        </div>
        <div class="modal-footer">
          <button class="btn btn-cancel" @click="closeViewModal">关闭</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script lang="ts">
import { defineComponent, reactive, ref, computed, watch, onMounted, onUnmounted } from 'vue'
import { ElMessageBox } from 'element-plus'
import {
  personnelService,
  type Personnel,
  type PersonnelCreate,
  type PersonnelUpdate,
} from '../services/personnel'
import { userStore } from '../stores/userStore'
import LoadingSpinner from '../components/LoadingSpinner.vue'
import Toast from '../components/Toast.vue'
import SearchInput from '../components/SearchInput.vue'
import { useInputMemory } from '../utils/inputMemory'
import { useToast, usePageState, useAbortController } from '../composables'

export default defineComponent({
  name: 'PersonnelManagement',
  components: {
    LoadingSpinner,
    Toast,
    SearchInput,
  },
  setup() {
    const searchForm = reactive({
      name: '',
      department: '',
    })

    const { toast, success, error, warning } = useToast()
    const {
      loading,
      saving,
      isModalOpen,
      isViewModalOpen,
      isEditMode,
      editingId,
      openModal,
      closeModal,
      openViewModal,
      closeViewModal,
    } = usePageState()
    const { createController, abort, isAbortError } = useAbortController()

    const currentPage = ref(0)
    const pageSize = ref(10)
    const jumpPage = ref(1)
    const personnelData = ref<Personnel[]>([])
    const totalElements = ref(0)
    const totalPages = ref(0)

    const formData = reactive({
      name: '',
      gender: '',
      phone: '',
      department: '',
      role: '运维人员',
      address: '',
      remarks: '',
    })

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
      },
    })

    const currentUserRole = ref('运维人员')
    const currentUserDepartment = ref('')

    const viewData = reactive({
      id: 0,
      name: '',
      gender: '',
      phone: '',
      department: '',
      role: '',
      address: '',
      remarks: '',
      last_login_at: '',
    })

    const startIndex = computed(() => currentPage.value * pageSize.value)
    const displayedPages = computed(() => {
      const pages: number[] = []
      const maxVisible = 5
      let start = Math.max(0, currentPage.value - Math.floor(maxVisible / 2))
      const end = Math.min(totalPages.value, start + maxVisible)
      if (end - start < maxVisible) {
        start = Math.max(0, end - maxVisible)
      }
      for (let i = start; i < end; i++) {
        pages.push(i + 1)
      }
      return pages
    })

    const formatDate = (dateStr: string): string => {
      if (!dateStr) return '-'
      try {
        const date = new Date(dateStr)
        const year = date.getFullYear()
        const month = String(date.getMonth() + 1).padStart(2, '0')
        const day = String(date.getDate()).padStart(2, '0')
        const hours = String(date.getHours()).padStart(2, '0')
        const minutes = String(date.getMinutes()).padStart(2, '0')
        return `${year}-${month}-${day} ${hours}:${minutes}`
      } catch {
        return dateStr
      }
    }

    const getRoleClass = (role: string) => {
      switch (role) {
        case '管理员':
          return 'role-admin'
        case '部门经理':
          return 'role-manager'
        case '材料员':
          return 'role-material'
        case '运维人员':
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

    const canDelete = (_item: Personnel) => {
      return currentUserRole.value === '管理员'
    }

    const canEditRole = () => {
      return currentUserRole.value === '管理员'
    }

    const loadData = async () => {
      const controller = createController()

      loading.value = true
      try {
        const response = await personnelService.getList(
          {
            page: currentPage.value,
            size: pageSize.value,
            name: searchForm.name || undefined,
            department: searchForm.department || undefined,
            current_user_role: currentUserRole.value,
            current_user_department: currentUserDepartment.value || undefined,
          },
          controller.signal
        )

        if (response.code === 200 && response.data) {
          personnelData.value = response.data.content || []
          totalElements.value = response.data.totalElements ?? 0
          totalPages.value = response.data.totalPages ?? 0
        } else {
          error(response.message || '加载数据失败')
        }
      } catch (err) {
        if (isAbortError(err)) {
          return
        }
        error(err instanceof Error ? err.message : '加载数据失败，请检查网络连接')
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
        warning('请填写姓名')
        return false
      }
      if (!formData.gender?.trim()) {
        warning('请选择性别')
        return false
      }
      if (!formData.role?.trim()) {
        warning('请选择角色')
        return false
      }
      if (formData.phone && formData.phone.trim()) {
        const phonePattern = /^1[3-9]\d{9}$/
        if (!phonePattern.test(formData.phone.trim())) {
          warning('请输入有效的手机号码')
          return false
        }
      }
      return true
    }

    const resetForm = () => {
      formData.name = ''
      formData.gender = ''
      formData.phone = ''
      formData.department = ''
      formData.role = '运维人员'
      formData.address = ''
      formData.remarks = ''
    }

    const handleOpenModal = () => {
      resetForm()
      inputMemory.loadMemory()
      openModal()
    }

    const handleCloseModal = () => {
      if (!isEditMode.value) {
        inputMemory.saveMemory(formData)
      }
      closeModal()
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
            remarks: formData.remarks || undefined,
          }

          const response = await personnelService.update(editingId.value, updateData)

          if (response.code === 200) {
            success('更新成功')
            handleCloseModal()
            await loadData()
          } else {
            error(response.message || '更新失败')
          }
        } else {
          const createData: PersonnelCreate = {
            name: formData.name,
            gender: formData.gender,
            phone: formData.phone || undefined,
            department: formData.department || undefined,
            role: formData.role,
            address: formData.address || undefined,
            remarks: formData.remarks || undefined,
          }

          const response = await personnelService.create(createData)

          if (response.code === 200) {
            success('创建成功')
            handleCloseModal()
            await loadData()
          } else {
            error(response.message || '创建失败')
          }
        }
      } catch (err) {
        console.error('保存失败:', err)
        error(err instanceof Error ? err.message : '保存失败，请检查网络连接')
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
      viewData.last_login_at = item.last_login_at || ''
      openViewModal()
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
      openModal(item.id)
    }

    const handleDelete = async (item: Personnel) => {
      try {
        await ElMessageBox.confirm('确定要删除该人员吗？', '提示', {
          confirmButtonText: '确定',
          cancelButtonText: '取消',
          type: 'warning',
        })

        loading.value = true
        const response = await personnelService.delete(item.id)

        if (response.code === 200) {
          success('删除成功')
          await loadData()
        } else {
          error(response.message || '删除失败')
        }
      } catch (err) {
        if (err !== 'cancel') {
          console.error('删除失败:', err)
          error(err instanceof Error ? err.message : '删除失败，请检查网络连接')
        }
      } finally {
        loading.value = false
      }
    }

    const handleJump = () => {
      const page = jumpPage.value - 1
      if (page >= 0 && page < totalPages.value) {
        currentPage.value = page
      }
    }

    const handlePageSizeChange = () => {
      currentPage.value = 0
      loadData()
    }

    const goToPage = (page: number) => {
      if (page >= 0 && page < totalPages.value) {
        currentPage.value = page
      }
    }

    const nextPage = () => {
      if (currentPage.value < totalPages.value - 1) {
        currentPage.value++
      }
    }

    const prevPage = () => {
      if (currentPage.value > 0) {
        currentPage.value--
      }
    }

    let refreshTimer: ReturnType<typeof setInterval> | null = null

    const startOnlineStatusRefresh = () => {
      if (refreshTimer) {
        clearInterval(refreshTimer)
      }
      refreshTimer = setInterval(() => {
        loadData()
      }, 30000)
    }

    const stopOnlineStatusRefresh = () => {
      if (refreshTimer) {
        clearInterval(refreshTimer)
        refreshTimer = null
      }
    }

    watch(currentPage, () => {
      loadData()
    })

    const handleUserChanged = () => {
      const user = userStore.getUser()
      if (user) {
        currentUserRole.value = user.role
        currentUserDepartment.value = user.department || ''
      }
      loadData()
    }

    onMounted(() => {
      const user = userStore.getUser()
      if (user) {
        currentUserRole.value = user.role
        currentUserDepartment.value = user.department || ''
      }
      loadData()
      startOnlineStatusRefresh()
      window.addEventListener('user-changed', handleUserChanged)
    })

    onUnmounted(() => {
      abort()
      stopOnlineStatusRefresh()
      window.removeEventListener('user-changed', handleUserChanged)
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
      displayedPages,
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
      handleOpenModal,
      handleCloseModal,
      handleSave,
      handleView,
      handleEdit,
      handleDelete,
      handleJump,
      handlePageSizeChange,
      closeViewModal,
      handleSearch,
      goToPage,
      nextPage,
      prevPage,
      getRoleClass,
      formatDate,
      canEdit,
      canDelete,
      canEditRole,
    }
  },
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
  flex-direction: column;
  gap: 16px;
  align-items: flex-start;
  flex-wrap: wrap;
}

.search-row {
  display: flex;
  gap: 16px;
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
  background: #2e7d32;
  color: #fff;
}

.btn-add:hover:not(:disabled) {
  background: #1b5e20;
}

.btn-search {
  background: #2196f3;
  color: #fff;
}

.btn-search:hover {
  background: #1976d2;
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
  min-width: 1400px;
}

.data-table thead {
  background: #e0e0e0;
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
  color: #2e7d32;
}

.action-edit {
  color: #2196f3;
}

.action-delete {
  color: #d32f2f;
}

.role-admin {
  color: #d32f2f;
  font-weight: 600;
}

.role-manager {
  color: #1976d2;
  font-weight: 600;
}

.role-employee {
  color: #666;
  font-weight: 500;
}

.role-material {
  color: #ff9800;
  font-weight: 600;
}

.status-cell {
  white-space: nowrap;
}

.status-badge {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 4px 10px;
  border-radius: 12px;
  font-size: 13px;
  font-weight: 500;
}

.status-online {
  background: #e8f5e9;
  color: #2e7d32;
}

.status-online .status-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: #4caf50;
  animation: pulse 1.5s ease-in-out infinite;
}

.status-offline {
  background: #ffebee;
  color: #c62828;
}

.status-offline .status-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: #f44336;
}

.status-text {
  font-weight: 500;
}

.device-type {
  font-size: 12px;
  color: #666;
  margin-left: 2px;
}

@keyframes pulse {
  0%,
  100% {
    opacity: 1;
    transform: scale(1);
  }
  50% {
    opacity: 0.6;
    transform: scale(1.1);
  }
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
  border-color: #2196f3;
  color: #2196f3;
}

.page-btn:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}

.page-btn.active {
  background: #2196f3;
  color: #fff;
  border-color: #2196f3;
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
  border-color: #2196f3;
}

.page-go {
  min-width: 40px;
  height: 28px;
  padding: 0 8px;
  background: #2196f3;
  color: #fff;
  border: none;
  border-radius: 3px;
  font-size: 12px;
  cursor: pointer;
  transition: background 0.15s;
}

.page-go:hover {
  background: #1976d2;
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
  color: #d32f2f;
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
  background: #2196f3;
  color: #fff;
}

.btn-save:hover:not(:disabled) {
  background: #1976d2;
}
</style>
