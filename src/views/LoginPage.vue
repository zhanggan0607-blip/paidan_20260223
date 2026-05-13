<template>
  <div class="login">
    <div class="login__left">
      <div class="login__brand">
        <svg
          class="login__brand-icon"
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          stroke-width="1.5"
        >
          <path d="M12 2L2 7l10 5 10-5-10-5z" />
          <path d="M2 17l10 5 10-5" />
          <path d="M2 12l10 5 10-5" />
        </svg>
        <div class="login__brand-text">
          <span class="login__brand-name">SSTCP</span>
          <span class="login__brand-desc">维保管理系统</span>
        </div>
      </div>
      <div class="login__decoration">
        <div class="login__grid">
          <div
            v-for="i in 12"
            :key="i"
            class="login__grid-cell"
            :style="{ animationDelay: `${i * 0.05}s` }"
          />
        </div>
      </div>
    </div>

    <div class="login__right">
      <div class="login__form-wrapper">
        <h2 class="login__heading">
          登录
        </h2>
        <p class="login__subheading">
          请输入您的账户信息
        </p>

        <form
          class="login__form"
          @submit.prevent="handleLogin"
        >
          <div class="field">
            <label
              for="username"
              class="field__label"
            >用户名</label>
            <input
              id="username"
              v-model="formData.username"
              type="text"
              class="field__input"
              placeholder="请输入用户名"
              :disabled="loading"
              autocomplete="username"
            >
          </div>

          <div class="field">
            <label
              for="password"
              class="field__label"
            >密码</label>
            <input
              id="password"
              v-model="formData.password"
              type="password"
              class="field__input"
              placeholder="请输入密码"
              :disabled="loading"
              autocomplete="current-password"
            >
          </div>

          <div
            v-if="errorMessage"
            class="login__error"
          >
            {{ errorMessage }}
          </div>

          <button
            type="submit"
            class="login__submit"
            :disabled="loading"
          >
            <span v-if="loading">登录中...</span>
            <span v-else>登录</span>
          </button>
        </form>

        <p class="login__hint">
          默认密码为 Sstcp@手机号后4位，如无手机号则为 Sstcp@12345
        </p>
      </div>
    </div>
  </div>
</template>

<script lang="ts">
import { defineComponent, ref, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useUserStore } from '@/stores/userStore'
import { request } from '@/api/request'
import type { ApiResponse, LoginResponse } from '@sstcp/shared'
import { getDefaultPath } from '@/config/permission'

