<template>
  <div class="expiry-page">
    <div class="content-area">
      <div class="filters">
        <label>项目名称
          <input type="text" placeholder="请输入" v-model="filters.projectName" />
        </label>
        <label>客户名称
          <input type="text" placeholder="请输入" v-model="filters.customerName" />
        </label>
        <label>工单类型
          <select v-model="filters.type">
            <option value="">请选择工单类型</option>
            <option>临时维修工单</option>
            <option>定期巡检工单</option>
            <option>零星用工工单</option>
          </select>
        </label>
        <button class="btn btn-search" @click="search">搜索</button>
      </div>
      <div class="table-section">
        <table class="data-table">
          <thead>
            <tr>
              <th>序号</th>
              <th>工单编号</th>
              <th>项目编号</th>
              <th>项目名称</th>
              <th>工单类型</th>
              <th>开始日期</th>
              <th>提醒类型</th>
              <th>执行人员</th>
              <th>操作</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="(row, idx) in rows" :key="row.id">
              <td>{{ idx + 1 }}</td>
              <td>{{ row.id }}</td>
              <td>{{ row.projectId }}</td>
              <td>{{ row.projectName }}</td>
              <td>{{ row.type }}</td>
              <td>{{ row.planDate }}</td>
              <td>临期</td>
              <td>刘启智</td>
              <td class="action-cell">
                <a href="#" class="action-link action-view" @click="viewDetail(row)">查看</a>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
      <div class="pagination-area">
        <button class="page-btn" :disabled="true">上一页</button>
        <span class="page-num active">1</span>
        <span class="page-num">2</span>
        <span class="page-num">3</span>
        <span class="page-num">4</span>
        <span class="page-num">5</span>
        <span class="page-num">6</span>
        <span class="page-num">7</span>
        <span class="page-num">8</span>
        <span class="page-num">9</span>
        <button class="page-btn" :disabled="true">下一页</button>
        <select class="page-select" v-model="pageSize">
          <option value="10">10 条 / 页</option>
          <option value="20">20 条 / 页</option>
          <option value="50">50 条 / 页</option>
        </select>
        <div class="page-jump">
          <span>跳至</span>
          <input type="number" class="page-input" v-model.number="jumpPage" min="1" max="9" />
          <span>页</span>
        </div>
      </div>
    </div>

    <div v-if="isViewModalOpen" class="modal-overlay" @click.self="closeViewModal">
      <div class="modal-container">
        <div class="modal-header">
          <h3 class="modal-title">查看工单详情</h3>
          <button class="modal-close" @click="closeViewModal">×</button>
        </div>
        <div class="modal-body">
          <div class="form-grid">
            <div class="form-column">
              <div class="form-item">
                <label class="form-label">工单编号</label>
                <div class="form-value">{{ viewData.workOrderNo || '-' }}</div>
              </div>
              <div class="form-item">
                <label class="form-label">项目编号</label>
                <div class="form-value">{{ viewData.projectId || '-' }}</div>
              </div>
              <div class="form-item">
                <label class="form-label">项目名称</label>
                <div class="form-value">{{ viewData.projectName || '-' }}</div>
              </div>
              <div class="form-item">
                <label class="form-label">执行人员</label>
                <div class="form-value">{{ viewData.executor || '-' }}</div>
              </div>
            </div>
            <div class="form-column">
              <div class="form-item">
                <label class="form-label">工单类型</label>
                <div class="form-value">{{ viewData.workOrderType || '-' }}</div>
              </div>
              <div class="form-item">
                <label class="form-label">开始日期</label>
                <div class="form-value">{{ viewData.planStartDate || '-' }}</div>
              </div>
              <div class="form-item">
                <label class="form-label">提醒类型</label>
                <div class="form-value alert-type">临期</div>
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
import { defineComponent, ref, reactive } from 'vue'

interface Row {
  id: string
  projectId: string
  projectName: string
  type: string
  planDate: string
}

