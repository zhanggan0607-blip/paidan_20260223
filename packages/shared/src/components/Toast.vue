<template>
  <div
    v-if="visible"
    :class="['toast', `toast-${type}`, `toast-${position}`, { 'toast-show': show }]"
    @click="handleClick"
  >
    <div class="toast-icon">
      <span v-if="type === 'success'">✓</span>
      <span v-else-if="type === 'error'">✕</span>
      <span v-else-if="type === 'warning'">!</span>
      <span v-else>ℹ</span>
    </div>
    <div class="toast-message">{{ message }}</div>
  </div>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue'

const props = withDefaults(defineProps<{
  visible?: boolean
  message: string
  type?: 'success' | 'error' | 'warning' | 'info'
  duration?: number
  position?: 'top-right' | 'top-center' | 'bottom-center'
}>(), {
  visible: false,
  type: 'info',
  duration: 3000,
  position: 'top-right',
})

const show = ref(false)
let timer: ReturnType<typeof setTimeout> | null = null

const handleClick = () => {
  show.value = false
}

watch(
  () => props.visible,
  (newVal) => {
    if (newVal) {
      setTimeout(() => {
        show.value = true
      }, 10)

      if (timer) {
        clearTimeout(timer)
      }

      timer = setTimeout(() => {
        show.value = false
      }, props.duration)
    } else {
      show.value = false
      if (timer) {
        clearTimeout(timer)
      }
    }
  }
)
</script>

<style scoped>
.toast {
  position: fixed;
  min-width: 300px;
  max-width: 500px;
  padding: 16px 20px;
  border-radius: 8px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  display: flex;
  align-items: center;
  gap: 12px;
  z-index: 10000;
  opacity: 0;
  transition: all 0.3s ease-out;
  cursor: pointer;
}

.toast-top-right {
  top: 20px;
  right: 20px;
  transform: translateX(100%);
}

.toast-top-center {
  top: 20px;
  left: 50%;
  transform: translateX(-50%) translateY(-20px);
}

.toast-bottom-center {
  bottom: 20px;
  left: 50%;
  transform: translateX(-50%) translateY(20px);
}

.toast-show.toast-top-right {
  opacity: 1;
  transform: translateX(0);
}

.toast-show.toast-top-center {
  opacity: 1;
  transform: translateX(-50%) translateY(0);
}

.toast-show.toast-bottom-center {
  opacity: 1;
  transform: translateX(-50%) translateY(0);
}

.toast-success {
  background: #43a047;
  color: #fff;
}

.toast-error {
  background: #d32f2f;
  color: #fff;
}

.toast-warning {
  background: #ffa000;
  color: #fff;
}

.toast-info {
  background: #2196f3;
  color: #fff;
}

.toast-icon {
  width: 24px;
  height: 24px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 16px;
  font-weight: bold;
  flex-shrink: 0;
}

.toast-message {
  flex: 1;
  font-size: 14px;
  line-height: 1.5;
  word-break: break-word;
}
</style>