export default defineComponent({
  name: 'LoginPage',
  setup() {
    const userStore = useUserStore()
    const router = useRouter()
    const route = useRoute()

    const formData = ref({
      username: '',
      password: '',
    })

    const loading = ref(false)
    const errorMessage = ref('')

    onMounted(() => {
      const token = userStore.token
      const currentUser = userStore.currentUser
      if (token && currentUser) {
        router.replace('/')
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
        const response = (await request.post('/auth/login-json', {
          username: formData.value.username,
          password: formData.value.password,
          device_type: 'pc',
        })) as ApiResponse<LoginResponse>

        if (response.code === 200 && response.data) {
          const { access_token, refresh_token, user } = response.data

          userStore.setToken(access_token)
          if (refresh_token) {
            userStore.setRefreshToken(refresh_token)
          }
          if (user) {
            userStore.setUser({
              id: user.id,
              name: user.name,
              role: user.role,
              department: user.department,
              phone: user.phone,
              must_change_password: (user as { must_change_password?: boolean }).must_change_password,
            })

            if ((user as { must_change_password?: boolean }).must_change_password) {
              router.replace('/change-password')
            } else {
              const redirect = (route.query.redirect as string) || getDefaultPath(user.role)
              router.replace(redirect)
            }
          } else {
            router.replace(getDefaultPath(undefined))
          }
        } else {
          errorMessage.value = response.message || '登录失败，请重试'
        }
      } catch (error: unknown) {
        const err = error as { message?: string; status?: number }
        if (err.status === 429) {
          errorMessage.value = err.message || '请求过于频繁，请稍后再试'
        } else {
          errorMessage.value = err.message || '登录失败，请检查网络连接'
        }
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
.login {
  min-height: 100vh;
  display: grid;
  grid-template-columns: 1fr 1fr;
  background: var(--color-bg-page);
}

.login__left {
  background: var(--color-sidebar-bg);
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  padding: var(--space-8);
  position: relative;
  overflow: hidden;
}

.login__brand {
  display: flex;
  align-items: center;
  gap: var(--space-3);
  position: relative;
  z-index: 1;
}

.login__brand-icon {
  width: 36px;
  height: 36px;
  color: var(--color-primary-light);
}

.login__brand-text {
  display: flex;
  flex-direction: column;
}

.login__brand-name {
  font-family: var(--font-mono);
  font-size: var(--text-2xl);
  font-weight: var(--weight-bold);
  color: #fff;
  letter-spacing: 0.1em;
  line-height: 1;
}

.login__brand-desc {
  font-size: var(--text-xs);
  color: var(--color-sidebar-text);
  opacity: 0.6;
  letter-spacing: 0.06em;
  margin-top: var(--space-1);
}

.login__decoration {
  position: absolute;
  inset: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  opacity: 0.08;
}

.login__grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: var(--space-4);
  padding: var(--space-8);
}

.login__grid-cell {
  width: 48px;
  height: 48px;
  border: 1px solid #fff;
  border-radius: var(--radius-sm);
  animation: gridPulse 3s ease-in-out infinite;
}

@keyframes gridPulse {
  0%, 100% { opacity: 0.3; }
  50% { opacity: 1; }
}

.login__right {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: var(--space-8);
}

.login__form-wrapper {
  width: 100%;
  max-width: 360px;
}

.login__heading {
  font-size: var(--text-2xl);
  font-weight: var(--weight-bold);
  color: var(--color-text-primary);
  margin-bottom: var(--space-1);
  letter-spacing: -0.01em;
}

.login__subheading {
  font-size: var(--text-sm);
  color: var(--color-text-secondary);
  margin-bottom: var(--space-8);
}

.login__form {
  display: flex;
  flex-direction: column;
  gap: var(--space-5);
}

.field {
  display: flex;
  flex-direction: column;
  gap: var(--space-1);
}

.field__label {
  font-size: var(--text-sm);
  font-weight: var(--weight-medium);
  color: var(--color-text-regular);
}

.field__input {
  padding: var(--space-2) var(--space-3);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-sm);
  font-size: var(--text-base);
  color: var(--color-text-primary);
  background: var(--color-bg-card);
  transition: border-color var(--transition-fast), box-shadow var(--transition-fast);
  height: 40px;
}

.field__input:focus {
  outline: none;
  border-color: var(--color-primary);
  box-shadow: 0 0 0 2px var(--color-primary-subtle);
}

.field__input:disabled {
  background: var(--color-bg-page);
  cursor: not-allowed;
}

.field__input::placeholder {
  color: var(--color-text-placeholder);
}

.login__error {
  font-size: var(--text-sm);
  color: var(--color-danger);
  padding: var(--space-2) var(--space-3);
  background: var(--color-danger-subtle);
  border-radius: var(--radius-sm);
  border: 1px solid var(--color-danger);
  border-opacity: 0.2;
}

.login__submit {
  padding: var(--space-3) var(--space-4);
  background: var(--color-primary);
  color: #fff;
  border: none;
  border-radius: var(--radius-sm);
  font-size: var(--text-base);
  font-weight: var(--weight-semibold);
  cursor: pointer;
  transition: background var(--transition-fast), transform var(--transition-fast);
  height: 40px;
  letter-spacing: 0.02em;
}

.login__submit:hover:not(:disabled) {
  background: var(--color-primary-dark);
}

.login__submit:active:not(:disabled) {
  transform: scale(0.98);
}

.login__submit:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.login__hint {
  margin-top: var(--space-6);
  font-size: var(--text-xs);
  color: var(--color-text-placeholder);
  text-align: center;
}

@media (max-width: 768px) {
  .login {
    grid-template-columns: 1fr;
  }

  .login__left {
    display: none;
  }
}
</style>