export default defineComponent({
  name: 'NearExpiryReminders',
  setup() {
    const filters = ref({ projectName: '', customerName: '', type: '' as string })
    const rows = ref<Row[]>([
      { id: 'WO-001', projectId: 'PRJ-2025-001', projectName: '上海中心大厦维保项目', type: '临时维修工单', planDate: '2026-01-10' },
      { id: 'WO-002', projectId: 'PRJ-2025-002', projectName: '环球金融中心维保项目', type: '定期巡检工单', planDate: '2026-02-15' },
      { id: 'WO-003', projectId: 'PRJ-2025-003', projectName: '金茂大厦维保项目', type: '零星用工工单', planDate: '2026-03-01' },
      { id: 'WO-004', projectId: 'PRJ-2025-004', projectName: '东方明珠塔维保项目', type: '临时维修工单', planDate: '2026-04-08' }
    ])
    const pageSize = ref(10)
    const jumpPage = ref(1)
    const isViewModalOpen = ref(false)
    const viewData = reactive({
      workOrderNo: '',
      projectId: '',
      projectName: '',
      workOrderType: '',
      planStartDate: '',
      executor: ''
    })

    const search = () => {
    }

    const viewDetail = (row: Row) => {
      viewData.workOrderNo = row.id
      viewData.projectId = row.projectId
      viewData.projectName = row.projectName
      viewData.workOrderType = row.type
      viewData.planStartDate = row.planDate
      viewData.executor = '刘启智'
      isViewModalOpen.value = true
    }

    const closeViewModal = () => {
      isViewModalOpen.value = false
    }

    return { filters, rows, pageSize, jumpPage, search, viewDetail, closeViewModal, isViewModalOpen, viewData }
  }
})
</script>

<style scoped>
.expiry-page {
  padding: 0;
}

.content-area {
  padding: 0;
  display: block;
}

.filters {
  display: flex;
  flex-wrap: nowrap;
  gap: 16px;
  align-items: center;
  margin-bottom: 16px;
  overflow-x: auto;
  white-space: nowrap;
  min-width: max-content;
}

.filters label {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
  color: #333;
}

.filters input,
.filters select {
  height: 36px;
  padding: 6px 12px;
  border: 1px solid #D9D9D9;
  border-radius: 4px;
  font-size: 14px;
  min-width: 180px;
}

.btn-search {
  background: #1890FF;
  color: #fff;
  height: 36px;
  border: none;
  border-radius: 4px;
  padding: 0 20px;
  cursor: pointer;
  font-size: 14px;
}

.btn-search:hover {
  background: #40a9ff;
}

.table-section {
  margin-top: 0;
}

.data-table {
  width: 100%;
  border-collapse: collapse;
  background: #fff;
}

.data-table thead {
  background: #E0E0E0;
}

.data-table th {
  padding: 12px 16px;
  text-align: left;
  font-weight: 600;
  color: #333;
  font-size: 14px;
  border: 1px solid #e0e0e0;
}

.data-table td {
  padding: 12px 16px;
  border: 1px solid #e0e0e0;
  font-size: 14px;
  color: #333;
}

.data-table tbody tr {
  background: #fff;
}

.data-table tbody tr:hover {
  background: #f5f5f5;
}

.btn-success {
  background: #28a745;
  color: #fff;
  border: none;
  padding: 6px 16px;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
}

.btn-success:hover {
  background: #218838;
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

.pagination-area {
  display: flex;
  flex-wrap: nowrap;
  align-items: center;
  gap: 8px;
  margin-top: 16px;
  padding: 16px 0;
  overflow-x: auto;
  white-space: nowrap;
  min-width: max-content;
}

.page-btn {
  border: 1px solid #e0e0e0;
  background: #fff;
  border-radius: 4px;
  padding: 6px 12px;
  cursor: pointer;
  font-size: 14px;
  color: #666;
}

.page-btn:hover:not(:disabled) {
  background: #f5f5f5;
}

.page-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.page-num {
  padding: 6px 12px;
  border: 1px solid #e0e0e0;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
  color: #666;
  background: #fff;
}

.page-num:hover {
  background: #f5f5f5;
}

.page-num.active {
  background: #1890FF;
  color: #fff;
  border-color: #1890FF;
}

.page-select {
  margin-left: 12px;
  height: 32px;
  padding: 4px 8px;
  border: 1px solid #e0e0e0;
  border-radius: 4px;
  font-size: 14px;
}

.page-jump {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  margin-left: 12px;
  font-size: 14px;
  color: #666;
}

.page-input {
  width: 60px;
  height: 32px;
  border: 1px solid #e0e0e0;
  border-radius: 4px;
  padding: 0 8px;
  font-size: 14px;
  text-align: center;
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
  min-height: 60px;
  padding: 4px 0;
}

.form-label {
  font-size: 14px;
  font-weight: 500;
  color: #424242;
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

.form-value.alert-type {
  color: #F5222D;
  font-weight: 500;
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

</style>
