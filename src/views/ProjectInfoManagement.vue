<template>
  <div class="project-info-management">
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
              for="search_projectName"
              class="search-label"
            >项目名称：</label>
            <SearchInput
              v-model="searchForm.projectName"
              input-id="search_projectName"
              field-key="ProjectInfoManagement_projectName"
              placeholder="请输入项目名称"
              @input="handleSearch"
            />
          </div>
          <div class="search-item">
            <label
              for="search_clientName"
              class="search-label"
            >客户名称：</label>
            <SearchInput
              v-model="searchForm.clientName"
              input-id="search_clientName"
              field-key="ProjectInfoManagement_clientName"
              placeholder="请输入客户名称"
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
            <th>维保频率</th>
            <th>客户单位</th>
            <th>运维人员</th>
            <th>操作</th>
          </tr>
        </thead>
        <tbody>
          <tr
            v-for="(item, index) in projectData"
            :key="item.id"
            :class="{ 'even-row': index % 2 === 0 }"
          >
            <td>{{ startIndex + index + 1 }}</td>
            <td>{{ item.project_id }}</td>
            <td>{{ item.project_name }}</td>
            <td>{{ formatDate(item.completion_date ?? '') }}</td>
            <td>{{ formatDate(item.maintenance_end_date ?? '') }}</td>
            <td>{{ item.maintenance_period }}</td>
            <td>{{ item.client_name }}</td>
            <td>{{ item.project_manager || '-' }}</td>
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
      <div class="modal-container">
        <div class="modal-header">
          <h3 class="modal-title">
            添加项目信息
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
                  for="projectName"
                  class="form-label"
                > <span class="required">*</span> 项目名称 </label>
                <input
                  id="projectName"
                  v-model="formData.project_name"
                  name="projectName"
                  type="text"
                  class="form-input"
                  placeholder="请输入"
                  maxlength="200"
                >
              </div>
              <div class="form-item">
                <label
                  for="projectStartDate"
                  class="form-label"
                > <span class="required">*</span> 项目开始日期 </label>
                <input
                  id="projectStartDate"
                  v-model="formData.completion_date"
                  name="projectStartDate"
                  type="date"
                  class="form-input"
                >
              </div>
              <div class="form-item">
                <label
                  for="maintenancePeriod"
                  class="form-label"
                > <span class="required">*</span> 维保频率 </label>
                <select
                  id="maintenancePeriod"
                  v-model="formData.maintenance_period"
                  name="maintenancePeriod"
                  class="form-input"
                >
                  <option value="">
                    请选择
                  </option>
                  <option value="每天">
                    每天
                  </option>
                  <option value="每周">
                    每周
                  </option>
                  <option value="每月">
                    每月
                  </option>
                  <option value="每季度">
                    每季度
                  </option>
                  <option value="每半年">
                    每半年
                  </option>
                </select>
              </div>
              <div class="form-item">
                <label
                  for="clientName"
                  class="form-label"
                > <span class="required">*</span> 客户单位 </label>
                <div class="client-select-wrapper">
                  <div class="client-input-row">
                    <select
                      id="clientName"
                      v-model="formData.client_source"
                      name="clientName"
                      class="form-input client-select"
                      @change="handleClientSourceChange('formData')"
                    >
                      <option value="">
                        选择已有客户
                      </option>
                      <option
                        v-for="customer in customerList"
                        :key="customer.id"
                        :value="customer.name"
                      >
                        {{ customer.name }}
                      </option>
                    </select>
                    <span class="client-or">或</span>
                    <input
                      id="clientNameManual"
                      v-model="formData.client_name_manual"
                      name="clientNameManual"
                      type="text"
                      class="form-input client-input"
                      placeholder="手动输入客户单位"
                      maxlength="100"
                      @input="handleClientManualInput('formData')"
                    >
                  </div>
                </div>
              </div>
              <div class="form-item">
                <label
                  for="clientContact"
                  class="form-label"
                >客户联系人</label>
                <div class="client-select-wrapper">
                  <div class="client-input-row">
                    <select
                      id="clientContact"
                      v-model="formData.client_contact_id"
                      name="clientContact"
                      class="form-input client-select"
                      :disabled="!formData.client_source"
                      @change="handleContactChange('formData')"
                    >
                      <option value="">
                        选择已有联系人
                      </option>
                      <option
                        v-for="contact in availableContacts"
                        :key="contact.id"
                        :value="contact.id"
                      >
                        {{ contact.contact_person }}{{ contact.phone ? ` (${contact.phone})` : ''
                        }}{{ contact.contact_position ? ` - ${contact.contact_position}` : '' }}
                      </option>
                    </select>
                    <span class="client-or">或</span>
                    <input
                      id="clientContactManual"
                      v-model="formData.client_contact_manual"
                      name="clientContactManual"
                      type="text"
                      class="form-input client-input"
                      placeholder="手动输入联系人"
                      maxlength="50"
                      :disabled="!formData.client_source && !formData.client_name_manual"
                      @input="handleContactManualInput('formData')"
                    >
                  </div>
                </div>
                <span
                  v-if="!formData.client_source && !formData.client_name_manual"
                  class="form-hint"
                >请先选择或输入客户单位</span>
              </div>
              <div class="form-item">
                <label
                  for="clientAddress"
                  class="form-label"
                > <span class="required">*</span> 客户地址 </label>
                <input
                  id="clientAddress"
                  v-model="formData.address"
                  name="clientAddress"
                  type="text"
                  class="form-input"
                  placeholder="请输入客户地址"
                  maxlength="200"
                >
              </div>
            </div>
            <div class="form-column">
              <div class="form-item">
                <label
                  for="projectId"
                  class="form-label"
                > <span class="required">*</span> 项目编号 </label>
                <input
                  id="projectId"
                  v-model="formData.project_id"
                  name="projectId"
                  type="text"
                  class="form-input"
                  placeholder="请输入"
                  maxlength="50"
                >
              </div>
              <div class="form-item">
                <label
                  for="projectAbbr"
                  class="form-label"
                >项目简称</label>
                <input
                  id="projectAbbr"
                  v-model="formData.project_abbr"
                  name="projectAbbr"
                  type="text"
                  class="form-input"
                  placeholder="请输入项目简称"
                  maxlength="50"
                >
              </div>
              <div class="form-item">
                <label
                  for="projectEndDate"
                  class="form-label"
                > <span class="required">*</span> 项目结束日期 </label>
                <input
                  id="projectEndDate"
                  v-model="formData.maintenance_end_date"
                  name="projectEndDate"
                  type="date"
                  class="form-input"
                >
                <span class="form-hint">截止日期指的是当日 23:59:59</span>
              </div>
              <div class="form-item">
                <label
                  for="maintenancePersonnel"
                  class="form-label"
                > <span class="required">*</span> 运维人员 </label>
                <select
                  id="maintenancePersonnel"
                  v-model="formData.project_manager"
                  name="maintenancePersonnel"
                  class="form-input"
                >
                  <option value="">
                    请选择
                  </option>
                  <option
                    v-for="person in personnelList"
                    :key="person"
                    :value="person"
                  >
                    {{ person }}
                  </option>
                </select>
              </div>
              <div class="form-item">
                <label
                  for="clientContactInfo"
                  class="form-label"
                >客户联系方式</label>
                <input
                  id="clientContactInfo"
                  v-model="formData.client_contact_info"
                  name="clientContactInfo"
                  type="text"
                  class="form-input"
                  placeholder="请输入客户联系方式"
                  maxlength="50"
                >
              </div>
              <div class="form-item">
                <label
                  for="clientContactPosition"
                  class="form-label"
                >客户联系人职位</label>
                <input
                  id="clientContactPosition"
                  v-model="formData.client_contact_position"
                  name="clientContactPosition"
                  type="text"
                  class="form-input"
                  placeholder="请输入客户联系人职位"
                  maxlength="20"
                >
              </div>
            </div>
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
      <div class="modal-container">
        <div class="modal-header">
          <h3 class="modal-title">
            查看项目信息
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
                <span class="form-label">项目名称</span>
                <div class="form-value">
                  {{ viewData.project_name || '-' }}
                </div>
              </div>
              <div class="form-item">
                <span class="form-label">项目开始日期</span>
                <div class="form-value">
                  {{ formatDate(viewData.completion_date) || '-' }}
                </div>
              </div>
              <div class="form-item">
                <span class="form-label">维保频率</span>
                <div class="form-value">
                  {{ viewData.maintenance_period || '-' }}
                </div>
              </div>
              <div class="form-item">
                <span class="form-label">客户单位</span>
                <div class="form-value">
                  {{ viewData.client_name || '-' }}
                </div>
              </div>
              <div class="form-item">
                <span class="form-label">运维人员</span>
                <div class="form-value">
                  {{ viewData.project_manager || '-' }}
                </div>
              </div>
              <div class="form-item">
                <span class="form-label">客户地址</span>
                <div class="form-value">
                  {{ viewData.address || '-' }}
                </div>
              </div>
            </div>
            <div class="form-column">
              <div class="form-item">
                <span class="form-label">项目编号</span>
                <div class="form-value">
                  {{ viewData.project_id || '-' }}
                </div>
              </div>
              <div class="form-item">
                <span class="form-label">项目简称</span>
                <div class="form-value">
                  {{ viewData.project_abbr || '-' }}
                </div>
              </div>
              <div class="form-item">
                <span class="form-label">项目结束日期</span>
                <div class="form-value">
                  {{ formatDate(viewData.maintenance_end_date) || '-' }}
                </div>
              </div>
              <div class="form-item">
                <span class="form-label">客户联系人</span>
                <div class="form-value">
                  {{ viewData.client_contact || '-' }}
                </div>
              </div>
              <div class="form-item">
                <span class="form-label">客户联系方式</span>
                <div class="form-value">
                  {{ viewData.client_contact_info || '-' }}
                </div>
              </div>
              <div class="form-item">
                <span class="form-label">客户联系人职位</span>
                <div class="form-value">
                  {{ viewData.client_contact_position || '-' }}
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

    <div
      v-if="isEditModalOpen"
      class="modal-overlay"
      @click.self="closeEditModal"
    >
      <div class="modal-container">
        <div class="modal-header">
          <h3 class="modal-title">
            编辑项目信息
          </h3>
          <button
            class="modal-close"
            @click="closeEditModal"
          >
            ×
          </button>
        </div>
        <div class="modal-body">
          <div class="form-grid">
            <div class="form-column">
              <div class="form-item">
                <label
                  for="projectName"
                  class="form-label"
                > <span class="required">*</span> 项目名称 </label>
                <input
                  id="projectName"
                  v-model="editData.project_name"
                  name="projectName"
                  type="text"
                  class="form-input"
                  placeholder="请输入"
                  maxlength="200"
                >
              </div>
              <div class="form-item">
                <label
                  for="projectStartDate"
                  class="form-label"
                > <span class="required">*</span> 项目开始日期 </label>
                <input
                  id="projectStartDate"
                  v-model="editData.completion_date"
                  name="projectStartDate"
                  type="date"
                  class="form-input"
                >
              </div>
              <div class="form-item">
                <label
                  for="maintenancePeriod"
                  class="form-label"
                > <span class="required">*</span> 维保频率 </label>
                <select
                  id="maintenancePeriod"
                  v-model="editData.maintenance_period"
                  name="maintenancePeriod"
                  class="form-input"
                >
                  <option value="">
                    请选择
                  </option>
                  <option value="每天">
                    每天
                  </option>
                  <option value="每周">
                    每周
                  </option>
                  <option value="每月">
                    每月
                  </option>
                  <option value="每季度">
                    每季度
                  </option>
                  <option value="每半年">
                    每半年
                  </option>
                </select>
              </div>
              <div class="form-item">
                <label
                  for="clientName"
                  class="form-label"
                > <span class="required">*</span> 客户单位 </label>
                <div class="client-select-wrapper">
                  <div class="client-input-row">
                    <select
                      id="clientName"
                      v-model="editData.client_source"
                      name="clientName"
                      class="form-input client-select"
                      @change="handleClientSourceChange('editData')"
                    >
                      <option value="">
                        选择已有客户
                      </option>
                      <option
                        v-for="customer in customerList"
                        :key="customer.id"
                        :value="customer.name"
                      >
                        {{ customer.name }}
                      </option>
                    </select>
                    <span class="client-or">或</span>
                    <input
                      id="editClientNameManual"
                      v-model="editData.client_name_manual"
                      name="editClientNameManual"
                      type="text"
                      class="form-input client-input"
                      placeholder="手动输入客户单位"
                      maxlength="100"
                      @input="handleClientManualInput('editData')"
                    >
                  </div>
                </div>
              </div>
              <div class="form-item">
                <label
                  for="clientContact"
                  class="form-label"
                >客户联系人</label>
                <div class="client-select-wrapper">
                  <div class="client-input-row">
                    <select
                      id="clientContact"
                      v-model="editData.client_contact_id"
                      name="clientContact"
                      class="form-input client-select"
                      :disabled="!editData.client_source"
                      @change="handleContactChange('editData')"
                    >
                      <option value="">
                        选择已有联系人
                      </option>
                      <option
                        v-for="contact in availableContacts"
                        :key="contact.id"
                        :value="contact.id"
                      >
                        {{ contact.contact_person }}{{ contact.phone ? ` (${contact.phone})` : ''
                        }}{{ contact.contact_position ? ` - ${contact.contact_position}` : '' }}
                      </option>
                    </select>
                    <span class="client-or">或</span>
                    <input
                      id="editClientContactManual"
                      v-model="editData.client_contact_manual"
                      name="editClientContactManual"
                      type="text"
                      class="form-input client-input"
                      placeholder="手动输入联系人"
                      maxlength="50"
                      :disabled="!editData.client_source && !editData.client_name_manual"
                      @input="handleContactManualInput('editData')"
                    >
                  </div>
                </div>
                <span
                  v-if="!editData.client_source && !editData.client_name_manual"
                  class="form-hint"
                >请先选择或输入客户单位</span>
              </div>
              <div class="form-item">
                <label
                  for="clientAddress"
                  class="form-label"
                > <span class="required">*</span> 客户地址 </label>
                <input
                  id="clientAddress"
                  v-model="editData.address"
                  name="clientAddress"
                  type="text"
                  class="form-input"
                  placeholder="请输入客户地址"
                  maxlength="200"
                >
              </div>
            </div>
            <div class="form-column">
              <div class="form-item">
                <label
                  for="projectId"
                  class="form-label"
                > <span class="required">*</span> 项目编号 </label>
                <input
                  id="projectId"
                  v-model="editData.project_id"
                  name="projectId"
                  type="text"
                  class="form-input"
                  placeholder="请输入"
                  maxlength="50"
                  readonly
                >
              </div>
              <div class="form-item">
                <label
                  for="projectAbbr"
                  class="form-label"
                >项目简称</label>
                <input
                  id="projectAbbr"
                  v-model="editData.project_abbr"
                  name="projectAbbr"
                  type="text"
                  class="form-input"
                  placeholder="请输入项目简称"
                  maxlength="50"
                >
              </div>
              <div class="form-item">
                <label
                  for="projectEndDate"
                  class="form-label"
                > <span class="required">*</span> 项目结束日期 </label>
                <input
                  id="projectEndDate"
                  v-model="editData.maintenance_end_date"
                  name="projectEndDate"
                  type="date"
                  class="form-input"
                >
                <span class="form-hint">截止日期指的是当日 23:59:59</span>
              </div>
              <div class="form-item">
                <label
                  for="maintenancePersonnel"
                  class="form-label"
                > <span class="required">*</span> 运维人员 </label>
                <select
                  id="maintenancePersonnel"
                  v-model="editData.project_manager"
                  name="maintenancePersonnel"
                  class="form-input"
                >
                  <option value="">
                    请选择
                  </option>
                  <option
                    v-for="person in personnelList"
                    :key="person"
                    :value="person"
                  >
                    {{ person }}
                  </option>
                </select>
              </div>
              <div class="form-item">
                <label
                  for="clientContactInfo"
                  class="form-label"
                >客户联系方式</label>
                <input
                  id="clientContactInfo"
                  v-model="editData.client_contact_info"
                  name="clientContactInfo"
                  type="text"
                  class="form-input"
                  placeholder="请输入客户联系方式"
                  maxlength="50"
                >
              </div>
              <div class="form-item">
                <label
                  for="clientContactPosition"
                  class="form-label"
                >客户联系人职位</label>
                <input
                  id="clientContactPosition"
                  v-model="editData.client_contact_position"
                  name="clientContactPosition"
                  type="text"
                  class="form-input"
                  placeholder="请输入客户联系人职位"
                  maxlength="20"
                >
              </div>
            </div>
          </div>
        </div>
        <div class="modal-footer">
          <button
            class="btn btn-cancel"
            @click="closeEditModal"
          >
            取消
          </button>
          <button
            class="btn btn-save"
            :disabled="saving"
            @click="handleUpdate"
          >
            {{ saving ? '保存中...' : '保存' }}
          </button>
        </div>
      </div>
    </div>

    <Toast
      :visible="toast.visible"
      :message="toast.message"
      :type="toast.type"
    />
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
import {
  projectInfoService,
  type ProjectInfo,
  type ProjectInfoCreate,
  type ProjectInfoUpdate,
} from '../services/projectInfo'
import { personnelService } from '../services/personnel'
import { customerService, type CustomerContact } from '../services/customer'
import { LoadingSpinner, Toast, SearchInput } from '@sstcp/shared'
import ConfirmDialog from '../components/ConfirmDialog.vue'
import { useInputMemory } from '../utils'
import {
  formatDate as formatDateUtil,
  formatDateForInput as formatDateForInputUtil,
} from '../config/constants'

