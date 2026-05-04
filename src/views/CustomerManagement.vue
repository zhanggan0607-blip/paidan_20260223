<template>
  <div class="customer-management">
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
              for="search_clientName"
              class="search-label"
            >客户单位：</label>
            <SearchInput
              v-model="searchForm.name"
              input-id="search_clientName"
              field-key="CustomerManagement_name"
              placeholder="请输入客户单位"
              @input="handleSearch"
            />
          </div>
          <div class="search-item">
            <label
              for="search_clientContact"
              class="search-label"
            >客户联系人：</label>
            <SearchInput
              v-model="searchForm.contact_person"
              input-id="search_clientContact"
              field-key="CustomerManagement_contact_person"
              placeholder="请输入客户联系人"
              @input="handleSearch"
            />
          </div>
        </div>
      </div>
      <div class="search-actions">
        <button
          class="btn btn-add"
          @click="openModal"
        >
          + 新增客户
        </button>
      </div>
    </div>

    <div class="table-section">
      <table class="data-table">
        <thead>
          <tr>
            <th>序号</th>
            <th>客户单位</th>
            <th>客户地址</th>
            <th>客户联系人</th>
            <th>客户联系方式</th>
            <th>客户联系人职位</th>
            <th>操作</th>
          </tr>
        </thead>
        <tbody>
          <tr
            v-for="(item, index) in customerData"
            :key="item.id"
            :class="{ 'even-row': index % 2 === 0 }"
          >
            <td>{{ startIndex + index + 1 }}</td>
            <td>{{ item.name }}</td>
            <td>{{ item.address || '-' }}</td>
            <td>
              <template v-if="item.contacts && item.contacts.length > 0">
                <div
                  v-for="contact in item.contacts"
                  :key="contact.id"
                  class="contact-item"
                >
                  {{ contact.contact_person }}
                </div>
              </template>
              <template v-else>
                -
              </template>
            </td>
            <td>
              <template v-if="item.contacts && item.contacts.length > 0">
                <div
                  v-for="contact in item.contacts"
                  :key="contact.id"
                  class="contact-item"
                >
                  {{ contact.phone || '-' }}
                </div>
              </template>
              <template v-else>
                -
              </template>
            </td>
            <td>
              <template v-if="item.contacts && item.contacts.length > 0">
                <div
                  v-for="contact in item.contacts"
                  :key="contact.id"
                  class="contact-item"
                >
                  {{ contact.contact_position || '-' }}
                </div>
              </template>
              <template v-else>
                -
              </template>
            </td>
            <td class="action-cell">
              <a
                href="#"
                class="action-link action-view"
                @click.prevent="handleView(item)"
              >查看</a>
              <a
                href="#"
                class="action-link action-edit"
                @click.prevent="handleEdit(item)"
              >编辑</a>
              <a
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
          @click="currentPage--"
        >
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
        <button
          class="page-btn page-nav"
          :disabled="currentPage >= totalPages - 1"
          @click="currentPage++"
        >
          &gt;
        </button>
        <select
          id="pageSize"
          v-model="pageSize"
          name="pageSize"
          class="page-select"
          @change="handlePageSizeChange"
        >
          <option value="10">
            10 条 / 页
          </option>
          <option value="20">
            20 条 / 页
          </option>
          <option value="50">
            50 条 / 页
          </option>
        </select>
        <div class="page-jump">
          <span>跳至</span>
          <input
            id="jumpPage"
            v-model="jumpPage"
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
      @click.self="closeModal"
    >
      <div class="modal-container modal-large">
        <div class="modal-header">
          <h3 class="modal-title">
            {{ isEditMode ? '编辑客户' : '新增客户' }}
          </h3>
          <button
            class="modal-close"
            @click="closeModal"
          >
            ×
          </button>
        </div>
        <div class="modal-body">
          <div class="form-grid">
            <div class="form-column">
              <div class="form-item">
                <label
                  for="clientName"
                  class="form-label"
                > <span class="required">*</span> 客户单位 </label>
                <input
                  id="clientName"
                  v-model="formData.name"
                  name="clientName"
                  type="text"
                  class="form-input"
                  placeholder="请输入"
                  maxlength="100"
                >
              </div>
            </div>
            <div class="form-column">
              <div class="form-item">
                <label
                  for="clientAddress"
                  class="form-label"
                >客户地址</label>
                <input
                  id="clientAddress"
                  v-model="formData.address"
                  name="clientAddress"
                  type="text"
                  class="form-input"
                  placeholder="请输入"
                  maxlength="200"
                >
              </div>
            </div>
          </div>

          <div class="contacts-section">
            <div class="contacts-header">
              <span class="form-label">联系人信息</span>
              <button
                type="button"
                class="btn btn-add-contact"
                @click="addContact"
              >
                + 添加联系人
              </button>
            </div>
            <div
              v-if="formData.contacts.length === 0"
              class="no-contacts"
            >
              暂无联系人，请点击"添加联系人"按钮添加
            </div>
            <div
              v-for="(contact, index) in formData.contacts"
              :key="index"
              class="contact-row"
            >
              <div class="contact-index">
                {{ index + 1 }}
              </div>
              <div class="contact-fields">
                <div class="contact-field">
                  <label
                    for="contact_contactName"
                    class="contact-label"
                  ><span class="required">*</span> 联系人姓名</label>
                  <input
                    id="contact_contactName"
                    v-model="contact.contact_person"
                    name="contact_contactName"
                    type="text"
                    class="form-input"
                    placeholder="请输入联系人姓名"
                    maxlength="50"
                  >
                </div>
                <div class="contact-field">
                  <label
                    for="contact_contactPhone"
                    class="contact-label"
                  >联系方式</label>
                  <input
                    id="contact_contactPhone"
                    v-model="contact.phone"
                    name="contact_contactPhone"
                    type="text"
                    class="form-input"
                    placeholder="请输入手机号码"
                    maxlength="11"
                  >
                </div>
                <div class="contact-field">
                  <label
                    for="contact_contactPosition"
                    class="contact-label"
                  >联系人职位</label>
                  <input
                    id="contact_contactPosition"
                    v-model="contact.contact_position"
                    name="contact_contactPosition"
                    type="text"
                    class="form-input"
                    placeholder="请输入职位"
                    maxlength="50"
                  >
                </div>
              </div>
              <button
                type="button"
                class="btn btn-remove-contact"
                @click="removeContact(index)"
              >
                删除
              </button>
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
            @click="closeModal"
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
      <div class="modal-container modal-large">
        <div class="modal-header">
          <h3 class="modal-title">
            查看客户
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
                <span class="form-label">客户单位</span>
                <div class="form-value">
                  {{ viewData.name || '-' }}
                </div>
              </div>
            </div>
            <div class="form-column">
              <div class="form-item">
                <span class="form-label">客户地址</span>
                <div class="form-value">
                  {{ viewData.address || '-' }}
                </div>
              </div>
            </div>
          </div>

          <div class="contacts-section view-mode">
            <div class="contacts-header">
              <span class="form-label">联系人信息</span>
            </div>
            <div
              v-if="!viewData.contacts || viewData.contacts.length === 0"
              class="no-contacts"
            >
              暂无联系人信息
            </div>
            <div
              v-else
              class="contacts-view-list"
            >
              <div
                v-for="(contact, index) in viewData.contacts"
                :key="contact.id"
                class="contact-view-item"
              >
                <div class="contact-view-index">
                  {{ index + 1 }}
                </div>
                <div class="contact-view-info">
                  <div class="contact-view-row">
                    <span class="contact-view-label">联系人姓名：</span>
                    <span class="contact-view-value">{{ contact.contact_person || '-' }}</span>
                  </div>
                  <div class="contact-view-row">
                    <span class="contact-view-label">联系方式：</span>
                    <span class="contact-view-value">{{ contact.phone || '-' }}</span>
                  </div>
                  <div class="contact-view-row">
                    <span class="contact-view-label">联系人职位：</span>
                    <span class="contact-view-value">{{ contact.contact_position || '-' }}</span>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <div class="form-item-full">
            <span class="form-label">备注</span>
            <div class="form-value form-value-textarea">
              {{ viewData.remarks || '-' }}
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
import {
  defineComponent,
  reactive,
  ref,
  computed,
  watch,
  onMounted,
  onUnmounted,
  watchEffect,
} from 'vue'
import { ElMessageBox } from 'element-plus'
import {
  customerService,
  type Customer,
  type CustomerCreate,
  type CustomerUpdate,
  type CustomerContact,
  type CustomerContactCreate,
} from '../services/customer'
import { LoadingSpinner, Toast, SearchInput } from '@sstcp/shared'
import { useInputMemory, createDebounce } from '../utils'

