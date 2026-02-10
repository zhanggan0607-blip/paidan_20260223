<template>
  <div v-if="visible" :class="['toast', `toast-${type}`, { 'toast-show': show }]" @click="handleClick">
    <div class="toast-icon">
      <span v-if="type === 'success'">✓</span>
      <span v-else-if="type === 'error'">✕</span>
      <span v-else-if="type === 'warning'">!</span>
      <span v-else>ℹ</span>
    </div>
    <div class="toast-message">{{ message }}</div>
  </div>
</template>

<script lang="ts">
import { defineComponent, ref, watch } from 'vue'

export default defineComponent({
  name: 'Toast',
  props: {
    visible: {
      type: Boolean,
      default: false
    },
    message: {
      type: String,
      required: true
    },
    type: {
      type: String as () => 'success' | 'error' | 'warning' | 'info',
      default: 'info'
    },
    duration: {
      type: Number,
      default: 3000
    }
  },
  setup(props) {
    const show = ref(false)
    let timer: number | null = null

    const handleClick = () => {
      show.value = false
    }

    watch(() => props.visible, (newVal) => {
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
    })

    return {
      show,
      handleClick
    }
  }
})
</script>

<style scoped>
.toast {
  position: fixed;
  top: 20px;
  right: 20px;
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
  transform: translateX(100%);
  transition: all 0.3s ease-out;
}

.toast-show {
  opacity: 1;
  transform: translateX(0);
}

.toast-success {
  background: #43a047;
  color: #fff;
}

.toast-error {
  background: #D32F2F;
  color: #fff;
}

.toast-warning {
  background: #FFA000;
  color: #fff;
}

.toast-info {
  background: #2196F3;
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