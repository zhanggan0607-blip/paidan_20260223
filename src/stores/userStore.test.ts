/**
 * PC端用户Store测试
 * 测试用户状态管理、权限判断、持久化
 */
import { describe, it, expect, beforeEach } from 'vitest'
import { userStore } from './userStore'

describe('userStore', () => {
  beforeEach(() => {
    localStorage.clear()
    userStore.clearUser()
  })

  describe('初始状态', () => {
    it('初始状态应为未登录', () => {
      expect(userStore.isLoggedIn.value).toBe(false)
      expect(userStore.getUser()).toBeNull()
      expect(userStore.getToken()).toBeNull()
    })
  })

  describe('setUser', () => {
    it('设置用户后应更新currentUser', () => {
      const user = {
        id: 1,
        name: '测试管理员',
        role: '管理员' as const,
        department: '技术部',
        phone: '13800000001',
      }
      userStore.setUser(user)
      expect(userStore.getUser()).toEqual(user)
    })

    it('设置管理员后isAdmin应为true', () => {
      userStore.setUser({
        id: 1,
        name: '管理员',
        role: '管理员',
        department: '技术部',
        phone: '13800000001',
      })
      expect(userStore.isAdmin()).toBe(true)
      expect(userStore.isManager()).toBe(true)
    })

    it('设置运维人员后isAdmin应为false', () => {
      userStore.setUser({
        id: 2,
        name: '运维人员',
        role: '运维人员',
        department: '运维部',
        phone: '13800000002',
      })
      expect(userStore.isAdmin()).toBe(false)
      expect(userStore.isManager()).toBe(false)
    })

    it('设置部门经理后isManager应为true，isAdmin也应为true（ADMIN_ROLES包含部门经理）', () => {
      userStore.setUser({
        id: 3,
        name: '部门经理',
        role: '部门经理',
        department: '运维部',
        phone: '13800000003',
      })
      expect(userStore.isManager()).toBe(true)
      expect(userStore.isAdmin()).toBe(true)
    })
  })

  describe('setToken', () => {
    it('设置token后应更新token值', () => {
      userStore.setToken('test-token-123')
      expect(userStore.getToken()).toBe('test-token-123')
    })

    it('设置token和user后isLoggedIn应为true', () => {
      userStore.setToken('test-token')
      userStore.setUser({
        id: 1,
        name: '测试',
        role: '管理员',
        department: '技术部',
        phone: '13800000001',
      })
      expect(userStore.isLoggedIn.value).toBe(true)
    })

    it('仅设置token不设置user时isLoggedIn应为false', () => {
      userStore.setToken('test-token')
      expect(userStore.isLoggedIn.value).toBe(false)
    })
  })

  describe('clearUser', () => {
    it('清除用户后所有状态应重置', () => {
      userStore.setUser({
        id: 1,
        name: '测试',
        role: '管理员',
        department: '技术部',
        phone: '13800000001',
      })
      userStore.setToken('test-token')
      userStore.setRefreshToken('refresh-token')

      userStore.clearUser()

      expect(userStore.getUser()).toBeNull()
      expect(userStore.getToken()).toBeNull()
      expect(userStore.getRefreshToken()).toBeNull()
      expect(userStore.isLoggedIn.value).toBe(false)
    })
  })

  describe('权限判断', () => {
    it('管理员和部门经理应能删除工单', () => {
      userStore.setUser({
        id: 1,
        name: '管理员',
        role: '管理员',
        department: '技术部',
        phone: '13800000001',
      })
      expect(userStore.canDeleteWorkOrder()).toBe(true)

      userStore.setUser({
        id: 3,
        name: '部门经理',
        role: '部门经理',
        department: '运维部',
        phone: '13800000003',
      })
      expect(userStore.canDeleteWorkOrder()).toBe(true)
    })

    it('运维人员不能删除工单', () => {
      userStore.setUser({
        id: 2,
        name: '运维人员',
        role: '运维人员',
        department: '运维部',
        phone: '13800000002',
      })
      expect(userStore.canDeleteWorkOrder()).toBe(false)
    })

    it('canShowMenu应根据角色返回正确结果', () => {
      userStore.setUser({
        id: 1,
        name: '管理员',
        role: '管理员',
        department: '技术部',
        phone: '13800000001',
      })
      expect(userStore.canShowMenu('statistics')).toBe(true)
      expect(userStore.canShowMenu('personnel')).toBe(true)
    })

    it('运维人员也能看到统计菜单（STATISTICS_VIEW_ROLES包含运维人员）', () => {
      userStore.setUser({
        id: 2,
        name: '运维人员',
        role: '运维人员',
        department: '运维部',
        phone: '13800000002',
      })
      expect(userStore.canShowMenu('statistics')).toBe(true)
    })

    it('isMaterialManager应正确判断', () => {
      userStore.setUser({
        id: 4,
        name: '材料员',
        role: '材料员',
        department: '材料部',
        phone: '13800000004',
      })
      expect(userStore.isMaterialManager()).toBe(true)
    })
  })

  describe('localStorage持久化', () => {
    it('setToken后应同步到localStorage', () => {
      userStore.setToken('persisted-token')
      expect(localStorage.getItem('token')).toBe('persisted-token')
    })

    it('setUser后应同步到localStorage', () => {
      userStore.setUser({
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
      userStore.setToken('token-to-clear')
      userStore.setUser({
        id: 1,
        name: '待清除',
        role: '管理员',
        department: '技术部',
        phone: '13800000001',
      })
      userStore.clearUser()
      expect(localStorage.getItem('token')).toBeNull()
      expect(localStorage.getItem('user')).toBeNull()
    })

    it('setRefreshToken后应同步到localStorage', () => {
      userStore.setRefreshToken('refresh-persisted')
      expect(localStorage.getItem('refresh_token')).toBe('refresh-persisted')
    })
  })
})
