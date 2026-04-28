/**
 * 防抖工具函数
 * 用于延迟执行函数，避免频繁调用
 */

/**
 * 防抖函数类型
 */
export type DebouncedFunction<T extends (...args: unknown[]) => unknown> = (
  ...args: Parameters<T>
) => void

/**
 * 创建防抖函数
 * @param fn 需要防抖的函数
 * @param delay 延迟时间（毫秒），默认 300ms
 * @returns 防抖后的函数
 */
export function debounce<T extends (...args: unknown[]) => unknown>(
  fn: T,
  delay: number = 300
): DebouncedFunction<T> {
  let timer: ReturnType<typeof setTimeout> | null = null

  return function (this: unknown, ...args: Parameters<T>) {
    if (timer) {
      clearTimeout(timer)
    }
    timer = setTimeout(() => {
      fn.apply(this, args)
      timer = null
    }, delay)
  }
}

/**
 * 创建带清理功能的防抖函数
 * @param fn 需要防抖的函数
 * @param delay 延迟时间（毫秒），默认 300ms
 * @returns 包含防抖函数和清理函数的对象
 */
export function createDebounce<T extends (...args: unknown[]) => unknown>(
  fn: T,
  delay: number = 300
): {
  debounced: DebouncedFunction<T>
  cancel: () => void
} {
  let timer: ReturnType<typeof setTimeout> | null = null

  const debounced = function (this: unknown, ...args: Parameters<T>) {
    if (timer) {
      clearTimeout(timer)
    }
    timer = setTimeout(() => {
      fn.apply(this, args)
      timer = null
    }, delay)
  }

  const cancel = () => {
    if (timer) {
      clearTimeout(timer)
      timer = null
    }
  }

  return { debounced, cancel }
}
