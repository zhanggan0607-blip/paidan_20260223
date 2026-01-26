<template>
  <div class="project-info-management">
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
            <th>开始日期</th>
            <th>结束日期</th>
            <th>维保周期</th>
            <th>客户单位</th>
            <th>地址</th>
            <th>操作</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="(item, index) in projectData" :key="item.id" :class="{ 'even-row': index % 2 === 0 }">
            <td>{{ index + 1 }}</td>
            <td>{{ item.id }}</td>
            <td>{{ item.name }}</td>
            <td>{{ item.completionDate }}</td>
            <td>{{ item.maintenanceEndDate }}</td>
            <td>{{ item.maintenancePeriod }}</td>
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
        共 {{ projectData.length }} 条记录
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
                <input type="text" class="form-input" placeholder="请输入" v-model="formData.projectName" maxlength="200" />
              </div>
              <div class="form-item">
                <label class="form-label">
                  <span class="required">*</span> 项目编号
                </label>
                <input type="text" class="form-input" placeholder="请输入" v-model="formData.projectId" maxlength="20" />
              </div>
              <div class="form-item">
                <label class="form-label">
                  <span class="required">*</span> 开始日期
                </label>
                <input type="date" class="form-input" v-model="formData.completionDate" />
              </div>
              <div class="form-item">
                <label class="form-label">
                  <span class="required">*</span> 客户单位
                </label>
                <input type="text" class="form-input" placeholder="请输入" v-model="formData.clientUnit" maxlength="100" />
              </div>
              <div class="form-item">
                <label class="form-label">
                  <span class="required">*</span> 客户联系人
                </label>
                <input type="text" class="form-input" placeholder="请输入" v-model="formData.clientContact" maxlength="50" />
              </div>
              <div class="form-item">
                <label class="form-label">客户联系人职位</label>
                <input type="text" class="form-input" placeholder="请输入" v-model="formData.clientContactPosition" maxlength="20" />
              </div>
            </div>
            <div class="form-column">
              <div class="form-item">
                <label class="form-label">
                  <span class="required">*</span> 维保周期
                </label>
                <select class="form-input" v-model="formData.maintenancePeriod">
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
                <div class="input-with-icon">
                  <input 
                    type="text" 
                    class="form-input" 
                    v-model="formData.projectAbbr" 
                    @input="checkAbbrDuplicate(formData.projectAbbr)"
                  />
                  <span v-if="isAbbrDuplicate" class="icon-warning">!</span>
                </div>
                <span v-if="isAbbrDuplicate" class="form-error">简称重复</span>
              </div>
              <div class="form-item">
                <label class="form-label">
                  <span class="required">*</span> 结束日期
                </label>
                <input type="date" class="form-input" v-model="formData.maintenanceEndDate" />
                <span class="form-hint">截止日期指的是当日 23:59:59</span>
              </div>
              <div class="form-item">
                <label class="form-label">
                  <span class="required">*</span> 客户地址
                </label>
                <input type="text" class="form-input" placeholder="请输入" v-model="formData.clientAddress" maxlength="200" />
              </div>
              <div class="form-item">
                <label class="form-label">
                  <span class="required">*</span> 客户联系方式
                </label>
                <input type="text" class="form-input" placeholder="请输入" v-model="formData.clientContactInfo" maxlength="50" />
              </div>
            </div>
          </div>
        </div>
        <div class="modal-footer">
          <button class="btn btn-cancel" @click="closeModal">取消</button>
          <button class="btn btn-save" @click="handleSave">保存</button>
        </div>
      </div>
    </div>

    <div v-if="saveSuccess" class="save-success-toast">
      ✓ 保存成功
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
                <div class="form-value">{{ viewData.name || '-' }}</div>
              </div>
              <div class="form-item">
                <label class="form-label">项目编号</label>
                <div class="form-value">{{ viewData.id || '-' }}</div>
              </div>
              <div class="form-item">
                <label class="form-label">开始日期</label>
                <div class="form-value">{{ viewData.completionDate || '-' }}</div>
              </div>
              <div class="form-item">
                <label class="form-label">客户单位</label>
                <div class="form-value">{{ viewData.clientName || '-' }}</div>
              </div>
              <div class="form-item">
                <label class="form-label">客户联系人</label>
                <div class="form-value">{{ viewData.clientContact || '-' }}</div>
              </div>
              <div class="form-item">
                <label class="form-label">客户联系人职位</label>
                <div class="form-value">{{ viewData.clientContactPosition || '-' }}</div>
              </div>
            </div>
            <div class="form-column">
              <div class="form-item">
                <label class="form-label">维保周期</label>
                <div class="form-value">{{ viewData.maintenancePeriod || '-' }}</div>
              </div>
              <div class="form-item">
                <label class="form-label">项目目前简称</label>
                <div class="form-value">{{ viewData.projectAbbr || '-' }}</div>
              </div>
              <div class="form-item">
                <label class="form-label">结束日期</label>
                <div class="form-value">{{ viewData.maintenanceEndDate || '-' }}</div>
              </div>
              <div class="form-item">
                <label class="form-label">客户地址</label>
                <div class="form-value">{{ viewData.address || '-' }}</div>
              </div>
              <div class="form-item">
                <label class="form-label">客户联系方式</label>
                <div class="form-value">{{ viewData.clientContactInfo || '-' }}</div>
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
                <input type="text" class="form-input" placeholder="请输入" v-model="editData.name" maxlength="200" />
              </div>
              <div class="form-item">
                <label class="form-label">
                  <span class="required">*</span> 项目编号
                </label>
                <input type="text" class="form-input" placeholder="请输入" v-model="editData.id" maxlength="20" />
              </div>
              <div class="form-item">
                <label class="form-label">
                  <span class="required">*</span> 开始日期
                </label>
                <input type="date" class="form-input" v-model="editData.completionDate" />
              </div>
              <div class="form-item">
                <label class="form-label">
                  <span class="required">*</span> 客户单位
                </label>
                <input type="text" class="form-input" placeholder="请输入" v-model="editData.clientName" maxlength="100" />
              </div>
              <div class="form-item">
                <label class="form-label">
                  <span class="required">*</span> 客户联系人
                </label>
                <input type="text" class="form-input" placeholder="请输入" v-model="editData.clientContact" maxlength="50" />
              </div>
              <div class="form-item">
                <label class="form-label">客户联系人职位</label>
                <input type="text" class="form-input" placeholder="请输入" v-model="editData.clientContactPosition" maxlength="20" />
              </div>
            </div>
            <div class="form-column">
              <div class="form-item">
                <label class="form-label">
                  <span class="required">*</span> 维保周期
                </label>
                <select class="form-input" v-model="editData.maintenancePeriod">
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
                  <span class="required">*</span> 结束日期
                </label>
                <input type="date" class="form-input" v-model="editData.maintenanceEndDate" />
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
                <input type="text" class="form-input" placeholder="请输入" v-model="editData.clientContactInfo" maxlength="50" />
              </div>
            </div>
          </div>
        </div>
        <div class="modal-footer">
          <button class="btn btn-cancel" @click="closeEditModal">取消</button>
          <button class="btn btn-save" @click="handleUpdate">保存</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script lang="ts">
