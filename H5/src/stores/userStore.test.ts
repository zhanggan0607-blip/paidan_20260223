/**
 * H5端用户Store测试
 * 测试用户状态管理、权限判断、持久化
 */
import { describe, it, expect, beforeEach, vi } from 'vitest'
import { setActivePinia, createPinia } from 'pinia'
import { nextTick } from 'vue'
import { useUserStore } from '../stores/userStore'

describe('useUserStore', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    localStorage.clear()
  })

  describe('初始状态', () => {
    it('初始状态应为未登录', () => {
      const store = useUserStore()
      expect(store.isLoggedIn).toBe(false)
      expect(store.currentUser).toBeNull()
      expect(store.token).toBeNull()
    })

    it('初始角色判断应为false', () => {
      const store = useUserStore()
      expect(store.isAdmin).toBe(false)
      expect(store.isManager).toBe(false)
      expect(store.isEmployee).toBe(false)
    })
  })

  describe('setUser', () => {
    it('设置用户后应更新currentUser', () => {
      const store = useUserStore()
      const user = {
        id: 1,
        name: '测试用户',
        role: '管理员' as const,
        department: '技术部',
        phone: '13800000001',
      }
      store.setUser(user)
      expect(store.currentUser).toEqual(user)
    })

    it('设置管理员用户后isAdmin应为true', () => {
      const store = useUserStore()
      store.setUser({
        id: 1,
        name: '管理员',
        role: '管理员',
        department: '技术部',
        phone: '13800000001',
      })
      expect(store.isAdmin).toBe(true)
      expect(store.isManager).toBe(true)
    })

    it('设置运维人员后isAdmin应为false', () => {
      const store = useUserStore()
      store.setUser({
        id: 2,
        name: '运维人员',
        role: '运维人员',
        department: '运维部',
        phone: '13800000002',
      })
      expect(store.isAdmin).toBe(false)
      expect(store.isEmployee).toBe(true)
    })
  })

  describe('setToken', () => {
    it('设置token后应更新token值', () => {
      const store = useUserStore()
      store.setToken('test-token-123')
      expect(store.token).toBe('test-token-123')
    })

    it('设置token和user后isLoggedIn应为true', () => {
      const store = useUserStore()
      store.setToken('test-token-123')
      store.setUser({
        id: 1,
        name: '测试',
        role: '管理员',
        department: '技术部',
        phone: '13800000001',
      })
      expect(store.isLoggedIn).toBe(true)
    })

    it('仅设置token不设置user时isLoggedIn应为false', () => {
      const store = useUserStore()
      store.setToken('test-token-123')
      expect(store.isLoggedIn).toBe(false)
    })
  })

  describe('clearUser', () => {
    it('清除用户后所有状态应重置', () => {
      const store = useUserStore()
      store.setUser({
        id: 1,
        name: '测试',
        role: '管理员',
        department: '技术部',
        phone: '13800000001',
      })
      store.setToken('test-token')
      store.setRefreshToken('refresh-token')

      store.clearUser()

      expect(store.currentUser).toBeNull()
      expect(store.token).toBeNull()
      expect(store.refreshToken).toBeNull()
      expect(store.isLoggedIn).toBe(false)
    })
  })

  describe('权限判断', () => {
    it('管理员应能查看所有工单', () => {
      const store = useUserStore()
      store.setUser({
        id: 1,
        name: '管理员',
        role: '管理员',
        department: '技术部',
        phone: '13800000001',
      })
      expect(store.canViewAllWorkOrders()).toBe(true)
    })

    it('运维人员不能查看所有工单', () => {
      const store = useUserStore()
      store.setUser({
        id: 2,
        name: '运维人员',
        role: '运维人员',
        department: '运维部',
        phone: '13800000002',
      })
      expect(store.canViewAllWorkOrders()).toBe(false)
    })

    it('材料员不能查看工单', () => {
      const store = useUserStore()
      store.setUser({
        id: 3,
        name: '材料员',
        role: '材料员',
        department: '材料部',
        phone: '13800000003',
      })
      expect(store.canViewWorkOrder()).toBe(false)
    })

    it('管理员应能查看统计', () => {
      const store = useUserStore()
      store.setUser({
        id: 1,
        name: '管理员',
        role: '管理员',
        department: '技术部',
        phone: '13800000001',
      })
      expect(store.canViewStatistics()).toBe(true)
    })

    it('所有角色应能查看项目信息', () => {
      const store = useUserStore()
      store.setUser({
        id: 2,
        name: '运维人员',
        role: '运维人员',
        department: '运维部',
        phone: '13800000002',
      })
      expect(store.canViewProjectInfo()).toBe(true)
    })
  })

  describe('localStorage持久化', () => {
    it('setToken后应同步到localStorage', async () => {
      const store = useUserStore()
      store.setToken('persisted-token')
      await nextTick()
      expect(localStorage.getItem('token')).toBe('persisted-token')
    })

    it('setUser后应同步到localStorage', async () => {
      const store = useUserStore()
      store.setUser({
        id: 1,
        name: '持久化用户',
        role: '管理员',
        department: '技术部',
        phone: '13800000001',
      })
      await nextTick()
      const stored = localStorage.getItem('user')
      expect(stored).not.toBeNull()
      expect(JSON.parse(stored!).name).toBe('持久化用户')
    })

    it('clearUser后应清除localStorage', async () => {
      const store = useUserStore()
      store.setToken('token-to-clear')
      store.setUser({
        id: 1,
        name: '待清除',
        role: '管理员',
        department: '技术部',
        phone: '13800000001',
      })
      await nextTick()
      store.clearUser()
      await nextTick()
      expect(localStorage.getItem('token')).toBeNull()
      expect(localStorage.getItem('user')).toBeNull()
    })
  })
})
