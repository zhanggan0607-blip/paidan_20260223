/**
 * H5端API缓存测试
 * 测试缓存读写、TTL过期、键管理
 */
import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest'
import { apiCache, CACHE_KEYS, CACHE_TTL } from '../utils/apiCache'

describe('ApiCache', () => {
  beforeEach(() => {
    apiCache.clear()
    vi.useFakeTimers()
  })

  afterEach(() => {
    vi.useRealTimers()
  })

  describe('基本读写', () => {
    it('写入后应能读取', () => {
      apiCache.set('test-key', { name: '测试' })
      const result = apiCache.get<{ name: string }>('test-key')
      expect(result).toEqual({ name: '测试' })
    })

    it('未写入的key应返回null', () => {
      expect(apiCache.get('nonexistent')).toBeNull()
    })

    it('删除后应返回null', () => {
      apiCache.set('test-key', 'value')
      apiCache.delete('test-key')
      expect(apiCache.get('test-key')).toBeNull()
    })

    it('clear应清除所有缓存', () => {
      apiCache.set('key1', 'val1')
      apiCache.set('key2', 'val2')
      apiCache.clear()
      expect(apiCache.get('key1')).toBeNull()
      expect(apiCache.get('key2')).toBeNull()
    })
  })

  describe('TTL过期', () => {
    it('未过期的缓存应可读取', () => {
      apiCache.set('test-key', 'value', 60000)
      expect(apiCache.get('test-key')).toBe('value')
    })

    it('过期的缓存应返回null', () => {
      apiCache.set('test-key', 'value', 60000)
      vi.advanceTimersByTime(61000)
      expect(apiCache.get('test-key')).toBeNull()
    })

    it('不同TTL的缓存应独立过期', () => {
      apiCache.set('short', 'val1', 30000)
      apiCache.set('long', 'val2', 120000)
      vi.advanceTimersByTime(31000)
      expect(apiCache.get('short')).toBeNull()
      expect(apiCache.get('long')).toBe('val2')
    })
  })

  describe('has方法', () => {
    it('存在的缓存应返回true', () => {
      apiCache.set('test-key', 'value')
      expect(apiCache.has('test-key')).toBe(true)
    })

    it('不存在的缓存应返回false', () => {
      expect(apiCache.has('nonexistent')).toBe(false)
    })

    it('过期的缓存应返回false', () => {
      apiCache.set('test-key', 'value', 60000)
      vi.advanceTimersByTime(61000)
      expect(apiCache.has('test-key')).toBe(false)
    })
  })

  describe('缓存键常量', () => {
    it('CACHE_KEYS应包含必要的键', () => {
      expect(CACHE_KEYS.PROJECT_INFO).toBeDefined()
      expect(CACHE_KEYS.PERSONNEL).toBeDefined()
      expect(CACHE_KEYS.CUSTOMER).toBeDefined()
      expect(CACHE_KEYS.STATISTICS).toBeDefined()
      expect(CACHE_KEYS.TEMPORARY_REPAIR_PENDING).toBeDefined()
    })

    it('CACHE_TTL应包含三档时间', () => {
      expect(CACHE_TTL.SHORT).toBeLessThan(CACHE_TTL.MEDIUM)
      expect(CACHE_TTL.MEDIUM).toBeLessThan(CACHE_TTL.LONG)
    })
  })

  describe('数据类型支持', () => {
    it('应支持对象类型', () => {
      const data = { id: 1, name: '测试', items: [1, 2, 3] }
      apiCache.set('obj-key', data)
      expect(apiCache.get('obj-key')).toEqual(data)
    })

    it('应支持数组类型', () => {
      const data = [{ id: 1 }, { id: 2 }]
      apiCache.set('arr-key', data)
      expect(apiCache.get('arr-key')).toEqual(data)
    })

    it('应支持null值', () => {
      apiCache.set('null-key', null)
      expect(apiCache.get('null-key')).toBeNull()
    })
  })
})
