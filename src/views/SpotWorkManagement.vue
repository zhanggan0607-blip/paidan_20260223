<template>
  <div class="spot-work-page">
    <Toast :visible="toast.visible" :message="toast.message" :type="toast.type" />
    <div class="content">
      <div class="search-section">
        <div class="search-form">
          <div class="search-row">
            <div class="search-item">
              <label class="search-label">项目名称：</label>
              <SearchInput
                v-model="searchForm.project_name"
                field-key="SpotWorkManagement_project_name"
                placeholder="请输入项目名称"
                @input="handleSearch"
              />
            </div>
            <div class="search-item">
              <label class="search-label">工单编号：</label>
              <SearchInput
                v-model="searchForm.work_id"
                field-key="SpotWorkManagement_work_id"
                placeholder="请输入工单编号"
                @input="handleSearch"
              />
            </div>
          </div>
        </div>
        <div class="action-buttons">
          <button class="btn btn-add" @click="handleAdd">新增零星用工单</button>
        </div>
      </div>

      <div class="table-section">
        <table class="data-table">
          <thead>
            <tr>
              <th>序号</th>
              <th>项目编号</th>
              <th>项目名称</th>
              <th>零星用工编号</th>
              <th>用工周期</th>
              <th>用工天数</th>
              <th>施工人数</th>
              <th>客户联系人</th>
              <th>客户联系电话</th>
              <th>状态</th>
              <th>操作</th>
            </tr>
          </thead>
          <tbody>
            <tr v-if="loading">
              <td colspan="11" style="text-align: center; padding: 20px">加载中...</td>
            </tr>
            <tr v-else-if="workData.length === 0">
              <td colspan="11" style="text-align: center; padding: 20px">暂无数据</td>
            </tr>
            <tr
              v-for="(item, index) in workData"
              v-else
              :key="item.id"
              :class="{ 'even-row': index % 2 === 0 }"
            >
              <td>{{ (currentPage - 1) * pageSize + index + 1 }}</td>
              <td>{{ item.project_id }}</td>
              <td>{{ item.project_name }}</td>
              <td>{{ item.work_id }}</td>
              <td>
                {{ formatDate(item.plan_start_date) }} 至 {{ formatDate(item.plan_end_date) }}
              </td>
              <td>
                {{ item.work_days || calculateDays(item.plan_start_date, item.plan_end_date) }} 天
              </td>
              <td>{{ item.worker_count || 0 }} 人</td>
              <td>{{ item.client_contact || '-' }}</td>
              <td>{{ item.client_contact_info || '-' }}</td>
              <td>
                <span
                  v-if="item.status === WORK_STATUS.IN_PROGRESS"
                  class="status-tag status-in-progress"
                  >执行中</span
                >
                <span
                  v-else-if="item.status === WORK_STATUS.PENDING_CONFIRM"
                  class="status-tag status-waiting"
                  >待确认</span
                >
                <span
                  v-else-if="item.status === WORK_STATUS.COMPLETED"
                  class="status-tag status-completed"
                  >已完成</span
                >
                <span
                  v-else-if="item.status === WORK_STATUS.RETURNED"
                  class="status-tag status-returned"
                  >已退回</span
                >
                <span v-else class="status-tag">{{ item.status }}</span>
              </td>
              <td class="action-cell">
                <a href="#" class="action-link action-view" @click.prevent="handleView(item)"
                  >查看</a
                >
                <a
                  v-if="isAdmin"
                  href="#"
                  class="action-link action-edit"
                  @click.prevent="handleEdit(item)"
                  >编辑</a
                >
                <a
                  v-if="item.status === WORK_STATUS.COMPLETED"
                  href="#"
                  class="action-link action-export"
                  @click.prevent="handleExport(item)"
                  >导出</a
                >
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <div class="pagination-section">
        <div class="pagination-info">共 {{ totalElements }} 条记录</div>
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
          <button
            class="page-btn page-nav"
            :disabled="currentPage === totalPages"
            @click="currentPage++"
          >
            &gt;
          </button>
          <select v-model="pageSize" class="page-select">
            <option value="10">10 条 / 页</option>
            <option value="20">20 条 / 页</option>
            <option value="50">50 条 / 页</option>
          </select>
          <div class="page-jump">
            <span>跳至</span>
            <input v-model="jumpPage" type="number" class="page-input" min="1" :max="totalPages" />
            <span>页</span>
            <button class="page-btn page-go" @click="handleJump">Go</button>
          </div>
        </div>
      </div>
    </div>

    <div v-if="isAddModalOpen" class="modal-overlay" @click.self="closeAddModal">
      <div class="modal-container modal-large">
        <div class="modal-header">
          <h3 class="modal-title">新增零星用工单</h3>
          <button class="modal-close" @click="closeAddModal">×</button>
        </div>
        <div class="modal-body">
          <div class="form-grid">
            <div class="form-column">
              <div class="form-item">
                <label class="form-label"> <span class="required">*</span> 项目名称 </label>
                <select
                  v-model="formData.project_name"
                  class="form-input"
                  @change="handleProjectChange"
                >
                  <option value="">请选择项目</option>
                  <option
                    v-for="project in projectList"
                    :key="project.id"
                    :value="project.project_name"
                  >
                    {{ project.project_name }}
                  </option>
                </select>
              </div>
              <div class="form-item">
                <label class="form-label">项目编号</label>
                <div class="form-value-readonly">{{ formData.project_id || '-' }}</div>
              </div>
              <div class="form-item">
                <label class="form-label"> <span class="required">*</span> 计划开始日期 </label>
                <input
                  v-model="formData.plan_start_date"
                  type="date"
                  class="form-input"
                  @change="calculateWorkDays"
                />
              </div>
              <div class="form-item">
                <label class="form-label">用工天数</label>
                <div class="form-value-readonly">{{ workDays }} 天</div>
              </div>
              <div class="form-item">
                <label class="form-label">客户联系人</label>
                <input
                  v-model="formData.client_contact"
                  type="text"
                  class="form-input"
                  placeholder="请输入客户联系人"
                />
              </div>
            </div>
            <div class="form-column">
              <div class="form-item">
                <label class="form-label"> <span class="required">*</span> 运维人员 </label>
                <select v-model="formData.maintenance_personnel" class="form-input">
                  <option value="">请选择</option>
                  <option v-for="person in personnelList" :key="person.id" :value="person.name">
                    {{ person.name }}
                  </option>
                </select>
              </div>
              <div class="form-item">
                <label class="form-label">工单编号</label>
                <div class="form-value-readonly">{{ formData.work_id || '自动生成' }}</div>
              </div>
              <div class="form-item">
                <label class="form-label"> <span class="required">*</span> 计划结束日期 </label>
                <input
                  v-model="formData.plan_end_date"
                  type="date"
                  class="form-input"
                  @change="calculateWorkDays"
                />
              </div>
              <div class="form-item">
                <label class="form-label">施工人数</label>
                <div class="form-value-readonly">{{ workerCount }} 人</div>
              </div>
              <div class="form-item">
                <label class="form-label">客户联系电话</label>
                <input
                  v-model="formData.client_contact_info"
                  type="text"
                  class="form-input"
                  placeholder="请输入客户联系电话"
                />
              </div>
            </div>
          </div>
          <div class="form-item-full">
            <label class="form-label"> <span class="required">*</span> 工作内容 </label>
            <textarea
              v-model="formData.work_content"
              class="form-input form-textarea"
              placeholder="请输入工作内容"
              maxlength="800"
            ></textarea>
          </div>

          <div class="form-item-full">
            <label class="form-label">施工人员</label>
            <div class="worker-section">
              <button type="button" class="btn btn-worker" @click="openWorkerModal">
                {{ workerCount > 0 ? `已录入 ${workerCount} 人` : '录入施工人员' }}
              </button>
            </div>
          </div>

          <div class="form-item-full">
            <label class="form-label"> <span class="required">*</span> 现场图片 </label>
            <PhotoUpload v-model="formData.photos" :max-count="9" />
          </div>

          <div class="form-item-full">
            <label class="form-label"> <span class="required">*</span> 班组签字 </label>
            <div class="signature-section">
              <div v-if="formData.signature" class="signature-preview">
                <img :src="formData.signature" alt="班组签字" />
                <button class="btn-clear-signature" @click="formData.signature = ''">
                  清除签字
                </button>
              </div>
              <button v-else class="btn btn-signature" @click="openSignatureModal">点击签字</button>
            </div>
          </div>

          <div class="form-item-full">
            <label class="form-label">备注</label>
            <textarea
              v-model="formData.remarks"
              class="form-input form-textarea"
              placeholder="请输入备注"
              maxlength="500"
            ></textarea>
          </div>
        </div>
        <div class="modal-footer">
          <button class="btn btn-cancel" @click="closeAddModal">取消</button>
          <button class="btn btn-save" :disabled="saving" @click="handleSave">
            {{ saving ? '保存中...' : '保存' }}
          </button>
        </div>
      </div>
    </div>

    <div v-if="isEditModalOpen" class="modal-overlay" @click.self="closeEditModal">
      <div class="modal-container">
        <div class="modal-header">
          <h3 class="modal-title">编辑零星用工单</h3>
          <button class="modal-close" @click="closeEditModal">×</button>
        </div>
        <div class="modal-body">
          <div class="form-grid">
            <div class="form-column">
              <div class="form-item">
                <label class="form-label">项目名称</label>
                <div class="form-value-readonly">{{ editFormData.project_name }}</div>
              </div>
              <div class="form-item">
                <label class="form-label">工单编号</label>
                <div class="form-value-readonly">{{ editFormData.work_id }}</div>
              </div>
              <div class="form-item">
                <label class="form-label"> <span class="required">*</span> 计划开始日期 </label>
                <input v-model="editFormData.plan_start_date" type="date" class="form-input" />
              </div>
              <div class="form-item">
                <label class="form-label">客户联系人</label>
                <input
                  v-model="editFormData.client_contact"
                  type="text"
                  class="form-input"
                  placeholder="请输入客户联系人"
                />
              </div>
            </div>
            <div class="form-column">
              <div class="form-item">
                <label class="form-label"> <span class="required">*</span> 运维人员 </label>
                <select v-model="editFormData.maintenance_personnel" class="form-input">
                  <option value="">请选择</option>
                  <option v-for="person in personnelList" :key="person.id" :value="person.name">
                    {{ person.name }}
                  </option>
                </select>
              </div>
              <div class="form-item">
                <label class="form-label"> <span class="required">*</span> 计划结束日期 </label>
                <input v-model="editFormData.plan_end_date" type="date" class="form-input" />
              </div>
              <div class="form-item">
                <label class="form-label">客户联系方式</label>
                <input
                  v-model="editFormData.client_contact_info"
                  type="text"
                  class="form-input"
                  placeholder="请输入客户联系方式"
                />
              </div>
              <div class="form-item">
                <label class="form-label">状态</label>
                <select v-model="editFormData.status" class="form-input">
                  <option value="执行中">执行中</option>
                  <option value="待确认">待确认</option>
                  <option value="已完成">已完成</option>
                  <option value="已退回">已退回</option>
                </select>
              </div>
            </div>
          </div>
          <div class="form-item-full">
            <label class="form-label">备注</label>
            <textarea
              v-model="editFormData.remarks"
              class="form-input form-textarea"
              placeholder="请输入备注"
              maxlength="500"
            ></textarea>
          </div>
        </div>
        <div class="modal-footer">
          <button class="btn btn-cancel" @click="closeEditModal">取消</button>
          <button class="btn btn-save" :disabled="saving" @click="handleUpdate">
            {{ saving ? '保存中...' : '保存' }}
          </button>
        </div>
      </div>
    </div>

    <div v-if="showSignatureModal" class="modal-overlay" @click.self="showSignatureModal = false">
      <div class="modal-container signature-modal">
        <div class="modal-header">
          <h3 class="modal-title">班组签字</h3>
          <button class="modal-close" @click="showSignatureModal = false">×</button>
        </div>
        <div class="modal-body">
          <SignaturePad @confirm="handleSignatureConfirm" @cancel="showSignatureModal = false" />
        </div>
      </div>
    </div>

    <WorkerEntryModal
      v-if="showWorkerModal"
      :project-id="formData.project_id"
      :project-name="formData.project_name"
      :work-date-start="formData.plan_start_date"
      :work-date-end="formData.plan_end_date"
      :initial-workers="workers"
      @close="showWorkerModal = false"
      @confirm="handleWorkerConfirm"
    />
  </div>
