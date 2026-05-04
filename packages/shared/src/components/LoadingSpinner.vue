<template>
  <div v-if="visible" class="loading-overlay" :class="{ 'loading-overlay-fullscreen': fullscreen }">
    <div class="loading-spinner" :style="{ width: size, height: size }"></div>
    <div v-if="text" class="loading-text">{{ text }}</div>
  </div>
</template>

<script setup lang="ts">
withDefaults(defineProps<{
  visible?: boolean
  text?: string
  size?: string
  fullscreen?: boolean
}>(), {
  visible: false,
  text: '加载中...',
  size: '50px',
  fullscreen: true,
})
</script>

<style scoped>
.loading-overlay {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  background: rgba(255, 255, 255, 0.9);
}

.loading-overlay-fullscreen {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  z-index: 9999;
}

.loading-spinner {
  border: 4px solid #f3f3f3;
  border-top: 4px solid #2196f3;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  0% {
    transform: rotate(0deg);
  }
  100% {
    transform: rotate(360deg);
  }
}

.loading-text {
  margin-top: 20px;
  font-size: 16px;
  color: #333;
  font-weight: 500;
}
</style>
