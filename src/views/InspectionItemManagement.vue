<template>
  <div class="inspection-item-management">
    <div class="search-section">
      <div class="search-form">
        <div class="search-item">
          <label class="search-label">事项编号：</label>
          <input type="text" class="search-input" placeholder="请输入" v-model="searchForm.itemCode" />
        </div>
        <div class="search-item">
          <label class="search-label">事项名称：</label>
          <input type="text" class="search-input" placeholder="请输入" v-model="searchForm.itemName" />
        </div>
        <div class="search-item">
          <label class="search-label">事项类型：</label>
          <select class="search-select" v-model="searchForm.itemType">
            <option value="">全部</option>
            <option value="定期巡检">定期巡检</option>
            <option value="临时维修">临时维修</option>
            <option value="零星用工">零星用工</option>
          </select>
        </div>
      </div>
      <div class="search-actions">
        <button class="btn btn-add" @click="handleAdd">
          + 新增巡查事项
        </button>
        <button class="btn btn-search" @click="handleSearch">搜索</button>
      </div>
    </div>

    <div class="table-section">
      <table class="data-table">
        <thead>
          <tr>
            <th>序号</th>
            <th>事项编号</th>
            <th>事项名称</th>
            <th>事项类型</th>
            <th>检查内容</th>
            <th>检查标准</th>
            <th>操作</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="(item, index) in filteredData" :key="item.id" :class="{ 'even-row': index % 2 === 0 }">
            <td>{{ index + 1 }}</td>
            <td>{{ item.itemCode }}</td>
            <td>{{ item.itemName }}</td>
            <td>{{ item.itemType }}</td>
            <td>{{ item.checkContent }}</td>
            <td>{{ item.checkStandard }}</td>
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
        共 {{ filteredData.length }} 条记录
      </div>
      <div class="pagination-controls">
        <button class="page-btn" :disabled="currentPage === 1" @click="currentPage--">
          &lt;
        </button>
        <button
          v-for="page in totalPages"
          :key="page"
          class="page-btn"
          :class="{ active: page === currentPage }"
          @click="currentPage = page"
        >
          {{ page }}
        </button>
        <button class="page-btn" :disabled="currentPage === totalPages" @click="currentPage++">
          &gt;
        </button>
        <select class="page-select" v-model="pageSize">
          <option value="10">10 条 / 页</option>
          <option value="20">20 条 / 页</option>
          <option value="50">50 条 / 页</option>
        </select>
      </div>
    </div>

    <div v-if="isModalOpen" class="modal-overlay" @click.self="closeModal">
      <div class="modal-container">
        <div class="modal-header">
          <h3 class="modal-title">{{ isEdit ? '编辑巡查事项' : '新增巡查事项' }}</h3>
          <button class="modal-close" @click="closeModal">×</button>
        </div>
        <div class="modal-body">
          <div class="form-grid">
            <div class="form-column">
              <div class="form-item">
                <label class="form-label">
                  <span class="required">*</span> 事项编号
                </label>
                <input type="text" class="form-input" placeholder="请输入" v-model="formData.itemCode" :disabled="isEdit" />
              </div>
              <div class="form-item">
                <label class="form-label">
                  <span class="required">*</span> 事项名称
                </label>
                <input type="text" class="form-input" placeholder="请输入" v-model="formData.itemName" />
              </div>
              <div class="form-item">
                <label class="form-label">
                  <span class="required">*</span> 事项类型
                </label>
                <select class="form-input" v-model="formData.itemType">
                  <option value="">请选择</option>
                  <option value="定期巡检">定期巡检</option>
                  <option value="临时维修">临时维修</option>
                  <option value="零星用工">零星用工</option>
                </select>
              </div>
            </div>
            <div class="form-column">
              <div class="form-item">
                <label class="form-label">
                  <span class="required">*</span> 检查内容
                </label>
                <textarea class="form-textarea" placeholder="请输入检查内容" v-model="formData.checkContent" rows="3"></textarea>
              </div>
              <div class="form-item">
                <label class="form-label">
                  <span class="required">*</span> 检查标准
                </label>
                <textarea class="form-textarea" placeholder="请输入检查标准" v-model="formData.checkStandard" rows="3"></textarea>
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

    <div v-if="isViewModalOpen" class="modal-overlay" @click.self="closeViewModal">
      <div class="modal-container">
        <div class="modal-header">
          <h3 class="modal-title">查看巡查事项</h3>
          <button class="modal-close" @click="closeViewModal">×</button>
        </div>
        <div class="modal-body">
          <div class="form-grid">
            <div class="form-column">
              <div class="form-item">
                <label class="form-label">事项编号</label>
                <div class="form-value">{{ viewData.itemCode || '-' }}</div>
              </div>
              <div class="form-item">
                <label class="form-label">事项名称</label>
                <div class="form-value">{{ viewData.itemName || '-' }}</div>
              </div>
              <div class="form-item">
                <label class="form-label">事项类型</label>
                <div class="form-value">{{ viewData.itemType || '-' }}</div>
              </div>
            </div>
            <div class="form-column">
              <div class="form-item">
                <label class="form-label">检查内容</label>
                <div class="form-value">{{ viewData.checkContent || '-' }}</div>
              </div>
              <div class="form-item">
                <label class="form-label">检查标准</label>
                <div class="form-value">{{ viewData.checkStandard || '-' }}</div>
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
import { defineComponent, reactive, ref, computed } from 'vue'