export default defineComponent({
  name: 'ProjectInfoManagement',
  components: {
    LoadingSpinner,
    Toast,
    ConfirmDialog,
    SearchInput,
  },
  setup() {
    const searchForm = reactive({
      projectName: '',
      clientName: '',
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
    const personnelList = ref<string[]>([])
    const customerList = ref<
      { id: number; name: string; address?: string; contacts?: CustomerContact[] }[]
    >([])
    const availableContacts = ref<CustomerContact[]>([])

    const toast = reactive({
      visible: false,
      message: '',
      type: 'success' as 'success' | 'error' | 'warning' | 'info',
    })
    const confirmDialog = reactive({
      visible: false,
      title: '确认',
      message: '',
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
      project_manager: '',
      client_contact: '',
      client_contact_position: '',
      client_contact_info: '',
    })
    const editData = reactive({
      id: 0,
      project_id: '',
      project_name: '',
      completion_date: '',
      maintenance_end_date: '',
      maintenance_period: '',
      client_name: '',
      client_source: '',
      client_name_manual: '',
      client_contact_id: null as number | null,
      client_contact_manual: '',
      address: '',
      project_abbr: '',
      project_manager: '',
      client_contact: '',
      client_contact_position: '',
      client_contact_info: '',
    })
    const formData = reactive({
      project_name: '',
      project_id: '',
      completion_date: '',
      client_name: '',
      client_source: '',
      client_name_manual: '',
      client_contact_id: null as number | null,
      client_contact: '',
      client_contact_manual: '',
      client_contact_position: '',
      maintenance_period: '',
      project_abbr: '',
      project_manager: '',
      maintenance_end_date: '',
      address: '',
      client_contact_info: '',
    })
    const inputMemory = useInputMemory({
      pageName: 'ProjectInfoManagement',
      fields: [
        'project_name',
        'project_id',
        'completion_date',
        'client_name',
        'client_source',
        'client_name_manual',
        'client_contact',
        'client_contact_position',
        'maintenance_period',
        'project_abbr',
        'project_manager',
        'maintenance_end_date',
        'address',
        'client_contact_info',
      ],
      onRestore: (data) => {
        if (data.project_name) formData.project_name = data.project_name
        if (data.project_id) formData.project_id = data.project_id
        if (data.completion_date) formData.completion_date = data.completion_date
        if (data.client_name) formData.client_name = data.client_name
        if (data.client_source) formData.client_source = data.client_source
        if (data.client_name_manual) formData.client_name_manual = data.client_name_manual
        if (data.client_contact) formData.client_contact = data.client_contact
        if (data.client_contact_position)
          formData.client_contact_position = data.client_contact_position
        if (data.maintenance_period) formData.maintenance_period = data.maintenance_period
        if (data.project_abbr) formData.project_abbr = data.project_abbr
        if (data.project_manager) formData.project_manager = data.project_manager
        if (data.maintenance_end_date) formData.maintenance_end_date = data.maintenance_end_date
        if (data.address) formData.address = data.address
        if (data.client_contact_info) formData.client_contact_info = data.client_contact_info
      },
    })
    const startIndex = computed(() => currentPage.value * pageSize.value)
    const showToast = (
      message: string,
      type: 'success' | 'error' | 'warning' | 'info' = 'success'
    ) => {
      toast.message = message
      toast.type = type
      toast.visible = true
    }
    const formatDate = (dateStr: string) => {
      return formatDateUtil(dateStr)
    }
    const formatDateForInput = (dateStr: string) => {
      return formatDateForInputUtil(dateStr)
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
      loading.value = true
      try {
        const response = await projectInfoService.getList({
          page: currentPage.value,
          size: pageSize.value,
          project_name: searchForm.projectName || undefined,
          client_name: searchForm.clientName || undefined,
        })
        if (response.code === 200 && response.data) {
          projectData.value = response.data.items || []
          totalElements.value = response.data.total ?? 0
          totalPages.value = response.data.totalPages ?? 0
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
        showToast('请填写维保频率', 'warning')
        return false
      }
      const clientName = formData.client_name_manual?.trim() || formData.client_source
      if (!clientName) {
        showToast('请选择或输入客户单位', 'warning')
        return false
      }
      if (!formData.address?.trim()) {
        showToast('请填写客户地址', 'warning')
        return false
      }
      if (!formData.project_manager?.trim()) {
        showToast('请选择运维人员', 'warning')
        return false
      }
      return true
    }
    const openModal = () => {
      resetForm()
      inputMemory.loadMemory()
      isModalOpen.value = true
    }
    const closeModal = () => {
      inputMemory.saveMemory(formData)
      isModalOpen.value = false
    }

    const resetForm = () => {
      formData.project_name = ''
      formData.project_id = ''
      formData.completion_date = ''
      formData.client_name = ''
      formData.client_source = ''
      formData.client_name_manual = ''
      formData.client_contact_id = null
      formData.client_contact = ''
      formData.client_contact_manual = ''
      formData.client_contact_position = ''
      formData.maintenance_period = ''
      formData.project_abbr = ''
      formData.project_manager = ''
      formData.maintenance_end_date = ''
      formData.address = ''
      formData.client_contact_info = ''
      availableContacts.value = []
    }
    const handleContactChange = (target: 'formData' | 'editData') => {
      const contactId =
        target === 'formData' ? formData.client_contact_id : editData.client_contact_id
      if (contactId) {
        const contact = availableContacts.value.find((c) => c.id === contactId)
        if (contact) {
          if (target === 'formData') {
            formData.client_contact = contact.contact_person
            formData.client_contact_info = contact.phone || ''
            formData.client_contact_position = contact.contact_position || ''
          } else {
            editData.client_contact = contact.contact_person
            editData.client_contact_info = contact.phone || ''
            editData.client_contact_position = contact.contact_position || ''
          }
        }
      }
    }
    const handleSave = async () => {
      if (!checkFormValid()) {
        return
      }
      const clientName = formData.client_name_manual?.trim() || formData.client_source
      const isManualClient = !!formData.client_name_manual?.trim()
      const clientContact = formData.client_contact_manual?.trim() || formData.client_contact
      saving.value = true
      try {
        const createData: ProjectInfoCreate = {
          project_id: formData.project_id,
          project_name: formData.project_name,
          completion_date: formatDateForAPI(formData.completion_date),
          maintenance_end_date: formatDateForAPI(formData.maintenance_end_date),
          maintenance_period: formData.maintenance_period,
          client_name: clientName,
          address: formData.address,
          project_abbr: formData.project_abbr || undefined,
          project_manager: formData.project_manager || undefined,
          client_contact_id: formData.client_contact_id || undefined,
          client_contact: clientContact || undefined,
          client_contact_position: formData.client_contact_position || undefined,
          client_contact_info: formData.client_contact_info || undefined,
        }
        const response = await projectInfoService.create(createData)
        if (response.code === 200) {
          if (isManualClient && clientName) {
            try {
              const existingCustomer = customerList.value.find(
                (c) => c.name.toLowerCase() === clientName.toLowerCase()
              )
              if (!existingCustomer) {
                await customerService.create({
                  name: clientName,
                  address: formData.address || undefined,
                  contacts: clientContact
                    ? [
                        {
                          contact_person: clientContact,
                          phone: formData.client_contact_info || undefined,
                          contact_position: formData.client_contact_position || undefined,
                        },
                      ]
                    : undefined,
                })
                await loadCustomerList()
                window.dispatchEvent(new CustomEvent('customer-changed'))
              }
            } catch (syncError) {
              console.error('同步客户信息失败:', syncError)
            }
          }
          showToast('创建成功', 'success')
          closeModal()
          resetForm()
          currentPage.value = 0
          await loadData()
          window.dispatchEvent(new CustomEvent('project-info-changed'))
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
      viewData.completion_date = item.completion_date ?? ''
      viewData.maintenance_end_date = item.maintenance_end_date ?? ''
      viewData.maintenance_period = item.maintenance_period ?? ''
      viewData.client_name = item.client_name ?? ''
      viewData.address = item.address ?? ''
      viewData.project_abbr = item.project_abbr || ''
      viewData.project_manager = item.project_manager || ''
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
      editData.completion_date = formatDateForInput(item.completion_date ?? '')
      editData.maintenance_end_date = formatDateForInput(item.maintenance_end_date ?? '')
      editData.maintenance_period = item.maintenance_period ?? ''
      editData.client_name = item.client_name ?? ''
      editData.client_source = ''
      editData.client_name_manual = item.client_name ?? ''
      editData.client_contact_id = item.client_contact_id || null
      editData.client_contact = item.client_contact || ''
      editData.client_contact_manual = item.client_contact || ''
      editData.client_contact_position = item.client_contact_position || ''
      editData.client_contact_info = item.client_contact_info || ''

      let matchingCustomer = customerList.value.find((c) => c.name === item.client_name)
      if (!matchingCustomer) {
        const clientName = item.client_name ?? ''
        matchingCustomer = customerList.value.find(
          (c) => c.name.includes(clientName) || clientName.includes(c.name)
        )
      }

      if (matchingCustomer) {
        editData.client_source = matchingCustomer.name
        editData.client_name = matchingCustomer.name
        editData.client_name_manual = ''
        availableContacts.value = matchingCustomer.contacts || []
      }
      editData.address = item.address ?? ''
      editData.project_abbr = item.project_abbr || ''
      editData.project_manager = item.project_manager || ''
      isEditModalOpen.value = true
    }
    const closeViewModal = () => {
      isViewModalOpen.value = false
    }
    const closeEditModal = () => {
      isEditModalOpen.value = false
      editingId.value = null
      availableContacts.value = []
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
        showToast('请填写维保频率', 'warning')
        return false
      }
      const clientName = editData.client_name_manual?.trim() || editData.client_source
      if (!clientName) {
        showToast('请选择或输入客户单位', 'warning')
        return false
      }
      if (!editData.address?.trim()) {
        showToast('请填写客户地址', 'warning')
        return false
      }
      if (!editData.project_manager?.trim()) {
        showToast('请选择运维人员', 'warning')
        return false
      }
      return true
    }
    const handleUpdate = async () => {
      if (!checkEditFormValid() || editingId.value === null) {
        return
      }
      const clientName = editData.client_name_manual?.trim() || editData.client_source
      const isManualClient = !!editData.client_name_manual?.trim()
      const clientContact = editData.client_contact_manual?.trim() || editData.client_contact
      saving.value = true
      try {
        const updateData: ProjectInfoUpdate = {
          project_id: editData.project_id,
          project_name: editData.project_name,
          completion_date: formatDateForAPI(editData.completion_date),
          maintenance_end_date: formatDateForAPI(editData.maintenance_end_date),
          maintenance_period: editData.maintenance_period,
          client_name: clientName,
          address: editData.address,
          project_abbr: editData.project_abbr || undefined,
          project_manager: editData.project_manager || undefined,
          client_contact_id: editData.client_contact_id || undefined,
          client_contact: clientContact || undefined,
          client_contact_position: editData.client_contact_position || undefined,
          client_contact_info: editData.client_contact_info || undefined,
        }
        const response = await projectInfoService.update(editingId.value, updateData)
        if (response.code === 200) {
          if (isManualClient && clientName) {
            try {
              const existingCustomer = customerList.value.find(
                (c) => c.name.toLowerCase() === clientName.toLowerCase()
              )
              if (!existingCustomer) {
                await customerService.create({
                  name: clientName,
                  address: editData.address || undefined,
                  contacts: clientContact
                    ? [
                        {
                          contact_person: clientContact,
                          phone: editData.client_contact_info || undefined,
                          contact_position: editData.client_contact_position || undefined,
                        },
                      ]
                    : undefined,
                })
                await loadCustomerList()
                window.dispatchEvent(new CustomEvent('customer-changed'))
              }
            } catch (syncError) {
              console.error('同步客户信息失败:', syncError)
            }
          }
          showToast('更新成功', 'success')
          closeEditModal()
          await loadData()
          window.dispatchEvent(new CustomEvent('project-info-changed'))
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
      showConfirm('确定要删除该项目吗？', async () => {
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
          if (
            error.status === 400 &&
            error.message &&
            error.message.includes('请确认是否级联删除')
          ) {
            loading.value = false
            showConfirm(error.message + '\n\n是否确认删除项目及其所有关联数据？', async () => {
              loading.value = true
              try {
                const cascadeResponse = await projectInfoService.delete(item.id, true)
                if (cascadeResponse.code === 200) {
                  showToast('删除成功', 'success')
                  await loadData()
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
          } else if (error.status === 404) {
            showToast('该项目已被删除，请刷新列表', 'warning')
            await loadData()
          } else if (error.status === 400 && error.message) {
            showToast(error.message, 'warning')
          } else {
            showToast(error.message || '删除失败，请检查网络连接', 'error')
          }
        } finally {
          loading.value = false
        }
      })
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
    const loadPersonnel = async () => {
      try {
        const response = await personnelService.getAll()
        if (response.code === 200 && response.data) {
          personnelList.value = response.data.map((p) => p.name)
        }
      } catch (error) {
        console.error('加载人员列表失败:', error)
      }
    }
    const loadCustomerList = async () => {
      try {
        const response = await customerService.getList({ page: 0, size: 100 })
        if (response.code === 200 && response.data) {
          customerList.value = (response.data.items || response.data.content || []).map((c: any) => ({
            id: c.id,
            name: c.name ?? '',
            contacts: c.contacts || [],
          }))
        }
      } catch (error) {
        console.error('加载客户列表失败:', error)
      }
    }
    const handleClientSourceChange = async (target: 'formData' | 'editData') => {
      if (target === 'formData') {
        if (formData.client_source) {
          formData.client_name_manual = ''
          formData.client_name = formData.client_source
          formData.client_contact_id = null
          formData.client_contact = ''
          formData.client_contact_info = ''
          formData.client_contact_position = ''
          const selectedCustomer = customerList.value.find((c) => c.name === formData.client_source)
          if (selectedCustomer) {
            availableContacts.value = selectedCustomer.contacts || []
            formData.address = selectedCustomer.address || formData.address
          } else {
            availableContacts.value = []
          }
        } else {
          availableContacts.value = []
        }
      } else {
        if (editData.client_source) {
          editData.client_name_manual = ''
          editData.client_name = editData.client_source
          editData.client_contact_id = null
          editData.client_contact = ''
          editData.client_contact_info = ''
          editData.client_contact_position = ''
          const selectedCustomer = customerList.value.find((c) => c.name === editData.client_source)
          if (selectedCustomer) {
            availableContacts.value = selectedCustomer.contacts || []
            editData.address = selectedCustomer.address || editData.address
          } else {
            availableContacts.value = []
          }
        } else {
          availableContacts.value = []
        }
      }
    }
    const handleClientManualInput = (target: 'formData' | 'editData') => {
      if (target === 'formData') {
        if (formData.client_name_manual?.trim()) {
          formData.client_source = ''
          formData.client_name = formData.client_name_manual.trim()
          availableContacts.value = []
          formData.client_contact_id = null
        }
      } else {
        if (editData.client_name_manual?.trim()) {
          editData.client_source = ''
          editData.client_name = editData.client_name_manual.trim()
          availableContacts.value = []
          editData.client_contact_id = null
        }
      }
    }

    const handleContactManualInput = (target: 'formData' | 'editData') => {
      if (target === 'formData') {
        if (formData.client_contact_manual?.trim()) {
          formData.client_contact_id = null
          formData.client_contact = formData.client_contact_manual.trim()
        }
      } else {
        if (editData.client_contact_manual?.trim()) {
          editData.client_contact_id = null
          editData.client_contact = editData.client_contact_manual.trim()
        }
      }
    }
    const handleCustomerChanged = () => {
      loadCustomerList()
    }
    onMounted(() => {
      loadData()
      loadPersonnel()
      loadCustomerList()
      window.addEventListener('user-changed', handleUserChanged)
      window.addEventListener('customer-changed', handleCustomerChanged)
    })
    onUnmounted(() => {
      window.removeEventListener('user-changed', handleUserChanged)
      window.removeEventListener('customer-changed', handleCustomerChanged)
    })
    const handleUserChanged = () => {
      loadData()
    }
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
      confirmDialog,
      personnelList,
      customerList,
      availableContacts,
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
      formatDate,
      handleConfirm,
      handleCancelConfirm,
      handleClientSourceChange,
      handleClientManualInput,
      handleContactManualInput,
      handleContactChange,
    }
  },
})
</script>
<style scoped>
.project-info-management {
  background: var(--color-bg-card);
  border: 1px solid var(--color-border-light);
  border-radius: var(--radius-md);
  padding: var(--space-5);
  position: relative;
}
.search-section {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--space-5);
  padding: var(--space-4);
  background: var(--color-bg-page);
  border-radius: var(--radius-sm);
}
.search-form {
  display: flex;
  flex-direction: column;
  gap: var(--space-4);
  align-items: flex-start;
}
.search-row {
  display: flex;
  gap: var(--space-4);
  align-items: center;
  flex-wrap: wrap;
}
.search-item {
  display: flex;
  align-items: center;
  gap: var(--space-2);
}
.search-label {
  font-size: var(--text-sm);
  font-weight: var(--weight-medium);
  color: var(--color-text-regular);
  white-space: nowrap;
}
.search-input {
  width: 200px;
  padding: var(--space-2) var(--space-3);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-sm);
  font-size: var(--text-sm);
  color: var(--color-text-primary);
  background: var(--color-bg-card);
  transition: border-color var(--transition-fast);
}
.search-input:focus {
  outline: none;
  border-color: var(--color-primary);
  box-shadow: 0 0 0 2px var(--color-primary-subtle);
}
.search-input::placeholder {
  color: var(--color-text-placeholder);
}
.search-actions {
  display: flex;
  flex-wrap: nowrap;
  gap: var(--space-2);
  overflow-x: auto;
  white-space: nowrap;
  min-width: max-content;
  align-items: center;
}
.btn {
  padding: var(--space-2) var(--space-4);
  border: none;
  border-radius: var(--radius-sm);
  font-size: var(--text-sm);
  font-weight: var(--weight-medium);
  cursor: pointer;
  transition: all var(--transition-fast);
}
.btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}
.btn-add {
  background: var(--color-primary);
  color: #fff;
}
.btn-add:hover:not(:disabled) {
  background: var(--color-primary-dark);
}
.btn-search {
  background: var(--color-primary);
  color: #fff;
}
.btn-search:hover {
  background: var(--color-primary-dark);
}
.table-section {
  margin-bottom: var(--space-5);
  border: 1px solid var(--color-border-light);
  border-radius: var(--radius-sm);
  overflow: hidden;
}
.data-table {
  width: 100%;
  border-collapse: collapse;
}
.data-table thead {
  background: var(--color-bg-page);
}
.data-table th {
  padding: var(--space-3) var(--space-4);
  text-align: left;
  font-size: var(--text-xs);
  font-weight: var(--weight-semibold);
  color: var(--color-text-regular);
  border-bottom: 1px solid var(--color-border);
  text-transform: uppercase;
  letter-spacing: 0.04em;
  white-space: nowrap;
}
.data-table td {
  padding: var(--space-3) var(--space-4);
  text-align: left;
  font-size: var(--text-sm);
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
  gap: var(--space-4);
  overflow-x: auto;
  white-space: nowrap;
  min-width: max-content;
  align-items: center;
}
.action-link {
  font-size: var(--text-sm);
  text-decoration: none;
  transition: opacity var(--transition-fast);
}
.action-link:hover {
  opacity: 0.7;
}
.action-view {
  color: var(--color-primary);
}
.action-edit {
  color: var(--color-accent);
}
.action-delete {
  color: var(--color-danger);
}
.pagination-section {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: var(--space-4) 0;
}
.pagination-info {
  font-size: var(--text-sm);
  color: var(--color-text-secondary);
  font-family: var(--font-mono);
}
.pagination-controls {
  display: flex;
  flex-wrap: nowrap;
  align-items: center;
  gap: var(--space-2);
  overflow-x: auto;
  white-space: nowrap;
  min-width: max-content;
}
.page-btn {
  min-width: 32px;
  height: 32px;
  padding: 0 var(--space-2);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-sm);
  background: var(--color-bg-card);
  font-size: var(--text-sm);
  font-family: var(--font-mono);
  color: var(--color-text-regular);
  cursor: pointer;
  transition: all var(--transition-fast);
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
  color: #fff;
  border-color: var(--color-primary);
}
.page-nav {
  font-size: var(--text-md);
}
.page-select {
  padding: var(--space-1) var(--space-3);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-sm);
  font-size: var(--text-sm);
  color: var(--color-text-regular);
  background: var(--color-bg-card);
  cursor: pointer;
}
.page-jump {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  font-size: var(--text-sm);
  color: var(--color-text-secondary);
}
.page-input {
  width: 48px;
  padding: var(--space-1) var(--space-2);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-sm);
  font-size: var(--text-sm);
  font-family: var(--font-mono);
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
  padding: 0 var(--space-2);
  background: var(--color-primary);
  color: #fff;
  border: none;
  border-radius: var(--radius-sm);
  font-size: var(--text-xs);
  cursor: pointer;
  transition: background var(--transition-fast);
}
.page-go:hover {
  background: var(--color-primary-dark);
}
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: var(--color-bg-overlay);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: var(--z-modal);
}
.modal-container {
  background: var(--color-bg-card);
  border-radius: var(--radius-lg);
  width: 900px;
  max-width: 95vw;
  max-height: 90vh;
  overflow-y: auto;
  box-shadow: var(--shadow-xl);
}
.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: var(--space-5) var(--space-6);
  border-bottom: 1px solid var(--color-border-light);
}
.modal-title {
  font-size: var(--text-lg);
  font-weight: var(--weight-semibold);
  color: var(--color-text-primary);
  margin: 0;
}
.modal-close {
  width: 32px;
  height: 32px;
  border: none;
  background: none;
  font-size: var(--text-xl);
  color: var(--color-text-secondary);
  cursor: pointer;
  transition: color var(--transition-fast);
  display: flex;
  align-items: center;
  justify-content: center;
}
.modal-close:hover {
  color: var(--color-text-primary);
}
.modal-body {
  padding: var(--space-6);
}
.form-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: var(--space-5) var(--space-10);
  align-items: start;
}
.form-column {
  display: flex;
  flex-direction: column;
}
.form-item {
  display: flex;
  flex-direction: column;
  gap: var(--space-2);
  min-height: 90px;
  padding: var(--space-1) 0;
}
.form-item-inline {
  display: flex;
  gap: var(--space-4);
  padding: var(--space-1) 0;
}
.form-item-half {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: var(--space-2);
}
.form-label {
  font-size: var(--text-sm);
  font-weight: var(--weight-medium);
  color: var(--color-text-regular);
}
.required {
  color: var(--color-danger);
  margin-right: var(--space-1);
}
.form-input {
  padding: var(--space-2) var(--space-3);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-sm);
  font-size: var(--text-sm);
  color: var(--color-text-primary);
  background: var(--color-bg-card);
  transition: border-color var(--transition-fast);
}
.form-input:focus {
  outline: none;
  border-color: var(--color-primary);
  box-shadow: 0 0 0 2px var(--color-primary-subtle);
}
.form-input::placeholder {
  color: var(--color-text-placeholder);
}
.form-input-readonly {
  background: var(--color-bg-page);
  color: var(--color-text-secondary);
  cursor: not-allowed;
}
.form-input-readonly:focus {
  outline: none;
  border-color: var(--color-border);
  box-shadow: none;
}
.form-hint {
  font-size: var(--text-xs);
  color: var(--color-text-placeholder);
}
.form-value {
  padding: var(--space-2) var(--space-3);
  background: var(--color-bg-page);
  border: 1px solid var(--color-border-light);
  border-radius: var(--radius-sm);
  font-size: var(--text-sm);
  color: var(--color-text-primary);
  min-height: 36px;
  display: flex;
  align-items: center;
}
.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: var(--space-3);
  padding: var(--space-5) var(--space-6);
  border-top: 1px solid var(--color-border-light);
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
  color: #fff;
}
.btn-save:hover:not(:disabled) {
  background: var(--color-primary-dark);
}
.client-select-wrapper {
  display: flex;
  flex-direction: column;
  gap: var(--space-2);
}
.client-input-row {
  display: flex;
  align-items: center;
  gap: var(--space-2);
}
.client-select {
  flex: 1;
  cursor: pointer;
}
.client-or {
  font-size: var(--text-sm);
  color: var(--color-text-secondary);
  white-space: nowrap;
}
.client-input {
  flex: 1;
  margin-top: 0;
}
</style>
