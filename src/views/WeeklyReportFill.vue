<template>
  <div class="weekly-report-fill-container">
    <div class="main-layout">
      <div class="content-area">
        <div class="content-wrapper">
          <div class="page-header">
            <h2 class="page-title">新报部门周报</h2>
          </div>

          <div class="form-section">
            <div class="form-card">
              <div class="form-card-header">
                <h3>基本信息</h3>
              </div>
              <div class="form-card-body">
                <div class="form-grid two-columns">
                  <div class="form-item">
                    <label class="form-label">
                      <span class="required">*</span> 填报日期
                    </label>
                    <input v-model="formData.reportDate" type="date" class="form-input" @change="generateReportId" />
                  </div>
                  <div class="form-item">
                    <label class="form-label">周报编号</label>
                    <input v-model="formData.reportId" type="text" class="form-input" readonly disabled />
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
                    <span class="required">*</span> 本周工作总结
                  </label>
                  <textarea 
                    v-model="formData.workSummary" 
                    class="form-textarea" 
                    placeholder="请输入本周工作总结"
                    rows="4"
                    maxlength="1000"
                  ></textarea>
                  <div class="word-count">{{ formData.workSummary.length }}/1000</div>
                </div>
                <div class="form-item full-width">
                  <label class="form-label">下周工作计划</label>
                  <textarea 
                    v-model="formData.nextWeekPlan" 
                    class="form-textarea" 
                    placeholder="请输入下周工作计划"
                    rows="3"
                  ></textarea>
                </div>
                <div class="form-item full-width">
                  <label class="form-label">存在问题</label>
                  <textarea 
                    v-model="formData.issues" 
                    class="form-textarea" 
                    placeholder="请输入存在问题"
                    rows="3"
                  ></textarea>
                </div>
                <div class="form-item full-width">
                  <label class="form-label">建议措施</label>
                  <textarea 
                    v-model="formData.suggestions" 
                    class="form-textarea" 
                    placeholder="请输入建议措施"
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
import { defineComponent, ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import apiClient from '@/utils/api'
import type { ApiResponse } from '@/types/api'
import { formatDate } from '@/config/constants'

export default defineComponent({
  name: 'WeeklyReportFill',
  setup() {
    const router = useRouter()
    const submitting = ref(false)

    const formData = ref({
      reportId: '',
      reportDate: formatDate(new Date()),
      workSummary: '',
      nextWeekPlan: '',
      issues: '',
      suggestions: ''
    })

    /**
     * 生成周报编号
     */
    const generateReportId = async () => {
      if (!formData.value.reportDate) return
      
      try {
        const response = await apiClient.get('/weekly-report/generate-id', {
          params: { report_date: formData.value.reportDate }
        }) as unknown as ApiResponse<{ report_id: string }>
        
        if (response.code === 200 && response.data) {
          formData.value.reportId = response.data.report_id
        }
      } catch (error) {
        console.error('Failed to generate report id:', error)
        const today = formData.value.reportDate.replace(/-/g, '')
        formData.value.reportId = `ZB-${today}-01`
      }
    }

    /**
     * 提交表单
     */
    const handleSubmit = async () => {
      if (!formData.value.workSummary) {
        alert('请输入本周工作总结')
        return
      }
      
      submitting.value = true
      
      try {
        const response = await apiClient.post('/weekly-report', {
          report_id: formData.value.reportId,
          report_date: formData.value.reportDate,
          work_summary: formData.value.workSummary,
          next_week_plan: formData.value.nextWeekPlan,
          issues: formData.value.issues,
          suggestions: formData.value.suggestions
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

    onMounted(() => {
      generateReportId()
    })

    return {
      formData,
      submitting,
      generateReportId,
      handleSubmit,
      handleCancel
    }
  }
})
</script>

<style scoped>
.weekly-report-fill-container {
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
  grid-template-columns: repeat(2, 1fr);
  gap: 20px;
}

.form-grid.two-columns {
  grid-template-columns: repeat(2, 1fr);
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
  min-height: 80px;
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
