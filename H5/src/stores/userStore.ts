/**
 * H5端用户状态管理 - Pinia Store
 * 使用标准的Pinia Store模式，支持DevTools调试和持久化
 *
 * 状态存储：localStorage (token/refresh_token/user)
 * 登录判断：isLoggedIn = !!token && !!currentUser
 */
import { defineStore } from 'pinia'
import { ref, computed, watch } from 'vue'
import type { User } from '@sstcp/shared'
import {
  RoleCode,
  hasPermission,
  isManagerRole,
  isAdminRole,
  isMaterialManager,
} from '../config/permission'

const USER_STORAGE_KEY = 'user'
const TOKEN_STORAGE_KEY = 'token'
const REFRESH_TOKEN_STORAGE_KEY = 'refresh_token'

function loadUserFromStorage(): User | null {
  const userStr = localStorage.getItem(USER_STORAGE_KEY)
  if (userStr) {
    try {
      return JSON.parse(userStr)
    } catch {
      return null
    }
  }
  return null
}

function decodeJwtPayload(token: string): { exp?: number; [key: string]: unknown } | null {
  try {
    const parts = token.split('.')
    if (parts.length !== 3) return null
    const base64 = parts[1].replace(/-/g, '+').replace(/_/g, '/')
    const jsonStr = decodeURIComponent(
      atob(base64)
        .split('')
        .map((c) => '%' + ('00' + c.charCodeAt(0).toString(16)).slice(-2))
        .join('')
    )
    return JSON.parse(jsonStr)
  } catch {
    return null
  }
}

function isTokenExpired(token: string): boolean {
  const payload = decodeJwtPayload(token)
  if (!payload || !payload.exp) return true
  return Date.now() >= payload.exp * 1000
}

async function refreshAccessToken(refreshTokenValue: string): Promise<{ accessToken: string; refreshToken: string } | null> {
  try {
    const basePath = import.meta.env.PROD ? '/api/v1' : (import.meta.env.VITE_API_BASE_URL || '/api/v1')
    const response = await fetch(`${basePath}/auth/refresh`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ refresh_token: refreshTokenValue }),
    })
    if (!response.ok) return null
    const result = await response.json()
    if (result.code === 200 && result.data?.access_token) {
      return {
        accessToken: result.data.access_token,
        refreshToken: result.data.refresh_token || refreshTokenValue,
      }
    }
    return null
  } catch {
    return null
  }
}

async function fetchCurrentUser(tokenValue: string): Promise<User | null> {
  if (isTokenExpired(tokenValue)) return null
  try {
    const basePath = import.meta.env.PROD ? '/api/v1' : (import.meta.env.VITE_API_BASE_URL || '/api/v1')
    const response = await fetch(`${basePath}/auth/me`, {
      headers: { Authorization: `Bearer ${tokenValue}` },
    })
    if (!response.ok) return null
    const result = await response.json()
    if (result.code === 200 && result.data) {
      return {
        id: result.data.id,
        name: result.data.name,
        role: result.data.role,
        department: result.data.department,
        phone: result.data.phone,
        must_change_password: result.data.must_change_password,
      } as User
    }
    return null
  } catch {
    return null
  }
}

