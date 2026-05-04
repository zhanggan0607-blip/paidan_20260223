<template>
  <div class="personnel-management">
    <LoadingSpinner
      :visible="loading"
      text="加载中..."
    />
    <Toast
      :visible="toast.visible"
      :message="toast.message"
      :type="toast.type"
    />

    <div class="search-section">
      <div class="search-form">
        <div class="search-row">
          <div class="search-item">
            <label
              for="search_name"
              class="search-label"
            >姓名：</label>
            <SearchInput
              v-model="searchForm.name"
              input-id="search_name"
              field-key="PersonnelManagement_name"
              placeholder="请输入姓名"
              @input="handleSearch"
            />
          </div>
          <div class="search-item">
            <label
              for="search_部门"
              class="search-label"
            >部门：</label>
            <SearchInput
              v-model="searchForm.department"
              input-id="search_部门"
              field-key="PersonnelManagement_department"
              placeholder="请输入部门"
              @input="handleSearch"
            />
          </div>
        </div>
      </div>
      <div class="search-actions">
        <button
          class="btn btn-add"
          @click="handleOpenModal"
        >
          + 新增人员
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
            <td :class="getRoleClass(item.role ?? '')">
              {{ item.role }}
            </td>
            <td>{{ item.phone || '-' }}</td>
            <td>{{ item.last_login_at ? formatDate(item.last_login_at) : '-' }}</td>
            <td class="status-cell">
              <span
                class="status-badge"
                :class="{
                  'status-online': getUserOnlineStatus(item.id).is_online,
                  'status-offline': !getUserOnlineStatus(item.id).is_online,
                }"
              >
                <span class="status-dot" />
                <span class="status-text">{{
                  getUserOnlineStatus(item.id).is_online ? '在线' : '离线'
                }}</span>
                <span
                  v-if="
                    getUserOnlineStatus(item.id).is_online &&
                      getUserOnlineStatus(item.id).device_type
                  "
                  class="device-type"
                >
                  ({{ getUserOnlineStatus(item.id).device_type === 'pc' ? '电脑端' : '手机端' }})
                </span>
              </span>
            </td>
            <td class="action-cell">
              <a
                href="#"
                class="action-link action-view"
                @click.prevent="handleView(item)"
              >查看</a>
              <a
                v-if="canEdit(item)"
                href="#"
                class="action-link action-edit"
                @click.prevent="handleEdit(item)"
              >编辑</a>
              <a
                v-if="canDelete(item)"
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
          :disabled="currentPage === 0"
          @click="prevPage"
        >
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
        <select
          v-model.number="pageSize"
          class="page-select"
          @change="handlePageSizeChange"
        >
          <option :value="10">
            10 条 / 页
          </option>
          <option :value="20">
            20 条 / 页
          </option>
          <option :value="50">
            50 条 / 页
          </option>
        </select>
        <div class="page-jump">
          <span>跳至</span>
          <input
            id="jumpPage"
            v-model.number="jumpPage"
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

    <div
      v-if="isModalOpen"
      class="modal-overlay"
      @click.self="handleCloseModal"
    >
      <div class="modal-container">
        <div class="modal-header">
          <h3 class="modal-title">
            {{ isEditMode ? '编辑人员' : '新增人员' }}
          </h3>
          <button
            class="modal-close"
            @click="handleCloseModal"
          >
            ×
          </button>
        </div>
        <div class="modal-body">
          <div class="form-grid">
            <div class="form-column">
              <div class="form-item">
                <label
                  for="name"
                  class="form-label"
                > <span class="required">*</span> 姓名 </label>
                <input
                  id="name"
                 
                  v-model="formData.name"
                  name="name"
                  type="text"
                  class="form-input"
                  placeholder="请输入"
                  maxlength="50"
                  autocomplete="name"
                >
              </div>
              <div class="form-item">
                <label
                  for="gender"
                  class="form-label"
                > <span class="required">*</span> 性别 </label>
                <select
                  id="gender"
                  v-model="formData.gender"
                  name="gender"
                  class="form-input"
                >
                  <option value="">
                    请选择
                  </option>
                  <option value="男">
                    男
                  </option>
                  <option value="女">
                    女
                  </option>
                  <option value="其他">
                    其他
                  </option>
                </select>
              </div>
              <div class="form-item">
                <label
                  for="phone"
                  class="form-label"
                >联系电话</label>
                <input
                  id="phone"
                 
                  v-model="formData.phone"
                  name="phone"
                  type="tel"
                  class="form-input"
                  placeholder="请输入手机号码"
                  maxlength="11"
                  autocomplete="tel"
                >
              </div>
            </div>
            <div class="form-column">
              <div class="form-item">
                <label
                  for="department"
                  class="form-label"
                >所属部门</label>
                <input
                  id="department"
                 
                  v-model="formData.department"
                  name="department"
                  type="text"
                  class="form-input"
                  placeholder="请输入"
                  maxlength="100"
                  autocomplete="organization"
                >
              </div>
              <div class="form-item">
                <label
                  for="role"
                  class="form-label"
                > <span class="required">*</span> 角色 </label>
                <select
                  id="role"
                  v-model="formData.role"
                  name="role"
                  class="form-input"
                  :disabled="!canEditRole()"
                >
                  <option value="">
                    请选择
                  </option>
                  <option value="管理员">
                    管理员
                  </option>
                  <option value="部门经理">
                    部门经理
                  </option>
                  <option value="材料员">
                    材料员
                  </option>
                  <option value="运维人员">
                    运维人员
                  </option>
                </select>
              </div>
              <div class="form-item">
                <label
                  for="address"
                  class="form-label"
                >地址</label>
                <input
                  id="address"
                 
                  v-model="formData.address"
                  name="address"
                  type="text"
                  class="form-input"
                  placeholder="请输入"
                  maxlength="200"
                  autocomplete="street-address"
                >
              </div>
            </div>
          </div>
          <div class="form-item-full">
            <label
              for="remarks"
              class="form-label"
            >备注</label>
            <textarea
              id="remarks"
              v-model="formData.remarks"
              name="remarks"
              class="form-textarea"
              placeholder="请输入"
              rows="3"
              maxlength="500"
            />
          </div>
        </div>
        <div class="modal-footer">
          <button
            class="btn btn-cancel"
            @click="handleCloseModal"
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
      v-if="isViewModalOpen"
      class="modal-overlay"
      @click.self="closeViewModal"
    >
      <div class="modal-container">
        <div class="modal-header">
          <h3 class="modal-title">
            查看人员
          </h3>
          <button
            class="modal-close"
            @click="closeViewModal"
          >
            ×
          </button>
        </div>
        <div class="modal-body">
          <div class="form-grid">
            <div class="form-column">
              <div class="form-item">
                <span class="form-label">姓名</span>
                <div class="form-value">
                  {{ viewData.name || '-' }}
                </div>
              </div>
              <div class="form-item">
                <span class="form-label">性别</span>
                <div class="form-value">
                  {{ viewData.gender || '-' }}
                </div>
              </div>
              <div class="form-item">
                <span class="form-label">联系电话</span>
                <div class="form-value">
                  {{ viewData.phone || '-' }}
                </div>
              </div>
              <div class="form-item">
                <span class="form-label">最后登录时间</span>
                <div class="form-value">
                  {{ viewData.last_login_at ? formatDate(viewData.last_login_at) : '-' }}
                </div>
              </div>
            </div>
            <div class="form-column">
              <div class="form-item">
                <span class="form-label">所属部门</span>
                <div class="form-value">
                  {{ viewData.department || '-' }}
                </div>
              </div>
              <div class="form-item">
                <span class="form-label">角色</span>
                <div
                  class="form-value"
                  :class="getRoleClass(viewData.role)"
                >
                  {{ viewData.role || '-' }}
                </div>
              </div>
              <div class="form-item">
                <span class="form-label">地址</span>
                <div class="form-value">
                  {{ viewData.address || '-' }}
                </div>
              </div>
              <div class="form-item">
                <span class="form-label">备注</span>
                <div class="form-value form-value-textarea">
                  {{ viewData.remarks || '-' }}
                </div>
              </div>
            </div>
          </div>
        </div>
        <div class="modal-footer">
          <button
            class="btn btn-cancel"
            @click="closeViewModal"
          >
            关闭
          </button>
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
import { useUserStore } from '../stores/userStore'
import { LoadingSpinner, Toast, SearchInput } from '@sstcp/shared'
import { useInputMemory } from '../utils'
import { useToast, usePageState, useAbortController } from '../composables'
import { useOnlineStatusWebSocket } from '../composables/useOnlineStatusWebSocket'

