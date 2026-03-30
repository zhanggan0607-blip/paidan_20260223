/**
 * Toast 消息提示 Composable
 * 提供统一的 Toast 消息管理
 */
import { ref, readonly } from 'vue'

interface ToastState {
  visible: boolean
  message: string
  type: 'success' | 'error' | 'warning' | 'info'
}

const toastState = ref<ToastState>({
  visible: false,
  message: '',
  type: 'success',
})

let hideTimer: ReturnType<typeof setTimeout> | null = null

export function useToast() {
  const show = (
    message: string,
    type: 'success' | 'error' | 'warning' | 'info' = 'success',
    duration: number = 3000
  ) => {
    if (hideTimer) {
      clearTimeout(hideTimer)
    }

    toastState.value = {
      visible: true,
      message,
      type,
    }

    hideTimer = setTimeout(() => {
      toastState.value.visible = false
    }, duration)
  }

  const hide = () => {
    if (hideTimer) {
      clearTimeout(hideTimer)
    }
    toastState.value.visible = false
  }

  const success = (message: string, duration?: number) => show(message, 'success', duration)
  const error = (message: string, duration?: number) => show(message, 'error', duration)
  const warning = (message: string, duration?: number) => show(message, 'warning', duration)
  const info = (message: string, duration?: number) => show(message, 'info', duration)

  return {
    toast: readonly(toastState),
    show,
    hide,
    success,
    error,
    warning,
    info,
  }
}