export const useUserStore = defineStore('user', () => {
  const currentUser = ref<User | null>(loadUserFromStorage())
  const token = ref<string | null>(localStorage.getItem(TOKEN_STORAGE_KEY))
  const refreshToken = ref<string | null>(localStorage.getItem(REFRESH_TOKEN_STORAGE_KEY))

  watch(
    currentUser,
    (newUser) => {
      if (newUser) {
        localStorage.setItem(USER_STORAGE_KEY, JSON.stringify(newUser))
      } else {
        localStorage.removeItem(USER_STORAGE_KEY)
      }
    },
    { deep: true }
  )

  watch(token, (newToken) => {
    if (newToken) {
      localStorage.setItem(TOKEN_STORAGE_KEY, newToken)
    } else {
      localStorage.removeItem(TOKEN_STORAGE_KEY)
    }
  })

  watch(refreshToken, (newRefreshToken) => {
    if (newRefreshToken) {
      localStorage.setItem(REFRESH_TOKEN_STORAGE_KEY, newRefreshToken)
    } else {
      localStorage.removeItem(REFRESH_TOKEN_STORAGE_KEY)
    }
  })

  if (typeof window !== 'undefined') {
    window.addEventListener('storage', (e: StorageEvent) => {
      if (e.key === TOKEN_STORAGE_KEY) {
        token.value = e.newValue
      }
      if (e.key === REFRESH_TOKEN_STORAGE_KEY) {
        refreshToken.value = e.newValue
      }
      if (e.key === USER_STORAGE_KEY) {
        if (e.newValue) {
          try {
            currentUser.value = JSON.parse(e.newValue)
          } catch {
            currentUser.value = null
          }
        } else {
          currentUser.value = null
        }
      }
    })
  }

  const isLoggedIn = computed(() => !!token.value && !!currentUser.value)
  const isAdmin = computed(() => isAdminRole(currentUser.value?.role))
  const isDepartmentManager = computed(() => currentUser.value?.role === RoleCode.DEPARTMENT_MANAGER)
  const isMaterialManagerRole = computed(() => isMaterialManager(currentUser.value?.role))
  const isEmployee = computed(() => currentUser.value?.role === RoleCode.EMPLOYEE)
  const isManager = computed(() => isManagerRole(currentUser.value?.role))

  function setUser(user: User): void {
    currentUser.value = user
    window.dispatchEvent(new CustomEvent('user-changed', { detail: user }))
  }

  function clearUser(): void {
    currentUser.value = null
    token.value = null
    refreshToken.value = null
    window.dispatchEvent(new CustomEvent('user-changed', { detail: null }))
  }

  async function validateToken(): Promise<boolean> {
    if (!token.value) {
      clearUser()
      return false
    }

    let user = await fetchCurrentUser(token.value)
    if (user) {
      currentUser.value = user
      return true
    }

    if (refreshToken.value) {
      const tokens = await refreshAccessToken(refreshToken.value)
      if (tokens) {
        token.value = tokens.accessToken
        refreshToken.value = tokens.refreshToken
        user = await fetchCurrentUser(tokens.accessToken)
        if (user) {
          currentUser.value = user
          return true
        }
      }
    }

    clearUser()
    return false
  }

  function setToken(newToken: string): void {
    token.value = newToken
  }

  function setRefreshToken(newRefreshToken: string): void {
    refreshToken.value = newRefreshToken
  }

  function canViewAllWorkOrders(): boolean {
    return hasPermission(currentUser.value?.role, 'view_all_work_orders')
  }

  function canViewPersonnel(): boolean {
    return hasPermission(currentUser.value?.role, 'view_personnel')
  }

  function canViewStatistics(): boolean {
    return hasPermission(currentUser.value?.role, 'view_statistics')
  }

  function canViewProjectManagement(): boolean {
    return hasPermission(currentUser.value?.role, 'view_project_management')
  }

  function canViewWorkOrder(): boolean {
    return !isMaterialManager(currentUser.value?.role)
  }

  function canViewSparePartsInventory(): boolean {
    return hasPermission(currentUser.value?.role, 'view_spare_parts_inventory')
  }

  function canViewSparePartsStock(): boolean {
    return hasPermission(currentUser.value?.role, 'view_spare_parts_stock')
  }

  function canViewSparePartsIssue(): boolean {
    return hasPermission(currentUser.value?.role, 'view_spare_parts_issue')
  }

  function canViewRepairToolsStock(): boolean {
    return hasPermission(currentUser.value?.role, 'view_repair_tools_stock')
  }

  function canViewRepairToolsInbound(): boolean {
    return hasPermission(currentUser.value?.role, 'view_repair_tools_inbound')
  }

  function canViewRepairToolsIssue(): boolean {
    return hasPermission(currentUser.value?.role, 'view_repair_tools_issue')
  }

  function canViewAlerts(): boolean {
    return hasPermission(currentUser.value?.role, 'view_alerts')
  }

  function canViewSystemManagement(): boolean {
    return hasPermission(currentUser.value?.role, 'view_system_management')
  }

  function canViewPeriodicInspection(): boolean {
    return !isMaterialManager(currentUser.value?.role)
  }

  function canApprovePeriodicInspection(): boolean {
    return hasPermission(currentUser.value?.role, 'approve_periodic_inspection')
  }

  function canApproveTemporaryRepair(): boolean {
    return hasPermission(currentUser.value?.role, 'approve_temporary_repair')
  }

  function canApproveSpotWork(): boolean {
    return hasPermission(currentUser.value?.role, 'approve_spot_work')
  }

  function canViewTemporaryRepair(): boolean {
    return !isMaterialManager(currentUser.value?.role)
  }

  function canViewSpotWork(): boolean {
    return !isMaterialManager(currentUser.value?.role)
  }

  function canApplySpotWork(): boolean {
    return hasPermission(currentUser.value?.role, 'apply_spot_work')
  }

  function canViewProjectInfo(): boolean {
    return true
  }

  function canQuickFillSpotWork(): boolean {
    return !isMaterialManager(currentUser.value?.role)
  }

  function canViewMaintenanceLog(): boolean {
    return hasPermission(currentUser.value?.role, 'view_maintenance_log')
  }

  function canViewMaintenanceLogDetail(): boolean {
    return hasPermission(currentUser.value?.role, 'view_maintenance_log_detail')
  }

  function canFillMaintenanceLog(): boolean {
    return hasPermission(currentUser.value?.role, 'fill_maintenance_log')
  }

  function canViewAllMaintenanceLog(): boolean {
    return hasPermission(currentUser.value?.role, 'view_all_maintenance_log')
  }

  function canViewDepartmentWeeklyReport(): boolean {
    return hasPermission(currentUser.value?.role, 'view_department_weekly_report')
  }

  function canViewAllWeeklyReport(): boolean {
    return hasPermission(currentUser.value?.role, 'view_all_weekly_report')
  }

  function canApproveWeeklyReport(): boolean {
    return hasPermission(currentUser.value?.role, 'approve_weekly_report')
  }

  function canViewWorkList(): boolean {
    return !isMaterialManager(currentUser.value?.role)
  }

  function canViewSignature(): boolean {
    return !isMaterialManager(currentUser.value?.role)
  }

  function checkPermission(permissionId: string): boolean {
    return hasPermission(currentUser.value?.role, permissionId)
  }

  return {
    currentUser,
    token,
    refreshToken,
    isLoggedIn,
    isAdmin,
    isDepartmentManager,
    isMaterialManagerRole,
    isEmployee,
    isManager,
    setUser,
    clearUser,
    validateToken,
    setToken,
    setRefreshToken,
    canViewAllWorkOrders,
    canViewPersonnel,
    canViewStatistics,
    canViewProjectManagement,
    canViewWorkOrder,
    canViewSparePartsInventory,
    canViewSparePartsStock,
    canViewSparePartsIssue,
    canViewRepairToolsStock,
    canViewRepairToolsInbound,
    canViewRepairToolsIssue,
    canViewAlerts,
    canViewSystemManagement,
    canViewPeriodicInspection,
    canApprovePeriodicInspection,
    canApproveTemporaryRepair,
    canApproveSpotWork,
    canViewTemporaryRepair,
    canViewSpotWork,
    canApplySpotWork,
    canViewProjectInfo,
    canQuickFillSpotWork,
    canViewMaintenanceLog,
    canViewMaintenanceLogDetail,
    canFillMaintenanceLog,
    canViewAllMaintenanceLog,
    canViewDepartmentWeeklyReport,
    canViewAllWeeklyReport,
    canApproveWeeklyReport,
    canViewWorkList,
    canViewSignature,
    checkPermission,
  }
})