export default defineComponent({
  name: 'PersonnelManagement',
  components: {
    LoadingSpinner,
    Toast,
    SearchInput,
  },
  setup() {
    const userStore = useUserStore()
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
    const { isConnected: wsConnected, getUserOnlineStatus } = useOnlineStatusWebSocket()

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
          personnelData.value = response.data.items || []
          totalElements.value = response.data.total ?? 0
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
      viewData.gender = item.gender ?? ''
      viewData.phone = item.phone || ''
      viewData.department = item.department || ''
      viewData.role = item.role ?? ''
      viewData.address = item.address || ''
      viewData.remarks = item.remarks || ''
      viewData.last_login_at = item.last_login_at || ''
      openViewModal()
    }

    const handleEdit = (item: Personnel) => {
      editingId.value = item.id
      formData.name = item.name
      formData.gender = item.gender ?? ''
      formData.phone = item.phone || ''
      formData.department = item.department || ''
      formData.role = item.role ?? ''
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

    watch(currentPage, () => {
      loadData()
    })

    const handleUserChanged = () => {
      const user = userStore.currentUser
      if (user) {
        currentUserRole.value = user.role
        currentUserDepartment.value = user.department || ''
      }
      loadData()
    }

    onMounted(() => {
      const user = userStore.currentUser
      if (user) {
        currentUserRole.value = user.role
        currentUserDepartment.value = user.department || ''
      }
      loadData()
      window.addEventListener('user-changed', handleUserChanged)
    })

    onUnmounted(() => {
      abort()
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
      wsConnected,
      getUserOnlineStatus,
    }
  },
})
</script>

<style scoped>
.personnel-management {
  background: var(--color-bg-card);
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
  background: var(--color-bg-page);
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
  color: var(--color-text-regular);
  white-space: nowrap;
}

.search-input {
  width: 200px;
  padding: 8px 12px;
  border: 1px solid var(--color-border);
  border-radius: 3px;
  font-size: 14px;
  color: var(--color-text-primary);
  background: var(--color-bg-card);
  transition: border-color 0.15s;
}

.search-input:focus {
  outline: none;
  border-color: var(--color-primary);
  box-shadow: 0 0 0 2px rgba(25, 118, 210, 0.1);
}

.search-input::placeholder {
  color: var(--color-text-placeholder);
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
  background: var(--color-success);
  color: var(--color-bg-card);
}

.btn-add:hover:not(:disabled) {
  background: var(--color-success);
}

.btn-search {
  background: var(--color-primary);
  color: var(--color-bg-card);
}

.btn-search:hover {
  background: var(--color-primary);
}

.table-section {
  margin-bottom: 20px;
  border: 1px solid var(--color-border);
  border-radius: 4px;
  overflow-x: auto;
}

.data-table {
  width: 100%;
  border-collapse: collapse;
  min-width: 1400px;
}

.data-table thead {
  background: var(--color-border);
}

.data-table th {
  padding: 12px 16px;
  text-align: left;
  font-size: 14px;
  font-weight: 600;
  color: var(--color-text-primary);
  border-bottom: 1px solid var(--color-border);
  white-space: nowrap;
}

.data-table td {
  padding: 12px 16px;
  text-align: left;
  font-size: 14px;
  color: var(--color-text-regular);
  border-bottom: 1px solid var(--color-border-light);
}

.data-table tbody tr:hover {
  background: var(--color-bg-page);
}

.even-row {
  background: var(--color-bg-page);
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
  color: var(--color-success);
}

.action-edit {
  color: var(--color-primary);
}

.action-delete {
  color: var(--color-danger);
}

.role-admin {
  color: var(--color-danger);
  font-weight: 600;
}

.role-manager {
  color: var(--color-primary);
  font-weight: 600;
}

.role-employee {
  color: var(--color-text-secondary);
  font-weight: 500;
}

.role-material {
  color: var(--color-warning);
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
  background: var(--color-success-subtle);
  color: var(--color-success);
}

.status-online .status-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: var(--color-success);
  animation: pulse 1.5s ease-in-out infinite;
}