</template>

<script lang="ts">
import { defineComponent, ref, onMounted, onUnmounted, reactive, watch, computed } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessageBox } from 'element-plus'
import { spotWorkService, type SpotWork } from '@/services/spotWork'
import { projectInfoService, type ProjectInfo } from '@/services/projectInfo'
import { personnelService, type Personnel } from '@/services/personnel'
import Toast from '@/components/Toast.vue'
import SearchInput from '@/components/SearchInput.vue'
import PhotoUpload from '@/components/PhotoUpload.vue'
import SignaturePad from '@/components/SignaturePad.vue'
import WorkerEntryModal from '@/components/WorkerEntryModal.vue'
import { WORK_STATUS, formatDate as formatDateUtil } from '@/config/constants'
import { userStore } from '@/stores/userStore'

interface WorkerInfo {
  id?: number
  name: string
  gender: string
  birthDate: string
  address: string
  idCardNumber: string
  issuingAuthority: string
  validPeriod: string
  idCardFront: string
  idCardBack: string
}

interface WorkItem {
  id: number
  work_id: string
  project_id: string
  project_name: string
  plan_start_date: string
  plan_end_date: string
  client_name: string
  client_contact: string
  client_contact_info: string
  maintenance_personnel: string
  status: string
  remarks?: string
  work_content?: string
  worker_count?: number
  work_days?: number
  photos?: string[]
  signature?: string
}

