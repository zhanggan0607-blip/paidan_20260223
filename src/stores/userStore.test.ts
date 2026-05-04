import { describe, it, expect, beforeEach } from 'vitest'
import { useUserStore } from './userStore'
import { setActivePinia, createPinia } from 'pinia'

describe('userStore', () => {
  beforeEach(() => {
    localStorage.clear()
    setActivePinia(createPinia())
  })

  function getStore() {
    return useUserStore()
  }

  describe('初始状态', () => {
    it('初始状态应为未登录', () => {
      expect(getStore().isLoggedIn).toBe(false)
      expect(getStore().currentUser).toBeNull()
      expect(getStore().token).toBeNull()
    })
  })

  describe('setUser', () => {
    it('设置用户后应更新currentUser', () => {
      const store = getStore()
      const user = {
        id: 1,
        name: '测试管理员',
        role: '管理员' as const,
        department: '技术部',
        phone: '13800000001',
      }
      store.setUser(user)
      expect(store.currentUser).toEqual(user)
    })

    it('设置管理员后isAdmin应为true', () => {
      const store = getStore()
      store.setUser({
        id: 1,
        name: '管理员',
        role: '管理员',
        department: '技术部',
        phone: '13800000001',
      })
      expect(store.isAdmin()).toBe(true)
      expect(store.isManager()).toBe(true)
    })

    it('设置运维人员后isAdmin应为false', () => {
      const store = getStore()
      store.setUser({
        id: 2,
        name: '运维人员',
        role: '运维人员',
        department: '运维部',
        phone: '13800000002',
      })
      expect(store.isAdmin()).toBe(false)
      expect(store.isManager()).toBe(false)
    })

    it('设置部门经理后isManager应为true，isAdmin也应为true', () => {
      const store = getStore()
      store.setUser({
        id: 3,
        name: '部门经理',
        role: '部门经理',
        department: '运维部',
        phone: '13800000003',
      })
      expect(store.isManager()).toBe(true)
      expect(store.isAdmin()).toBe(true)
    })
  })

  describe('setToken', () => {
    it('设置token后应更新token值', () => {
      const store = getStore()
      store.setToken('test-token-123')
      expect(store.token).toBe('test-token-123')
    })

    it('设置token和user后isLoggedIn应为true', () => {
      const store = getStore()
      store.setToken('test-token')
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
      const store = getStore()
      store.setToken('test-token')
      expect(store.isLoggedIn).toBe(false)
    })
  })

  describe('clearUser', () => {
    it('清除用户后所有状态应重置', () => {
      const store = getStore()
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
    it('管理员和部门经理应能删除工单', () => {
      const store = getStore()
      store.setUser({
        id: 1,
        name: '管理员',
        role: '管理员',
        department: '技术部',
        phone: '13800000001',
      })
      expect(store.canDeleteWorkOrder()).toBe(true)

      store.setUser({
        id: 3,
        name: '部门经理',
        role: '部门经理',
        department: '运维部',
        phone: '13800000003',
      })
      expect(store.canDeleteWorkOrder()).toBe(true)
    })

    it('运维人员不能删除工单', () => {
      const store = getStore()
      store.setUser({
        id: 2,
        name: '运维人员',
        role: '运维人员',
        department: '运维部',
        phone: '13800000002',
      })
      expect(store.canDeleteWorkOrder()).toBe(false)
    })

    it('canShowMenu应根据角色返回正确结果', () => {
      const store = getStore()
      store.setUser({
        id: 1,
        name: '管理员',
        role: '管理员',
        department: '技术部',
        phone: '13800000001',
      })
      expect(store.canShowMenu('statistics')).toBe(true)
      expect(store.canShowMenu('personnel')).toBe(true)
    })

    it('运维人员也能看到统计菜单', () => {
      const store = getStore()
      store.setUser({
        id: 2,
        name: '运维人员',
        role: '运维人员',
        department: '运维部',
        phone: '13800000002',
      })
      expect(store.canShowMenu('statistics')).toBe(true)
    })

    it('isMaterialManager应正确判断', () => {
      const store = getStore()
      store.setUser({
        id: 4,
        name: '材料员',
        role: '材料员',
        department: '材料部',
        phone: '13800000004',
      })
      expect(store.isMaterialManager()).toBe(true)
    })
  })

  describe('localStorage持久化', () => {
    it('setToken后应同步到localStorage', () => {
      const store = getStore()
      store.setToken('persisted-token')
      expect(localStorage.getItem('token')).toBe('persisted-token')
    })

    it('setUser后应同步到localStorage', () => {
      const store = getStore()
      store.setUser({
        id: 1,
        name: '持久化用户',
        role: '管理员',
        department: '技术部',
        phone: '13800000001',
      })
      const stored = localStorage.getItem('user')
      expect(stored).not.toBeNull()
      expect(JSON.parse(stored!).name).toBe('持久化用户')
    })

    it('clearUser后应清除localStorage', () => {
      const store = getStore()
      store.setToken('token-to-clear')
      store.setUser({
        id: 1,
        name: '待清除',
        role: '管理员',
        department: '技术部',
        phone: '13800000001',
      })
      store.clearUser()
      expect(localStorage.getItem('token')).toBeNull()
      expect(localStorage.getItem('user')).toBeNull()
    })

    it('setRefreshToken后应同步到localStorage', () => {
      const store = getStore()
      store.setRefreshToken('refresh-persisted')
      expect(localStorage.getItem('refresh_token')).toBe('refresh-persisted')
    })
  })
})
