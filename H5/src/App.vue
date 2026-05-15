<script setup lang="ts">
import { RouterView } from 'vue-router'
import { onMounted, onUnmounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from './stores/userStore'
import { dingtalkService } from './services/dingtalk'
import { onlineUserService } from './services/onlineUser'
import { showLoadingToast, closeToast, showSuccessToast, showFailToast } from 'vant'
import { useHeartbeatControl } from './composables/useHeartbeatControl'
import { useDingtalkAuth } from './composables/useDingtalkAuth'

const router = useRouter()
const userStore = useUserStore()
const isInitialized = ref(false)
let heartbeatTimer: number | null = null
const HEARTBEAT_INTERVAL = 2 * 60 * 1000

const { dingtalkAuthReady, isDingtalkEnv } = useDingtalkAuth()

const heartbeatControl = useHeartbeatControl()

const sendHeartbeat = async () => {
  if (heartbeatControl.getIsPaused()) return

  const user = userStore.currentUser
  if (!user || !userStore.isLoggedIn) return

  try {
    await onlineUserService.heartbeat('h5', user.id, user.name)
  } catch {}
}

const startHeartbeat = () => {
  stopHeartbeat()
  sendHeartbeat()
  heartbeatTimer = window.setInterval(() => {
    if (!heartbeatControl.getIsPaused()) {
      sendHeartbeat()
    }
  }, HEARTBEAT_INTERVAL)
}

const stopHeartbeat = () => {
  if (heartbeatTimer) {
    clearInterval(heartbeatTimer)
    heartbeatTimer = null
  }
}

onMounted(async () => {
  if (userStore.isLoggedIn) {
    const isValid = await userStore.validateToken()
    if (isValid) {
      isInitialized.value = true
      startHeartbeat()
      return
    }
    userStore.clearUser()
  }

  if (dingtalkService.isInDingTalk()) {
    isDingtalkEnv.value = true
    showLoadingToast({
      message: '钉钉登录中...',
      forbidClick: true,
      duration: 0,
    })

    try {
      const authCode = await dingtalkService.getAuthCode()
      const response = await dingtalkService.login(authCode)

      if (response.code === 200 && response.data) {
        userStore.setToken(response.data.access_token)
        if (response.data.refresh_token) {
          userStore.setRefreshToken(response.data.refresh_token)
        }
        userStore.setUser(response.data.user)
        closeToast()
        showSuccessToast('登录成功')
        startHeartbeat()
        router.replace('/')
      } else {
        closeToast()
        showFailToast(response.message || '钉钉登录失败')
        setTimeout(() => router.replace('/login'), 1500)
      }
    } catch (error: any) {
      console.error('钉钉免登失败:', error)
      closeToast()
      if (error?.status === 403) {
        showFailToast('您未在系统中注册，请联系管理员')
      } else {
        showFailToast(error.message || '钉钉登录失败，请刷新重试')
        setTimeout(() => router.replace('/login'), 1500)
      }
    }
  } else {
    router.replace('/login')
  }

  isInitialized.value = true
  dingtalkAuthReady.value = true
})

onUnmounted(() => {
  stopHeartbeat()
})
</script>

<template>
  <router-view v-if="isInitialized" v-slot="{ Component }">
    <keep-alive
      :include="[
        'WorkListPage',
        'MaintenanceLogPage',
        'WeeklyReportListPage',
        'SpotWorkApplyPage',
        'SpotWorkQuickFillPage',
        'TemporaryRepairPage',
      ]"
    >
      <component :is="Component" />
    </keep-alive>
  </router-view>
  <div v-else class="loading-container">
    <van-loading size="24px">加载中...</van-loading>
  </div>
</template>

<style>
.loading-container {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100vh;
  background: var(--color-bg-page);
  color: var(--color-text-secondary);
}
</style>