export default defineComponent({
  name: 'SpotWorkManagement',
  components: {
    Toast,
    SearchInput,
    PhotoUpload,
    SignaturePad,
    WorkerEntryModal,
  },
  setup() {
    const router = useRouter()
    const currentPage = ref(1)
    const pageSize = ref(10)
    const jumpPage = ref(1)
    const loading = ref(false)
    const saving = ref(false)
    const totalElements = ref(0)
    const totalPages = ref(1)
    const isAddModalOpen = ref(false)
    const isEditModalOpen = ref(false)
    const editingId = ref<number | null>(null)
    const showSignatureModal = ref(false)
    const showWorkerModal = ref(false)

    const isAdmin = ref(userStore.isAdmin())

    const toast = reactive({
      visible: false,
      message: '',
      type: 'success' as 'success' | 'error' | 'warning' | 'info',
    })

    const showToast = (
      message: string,
      type: 'success' | 'error' | 'warning' | 'info' = 'success'
    ) => {
      toast.message = message
      toast.type = type
      toast.visible = true
      setTimeout(() => {
        toast.visible = false
      }, 3000)
    }

    const searchForm = ref({
      project_name: '',
      work_id: '',
      status: '',
    })

    const projectList = ref<ProjectInfo[]>([])
    const personnelList = ref<Personnel[]>([])
    const workers = ref<WorkerInfo[]>([])

    const formData = ref({
      project_name: '',
      project_id: '',
      work_id: '',
      client_name: '',
      client_contact: '',
      client_contact_info: '',
      plan_start_date: '',
      plan_end_date: '',
      maintenance_personnel: '',
      status: WORK_STATUS.IN_PROGRESS,
      work_content: '',
      remarks: '',
      photos: [] as string[],
      signature: '',
    })

    const editFormData = ref({
      id: 0,
      work_id: '',
      project_id: '',
      project_name: '',
      plan_start_date: '',
      plan_end_date: '',
      client_contact: '',
      client_contact_info: '',
      maintenance_personnel: '',
      status: '',
      remarks: '',
    })

    const workDays = computed(() => {
      if (!formData.value.plan_start_date || !formData.value.plan_end_date) return 0
      const start = new Date(formData.value.plan_start_date)
      const end = new Date(formData.value.plan_end_date)
      const diffTime = Math.abs(end.getTime() - start.getTime())
      return Math.ceil(diffTime / (1000 * 60 * 60 * 24)) + 1
    })

    const workerCount = computed(() => workers.value.length)

    const calculateDays = (startDate: string, endDate: string) => {
      if (!startDate || !endDate) return 0
      const start = new Date(startDate)
      const end = new Date(endDate)
      const diffTime = Math.abs(end.getTime() - start.getTime())
      return Math.ceil(diffTime / (1000 * 60 * 60 * 24)) + 1
    }

    const calculateWorkDays = () => {
      // This is just to trigger the computed property update
    }

    const workData = ref<WorkItem[]>([])

    const loadData = async () => {
      loading.value = true
      try {
        const response = await spotWorkService.getList({
          page: currentPage.value - 1,
          size: pageSize.value,
          project_name: searchForm.value.project_name || undefined,
          work_id: searchForm.value.work_id || undefined,
          status: searchForm.value.status || undefined,
        })

        if (response.code === 200 && response.data) {
          workData.value = (response.data.content || []).map((item: SpotWork) => ({
            id: item.id,
            work_id: item.work_id,
            project_id: item.project_id,
            project_name: item.project_name,
            plan_start_date: item.plan_start_date,
            plan_end_date: item.plan_end_date,
            client_name: item.client_name || '',
            client_contact: item.client_contact || '',
            client_contact_info: item.client_contact_info || '',
            maintenance_personnel: item.maintenance_personnel || '',
            status: item.status || '执行中',
            remarks: item.remarks || '',
            work_content: item.work_content || '',
            worker_count: item.worker_count || 0,
            photos:
              typeof item.photos === 'string'
                ? item.photos.split(',').filter(Boolean)
                : item.photos || [],
            signature: item.signature || '',
          }))
          totalElements.value = response.data.totalElements || 0
          totalPages.value = response.data.totalPages || 1
        }
      } catch (error: any) {
        console.error('加载数据失败:', error)
      } finally {
        loading.value = false
      }
    }

    const formatDate = (dateStr: string) => {
      return formatDateUtil(dateStr)
    }

    const handleSearch = () => {
      currentPage.value = 1
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
      const selectedProject = projectList.value.find(
        (p) => p.project_name === formData.value.project_name
      )
      if (selectedProject) {
        formData.value.project_id = selectedProject.project_id
        formData.value.client_name = selectedProject.client_name
        formData.value.client_contact = selectedProject.client_contact || ''
        formData.value.client_contact_info = selectedProject.client_contact_info || ''
        formData.value.maintenance_personnel = selectedProject.project_manager || ''
        await generateWorkId()
      }
    }

    const generateWorkId = async () => {
      if (!formData.value.project_id) return

      try {
        const today = new Date()
        const year = today.getFullYear()
        const month = String(today.getMonth() + 1).padStart(2, '0')
        const day = String(today.getDate()).padStart(2, '0')
        const dateStr = `${year}${month}${day}`
        const prefix = `YG-${formData.value.project_id}-${dateStr}`

        const response = await spotWorkService.getAll()

        if (response.code === 200) {
          const existingWorks = response.data.filter(
            (item) => item.work_id && item.work_id.startsWith(prefix)
          )
          const nextNumber = existingWorks.length + 1
          formData.value.work_id = `${prefix}-${String(nextNumber).padStart(2, '0')}`
        }
      } catch (error) {
        console.error('生成用工单编号失败:', error)
        const today = new Date()
        const year = today.getFullYear()
        const month = String(today.getMonth() + 1).padStart(2, '0')
        const day = String(today.getDate()).padStart(2, '0')
        const dateStr = `${year}${month}${day}`
        formData.value.work_id = `YG-${formData.value.project_id}-${dateStr}-01`
      }
    }

    const getTodayDate = () => {
      const today = new Date()
      const year = today.getFullYear()
      const month = String(today.getMonth() + 1).padStart(2, '0')
      const day = String(today.getDate()).padStart(2, '0')
      return `${year}-${month}-${day}`
    }

    const handleAdd = () => {
      resetForm()
      isAddModalOpen.value = true
    }

    const closeAddModal = () => {
      isAddModalOpen.value = false
      resetForm()
    }

    const resetForm = () => {
      const today = getTodayDate()
      formData.value = {
        project_name: '',
        project_id: '',
        work_id: '',
        client_name: '',
        client_contact: '',
        client_contact_info: '',
        plan_start_date: today,
        plan_end_date: today,
        maintenance_personnel: '',
        status: WORK_STATUS.IN_PROGRESS,
        work_content: '',
        remarks: '',
        photos: [],
        signature: '',
      }
      workers.value = []
    }

    const openSignatureModal = () => {
      showSignatureModal.value = true
    }

    const handleSignatureConfirm = (signatureData: string) => {
      formData.value.signature = signatureData
      showSignatureModal.value = false
    }

    const openWorkerModal = () => {
      showWorkerModal.value = true
    }

    const handleWorkerConfirm = (workerList: WorkerInfo[]) => {
      workers.value = workerList
      showWorkerModal.value = false
    }

    const handleSave = async () => {
      if (!formData.value.project_name) {
        showToast('请选择项目名称', 'error')
        return
      }
      if (!formData.value.maintenance_personnel) {
        showToast('请选择运维人员', 'error')
        return
      }
      if (!formData.value.plan_start_date) {
        showToast('请选择计划开始日期', 'error')
        return
      }
      if (!formData.value.plan_end_date) {
        showToast('请选择计划结束日期', 'error')
        return
      }
      if (!formData.value.work_content) {
        showToast('请输入工作内容', 'error')
        return
      }
      if (formData.value.photos.length === 0) {
        showToast('请上传现场图片', 'error')
        return
      }
      if (!formData.value.signature) {
        showToast('请完成班组签字', 'error')
        return
      }

      saving.value = true

      try {
        const response = await spotWorkService.create({
          work_id: formData.value.work_id,
          project_id: formData.value.project_id,
          project_name: formData.value.project_name,
          plan_start_date: formData.value.plan_start_date,
          plan_end_date: formData.value.plan_end_date,
          client_name: formData.value.client_name,
          client_contact: formData.value.client_contact,
          client_contact_info: formData.value.client_contact_info,
          maintenance_personnel: formData.value.maintenance_personnel,
          status: '待确认',
          work_content: formData.value.work_content,
          remarks: formData.value.remarks || '',
          photos: JSON.stringify(formData.value.photos),
          signature: formData.value.signature,
        })

        if (response.code === 200) {
          if (workers.value.length > 0) {
            try {
              await spotWorkService.create({
                project_id: formData.value.project_id,
                project_name: formData.value.project_name,
                plan_start_date: formData.value.plan_start_date,
                plan_end_date: formData.value.plan_end_date,
                work_id: response.data.work_id,
              } as any)
            } catch (e) {
              console.error('Failed to save workers:', e)
            }
          }
          showToast('保存成功', 'success')
          await loadData()
          closeAddModal()
        } else {
          showToast(response.message || '保存失败', 'error')
        }
      } catch (error: any) {
        console.error('保存失败:', error)
        showToast('保存失败，请检查网络连接', 'error')
      } finally {
        saving.value = false
      }
    }

    const handleView = (item: WorkItem) => {
      router.push({
        name: 'SpotWorkDetail',
        query: { id: item.id },
      })
    }

    const handleEdit = async (item: WorkItem) => {
      try {
        const response = await spotWorkService.getById(item.id)
        if (response.code === 200) {
          const data = response.data
          editFormData.value = {
            id: data.id,
            work_id: data.work_id,
            project_id: data.project_id,
            project_name: data.project_name,
            plan_start_date: data.plan_start_date ? data.plan_start_date.split('T')[0] : '',
            plan_end_date: data.plan_end_date ? data.plan_end_date.split('T')[0] : '',
            client_contact: data.client_contact || '',
            client_contact_info: data.client_contact_info || '',
            maintenance_personnel: data.maintenance_personnel || '',
            status: data.status || '执行中',
            remarks: data.remarks || '',
          }
          editingId.value = data.id
          isEditModalOpen.value = true
        }
      } catch (error) {
        console.error('获取工单详情失败:', error)
        showToast('获取工单详情失败', 'error')
      }
    }

    const closeEditModal = () => {
      isEditModalOpen.value = false
      editingId.value = null
    }

    const handleUpdate = async () => {
      if (!editFormData.value.maintenance_personnel) {
        showToast('请选择运维人员', 'error')
        return
      }
      if (!editFormData.value.plan_start_date) {
        showToast('请选择计划开始日期', 'error')
        return
      }
      if (!editFormData.value.plan_end_date) {
        showToast('请选择计划结束日期', 'error')
        return
      }

      saving.value = true

      try {
        const response = await spotWorkService.update(editFormData.value.id, {
          work_id: editFormData.value.work_id,
          project_id: editFormData.value.project_id,
          project_name: editFormData.value.project_name,
          plan_start_date: editFormData.value.plan_start_date,
          plan_end_date: editFormData.value.plan_end_date,
          client_name: '',
          client_contact: editFormData.value.client_contact,
          client_contact_info: editFormData.value.client_contact_info,
          maintenance_personnel: editFormData.value.maintenance_personnel,
          status: editFormData.value.status,
          remarks: editFormData.value.remarks || '',
        })

        if (response.code === 200) {
          showToast('更新成功', 'success')
          await loadData()
          closeEditModal()
        } else {
          showToast(response.message || '更新失败', 'error')
        }
      } catch (error: any) {
        console.error('更新失败:', error)
        showToast('更新失败，请检查网络连接', 'error')
      } finally {
        saving.value = false
      }
    }

    const handleExport = (item: WorkItem) => {
      console.log('导出:', item)
      showToast('导出功能开发中', 'info')
    }

    const handleDelete = async (item: WorkItem) => {
      try {
        await ElMessageBox.confirm(`确定要删除用工单 ${item.work_id} 吗？`, '提示', {
          confirmButtonText: '确定',
          cancelButtonText: '取消',
          type: 'warning',
        })

        await spotWorkService.delete(item.id)
        showToast('删除成功', 'success')
        loadData()
      } catch (error: any) {
        if (error !== 'cancel') {
          console.error('删除失败:', error)
          showToast('删除失败', 'error')
        }
      }
    }

    const handleJump = () => {
      const page = parseInt(String(jumpPage.value))
      if (page >= 1 && page <= totalPages.value) {
        currentPage.value = page
      }
    }

    const handleProjectInfoChanged = () => {
      loadProjects()
    }

    watch([currentPage, pageSize], () => {
      loadData()
    })

    onMounted(() => {
      loadProjects()
      loadPersonnel()
      loadData()
      window.addEventListener('user-changed', handleUserChanged)
      window.addEventListener('project-info-changed', handleProjectInfoChanged)
    })

    onUnmounted(() => {
      window.removeEventListener('user-changed', handleUserChanged)
      window.removeEventListener('project-info-changed', handleProjectInfoChanged)
    })

    const handleUserChanged = () => {
      isAdmin.value = userStore.isAdmin()
      loadData()
    }

    return {
      currentPage,
      pageSize,
      jumpPage,
      loading,
      saving,
      totalElements,
      totalPages,
      isAddModalOpen,
      isEditModalOpen,
      editingId,
      isAdmin,
      toast,
      searchForm,
      formData,
      editFormData,
      projectList,
      personnelList,
      workData,
      workers,
      workDays,
      workerCount,
      showSignatureModal,
      showWorkerModal,
      formatDate,
      WORK_STATUS,
      handleSearch,
      handleProjectChange,
      handleAdd,
      closeAddModal,
      handleSave,
      handleView,
      handleEdit,
      closeEditModal,
      handleUpdate,
      handleExport,
      handleDelete,
      handleJump,
      showToast,
      calculateDays,
      calculateWorkDays,
      openSignatureModal,
      handleSignatureConfirm,
      openWorkerModal,
      handleWorkerConfirm,
    }
  },
})
</script>