.status-offline {
  background: var(--color-danger-subtle);
  color: var(--color-danger);
}

.status-offline .status-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: var(--color-danger);
}

.status-text {
  font-weight: 500;
}

.device-type {
  font-size: 12px;
  color: var(--color-text-secondary);
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
  color: var(--color-text-secondary);
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
  border: 1px solid var(--color-border);
  border-radius: 3px;
  background: var(--color-bg-card);
  font-size: 14px;
  color: var(--color-text-primary);
  cursor: pointer;
  transition: all 0.15s;
  display: flex;
  align-items: center;
  justify-content: center;
}

.page-btn:hover:not(:disabled) {
  border-color: var(--color-primary);
  color: var(--color-primary);
}

.page-btn:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}

.page-btn.active {
  background: var(--color-primary);
  color: var(--color-bg-card);
  border-color: var(--color-primary);
}

.page-nav {
  font-size: 16px;
}

.page-select {
  padding: 6px 12px;
  border: 1px solid var(--color-border);
  border-radius: 3px;
  font-size: 14px;
  color: var(--color-text-primary);
  background: var(--color-bg-card);
  cursor: pointer;
}

.page-jump {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
  color: var(--color-text-secondary);
}

.page-input {
  width: 48px;
  padding: 6px 8px;
  border: 1px solid var(--color-border);
  border-radius: 3px;
  font-size: 14px;
  color: var(--color-text-primary);
  text-align: center;
  background: var(--color-bg-card);
}

