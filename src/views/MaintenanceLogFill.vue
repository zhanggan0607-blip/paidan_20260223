<template>
  <div class="maintenance-log-fill-container">
    <div class="main-layout">
      <div class="content-area">
        <div class="content-wrapper">
          <div class="page-header">
            <h2 class="page-title">
              {{ pageTitle }}
            </h2>
          </div>

          <div class="form-section">
            <div class="form-card">
              <div class="form-card-header">
                <h3>基本信息</h3>
              </div>
              <div class="form-card-body">
                <div class="form-grid">
                  <div class="form-item">
                    <label for="projectName" class="form-label">项目名称</label>
                    <select id="projectName" name="projectName"
                      v-model="formData.projectId"
                      class="form-select"
                      @change="handleProjectChange"
                    >
                      <option value="">
                        请选择项目
                      </option>
                      <option
                        v-for="project in projectList"
                        :key="project.project_id"
                        :value="project.project_id"
                      >
                        {{ project.project_name }}
                      </option>
                    </select>
                  </div>
                  <div class="form-item">
                    <label for="projectId" class="form-label">项目编号</label>
                    <input id="projectId" name="projectId"
                      v-model="formData.projectId"
                      type="text"
                      class="form-input"
                      readonly
                      disabled
                    >
                  </div>
                  <div class="form-item">
                    <label for="reportDate" class="form-label">填报日期</label>
                    <input id="reportDate" name="reportDate"
                      v-model="formData.logDate"
                      type="date"
                      class="form-input"
                      readonly
                      disabled
                    >
                  </div>
                </div>
              </div>
            </div>

            <div class="form-card">
              <div class="form-card-header">
                <h3>工作内容</h3>
              </div>
              <div class="form-card-body">
                <div class="form-item full-width">
                  <label for="workContent" class="form-label"> <span class="required">*</span> 工作内容 </label>
                  <textarea id="workContent" name="workContent"
                    v-model="formData.workContent"
                    class="form-textarea"
                    placeholder="请输入工作内容"
                    rows="5"
                    maxlength="800"
                    show-word-limit
                  />
                  <div class="word-count">
                    {{ formData.workContent.length }}/800
                  </div>
                </div>
                <div class="form-item full-width">
                  <label for="remarks" class="form-label">备注</label>
                  <textarea id="remarks" name="remarks"
                    v-model="formData.remark"
                    class="form-textarea"
                    placeholder="请输入备注"
                    rows="3"
                  />
                </div>
              </div>
            </div>

            <div class="form-actions">
              <button
                class="btn btn-cancel"
                @click="handleCancel"
              >
                取消
              </button>
              <button
                class="btn btn-submit"
                :disabled="submitting"
                @click="handleSubmit"
              >
                {{
                  submitting
                    ? isEditMode
                      ? '保存中...'
                      : '提交中...'
                    : isEditMode
                      ? '保存修改'
                      : '提交'
                }}
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script lang="ts">
import { defineComponent, ref, computed, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { request } from '@/api/request'
import type { ApiResponse } from '@/types/api'
import { userStore } from '@/stores/userStore'
import { formatDate } from '@/config/constants'
import { ElNotification, ElMessage } from 'element-plus'

interface ProjectInfo {
  id: number
  project_id: string
  project_name: string
  client_name: string
}

interface MaintenanceLog {
  id: number
  project_id: string
  project_name: string
  log_date: string
  work_content: string
  remark: string
  images: string | string[]
}

export default defineComponent({
  name: 'MaintenanceLogFill',
  setup() {
    const router = useRouter()
    const submitting = ref(false)
    const projectList = ref<ProjectInfo[]>([])
    const isEditMode = ref(false)
    const editLogId = ref<number | null>(null)

    const isDepartmentManager = computed(() => {
      return userStore.isDepartmentManager()
    })

    const pageTitle = computed(() => {
      if (isEditMode.value) {
        return '修改日志'
      }
      if (isDepartmentManager.value) {
        return '新报周报'
      }
      return '新报日志'
    })

    const formData = ref({
      projectId: '',
      projectName: '',
      logType: 'maintenance',
      logDate: formatDate(new Date()),
      workContent: '',
      remark: '',
    })

    /**
     * 获取项目列表
     */
    const fetchProjectList = async () => {
      try {
        const response = (await request.get('/project-info/all/list')) as unknown as ApiResponse<
          ProjectInfo[]
        >
        if (response.code === 200) {
          projectList.value = response.data || []
        }
      } catch (error) {
        console.error('Failed to fetch project list:', error)
      }
    }

    /**
     * 检查当天是否已有维保日志
     */
    const checkTodayLog = async () => {
      try {
        const response = (await request.get(
          '/maintenance-log/today'
        )) as unknown as ApiResponse<MaintenanceLog | null>
        if (response.code === 200 && response.data) {
          isEditMode.value = true
          editLogId.value = response.data.id
          formData.value.projectId = response.data.project_id || ''
          formData.value.projectName = response.data.project_name || ''
          formData.value.logDate = response.data.log_date || formatDate(new Date())
          formData.value.workContent = response.data.work_content || ''
          formData.value.remark = response.data.remark || ''
        }
      } catch (error) {
        console.error('Failed to check today log:', error)
      }
    }

    /**
     * 项目选择变更
     */
    const handleProjectChange = () => {
      const project = projectList.value.find((p) => p.project_id === formData.value.projectId)
      if (project) {
        formData.value.projectName = project.project_name
      }
    }

    /**
     * 提交表单
     */
    const handleSubmit = async () => {
      if (!formData.value.workContent) {
        ElMessage.warning('请输入工作内容')
        return
      }

      submitting.value = true

      try {
        const submitData = {
          project_id: formData.value.projectId,
          project_name: formData.value.projectName,
          log_type: formData.value.logType,
          log_date: formData.value.logDate,
          work_content: formData.value.workContent,
          remark: formData.value.remark,
          images: [] as any[],
        }

        let response
        if (isEditMode.value && editLogId.value) {
          response = (await request.put(
            `/maintenance-log/${editLogId.value}`,
            submitData
          )) as unknown as ApiResponse<null>
        } else {
          response = (await request.post(
            '/maintenance-log',
            submitData
          )) as unknown as ApiResponse<null>
        }

        if (response.code === 200) {
          ElMessage.success(isEditMode.value ? '修改成功' : '提交成功')
          ElNotification({
            title: '提示',
            message: '日志只可当日可修改',
            type: 'warning',
            duration: 4000,
            position: 'top-right',
          })
          setTimeout(() => {
            router.back()
          }, 500)
        } else {
          ElMessage.error(response.message || '提交失败')
        }
      } catch (error) {
        console.error('Failed to submit:', error)
        ElMessage.error('提交失败，请重试')
      } finally {
        submitting.value = false
      }
    }

    /**
     * 取消
     */
    const handleCancel = () => {
      router.back()
    }

    const handleUserChanged = () => {
      // 用户状态由 userStore 管理
    }

    onMounted(async () => {
      await fetchProjectList()
      await checkTodayLog()
      window.addEventListener('user-changed', handleUserChanged)
    })

    onUnmounted(() => {
      window.removeEventListener('user-changed', handleUserChanged)
    })

    return {
      currentUser: userStore.readonlyCurrentUser,
      isDepartmentManager,
      pageTitle,
      formData,
      projectList,
      submitting,
      isEditMode,
      handleProjectChange,
      handleSubmit,
      handleCancel,
    }
  },
})
</script>

<style scoped>
.maintenance-log-fill-container {
  min-height: 100vh;
  background: var(--color-bg-page);
}

.main-layout {
  display: flex;
  min-height: 100vh;
}

.content-area {
  flex: 1;
  display: flex;
  flex-direction: column;
  background: var(--color-bg-page);
}

.content-wrapper {
  display: flex;
  flex-direction: column;
  gap: 20px;
  padding: 20px;
  flex: 1;
  overflow-y: auto;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.page-title {
  font-size: 20px;
  font-weight: 600;
  color: var(--color-text-primary);
  margin: 0;
}

.form-section {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.form-card {
  background: var(--color-bg-card);
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
  overflow: hidden;
}

.form-card-header {
  padding: 16px 20px;
  border-bottom: 1px solid var(--color-border);
  background: var(--color-bg-page);
}

.form-card-header h3 {
  margin: 0;
  font-size: 16px;
  font-weight: 600;
  color: var(--color-text-primary);
}

.form-card-body {
  padding: 20px;
}

.form-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 20px;
}

.form-item {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.form-item.full-width {
  grid-column: 1 / -1;
}

.form-label {
  font-size: 14px;
  font-weight: 500;
  color: var(--color-text-primary);
}

.required {
  color: var(--color-danger);
  margin-right: 2px;
}

.form-input,
.form-select,
.form-textarea {
  padding: 10px 12px;
  border: 1px solid var(--color-border);
  border-radius: 4px;
  font-size: 14px;
  transition: border-color 0.2s;
}

.form-input:focus,
.form-select:focus,
.form-textarea:focus {
  outline: none;
  border-color: var(--color-primary);
  box-shadow: 0 0 0 3px rgba(25, 118, 210, 0.1);
}

.form-textarea {
  min-height: 100px;
  resize: vertical;
}

.word-count {
  text-align: right;
  font-size: 12px;
  color: var(--color-text-placeholder);
}

.form-actions {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  padding: 20px 0;
}

.btn {
  padding: 10px 32px;
  border: none;
  border-radius: 4px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-cancel {
  background: var(--color-bg-page);
  color: var(--color-text-secondary);
}

.btn-cancel:hover {
  background: var(--color-border);
}

.btn-submit {
  background: linear-gradient(135deg, var(--color-primary) 0%, #42a5f5 100%);
  color: var(--color-bg-card);
}

.btn-submit:hover:not(:disabled) {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(25, 118, 210, 0.3);
}

.btn-submit:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}
</style>