export default defineComponent({
  name: 'CustomerManagement',
  components: {
    LoadingSpinner,
    Toast,
    SearchInput,
  },
  setup() {
    const searchForm = reactive({
      name: '',
      contact_person: '',
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

    const customerData = ref<Customer[]>([])
    const totalElements = ref(0)
    const totalPages = ref(0)

    const toast = reactive({
      visible: false,
      message: '',
      type: 'success' as 'success' | 'error' | 'warning' | 'info',
    })

    interface ContactFormItem {
      contact_person: string
      phone: string
      contact_position: string
    }

    const formData = reactive({
      name: '',
      address: '',
      contacts: [] as ContactFormItem[],
      remarks: '',
    })

    let abortController: AbortController | null = null

    const inputMemory = useInputMemory({
      pageName: 'CustomerManagement',
      fields: ['name', 'address', 'remarks'],
      onRestore: (data) => {
        if (data.name) formData.name = data.name
        if (data.address) formData.address = data.address
        if (data.remarks) formData.remarks = data.remarks
      },
    })

    const viewData = reactive({
      id: 0,
      name: '',
      address: '',
      contacts: [] as CustomerContact[],
      remarks: '',
    })

    const startIndex = computed(() => currentPage.value * pageSize.value)

    /**
     * 显示Toast提示消息
     * @param message 提示消息内容
     * @param type 提示类型：success/error/warning/info
     */
    const showToast = (
      message: string,
      type: 'success' | 'error' | 'warning' | 'info' = 'success'
    ) => {
      toast.message = message
      toast.type = type
      toast.visible = true
    }

    /**
     * 加载客户列表数据
     * 根据当前页码、每页大小和搜索条件从后端获取数据
     * 支持请求取消，避免重复请求
     */
    const loadData = async () => {
      if (abortController) {
        abortController.abort()
      }
      abortController = new AbortController()

      loading.value = true
      try {
        const response = await customerService.getList(
          {
            page: currentPage.value,
            size: pageSize.value,
            name: searchForm.name || undefined,
            contact_person: searchForm.contact_person || undefined,
          },
          abortController.signal
        )

        if (response.code === 200) {
          customerData.value = response.data.items || response.data.content || []
          totalElements.value = response.data.total ?? response.data.totalElements ?? 0
          totalPages.value = response.data.totalPages
        } else {
          showToast(response.message || '加载数据失败', 'error')
        }
      } catch (error: any) {
        if (error instanceof Error && error.name === 'AbortError') {
          return
        }
        if (error?.canceled) {
          return
        }
        showToast(error.message || '加载数据失败，请检查网络连接', 'error')
      } finally {
        loading.value = false
      }
    }

    /**
     * 处理搜索按钮点击事件
     * 重置页码并重新加载数据
     * 使用防抖避免频繁请求
     */
    const { debounced: debouncedSearch, cancel: cancelSearchDebounce } = createDebounce(() => {
      currentPage.value = 0
      loadData()
    }, 300)

    const handleSearch = () => {
      debouncedSearch()
    }

    /**
     * 添加联系人
     */
    const addContact = () => {
      formData.contacts.push({
        contact_person: '',
        phone: '',
        contact_position: '',
      })
    }

    /**
     * 删除联系人
     * @param index 联系人索引
     */
    const removeContact = (index: number) => {
      formData.contacts.splice(index, 1)
    }

    /**
     * 校验表单数据
     * 检查必填字段和手机号格式
     * @returns 表单是否有效
     */
    const checkFormValid = (): boolean => {
      if (!formData.name?.trim()) {
        showToast('请填写客户单位', 'warning')
        return false
      }
      if (formData.contacts.length === 0) {
        showToast('请至少添加一个联系人', 'warning')
        return false
      }
      for (let i = 0; i < formData.contacts.length; i++) {
        const contact = formData.contacts[i]
        if (!contact.contact_person?.trim()) {
          showToast(`第${i + 1}个联系人的姓名不能为空`, 'warning')
          return false
        }
        if (contact.phone && contact.phone.trim()) {
          const phonePattern = /^1[3-9]\d{9}$/
          if (!phonePattern.test(contact.phone.trim())) {
            showToast(`第${i + 1}个联系人的手机号码格式不正确`, 'warning')
            return false
          }
        }
      }
      return true
    }

    /**
     * 打开新增客户弹窗
     * 重置表单并加载输入记忆
     */
    const openModal = () => {
      resetForm()
      isEditMode.value = false
      inputMemory.loadMemory()
      isModalOpen.value = true
    }

    /**
     * 关闭客户编辑弹窗
     * 新增模式下保存输入记忆
     */
    const closeModal = () => {
      if (!isEditMode.value) {
        inputMemory.saveMemory(formData)
      }
      isModalOpen.value = false
    }

    /**
     * 重置表单数据为默认值
     */
    const resetForm = () => {
      formData.name = ''
      formData.address = ''
      formData.contacts = []
      formData.remarks = ''
    }

    /**
     * 保存客户信息
     * 根据编辑模式调用创建或更新接口
     */
    const handleSave = async () => {
      if (!checkFormValid()) {
        return
      }

      saving.value = true
      try {
        const contactsData: CustomerContactCreate[] = formData.contacts.map((c) => ({
          contact_person: c.contact_person?.trim() || '',
          phone: c.phone?.trim() || undefined,
          contact_position: c.contact_position?.trim() || undefined,
        }))

        if (isEditMode.value && editingId.value !== null) {
          const updateData: CustomerUpdate = {
            name: formData.name?.trim() || undefined,
            address: formData.address?.trim() || undefined,
            contacts: contactsData,
            remarks: formData.remarks?.trim() || undefined,
          }

          const response = await customerService.update(editingId.value, updateData)

          if (response.code === 200) {
            showToast('更新成功', 'success')
            closeModal()
            await loadData()
            window.dispatchEvent(new CustomEvent('customer-changed'))
          } else {
            showToast(response.message || '更新失败', 'error')
          }
        } else {
          const createData: CustomerCreate = {
            name: formData.name?.trim() || '',
            address: formData.address?.trim() || undefined,
            contacts: contactsData,
            remarks: formData.remarks?.trim() || undefined,
          }

          const response = await customerService.create(createData)

          if (response.code === 200) {
            showToast('创建成功', 'success')
            closeModal()
            await loadData()
            window.dispatchEvent(new CustomEvent('customer-changed'))
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

    /**
     * 查看客户详情
     * @param item 客户信息
     */
    const handleView = (item: Customer) => {
      viewData.id = item.id
      viewData.name = item.name ?? ''
      viewData.address = item.address || ''
      viewData.contacts = item.contacts || []
      viewData.remarks = item.remarks || ''
      isViewModalOpen.value = true
    }

    /**
     * 编辑客户信息
     * 将客户数据填充到表单并打开编辑弹窗
     * @param item 客户信息
     */
    const handleEdit = (item: Customer) => {
      editingId.value = item.id
      formData.name = item.name ?? ''
      formData.address = item.address || ''
      formData.contacts = (item.contacts || []).map((c) => ({
        contact_person: c.contact_person || '',
        phone: c.phone || '',
        contact_position: c.contact_position || '',
      }))
      formData.remarks = item.remarks || ''
      isEditMode.value = true
      isModalOpen.value = true
    }

    /**
     * 关闭查看详情弹窗
     */
    const closeViewModal = () => {
      isViewModalOpen.value = false
    }

    /**
     * 删除客户
     * 弹出确认框，确认后调用删除接口
     * 支持级联删除关联数据
     * @param item 客户信息
     */
    const handleDelete = async (item: Customer) => {
      try {
        await ElMessageBox.confirm('确定要删除该客户吗？', '提示', {
          confirmButtonText: '确定',
          cancelButtonText: '取消',
          type: 'warning',
        })
      } catch {
        return
      }

      loading.value = true
      try {
        const response = await customerService.delete(item.id)

        if (response.code === 200) {
          showToast(response.message || '删除成功', 'success')
          await loadData()
          window.dispatchEvent(new CustomEvent('customer-changed'))
        } else {
          showToast(response.message || '删除失败', 'error')
        }
      } catch (error: any) {
        console.error('删除失败:', error)
        if (error.status === 400 && error.message && error.message.includes('请确认是否级联删除')) {
          loading.value = false
          ElMessageBox.confirm(error.message + '\n\n是否确认删除客户及其所有关联数据？', '提示', {
            confirmButtonText: '确定',
            cancelButtonText: '取消',
            type: 'warning',
          })
            .then(async () => {
              loading.value = true
              try {
                const cascadeResponse = await customerService.delete(item.id, true)
                if (cascadeResponse.code === 200) {
                  showToast(cascadeResponse.message || '删除成功', 'success')
                  await loadData()
                  window.dispatchEvent(new CustomEvent('customer-changed'))
                } else {
                  showToast(cascadeResponse.message || '删除失败', 'error')
                }
              } catch (cascadeError: any) {
                console.error('级联删除失败:', cascadeError)
                showToast(cascadeError.message || '删除失败', 'error')
              } finally {
                loading.value = false
              }
            })
            .catch(() => {})
        } else if (error.status === 400 && error.message) {
          showToast(error.message, 'warning')
        } else {
          showToast(error.message || '删除失败，请检查网络连接', 'error')
        }
      } finally {
        loading.value = false
      }
    }

    /**
     * 跳转到指定页码
     */
    const handleJump = () => {
      const page = parseInt(jumpPage.value.toString())
      if (page >= 1 && page <= totalPages.value) {
        currentPage.value = page - 1
      }
    }

    /**
     * 处理每页大小变更
     * 重置页码并重新加载数据
     */
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
      window.addEventListener('user-changed', handleUserChanged)
      window.addEventListener('customer-changed', handleCustomerChanged)
    })

    onUnmounted(() => {
      if (abortController) {
        abortController.abort()
      }
      cancelSearchDebounce()
      window.removeEventListener('user-changed', handleUserChanged)
      window.removeEventListener('customer-changed', handleCustomerChanged)
    })

    /**
     * 处理用户变更事件
     * 重新加载客户数据
     */
    const handleUserChanged = () => {
      loadData()
    }

    /**
     * 处理客户变更事件
     * 重新加载客户数据
     */
    const handleCustomerChanged = () => {
      loadData()
    }

    return {
      searchForm,
      customerData,
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
      addContact,
      removeContact,
    }
  },
})
</script>

<style scoped>
.customer-management {
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
  min-width: 1000px;
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
  vertical-align: top;
}

.data-table tbody tr:hover {
  background: var(--color-bg-page);
}

.even-row {
  background: var(--color-bg-page);
}

.contact-item {
  padding: 4px 0;
  border-bottom: 1px dashed var(--color-border);
}

.contact-item:last-child {
  border-bottom: none;
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
  width: 800px;
  max-width: 95vw;
  max-height: 90vh;
  overflow-y: auto;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
}

.modal-large {
  width: 900px;
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
  margin-bottom: 24px;
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

.contacts-section {
  margin-bottom: 24px;
  padding: 16px;
  background: var(--color-bg-page);
  border-radius: 4px;
  border: 1px solid var(--color-border);
}

.contacts-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.btn-add-contact {
  padding: 6px 12px;
  background: var(--color-primary);
  color: var(--color-bg-card);
  border: none;
  border-radius: 3px;
  font-size: 13px;
  cursor: pointer;
  transition: background 0.15s;
}

.btn-add-contact:hover {
  background: var(--color-primary);
}

.no-contacts {
  text-align: center;
  color: var(--color-text-placeholder);
  padding: 20px;
  font-size: 14px;
}

.contact-row {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  padding: 12px;
  margin-bottom: 12px;
  background: var(--color-bg-card);
  border-radius: 4px;
  border: 1px solid var(--color-border);
}

.contact-row:last-child {
  margin-bottom: 0;
}

.contact-index {
  width: 24px;
  height: 24px;
  background: var(--color-primary);
  color: var(--color-bg-card);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
  font-weight: 600;
  flex-shrink: 0;
  margin-top: 8px;
}

.contact-fields {
  flex: 1;
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
}

.contact-field {
  flex: 1;
  min-width: 150px;
}

.contact-label {
  display: block;
  font-size: 12px;
  color: var(--color-text-secondary);
  margin-bottom: 4px;
}

.btn-remove-contact {
  padding: 4px 8px;
  background: var(--color-bg-card);
  color: var(--color-danger);
  border: 1px solid var(--color-danger);
  border-radius: 3px;
  font-size: 12px;
  cursor: pointer;
  transition: all 0.15s;
  flex-shrink: 0;
  margin-top: 24px;
}

.btn-remove-contact:hover {
  background: var(--color-danger);
  color: var(--color-bg-card);
}

.contacts-section.view-mode {
  background: var(--color-bg-card);
  padding: 0;
  border: none;
}

.contacts-view-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.contact-view-item {
  display: flex;
  gap: 16px;
  padding: 16px;
  background: var(--color-bg-page);
  border-radius: 4px;
  border: 1px solid var(--color-border);
}

.contact-view-index {
  width: 28px;
  height: 28px;
  background: var(--color-primary);
  color: var(--color-bg-card);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 14px;
  font-weight: 600;
  flex-shrink: 0;
}

.contact-view-info {
  flex: 1;
}

.contact-view-row {
  display: flex;
  margin-bottom: 8px;
}

.contact-view-row:last-child {
  margin-bottom: 0;
}

.contact-view-label {
  width: 100px;
  color: var(--color-text-secondary);
  font-size: 14px;
  flex-shrink: 0;
}

.contact-view-value {
  color: var(--color-text-primary);
  font-size: 14px;
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
