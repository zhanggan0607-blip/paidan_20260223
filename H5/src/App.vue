<script setup lang="ts">
import { RouterView } from 'vue-router'
import { onMounted, ref } from 'vue'
import { userStore } from './stores/userStore'
import { dingtalkService } from './services/dingtalk'
import { showLoadingToast, closeToast, showSuccessToast, showFailToast } from 'vant'

const isInitialized = ref(false)

onMounted(async () => {
  if (userStore.isLoggedIn()) {
    isInitialized.value = true
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
