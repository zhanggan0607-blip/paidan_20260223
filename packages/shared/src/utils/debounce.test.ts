/**
 * 防抖工具函数测试
 */
import { describe, it, expect, vi } from 'vitest'
import { debounce, createDebounce } from './debounce'

describe('debounce', () => {
  it('应在延迟后执行函数', () => {
    vi.useFakeTimers()
    const fn = vi.fn()
    const debounced = debounce(fn, 300)

    debounced()
    expect(fn).not.toHaveBeenCalled()

    vi.advanceTimersByTime(300)
    expect(fn).toHaveBeenCalledTimes(1)

    vi.useRealTimers()
  })

  it('应在延迟内多次调用只执行最后一次', () => {
    vi.useFakeTimers()
    const fn = vi.fn()
    const debounced = debounce(fn, 300)

    debounced()
    debounced()
    debounced()

    vi.advanceTimersByTime(300)
    expect(fn).toHaveBeenCalledTimes(1)

    vi.useRealTimers()
  })

  it('应传递参数给原函数', () => {
    vi.useFakeTimers()
    const fn = vi.fn()
    const debounced = debounce(fn, 100)

    debounced('arg1', 'arg2')

    vi.advanceTimersByTime(100)
    expect(fn).toHaveBeenCalledWith('arg1', 'arg2')

    vi.useRealTimers()
  })

  it('默认延迟应为300ms', () => {
    vi.useFakeTimers()
    const fn = vi.fn()
    const debounced = debounce(fn)

    debounced()
    vi.advanceTimersByTime(299)
    expect(fn).not.toHaveBeenCalled()

    vi.advanceTimersByTime(1)
    expect(fn).toHaveBeenCalledTimes(1)

    vi.useRealTimers()
  })
})

describe('createDebounce', () => {
  it('应返回防抖函数和取消函数', () => {
    const fn = vi.fn()
    const { debounced, cancel } = createDebounce(fn, 300)

    expect(typeof debounced).toBe('function')
    expect(typeof cancel).toBe('function')
  })

  it('取消后不应执行函数', () => {
    vi.useFakeTimers()
    const fn = vi.fn()
    const { debounced, cancel } = createDebounce(fn, 300)

    debounced()
    cancel()

    vi.advanceTimersByTime(300)
    expect(fn).not.toHaveBeenCalled()

    vi.useRealTimers()
  })

  it('取消后再次调用应正常工作', () => {
    vi.useFakeTimers()
    const fn = vi.fn()
    const { debounced, cancel } = createDebounce(fn, 300)

    debounced()
    cancel()
    debounced()

    vi.advanceTimersByTime(300)
    expect(fn).toHaveBeenCalledTimes(1)

    vi.useRealTimers()
  })
})
