<script setup lang="ts">
/**
 * 登录页面
 * 提供用户名密码登录方式
 */
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { showToast, showLoadingToast, closeToast } from 'vant'
import { authService } from '../services/auth'
import { userStore } from '../stores/userStore'
import { onlineUserService } from '../services/onlineUser'

const router = useRouter()

const username = ref('')
const password = ref('')
const loading = ref(false)

/**
 * 处理登录
 */
const handleLogin = async () => {
  if (!username.value.trim()) {
    showToast('请输入用户名')
    return
  }
  if (!password.value.trim()) {
    showToast('请输入密码')
    return
  }

  loading.value = true
  showLoadingToast({
    message: '登录中...',
    forbidClick: true,
    duration: 0,
  })

  try {
    const response = await authService.login({
      username: username.value.trim(),
      password: password.value,
      device_type: 'h5',
    })

    if (response.code === 200 && response.data) {
      const user = response.data.user
      if (!user) {
        showToast('登录失败：用户信息为空')
        return
      }

      userStore.setToken(response.data.access_token)
      if (response.data.refresh_token) {
        userStore.setRefreshToken(response.data.refresh_token)
      }
      userStore.setUser({
        id: user.id,
        name: user.name,
        role: user.role,
        department: user.department || '',
        phone: user.phone || '',
      })

      await onlineUserService.recordLogin('h5', user.id, user.name)

      showToast({
        type: 'success',
        message: '登录成功',
      })

      router.replace('/')
    } else {
      showToast(response.message || '登录失败')
    }
  } catch (error: any) {
    console.error('登录失败:', error)
    showToast(error.message || '登录失败，请重试')
  } finally {
    loading.value = false
    closeToast()
  }
}
</script>

<template>
  <div class="login-page">
    <div class="login-header">
      <h1>SSTCP维保系统</h1>
      <p>运维人员手机端</p>
    </div>

    <div class="login-form">
      <van-cell-group inset>
        <van-field
          v-model="username"
          label="用户名"
          placeholder="请输入用户名"
          :rules="[{ required: true, message: '请输入用户名' }]"
        />
        <van-field
          v-model="password"
          type="password"
          label="密码"
          placeholder="请输入密码"
          :rules="[{ required: true, message: '请输入密码' }]"
          @keyup.enter="handleLogin"
        />
      </van-cell-group>

      <div class="login-button">
        <van-button type="primary" block :loading="loading" @click="handleLogin"> 登录 </van-button>
      </div>

      <div class="login-tip">
        <p>提示：默认密码为手机号后6位</p>
      </div>
    </div>
  </div>
</template>

<style scoped>
.login-page {
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  display: flex;
  flex-direction: column;
  justify-content: center;
  padding: 20px;
}

.login-header {
  text-align: center;
  margin-bottom: 40px;
  color: #fff;
}

.login-header h1 {
  font-size: 28px;
  margin-bottom: 10px;
}

.login-header p {
  font-size: 14px;
  opacity: 0.8;
}

.login-form {
  background: #fff;
  border-radius: 12px;
  padding: 20px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
}

.login-button {
  margin-top: 24px;
  padding: 0 16px;
}

.login-tip {
  margin-top: 16px;
  text-align: center;
  color: #999;
  font-size: 12px;
}

:deep(.van-cell-group--inset) {
  margin: 0;
}
</style>
