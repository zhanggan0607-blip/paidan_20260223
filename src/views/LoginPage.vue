<template>
  <div class="login-container">
    <div class="login-box">
      <div class="login-header">
        <h1>SSTCP维保系统</h1>
        <p>请登录您的账户</p>
      </div>

      <form class="login-form" @submit.prevent="handleLogin">
        <div class="form-group">
          <label for="username">用户名</label>
          <input
            id="username"
            v-model="formData.username"
            type="text"
            placeholder="请输入用户名"
            :disabled="loading"
            autocomplete="username"
          />
        </div>

        <div class="form-group">
          <label for="password">密码</label>
          <input
            id="password"
            v-model="formData.password"
            type="password"
            placeholder="请输入密码"
            :disabled="loading"
            autocomplete="current-password"
          />
        </div>

        <div v-if="errorMessage" class="error-message">
          {{ errorMessage }}
        </div>

        <button type="submit" class="login-button" :disabled="loading">
          {{ loading ? '登录中...' : '登录' }}
        </button>
      </form>

      <div class="login-footer">
        <p>默认密码为手机号后6位，如无手机号则为123456</p>
      </div>
    </div>
  </div>
</template>

<script lang="ts">
import { defineComponent, ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { userStore } from '@/stores/userStore'
import api from '@/utils/api'
import type { ApiResponse, LoginResponse } from '@sstcp/shared'

export default defineComponent({
  name: 'LoginPage',
  setup() {
    const router = useRouter()

    const formData = ref({
      username: '',
      password: '',
    })

    const loading = ref(false)
    const errorMessage = ref('')

    onMounted(() => {
      const token = userStore.getToken()
      if (token) {
        router.push('/')
      }
    })

    const handleLogin = async () => {
      if (!formData.value.username.trim()) {
        errorMessage.value = '请输入用户名'
        return
      }

      if (!formData.value.password) {
        errorMessage.value = '请输入密码'
        return
      }

      loading.value = true
      errorMessage.value = ''

      try {
        const response = (await api.post('/auth/login-json', {
          username: formData.value.username,
          password: formData.value.password,
          device_type: 'pc',
        })) as ApiResponse<LoginResponse>

        if (response.code === 200 && response.data) {
          const { access_token, user } = response.data

          userStore.setToken(access_token)
          if (user) {
            userStore.setUser({
              id: user.id,
              name: user.name,
              role: user.role,
              department: user.department,
              phone: user.phone,
            })

            if ((user as { must_change_password?: boolean }).must_change_password) {
              router.push('/change-password')
            } else {
              router.push('/')
            }
          } else {
            router.push('/')
          }
        } else {
          errorMessage.value = response.message || '登录失败，请重试'
        }
      } catch (error: unknown) {
        const err = error as { message?: string }
        errorMessage.value = err.message || '登录失败，请检查网络连接'
      } finally {
        loading.value = false
      }
    }

    return {
      formData,
      loading,
      errorMessage,
      handleLogin,
    }
  },
})
</script>

<style scoped>
.login-container {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 20px;
}

.login-box {
  background: white;
  border-radius: 12px;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.2);
  padding: 40px;
  width: 100%;
  max-width: 400px;
}

.login-header {
  text-align: center;
  margin-bottom: 30px;
}

.login-header h1 {
  font-size: 28px;
  color: #333;
  margin-bottom: 8px;
}

.login-header p {
  color: #666;
  font-size: 14px;
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

.login-button {
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

.login-button:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
}

.login-button:disabled {
  opacity: 0.7;
  cursor: not-allowed;
}

.login-footer {
  margin-top: 24px;
  text-align: center;
}

.login-footer p {
  color: #999;
  font-size: 12px;
}
</style>