export interface InspectionItem {
  id: string
  itemCode: string
  itemName: string
  itemType: string
  checkContent: string
  checkStandard: string
}

export default defineComponent({
  name: 'InspectionItemManagement',
  setup() {
    const searchForm = reactive({
      itemCode: '',
      itemName: '',
      itemType: ''
    })

    const currentPage = ref(1)
    const pageSize = ref(10)
    const isModalOpen = ref(false)
    const isViewModalOpen = ref(false)
    const isEdit = ref(false)
    const editingId = ref('')

    const formData = reactive({
      itemCode: '',
      itemName: '',
      itemType: '',
      checkContent: '',
      checkStandard: ''
    })

    const viewData = reactive({
      itemCode: '',
      itemName: '',
      itemType: '',
      checkContent: '',
      checkStandard: ''
    })

    const tableData = ref<InspectionItem[]>([
      {
        id: '1',
        itemCode: 'XC-001',
        itemName: '电梯运行检查',
        itemType: '定期巡检',
        checkContent: '检查电梯运行是否正常，有无异常声响',
        checkStandard: '电梯运行平稳，无异常声响，门开关灵活'
      },
      {
        id: '2',
        itemCode: 'XC-002',
        itemName: '消防设施检查',
        itemType: '定期巡检',
        checkContent: '检查消防设施是否完好有效',
        checkStandard: '灭火器在有效期内，压力正常'
      },
      {
        id: '3',
        itemCode: 'XC-003',
        itemName: '空调系统检查',
        itemType: '定期巡检',
        checkContent: '检查空调制冷制热功能是否正常',
        checkStandard: '空调运行正常，温度调节有效'
      },
      {
        id: '4',
        itemCode: 'XC-004',
        itemName: '照明系统检查',
        itemType: '定期巡检',
        checkContent: '检查各区域照明是否正常',
        checkStandard: '所有照明设备正常工作，无闪烁'
      }
    ])

    const originalData = [...tableData.value]

    const filteredData = computed(() => {
      let result = originalData

      if (searchForm.itemCode.trim()) {
        result = result.filter(item =>
          item.itemCode.toLowerCase().includes(searchForm.itemCode.toLowerCase().trim())
        )
      }

      if (searchForm.itemName.trim()) {
        result = result.filter(item =>
          item.itemName.toLowerCase().includes(searchForm.itemName.toLowerCase().trim())
        )
      }

      if (searchForm.itemType) {
        result = result.filter(item => item.itemType === searchForm.itemType)
      }

      return result
    })

    const totalPages = computed(() => Math.ceil(filteredData.value.length / pageSize.value))

    const handleSearch = () => {
      currentPage.value = 1
    }

    const handleAdd = () => {
      isEdit.value = false
      formData.itemCode = ''
      formData.itemName = ''
      formData.itemType = ''
      formData.checkContent = ''
      formData.checkStandard = ''
      isModalOpen.value = true
    }

    const closeModal = () => {
      isModalOpen.value = false
    }

    const handleSave = () => {
      if (!formData.itemCode.trim()) {
        alert('请填写事项编号')
        return
      }
      if (!formData.itemName.trim()) {
        alert('请填写事项名称')
        return
      }
      if (!formData.itemType) {
        alert('请选择事项类型')
        return
      }
      if (!formData.checkContent.trim()) {
        alert('请填写检查内容')
        return
      }
      if (!formData.checkStandard.trim()) {
        alert('请填写检查标准')
        return
      }

      if (isEdit.value) {
        const index = tableData.value.findIndex(p => p.id === editingId.value)
        if (index > -1) {
          tableData.value[index] = {
            id: editingId.value,
            itemCode: formData.itemCode,
            itemName: formData.itemName,
            itemType: formData.itemType,
            checkContent: formData.checkContent,
            checkStandard: formData.checkStandard
          }
        }
        const origIndex = originalData.findIndex(p => p.id === editingId.value)
        if (origIndex > -1) {
          originalData[origIndex] = { ...tableData.value[index] }
        }
      } else {
        const newItem: InspectionItem = {
          id: String(tableData.value.length + 1),
          itemCode: formData.itemCode,
          itemName: formData.itemName,
          itemType: formData.itemType,
          checkContent: formData.checkContent,
          checkStandard: formData.checkStandard
        }
        tableData.value = [newItem, ...tableData.value]
        originalData.unshift(newItem)
      }

      closeModal()
    }

    const handleView = (item: InspectionItem) => {
      viewData.itemCode = item.itemCode
      viewData.itemName = item.itemName
      viewData.itemType = item.itemType
      viewData.checkContent = item.checkContent
      viewData.checkStandard = item.checkStandard
      isViewModalOpen.value = true
    }

    const closeViewModal = () => {
      isViewModalOpen.value = false
    }

    const handleEdit = (item: InspectionItem) => {
      isEdit.value = true
      editingId.value = item.id
      formData.itemCode = item.itemCode
      formData.itemName = item.itemName
      formData.itemType = item.itemType
      formData.checkContent = item.checkContent
      formData.checkStandard = item.checkStandard
      isModalOpen.value = true
    }

    const handleDelete = (item: InspectionItem) => {
      if (!confirm('确定要删除该巡查事项吗？')) {
        return
      }
      const index = tableData.value.findIndex(p => p.id === item.id)
      const origIndex = originalData.findIndex(p => p.id === item.id)
      if (index > -1) {
        tableData.value.splice(index, 1)
      }
      if (origIndex > -1) {
        originalData.splice(origIndex, 1)
      }
    }

    return {
      searchForm,
      filteredData,
      currentPage,
      pageSize,
      totalPages,
      isModalOpen,
      isViewModalOpen,
      isEdit,
      formData,
      viewData,
      handleSearch,
      handleAdd,
      closeModal,
      handleSave,
      handleView,
      closeViewModal,
      handleEdit,
      handleDelete
    }
  }
})
</script>

