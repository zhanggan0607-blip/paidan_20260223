<template>
  <div class="maintenance-log-fill-container">
    <div class="main-layout">
      <div class="content-area">
        <div class="content-wrapper">
          <div class="page-header">
            <h2 class="page-title">{{ pageTitle }}</h2>
          </div>

          <div class="form-section">
            <div class="form-card">
              <div class="form-card-header">
                <h3>基本信息</h3>
              </div>
              <div class="form-card-body">
                <div class="form-grid">
                  <div class="form-item">
                    <label class="form-label">
                      <span class="required">*</span> 项目名称
                    </label>
                    <select v-model="formData.projectId" class="form-select" @change="handleProjectChange">
                      <option value="">请选择项目</option>
                      <option v-for="project in projectList" :key="project.project_id" :value="project.project_id">
                        {{ project.project_name }}
                      </option>
                    </select>
                  </div>
                  <div class="form-item">
                    <label class="form-label">项目编号</label>
                    <input v-model="formData.projectId" type="text" class="form-input" readonly disabled />
                  </div>
                  <div class="form-item">
                    <label class="form-label">
                      <span class="required">*</span> 填报日期
                    </label>
                    <input v-model="formData.logDate" type="date" class="form-input" />
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
                  <label class="form-label">
                    <span class="required">*</span> 工作内容
                  </label>
                  <textarea 
                    v-model="formData.workContent" 
                    class="form-textarea" 
                    placeholder="请输入工作内容"
                    rows="5"
                    maxlength="800"
                    show-word-limit
                  ></textarea>
                  <div class="word-count">{{ formData.workContent.length }}/800</div>
                </div>
                <div class="form-item full-width">
                  <label class="form-label">备注</label>
                  <textarea 
                    v-model="formData.remark" 
                    class="form-textarea" 
                    placeholder="请输入备注"
                    rows="3"
                  ></textarea>
                </div>
              </div>
            </div>

            <div class="form-actions">
              <button class="btn btn-cancel" @click="handleCancel">取消</button>
              <button class="btn btn-submit" @click="handleSubmit" :disabled="submitting">
                {{ submitting ? '提交中...' : '提交' }}
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
import apiClient from '@/utils/api'
import type { ApiResponse } from '@/types/api'
import { userStore } from '@/stores/userStore'
import { formatDate } from '@/config/constants'

interface ProjectInfo {
  id: number
  project_id: string
  project_name: string
  client_name: string
}

export default defineComponent({
  name: 'MaintenanceLogFill',
  setup() {
    const router = useRouter()
    const submitting = ref(false)
    const projectList = ref<ProjectInfo[]>([])

    const isDepartmentManager = computed(() => {
      return userStore.isDepartmentManager()
    })

    const pageTitle = computed(() => {
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
      remark: ''
    })

    /**
     * 获取项目列表
     */
    const fetchProjectList = async () => {
      try {
        const response = await apiClient.get('/project-info/all/list') as unknown as ApiResponse<ProjectInfo[]>
        if (response.code === 200) {
          projectList.value = response.data || []
        }
      } catch (error) {
        console.error('Failed to fetch project list:', error)
      }
    }

    /**
     * 项目选择变更
     */
    const handleProjectChange = () => {
      const project = projectList.value.find(p => p.project_id === formData.value.projectId)
      if (project) {
        formData.value.projectName = project.project_name
      }
    }

    /**
     * 提交表单
     */
    const handleSubmit = async () => {
      if (!formData.value.projectId) {
        alert('请选择项目名称')
        return
      }
      if (!formData.value.workContent) {
        alert('请输入工作内容')
        return
      }
      
      submitting.value = true
      
      try {
        const response = await apiClient.post('/maintenance-log', {
          project_id: formData.value.projectId,
          project_name: formData.value.projectName,
          log_type: formData.value.logType,
          log_date: formData.value.logDate,
          work_content: formData.value.workContent,
          remark: formData.value.remark,
          images: []
        }) as unknown as ApiResponse<null>
        
        if (response.code === 200) {
          alert('提交成功')
          router.back()
        } else {
          alert(response.message || '提交失败')
        }
      } catch (error) {
        console.error('Failed to submit:', error)
        alert('提交失败，请重试')
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

    onMounted(() => {
      fetchProjectList()
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
      handleProjectChange,
      handleSubmit,
      handleCancel
    }
  }
})
</script>

<style scoped>
.maintenance-log-fill-container {
  min-height: 100vh;
  background: #f8f9fa;
}

.main-layout {
  display: flex;
  min-height: 100vh;
}

.content-area {
  flex: 1;
  display: flex;
  flex-direction: column;
  background: #f8f9fa;
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
  color: #333;
  margin: 0;
}

.form-section {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.form-card {
  background: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
  overflow: hidden;
}

.form-card-header {
  padding: 16px 20px;
  border-bottom: 1px solid #e0e0e0;
  background: #f5f7fa;
}

.form-card-header h3 {
  margin: 0;
  font-size: 16px;
  font-weight: 600;
  color: #333;
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
  color: #333;
}

.required {
  color: #f44336;
  margin-right: 2px;
}

.form-input,
.form-select,
.form-textarea {
  padding: 10px 12px;
  border: 1px solid #e0e0e0;
  border-radius: 4px;
  font-size: 14px;
  transition: border-color 0.2s;
}

.form-input:focus,
.form-select:focus,
.form-textarea:focus {
  outline: none;
  border-color: #1976d2;
  box-shadow: 0 0 0 3px rgba(25, 118, 210, 0.1);
}

.form-textarea {
  min-height: 100px;
  resize: vertical;
}

.word-count {
  text-align: right;
  font-size: 12px;
  color: #999;
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
  background: #f5f5f5;
  color: #666;
}

.btn-cancel:hover {
  background: #e0e0e0;
}

.btn-submit {
  background: linear-gradient(135deg, #1976d2 0%, #42a5f5 100%);
  color: #fff;
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
