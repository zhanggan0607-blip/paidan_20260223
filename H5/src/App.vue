<script setup lang="ts">
import { RouterView } from 'vue-router'
import { onMounted, ref } from 'vue'
import { useUserStore } from './stores/user'
import { dingtalkService } from './services/dingtalk'
import { showLoadingToast, closeToast, showToast } from 'vant'

const userStore = useUserStore()
const isInitialized = ref(false)

onMounted(async () => {
  if (userStore.isLoggedIn) {
    isInitialized.value = true
    return
  }

  if (dingtalkService.isInDingTalk()) {
    const toast = showLoadingToast({
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
        showToast({
          message: '登录成功',
          type: 'success',
        })
      } else {
        showToast({
          message: response.message || '钉钉登录失败',
          type: 'fail',
        })
      }
    } catch (error: any) {
      console.error('钉钉免登失败:', error)
      showToast({
        message: error.message || '钉钉登录失败，请刷新重试',
        type: 'fail',
      })
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
