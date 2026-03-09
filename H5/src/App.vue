<script setup lang="ts">
import { RouterView } from 'vue-router'
import { onMounted, onUnmounted, ref } from 'vue'
import { userStore } from './stores/userStore'
import { dingtalkService } from './services/dingtalk'
import { onlineUserService } from './services/onlineUser'
import { showLoadingToast, closeToast, showSuccessToast, showFailToast } from 'vant'

const isInitialized = ref(false)
let heartbeatTimer: number | null = null
const HEARTBEAT_INTERVAL = 2 * 60 * 1000

const sendHeartbeat = async () => {
  const user = userStore.getUser()
  if (!user || !userStore.isLoggedIn()) return

  try {
    await onlineUserService.heartbeat('h5', user.id, user.name)
  } catch {
    // 忽略心跳错误
  }
}

const startHeartbeat = () => {
  stopHeartbeat()
  sendHeartbeat()
  heartbeatTimer = window.setInterval(sendHeartbeat, HEARTBEAT_INTERVAL)
}

const stopHeartbeat = () => {
  if (heartbeatTimer) {
    clearInterval(heartbeatTimer)
    heartbeatTimer = null
  }
}

onMounted(async () => {
  if (userStore.isLoggedIn()) {
    isInitialized.value = true
    startHeartbeat()
    return
  }

  if (dingtalkService.isInDingTalk()) {
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
        userStore.setUser(response.data.user)
        showSuccessToast('登录成功')
        startHeartbeat()
      } else {
        showFailToast(response.message || '钉钉登录失败')
      }
    } catch (error: any) {
      console.error('钉钉免登失败:', error)
      showFailToast(error.message || '钉钉登录失败，请刷新重试')
    } finally {
      closeToast()
    }
  }

  isInitialized.value = true
})

onUnmounted(() => {
  stopHeartbeat()
})
</script>

<template>
  <router-view v-if="isInitialized" v-slot="{ Component }">
    <keep-alive>
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
}
</style>