<style scoped>
.spot-work-page {
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
  align-items: center;
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
  min-width: 200px;
}

.search-input:focus {
  border-color: #1976d2;
  box-shadow: 0 0 0 2px rgba(25, 118, 210, 0.1);
}

.search-select {
  padding: 8px 12px;
  border: 1px solid #d0d7de;
  border-radius: 4px;
  font-size: 14px;
  outline: none;
  min-width: 120px;
  background: #fff;
  cursor: pointer;
}

.search-select:focus {
  border-color: #1976d2;
  box-shadow: 0 0 0 2px rgba(25, 118, 210, 0.1);
}

.action-buttons {
  display: flex;
  gap: 12px;
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
}

.data-table {
  width: 100%;
  border-collapse: collapse;
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

.action-export {
  color: #4caf50;
}

.action-export:hover {
  color: #45a049;
}

.status-tag {
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
  color: #fff;
}

.status-completed {
  background: #9e9e9e;
  color: #666;
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

.page-select:focus {
  border-color: #1976d2;
  box-shadow: 0 0 0 2px rgba(25, 118, 210, 0.1);
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

.page-input:focus {
  border-color: #1976d2;
  box-shadow: 0 0 0 2px rgba(25, 118, 210, 0.1);
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
  min-height: 90px;
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

.form-value-readonly {
  padding: 8px 12px;
  background: #f5f5f5;
  border: 1px solid #e0e0e0;
  border-radius: 3px;
  font-size: 14px;
  color: #666;
  min-height: 36px;
  display: flex;
  align-items: center;
}

.form-item-full {
  display: flex;
  flex-direction: column;
  gap: 8px;
  margin-top: 16px;
}

.form-textarea {
  min-height: 100px;
  resize: vertical;
  line-height: 1.5;
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

.modal-large {
  width: 1000px;
}

.signature-modal {
  width: 600px;
}

.worker-section {
  padding: 12px 0;
}

.btn-worker {
  background: #fff;
  color: #1976d2;
  border: 1px solid #1976d2;
  padding: 10px 20px;
}

.btn-worker:hover {
  background: #e3f2fd;
}

.signature-section {
  padding: 12px 0;
}

.signature-preview {
  display: flex;
  align-items: center;
  gap: 16px;
}

.signature-preview img {
  max-width: 200px;
  max-height: 100px;
  border: 1px solid #e0e0e0;
  border-radius: 4px;
  background: #fafafa;
}

.btn-clear-signature {
  padding: 6px 12px;
  border: 1px solid #f44336;
  border-radius: 4px;
  background: #fff;
  color: #f44336;
  font-size: 12px;
  cursor: pointer;
}

.btn-clear-signature:hover {
  background: #ffebee;
}

.btn-signature {
  background: #fff;
  color: #1976d2;
  border: 1px solid #1976d2;
  padding: 12px 24px;
}

.btn-signature:hover {
  background: #e3f2fd;
}
</style>
