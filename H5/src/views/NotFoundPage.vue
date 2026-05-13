<script setup lang="ts">
import { useRouter } from 'vue-router'
import { Button as VanButton } from 'vant'

const router = useRouter()

const goHome = () => {
  router.replace('/')
}
</script>

<template>
  <div class="not-found-page">
    <div class="not-found-content">
      <div class="error-code">404</div>
      <div class="error-message">页面不存在</div>
      <div class="error-desc">您访问的页面可能已被移除或暂时不可用</div>
      <van-button type="primary" class="home-btn" @click="goHome"> 返回首页 </van-button>
    </div>
  </div>
</template>

<style scoped>
.not-found-page {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  background: var(--color-bg-page, #f7f8fa);
}

.not-found-content {
  text-align: center;
  padding: 40px 20px;
}

.error-code {
  font-size: 72px;
  font-weight: 700;
  color: var(--color-primary, #1989fa);
  line-height: 1;
  margin-bottom: 16px;
}

.error-message {
  font-size: 20px;
  font-weight: 600;
  color: var(--color-text-primary, #323233);
  margin-bottom: 8px;
}

.error-desc {
  font-size: 14px;
  color: var(--color-text-secondary, #969799);
  margin-bottom: 32px;
}

.home-btn {
  min-width: 120px;
}
</style>