.page-input:focus {
  outline: none;
  border-color: var(--color-primary);
}

.page-go {
  min-width: 40px;
  height: 28px;
  padding: 0 8px;
  background: var(--color-primary);
  color: var(--color-bg-card);
  border: none;
  border-radius: 3px;
  font-size: 12px;
  cursor: pointer;
  transition: background 0.15s;
}

.page-go:hover {
  background: var(--color-primary);
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

.form-item-full {
  display: flex;
  flex-direction: column;
  gap: 8px;
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

.form-textarea {
  padding: 8px 12px;
  border: 1px solid var(--color-border);
  border-radius: 3px;
  font-size: 14px;
  color: var(--color-text-primary);
  background: var(--color-bg-card);
  transition: border-color 0.15s;
  resize: vertical;
  font-family: inherit;
}

.form-textarea:focus {
  outline: none;
  border-color: var(--color-primary);
  box-shadow: 0 0 0 2px rgba(25, 118, 210, 0.1);
}

.form-textarea::placeholder {
  color: var(--color-text-placeholder);
}

.form-value {
  padding: 8px 12px;
  background: var(--color-bg-page);
  border: 1px solid var(--color-border);
  border-radius: 3px;
  font-size: 14px;
  color: var(--color-text-primary);
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
  background: var(--color-primary);
}
</style>
