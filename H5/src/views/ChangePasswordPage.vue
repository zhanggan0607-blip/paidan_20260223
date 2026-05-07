<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { showToast, showLoadingToast, closeToast } from 'vant'
import { request } from '../api/request'
import { useUserStore } from '../stores/userStore'

const userStore = useUserStore()
const router = useRouter()

const formData = ref({
  old_password: '',
  new_password: '',
})
const confirmPassword = ref('')
const loading = ref(false)

const PASSWORD_MIN_LENGTH = 6

const validatePassword = (password: string): string | null => {
  if (password.length < PASSWORD_MIN_LENGTH) {
    return `新密码至少需要${PASSWORD_MIN_LENGTH}位`
  }
  return null
}

const handleChangePassword = async () => {
  if (!formData.value.old_password) {
    showToast('请输入旧密码')
    return
  }
  const passwordError = validatePassword(formData.value.new_password)
  if (passwordError) {
    showToast(passwordError)
    return
  }
  if (formData.value.new_password !== confirmPassword.value) {
    showToast('两次输入的新密码不一致')
    return
  }
  if (formData.value.old_password === formData.value.new_password) {
    showToast('新密码不能与旧密码相同')
    return
  }

  loading.value = true
  showLoadingToast({
    message: '修改中...',
    forbidClick: true,
    duration: 0,
  })

  try {
    const response = await request.post('/auth/change-password', formData.value) as any

    if (response.code === 200) {
      const user = userStore.currentUser
      if (user) {
        userStore.setUser({
          ...user,
          must_change_password: false,
        } as any)
      }
      showToast({ type: 'success', message: '密码修改成功' })
      setTimeout(() => {
        router.replace('/')
      }, 1000)
    } else {
      showToast(response.message || '修改失败')
    }
  } catch (error: any) {
    let msg = '修改失败，请重试'
    if (error?.message) {
      if (typeof error.message === 'string') {
        msg = error.message
      } else if (Array.isArray(error.message)) {
        msg = error.message.map((e: { msg?: string }) => e.msg || String(e)).join('; ')
      } else {
        msg = String(error.message)
      }
    }
    showToast(msg)
  } finally {
    loading.value = false
    closeToast()
  }
}
</script>

<template>
  <div class="change-password-page">
    <div class="change-password-header">
      <div class="header-grid"></div>
      <div class="header-content">
        <div class="brand-icon">
          <svg width="36" height="36" viewBox="0 0 36 36" fill="none">
            <rect x="2" y="2" width="32" height="32" rx="6" stroke="currentColor" stroke-width="2" />
            <path d="M10 18h16M18 10v16M12 12l12 12M24 12L12 24" stroke="currentColor" stroke-width="1.5" opacity="0.4" />
            <circle cx="18" cy="18" r="4" stroke="currentColor" stroke-width="2" />
          </svg>
        </div>
        <h1 class="brand-title">修改密码</h1>
        <p class="brand-subtitle">首次登录需要修改密码</p>
      </div>
    </div>

    <form class="change-password-form" @submit.prevent="handleChangePassword">
      <div class="form-title">设置新密码</div>

      <div class="form-fields">
        <div class="field-group">
          <label for="oldPassword" class="field-label">旧密码</label>
          <input
            v-model="formData.old_password"
            type="password" id="oldPassword" name="oldPassword"
            class="field-input"
            placeholder="请输入旧密码"
            autocomplete="current-password"
          />
        </div>
        <div class="field-group">
          <label for="newPassword" class="field-label">新密码</label>
          <input
            v-model="formData.new_password"
            type="password" id="newPassword" name="newPassword"
            class="field-input"
            placeholder="请输入新密码（至少6位）"
            autocomplete="new-password"
          />
        </div>
        <div class="field-group">
          <label for="confirmPassword" class="field-label">确认新密码</label>
          <input
            v-model="confirmPassword"
            type="password" id="confirmPassword" name="confirmPassword"
            class="field-input"
            placeholder="请再次输入新密码"
            autocomplete="new-password"
          />
        </div>
      </div>

      <button type="submit" class="submit-btn" :disabled="loading">
        <span v-if="!loading">确认修改</span>
        <span v-else>修改中...</span>
      </button>
    </form>
  </div>
</template>

<style scoped>
.change-password-page {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  background: var(--color-bg-page);
}

.change-password-header {
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
  color: #e74c3c;
  letter-spacing: 0.08em;
}

.change-password-form {
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

.submit-btn {
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

.submit-btn:active {
  background: var(--color-primary-dark);
  transform: scale(0.98);
}

.submit-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}
</style>
