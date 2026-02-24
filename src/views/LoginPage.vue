<template>
  <div class="login-page">
    <div class="login-container">
      <div class="login-header">
        <h1 class="login-title">SSTCP维保系统</h1>
        <p class="login-subtitle">请登录您的账号</p>
      </div>
      
      <form class="login-form" @submit.prevent="handleLogin">
        <div class="form-group">
          <label class="form-label">用户名</label>
          <input 
            type="text" 
            class="form-input" 
            v-model="username" 
            placeholder="请输入姓名"
            :disabled="loading"
          />
        </div>
        
        <div class="form-group">
          <label class="form-label">密码</label>
          <input 
            type="password" 
            class="form-input" 
            v-model="password" 
            placeholder="请输入密码（手机号后6位）"
            :disabled="loading"
          />
        </div>
        
        <div v-if="errorMessage" class="error-message">
          {{ errorMessage }}
        </div>
        
        <button type="submit" class="login-btn" :disabled="loading">
          {{ loading ? '登录中...' : '登录' }}
        </button>
      </form>
      
      <div class="login-footer">
        <p class="login-hint">提示：默认密码为手机号后6位</p>
      </div>
    </div>
  </div>
</template>

<script lang="ts">
import { defineComponent, ref } from 'vue'
import { useRouter } from 'vue-router'
import { userStore } from '../stores/userStore'
import apiClient from '../utils/api'

interface LoginResponse {
  access_token: string
  token_type: string
  user: {
    id: number
    name: string
    role: string
    department: string
    phone: string
  }
}

interface ApiResponse<T = any> {
  code: number
  message: string
  data: T
}

export default defineComponent({
  name: 'LoginPage',
  setup() {
    const router = useRouter()
    const username = ref('')
    const password = ref('')
    const loading = ref(false)
    const errorMessage = ref('')

    const handleLogin = async () => {
      if (!username.value.trim()) {
        errorMessage.value = '请输入用户名'
        return
      }
      if (!password.value.trim()) {
        errorMessage.value = '请输入密码'
        return
      }

      loading.value = true
      errorMessage.value = ''

      try {
        if (userStore.getToken()) {
          userStore.clearUser()
        }
        
        const response = await apiClient.post('/auth/login-json', {
          username: username.value.trim(),
          password: password.value,
          device_type: 'pc'
        }) as unknown as ApiResponse<LoginResponse>
        
        if (response.code === 200 && response.data) {
          userStore.setToken(response.data.access_token)
          userStore.setUser(response.data.user)
          
          router.push('/')
        } else {
          errorMessage.value = response.message || '登录失败，请检查用户名和密码'
        }
      } catch (error: any) {
        errorMessage.value = error.message || '登录失败，请稍后重试'
      } finally {
        loading.value = false
      }
    }

    return {
      username,
      password,
      loading,
      errorMessage,
      handleLogin
    }
  }
})
</script>

<style scoped>
.login-page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #001F3F 0%, #003366 100%);
}

.login-container {
  width: 400px;
  max-width: 90vw;
  background: #fff;
  border-radius: 8px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
  padding: 40px 32px;
}

.login-header {
  text-align: center;
  margin-bottom: 32px;
}

.login-title {
  font-size: 28px;
  font-weight: 700;
  color: #001F3F;
  margin: 0 0 8px 0;
}

.login-subtitle {
  font-size: 14px;
  color: #666;
  margin: 0;
}

.login-form {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.form-label {
  font-size: 14px;
  font-weight: 500;
  color: #333;
}

.form-input {
  padding: 12px 16px;
  border: 1px solid #e0e0e0;
  border-radius: 4px;
  font-size: 14px;
  color: #333;
  transition: border-color 0.15s, box-shadow 0.15s;
}

.form-input:focus {
  outline: none;
  border-color: #1976d2;
  box-shadow: 0 0 0 3px rgba(25, 118, 210, 0.1);
}

.form-input::placeholder {
  color: #999;
}

.form-input:disabled {
  background: #f5f5f5;
  cursor: not-allowed;
}

.error-message {
  padding: 12px 16px;
  background: #ffebee;
  border-radius: 4px;
  color: #c62828;
  font-size: 14px;
}

.login-btn {
  padding: 14px 24px;
  background: #1976d2;
  color: #fff;
  border: none;
  border-radius: 4px;
  font-size: 16px;
  font-weight: 500;
  cursor: pointer;
  transition: background 0.15s;
}

.login-btn:hover:not(:disabled) {
  background: #1565c0;
}

.login-btn:disabled {
  opacity: 0.7;
  cursor: not-allowed;
}

.login-footer {
  margin-top: 24px;
  text-align: center;
}

.login-hint {
  font-size: 12px;
  color: #999;
  margin: 0;
}
</style>
