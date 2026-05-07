<script setup lang="ts">
import { ref } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { showToast, showLoadingToast, closeToast } from 'vant'
import { authService } from '../services/auth'
import { useUserStore } from '../stores/userStore'
const userStore = useUserStore()
import { onlineUserService } from '../services/onlineUser'

const router = useRouter()
const route = useRoute()

const username = ref('')
const password = ref('')
const loading = ref(false)

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
        must_change_password: (user as { must_change_password?: boolean }).must_change_password,
      })

      await onlineUserService.recordLogin('h5', user.id, user.name)

      showToast({
        type: 'success',
        message: '登录成功',
      })

      if ((user as { must_change_password?: boolean }).must_change_password) {
        router.replace('/change-password')
      } else {
        const redirect = (route.query.redirect as string) || '/'
        router.replace(redirect)
      }
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
      <div class="header-grid"></div>
      <div class="header-content">
        <div class="brand-icon">
          <svg width="36" height="36" viewBox="0 0 36 36" fill="none">
            <rect x="2" y="2" width="32" height="32" rx="6" stroke="currentColor" stroke-width="2" />
            <path d="M10 18h16M18 10v16M12 12l12 12M24 12L12 24" stroke="currentColor" stroke-width="1.5" opacity="0.4" />
            <circle cx="18" cy="18" r="4" stroke="currentColor" stroke-width="2" />
          </svg>
        </div>
        <h1 class="brand-title">SSTCP</h1>
        <p class="brand-subtitle">维保管理系统</p>
        <p class="brand-device">移动端</p>
      </div>
    </div>

    <form class="login-form" @submit.prevent="handleLogin">
      <div class="form-title">账号登录</div>

      <div class="form-fields">
        <div class="field-group">
          <label for="username" class="field-label">用户名</label>
          <input
            v-model="username"
            type="text" id="username" name="username"
            class="field-input"
            placeholder="请输入用户名"
            autocomplete="username"
          />
        </div>
        <div class="field-group">
          <label for="password" class="field-label">密码</label>
          <input
            v-model="password"
            type="password" id="password" name="password"
            class="field-input"
            placeholder="请输入密码"
            autocomplete="current-password"
          />
        </div>
      </div>

      <button type="submit" class="login-btn" :disabled="loading">
        <span v-if="!loading">登 录</span>
        <span v-else>登录中...</span>
      </button>

      <div class="login-tip">
        <span>默认密码为 Sstcp@手机号后4位</span>
      </div>
    </form>
  </div>
</template>

<style scoped>
.login-page {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  background: var(--color-bg-page);
}

.login-header {
  position: relative;
  background: var(--color-nav-bg);
  padding: 48px 24px 36px;
  overflow: hidden;
}

.header-grid {
  position: absolute;
  inset: 0;
  background-image:
    linear-gradient(rgba(42, 122, 122, 0.08) 1px, transparent 1px),
    linear-gradient(90deg, rgba(42, 122, 122, 0.08) 1px, transparent 1px);
  background-size: 24px 24px;
}

.header-content {
  position: relative;
  display: flex;
  flex-direction: column;
  align-items: center;
}

.brand-icon {
  color: var(--color-primary-light);
  margin-bottom: 12px;
}

.brand-title {
  font-family: var(--font-mono);
  font-size: 28px;
  font-weight: var(--weight-bold);
  color: var(--color-nav-text-active);
  letter-spacing: 0.12em;
  margin-bottom: 4px;
}

.brand-subtitle {
  font-size: 13px;
  color: var(--color-nav-text);
  letter-spacing: 0.08em;
  margin-bottom: 2px;
}

.brand-device {
  font-family: var(--font-mono);
  font-size: 11px;
  color: var(--color-primary);
  letter-spacing: 0.1em;
  margin-top: 4px;
  padding: 2px 10px;
  border: 1px solid rgba(42, 122, 122, 0.3);
  border-radius: var(--radius-full);
}

.login-form {
  flex: 1;
  padding: 28px 24px;
  background: var(--color-bg-card);
  border-radius: 20px 20px 0 0;
  margin-top: -16px;
  position: relative;
  z-index: 1;
}

.form-title {
  font-size: 18px;
  font-weight: var(--weight-semibold);
  color: var(--color-text-primary);
  margin-bottom: 24px;
  letter-spacing: 0.04em;
}

.form-fields {
  display: flex;
  flex-direction: column;
  gap: 16px;
  margin-bottom: 28px;
}

.field-group {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.field-label {
  font-size: 12px;
  font-weight: var(--weight-medium);
  color: var(--color-text-secondary);
  letter-spacing: 0.04em;
}

.field-input {
  width: 100%;
  height: 44px;
  padding: 0 14px;
  font-size: 14px;
  font-family: var(--font-sans);
  color: var(--color-text-primary);
  background: var(--color-bg-page);
  border: 1px solid var(--color-border-light);
  border-radius: var(--radius-md);
  outline: none;
  transition: border-color var(--transition-fast), box-shadow var(--transition-fast);
}

.field-input::placeholder {
  color: var(--color-text-placeholder);
}

.field-input:focus {
  border-color: var(--color-primary);
  box-shadow: 0 0 0 3px var(--color-primary-subtle);
}

.login-btn {
  width: 100%;
  height: 46px;
  font-size: 15px;
  font-weight: var(--weight-semibold);
  font-family: var(--font-sans);
  color: var(--color-bg-card);
  background: var(--color-primary);
  border: none;
  border-radius: var(--radius-md);
  cursor: pointer;
  transition: background var(--transition-fast), transform var(--transition-fast);
  letter-spacing: 0.1em;
}

.login-btn:active {
  background: var(--color-primary-dark);
  transform: scale(0.98);
}

.login-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.login-tip {
  margin-top: 20px;
  text-align: center;
  font-size: 12px;
  color: var(--color-text-placeholder);
}
</style>
