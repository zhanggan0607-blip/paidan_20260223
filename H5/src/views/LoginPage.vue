<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { showLoadingToast, closeToast, showSuccessToast, showFailToast } from 'vant'
import api from '../utils/api'
import type { ApiResponse } from '../types'
import { userStore, type User } from '../stores/userStore'

const router = useRouter()

const username = ref('')
const password = ref('')
const loading = ref(false)
const currentUser = computed(() => userStore.readonlyCurrentUser.value)

onMounted(() => {
})

const handleLogin = async () => {
  if (!username.value.trim()) {
    showFailToast('请输入用户名')
    return
  }
  if (!password.value.trim()) {
    showFailToast('请输入密码')
    return
  }

  loading.value = true
  showLoadingToast({ message: '登录中...', forbidClick: true })

  try {
    if (userStore.getToken()) {
      userStore.clearUser()
    }
    
    const response = await api.post<unknown, ApiResponse<{ access_token: string; user: User }>>('/auth/login-json', {
      username: username.value.trim(),
      password: password.value.trim(),
      device_type: 'h5'
    })

    if (response.code === 200 && response.data) {
      userStore.setToken(response.data.access_token)
      userStore.setUser(response.data.user)
      
      showSuccessToast('登录成功')
      router.push('/')
    }
  } catch (error: any) {
    console.error('Login failed:', error)
    showFailToast(error.message || '登录失败')
  } finally {
    loading.value = false
    closeToast()
  }
}

const handleLogout = () => {
  userStore.clearUser()
  showSuccessToast('已退出登录')
}
</script>

<template>
  <div class="login-page">
    <van-nav-bar title="用户登录" fixed placeholder />
    
    <div class="content">
      <div v-if="currentUser" class="logged-in">
        <van-cell-group inset>
          <van-cell title="当前用户" :value="currentUser.name" />
          <van-cell title="角色" :value="currentUser.role" />
          <van-cell title="部门" :value="currentUser.department || '-'" />
        </van-cell-group>
        
        <div class="logout-btn">
          <van-button type="danger" block @click="handleLogout">退出登录</van-button>
        </div>
      </div>
      
      <div v-else class="login-form">
        <div class="login-header">
          <van-icon name="user-circle-o" size="60" color="#1989fa" />
          <div class="login-title">SSTCP维保系统</div>
          <div class="login-subtitle">请登录以继续使用</div>
        </div>
        
        <van-cell-group inset>
          <van-field
            v-model="username"
            label="用户名"
            placeholder="请输入姓名"
            :rules="[{ required: true, message: '请输入用户名' }]"
          />
          <van-field
            v-model="password"
            type="password"
            label="密码"
            placeholder="请输入密码（手机号后6位）"
            :rules="[{ required: true, message: '请输入密码' }]"
          />
        </van-cell-group>
        
        <div class="login-tip">
          <van-icon name="info-o" />
          <span>默认密码为手机号后6位，如无手机号则为123456</span>
        </div>
        
        <div class="login-btn">
          <van-button 
            type="primary" 
            block 
            :loading="loading"
            @click="handleLogin"
          >
            登录
          </van-button>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.login-page {
  min-height: 100vh;
  background-color: #f5f7fa;
}

.content {
  padding: 0;
}

.logged-in {
  padding-top: 40px;
}

.logout-btn {
  margin-top: 20px;
  padding: 0;
}

.login-form {
  padding-top: 40px;
}

.login-header {
  display: flex;
  flex-direction: column;
  align-items: center;
  margin-bottom: 30px;
}

.login-title {
  font-size: 24px;
  font-weight: bold;
  color: #323233;
  margin-top: 16px;
}

.login-subtitle {
  font-size: 14px;
  color: #969799;
  margin-top: 8px;
}

.login-tip {
  display: flex;
  align-items: center;
  gap: 4px;
  padding: 12px 0;
  font-size: 12px;
  color: #969799;
}

.login-btn {
  margin-top: 20px;
  padding: 0;
}

:deep(.van-cell-group--inset) {
  margin: 0;
}
</style>