<style scoped>
.inspection-item-management {
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
  width: 180px;
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
  border-color: #2196F3;
  box-shadow: 0 0 0 2px rgba(33, 150, 243, 0.1);
}

.search-select {
  width: 150px;
  padding: 8px 12px;
  border: 1px solid #e0e0e0;
  border-radius: 3px;
  font-size: 14px;
  color: #333;
  background: #fff;
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

.page-select {
  padding: 6px 12px;
  border: 1px solid #e0e0e0;
  border-radius: 3px;
  font-size: 14px;
  color: #333;
  background: #fff;
  cursor: pointer;
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
  width: 800px;
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
  grid-template-columns: 1fr 1fr;
  gap: 24px 40px;
}

.form-column {
  display: flex;
  flex-direction: column;
}

.form-item {
  display: flex;
  flex-direction: column;
  gap: 6px;
  min-height: 90px;
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
}

.form-input:focus {
  outline: none;
  border-color: #2196F3;
  box-shadow: 0 0 0 2px rgba(33, 150, 243, 0.1);
}

.form-textarea {
  padding: 8px 12px;
  border: 1px solid #e0e0e0;
  border-radius: 3px;
  font-size: 14px;
  color: #333;
  background: #fff;
  resize: vertical;
  font-family: inherit;
}

.form-textarea:focus {
  outline: none;
  border-color: #2196F3;
  box-shadow: 0 0 0 2px rgba(33, 150, 243, 0.1);
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
