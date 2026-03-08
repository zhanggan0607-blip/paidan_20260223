<template>
  <div class="change-password-container">
    <div class="change-password-box">
      <div class="change-password-header">
        <h1>修改密码</h1>
        <p>首次登录需要修改密码</p>
      </div>

      <form class="change-password-form" @submit.prevent="handleChangePassword">
        <div class="form-group">
          <label for="oldPassword">旧密码</label>
          <input
            id="oldPassword"
            v-model="formData.old_password"
            type="password"
            placeholder="请输入旧密码"
            :disabled="loading"
          />
        </div>

        <div class="form-group">
          <label for="newPassword">新密码</label>
          <input
            id="newPassword"
            v-model="formData.new_password"
            type="password"
            placeholder="请输入新密码（至少6位）"
            :disabled="loading"
          />
        </div>

        <div class="form-group">
          <label for="confirmPassword">确认新密码</label>
          <input
            id="confirmPassword"
            v-model="confirmPassword"
            type="password"
            placeholder="请再次输入新密码"
            :disabled="loading"
          />
        </div>

        <div v-if="errorMessage" class="error-message">
          {{ errorMessage }}
        </div>

        <div v-if="successMessage" class="success-message">
          {{ successMessage }}
        </div>

        <button type="submit" class="change-password-button" :disabled="loading">
          {{ loading ? '修改中...' : '确认修改' }}
        </button>
      </form>
    </div>
  </div>
</template>

<script lang="ts">
import { defineComponent, ref } from 'vue'
import { useRouter } from 'vue-router'
import api from '@/utils/api'
import type { ApiResponse } from '@sstcp/shared'

export default defineComponent({
  name: 'ChangePasswordPage',
  setup() {
    const router = useRouter()

    const formData = ref({
      old_password: '',
      new_password: '',
    })

    const confirmPassword = ref('')
    const loading = ref(false)
    const errorMessage = ref('')
    const successMessage = ref('')

    const handleChangePassword = async () => {
      errorMessage.value = ''
      successMessage.value = ''

      if (!formData.value.old_password) {
        errorMessage.value = '请输入旧密码'
        return
      }

      if (formData.value.new_password.length < 6) {
        errorMessage.value = '新密码至少需要6位'
        return
      }

      if (formData.value.new_password !== confirmPassword.value) {
        errorMessage.value = '两次输入的新密码不一致'
        return
      }

      if (formData.value.old_password === formData.value.new_password) {
        errorMessage.value = '新密码不能与旧密码相同'
        return
      }

      loading.value = true

      try {
        const response = (await api.post('/auth/change-password', formData.value)) as ApiResponse

        if (response.code === 200) {
          successMessage.value = '密码修改成功，正在跳转...'
          setTimeout(() => {
            router.push('/')
          }, 1500)
        } else {
          errorMessage.value = response.message || '修改失败，请重试'
        }
      } catch (error: unknown) {
        const err = error as { message?: string }
        errorMessage.value = err.message || '修改失败，请重试'
      } finally {
        loading.value = false
      }
    }

    return {
      formData,
      confirmPassword,
      loading,
      errorMessage,
      successMessage,
      handleChangePassword,
    }
  },
})
</script>

<style scoped>
.change-password-container {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 20px;
}

.change-password-box {
  background: white;
  border-radius: 12px;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.2);
  padding: 40px;
  width: 100%;
  max-width: 400px;
}

.change-password-header {
  text-align: center;
  margin-bottom: 30px;
}

.change-password-header h1 {
  font-size: 24px;
  color: #333;
  margin-bottom: 8px;
}

.change-password-header p {
  color: #e74c3c;
  font-size: 14px;
}

.change-password-form {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.form-group label {
  font-size: 14px;
  color: #333;
  font-weight: 500;
}

.form-group input {
  padding: 12px 16px;
  border: 1px solid #ddd;
  border-radius: 8px;
  font-size: 14px;
  transition:
    border-color 0.2s,
    box-shadow 0.2s;
}

.form-group input:focus {
  outline: none;
  border-color: #667eea;
  box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
}

.form-group input:disabled {
  background-color: #f5f5f5;
  cursor: not-allowed;
}

.error-message {
  color: #e74c3c;
  font-size: 14px;
  text-align: center;
  padding: 10px;
  background-color: #fdf2f2;
  border-radius: 6px;
}

.success-message {
  color: #27ae60;
  font-size: 14px;
  text-align: center;
  padding: 10px;
  background-color: #f0fdf4;
  border-radius: 6px;
}

.change-password-button {
  padding: 14px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
  border-radius: 8px;
  font-size: 16px;
  font-weight: 500;
  cursor: pointer;
  transition:
    transform 0.2s,
    box-shadow 0.2s;
}

.change-password-button:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
}

.change-password-button:disabled {
  opacity: 0.7;
  cursor: not-allowed;
}
</style>