import { defineComponent, reactive, ref, computed, watch } from 'vue'

export interface ProjectInfo {
  id: string
  name: string
  completionDate: string
  maintenanceEndDate: string
  maintenancePeriod: string
  clientName: string
  address: string
  projectAbbr?: string
  clientContact?: string
  clientContactPosition?: string
  clientContactInfo?: string
}

export default defineComponent({
  name: 'ProjectInfoManagement',
  setup() {
    const searchForm = reactive({
      projectName: '',
      clientName: ''
    })

    const currentPage = ref(1)
    const pageSize = ref(10)
    const jumpPage = ref(1)
    const isModalOpen = ref(false)
    const isAbbrDuplicate = ref(false)
    const saveSuccess = ref(false)
    const isViewModalOpen = ref(false)
    const isEditModalOpen = ref(false)
    const editingIndex = ref(-1)
    const viewData = reactive({
      id: '',
      name: '',
      completionDate: '',
      maintenanceEndDate: '',
      maintenancePeriod: '',
      clientName: '',
      address: '',
      projectAbbr: '',
      clientContact: '',
      clientContactPosition: '',
      clientContactInfo: ''
    })
    const editData = reactive({
      id: '',
      name: '',
      completionDate: '',
      maintenanceEndDate: '',
      maintenancePeriod: '',
      clientName: '',
      address: '',
      clientContact: '',
      clientContactPosition: '',
      clientContactInfo: ''
    })

    const formData = reactive({
      projectName: '',
      projectId: '',
      completionDate: '',
      clientUnit: '',
      clientContact: '',
      clientContactPosition: '',
      maintenancePeriod: '',
      projectAbbr: 'CXDP',
      maintenanceEndDate: '',
      clientAddress: '',
      clientContactInfo: ''
    })

    const projectData = ref<ProjectInfo[]>([
      {
        id: 'PRJ-2025-001',
        name: '上海中心大厦维保项目',
        completionDate: '2024-12-31',
        maintenanceEndDate: '2026-12-31',
        maintenancePeriod: '每半年',
        clientName: '上海城投（集团）有限公司',
        address: '上海市浦东新区陆家嘴银城中路501号'
      },
      {
        id: 'PRJ-2025-002',
        name: '环球金融中心维保项目',
        completionDate: '2023-06-30',
        maintenanceEndDate: '2025-06-30',
        maintenancePeriod: '每半年',
        clientName: '上海建工集团股份有限公司',
        address: '上海市浦东新区世纪大道100号'
      },
      {
        id: 'PRJ-2025-003',
        name: '金茂大厦维保项目',
        completionDate: '2024-03-15',
        maintenanceEndDate: '2025-03-15',
        maintenancePeriod: '每季度',
        clientName: '中国金茂控股集团有限公司',
        address: '上海市浦东新区世纪大道88号'
      },
      {
        id: 'PRJ-2025-004',
        name: '东方明珠塔维保项目',
        completionDate: '2024-09-01',
        maintenanceEndDate: '2025-03-01',
        maintenancePeriod: '每月',
        clientName: '上海文化广播影视集团有限公司',
        address: '上海市浦东新区世纪大道1号'
      }
    ])

    const originalData = ref<ProjectInfo[]>([...projectData.value])

    const totalPages = computed(() => Math.ceil(projectData.value.length / pageSize.value))

    const handleSearch = () => {
      const keyword = searchForm.projectName.toLowerCase().trim()
      const clientKeyword = searchForm.clientName.toLowerCase().trim()

      const filtered = originalData.value.filter(item => {
        const nameMatch = !keyword || item.name.toLowerCase().includes(keyword)
        const clientMatch = !clientKeyword || item.clientName.toLowerCase().includes(clientKeyword)
        return nameMatch && clientMatch
      })

      projectData.value = filtered
      currentPage.value = 1
    }

    watch(
      () => [searchForm.projectName, searchForm.clientName],
      () => {
        handleSearch()
      }
    )

    const checkFormValid = (): boolean => {
      if (!formData.projectName?.trim()) {
        alert('请填写项目名称')
        return false
      }
      if (!formData.projectId?.trim()) {
        alert('请填写项目编号')
        return false
      }
      if (!formData.completionDate) {
        alert('请填写开始日期')
        return false
      }
      if (!formData.maintenanceEndDate) {
        alert('请填写结束日期')
        return false
      }
      if (!formData.maintenancePeriod?.trim()) {
        alert('请填写维保周期')
        return false
      }
      if (!formData.clientUnit?.trim()) {
        alert('请填写客户单位')
        return false
      }
      if (!formData.clientAddress?.trim()) {
        alert('请填写客户地址')
        return false
      }
      if (isAbbrDuplicate.value) {
        alert('项目简称重复，请修改后保存')
        return false
      }
      return true
    }

    const checkAbbrDuplicate = (abbr: string) => {
      if (!abbr) {
        isAbbrDuplicate.value = false
        return
      }
      const existingAbbrs = projectData.value.map(item => item.name).map(name => {
        return name.substring(0, Math.min(4, name.length)).toUpperCase()
      })
      isAbbrDuplicate.value = existingAbbrs.includes(abbr.toUpperCase())
    }

    const openModal = () => {
      resetForm()
      isModalOpen.value = true
    }

    const closeModal = () => {
      isModalOpen.value = false
    }

    const resetForm = () => {
      formData.projectName = ''
      formData.projectId = ''
      formData.completionDate = ''
      formData.clientUnit = ''
      formData.clientContact = ''
      formData.clientContactPosition = ''
      formData.maintenancePeriod = ''
      formData.projectAbbr = 'CXDP'
      formData.maintenanceEndDate = ''
      formData.clientAddress = ''
      formData.clientContactInfo = ''
      isAbbrDuplicate.value = false
    }

    const handleSave = () => {
      if (!checkFormValid()) {
        return
      }

      const newItem: ProjectInfo = {
        id: formData.projectId,
        name: formData.projectName,
        completionDate: formData.completionDate,
        maintenanceEndDate: formData.maintenanceEndDate,
        maintenancePeriod: formData.maintenancePeriod,
        clientName: formData.clientUnit,
        address: formData.clientAddress
      }

      projectData.value = [newItem, ...projectData.value]
      originalData.value = [newItem, ...originalData.value]

      closeModal()
      resetForm()

      saveSuccess.value = true
      setTimeout(() => {
        saveSuccess.value = false
      }, 2000)
    }

    const handleView = (item: ProjectInfo) => {
      viewData.id = item.id
      viewData.name = item.name
      viewData.completionDate = item.completionDate
      viewData.maintenanceEndDate = item.maintenanceEndDate
      viewData.maintenancePeriod = item.maintenancePeriod
      viewData.clientName = item.clientName
      viewData.address = item.address
      viewData.projectAbbr = ''
      viewData.clientContact = ''
      viewData.clientContactPosition = ''
      viewData.clientContactInfo = ''
      isViewModalOpen.value = true
    }

    const handleEdit = (item: ProjectInfo) => {
      const index = projectData.value.findIndex(p => p.id === item.id)
      if (index > -1) {
        editingIndex.value = index
        editData.id = item.id
        editData.name = item.name
        editData.completionDate = item.completionDate
        editData.maintenanceEndDate = item.maintenanceEndDate
        editData.maintenancePeriod = item.maintenancePeriod
        editData.clientName = item.clientName
        editData.address = item.address
        editData.clientContact = ''
        editData.clientContactPosition = ''
        editData.clientContactInfo = ''
        isEditModalOpen.value = true
      }
    }

    const closeViewModal = () => {
      isViewModalOpen.value = false
    }

    const closeEditModal = () => {
      isEditModalOpen.value = false
      editingIndex.value = -1
    }

    const checkEditFormValid = (): boolean => {
      if (!editData.name?.trim()) {
        alert('请填写项目名称')
        return false
      }
      if (!editData.id?.trim()) {
        alert('请填写项目编号')
        return false
      }
      if (!editData.completionDate) {
        alert('请填写开始日期')
        return false
      }
      if (!editData.maintenanceEndDate) {
        alert('请填写结束日期')
        return false
      }
      if (!editData.maintenancePeriod?.trim()) {
        alert('请填写维保周期')
        return false
      }
      if (!editData.clientName?.trim()) {
        alert('请填写客户单位')
        return false
      }
      if (!editData.address?.trim()) {
        alert('请填写客户地址')
        return false
      }
      return true
    }

    const handleUpdate = () => {
      if (!checkEditFormValid()) {
        return
      }

      if (editingIndex.value > -1) {
        projectData.value[editingIndex.value] = {
          id: editData.id,
          name: editData.name,
          completionDate: editData.completionDate,
          maintenanceEndDate: editData.maintenanceEndDate,
          maintenancePeriod: editData.maintenancePeriod,
          clientName: editData.clientName,
          address: editData.address
        }
        originalData.value[editingIndex.value] = { ...projectData.value[editingIndex.value] }
      }

      closeEditModal()
      saveSuccess.value = true
      setTimeout(() => {
        saveSuccess.value = false
      }, 2000)
    }

    const handleDelete = (item: ProjectInfo) => {
      if (!confirm('确定要删除该项目吗？')) {
        return
      }
      const index = projectData.value.findIndex(p => p.id === item.id)
      const originalIndex = originalData.value.findIndex(p => p.id === item.id)
      if (index > -1) {
        projectData.value.splice(index, 1)
      }
      if (originalIndex > -1) {
        originalData.value.splice(originalIndex, 1)
      }
    }

    const handleJump = () => {
      const page = parseInt(jumpPage.value)
      if (page >= 1 && page <= totalPages.value) {
        currentPage.value = page
      }
    }

    return {
      searchForm,
      projectData,
      currentPage,
      pageSize,
      totalPages,
      jumpPage,
      isModalOpen,
      isAbbrDuplicate,
      saveSuccess,
      isViewModalOpen,
      isEditModalOpen,
      viewData,
      editData,
      formData,
      openModal,
      closeModal,
      handleSave,
      handleView,
      handleEdit,
      handleDelete,
      handleJump,
      checkAbbrDuplicate,
      closeViewModal,
      closeEditModal,
      handleUpdate
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
  gap: 10px;
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

.btn-add {
  background: #2E7D32;
  color: #fff;
}

.btn-add:hover {
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
  gap: 16px;
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
  align-items: center;
  gap: 8px;
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

.form-error {
  font-size: 12px;
  color: #D32F2F;
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

.input-with-icon {
  position: relative;
}

.input-with-icon .form-input {
  padding-right: 32px;
}

.icon-warning {
  position: absolute;
  right: 12px;
  top: 50%;
  transform: translateY(-50%);
  width: 20px;
  height: 20px;
  border-radius: 50%;
  background: #FFA000;
  color: #fff;
  font-size: 12px;
  font-weight: 600;
  display: flex;
  align-items: center;
  justify-content: center;
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

.save-success-toast {
  position: fixed;
  top: 20px;
  right: 20px;
  padding: 14px 20px;
  background: #43a047;
  color: #fff;
  border-radius: 3px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
  animation: slideIn 0.25s ease-out;
  z-index: 1001;
}

@keyframes slideIn {
  from {
    transform: translateX(100%);
    opacity: 0;
  }
  to {
    transform: translateX(0);
    opacity: 1;
  }
}
</style>
