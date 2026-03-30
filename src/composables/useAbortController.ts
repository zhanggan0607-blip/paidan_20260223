/**
 * AbortController Composable
 * 提供统一的请求取消管理，防止内存泄漏和竞态条件
 */
import { ref, computed, onUnmounted } from 'vue'

export function useAbortController() {
  const abortController = ref<AbortController | null>(null)

  /**
   * 创建新的 AbortController
   * 如果已存在则先取消之前的请求
   */
  const createController = (): AbortController => {
    if (abortController.value) {
      abortController.value.abort()
    }
    abortController.value = new AbortController()
    return abortController.value
  }

  /**
   * 取消当前请求
   */
  const abort = (): void => {
    if (abortController.value) {
      abortController.value.abort()
      abortController.value = null
    }
  }

  /**
   * 获取当前 signal
   */
  const getSignal = (): AbortSignal | undefined => {
    return abortController.value?.signal
  }

  /**
   * 检查是否已取消
   */
  const isAborted = computed(() => {
    return abortController.value?.signal.aborted ?? false
  })

  /**
   * 检查错误是否为取消错误
   */
  const isAbortError = (error: unknown): boolean => {
    return error instanceof Error && error.name === 'AbortError'
  }

  onUnmounted(() => {
    abort()
  })

  return {
    abortController,
    signal: computed(() => abortController.value?.signal),
    createController,
    abort,
    getSignal,
    isAborted,
    isAbortError,
  }
}
