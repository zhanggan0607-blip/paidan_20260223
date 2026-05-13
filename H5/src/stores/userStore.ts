import { defineStore } from 'pinia'
import { ref, computed, watch } from 'vue'
import type { User } from '@sstcp/shared'
import { decodeJwtPayload, isTokenExpired, fetchCurrentUser, refreshAccessToken } from '@sstcp/shared'
import { COMMON_PERMISSION_CONFIGS, hasPermission as sharedHasPermission } from '@sstcp/shared'

const TOKEN_KEY = 'h5_token'
const REFRESH_TOKEN_KEY = 'h5_refresh_token'
const USER_KEY = 'h5_user'

export const useUserStore = defineStore('user', () => {
  const storedToken = localStorage.getItem(TOKEN_KEY)
  const storedUser = localStorage.getItem(USER_KEY)
  const storedRefreshToken = localStorage.getItem(REFRESH_TOKEN_KEY)

  const currentUser = ref<User | null>(storedUser ? (() => {
    try { return JSON.parse(storedUser) } catch (_e) { return null }
  })() : null)
  const token = ref<string | null>(storedToken)
  const refreshToken = ref<string | null>(storedRefreshToken)

  watch(currentUser, (newUser) => {
    if (newUser) {
      localStorage.setItem(USER_KEY, JSON.stringify(newUser))
    } else {
      localStorage.removeItem(USER_KEY)
    }
    window.dispatchEvent(new CustomEvent('user-changed', { detail: newUser }))
  }, { deep: true, flush: 'sync' })

  watch(token, (newToken) => {
    if (newToken) {
      localStorage.setItem(TOKEN_KEY, newToken)
    } else {
      localStorage.removeItem(TOKEN_KEY)
    }
  }, { flush: 'sync' })

  watch(refreshToken, (newRefreshToken) => {
    if (newRefreshToken) {
      localStorage.setItem(REFRESH_TOKEN_KEY, newRefreshToken)
    } else {
      localStorage.removeItem(REFRESH_TOKEN_KEY)
    }
  }, { flush: 'sync' })

  window.addEventListener('storage', (e: StorageEvent) => {
    if (e.key === TOKEN_KEY) {
      token.value = e.newValue
    }
    if (e.key === USER_KEY) {
      if (e.newValue) {
        try {
          currentUser.value = JSON.parse(e.newValue)
        } catch (_e) {
          currentUser.value = null
        }
      } else {
        currentUser.value = null
      }
    }
    if (e.key === REFRESH_TOKEN_KEY) {
      refreshToken.value = e.newValue
    }
  })

  const isLoggedIn = computed(() => !!token.value && !!currentUser.value)

  function getUser(): User | null {
    return currentUser.value
  }

  function getToken(): string | null {
    return token.value
  }

  function getRefreshTokenValue(): string | null {
    return refreshToken.value
  }

  function setUser(user: User) {
    currentUser.value = user
  }

  function setToken(newToken: string) {
    token.value = newToken
  }

  function setRefreshToken(newRefreshToken: string) {
    refreshToken.value = newRefreshToken
  }

  function clearUser() {
    currentUser.value = null
    token.value = null
    refreshToken.value = null
  }

  async function validateToken(): Promise<boolean> {
    if (!token.value) {
      clearUser()
      return false
    }
    const basePath = import.meta.env.VITE_API_BASE_PATH || '/api/v1'
    const user = await fetchCurrentUser(token.value, basePath)
    if (user) {
      currentUser.value = user
      return true
    }
    clearUser()
    return false
  }

  async function refreshAccessTokenAction(): Promise<boolean> {
    if (!refreshToken.value) return false
    const basePath = import.meta.env.VITE_API_BASE_PATH || '/api/v1'
    const result = await refreshAccessToken(refreshToken.value, basePath)
    if (result) {
      token.value = result.accessToken
      refreshToken.value = result.refreshToken
      return true
    }
    clearUser()
    return false
  }

  function isAdmin(): boolean {
    return currentUser.value?.role === '管理员'
  }

  function isManager(): boolean {
    const role = currentUser.value?.role
    return role === '管理员' || role === '部门经理' || role === '主管'
  }

  function isDepartmentManager(): boolean {
    return currentUser.value?.role === '部门经理'
  }

  function isSupervisor(): boolean {
    return currentUser.value?.role === '主管'
  }

  function isWorker(): boolean {
    return currentUser.value?.role === '维保人员'
  }

  function isMaterialManager(): boolean {
    return currentUser.value?.role === '材料员'
  }

  function canViewStatistics(): boolean {
    return sharedHasPermission('view_statistics', currentUser.value?.role, COMMON_PERMISSION_CONFIGS)
  }

  function canViewPersonnel(): boolean {
    return sharedHasPermission('view_personnel', currentUser.value?.role, COMMON_PERMISSION_CONFIGS)
  }

  function canViewSpareParts(): boolean {
    return sharedHasPermission('view_spare_parts_stock', currentUser.value?.role, COMMON_PERMISSION_CONFIGS)
  }

  function canViewRepairTools(): boolean {
    return sharedHasPermission('view_repair_tools_stock', currentUser.value?.role, COMMON_PERMISSION_CONFIGS)
  }

  function canViewWorkOrder(): boolean {
    return sharedHasPermission('view_work_order', currentUser.value?.role, COMMON_PERMISSION_CONFIGS)
  }

  function canApprovePeriodicInspection(): boolean {
    return sharedHasPermission('approve_periodic_inspection', currentUser.value?.role, COMMON_PERMISSION_CONFIGS)
  }

  function canApproveTemporaryRepair(): boolean {
    return sharedHasPermission('approve_temporary_repair', currentUser.value?.role, COMMON_PERMISSION_CONFIGS)
  }

  function canApproveSpotWork(): boolean {
    return sharedHasPermission('approve_spot_work', currentUser.value?.role, COMMON_PERMISSION_CONFIGS)
  }

  function canFillMaintenanceLog(): boolean {
    return sharedHasPermission('fill_maintenance_log', currentUser.value?.role, COMMON_PERMISSION_CONFIGS)
  }

  function canViewMaintenanceLog(): boolean {
    return sharedHasPermission('view_maintenance_log', currentUser.value?.role, COMMON_PERMISSION_CONFIGS)
  }

  function canViewAllMaintenanceLog(): boolean {
    return sharedHasPermission('view_all_maintenance_log', currentUser.value?.role, COMMON_PERMISSION_CONFIGS)
  }

  function canFillWeeklyReport(): boolean {
    return sharedHasPermission('fill_weekly_report', currentUser.value?.role, COMMON_PERMISSION_CONFIGS)
  }

  function canViewWeeklyReport(): boolean {
    return sharedHasPermission('view_weekly_report', currentUser.value?.role, COMMON_PERMISSION_CONFIGS)
  }

  function canViewAlerts(): boolean {
    return sharedHasPermission('view_alerts', currentUser.value?.role, COMMON_PERMISSION_CONFIGS)
  }

  function canViewSystemManagement(): boolean {
    return sharedHasPermission('view_system_management', currentUser.value?.role, COMMON_PERMISSION_CONFIGS)
  }

  function canDeletePersonnel(): boolean {
    return sharedHasPermission('delete_personnel', currentUser.value?.role, COMMON_PERMISSION_CONFIGS)
  }

  function canEditPersonnelRole(): boolean {
    return sharedHasPermission('edit_personnel_role', currentUser.value?.role, COMMON_PERMISSION_CONFIGS)
  }

  function canViewProjectManagement(): boolean {
    return sharedHasPermission('view_project_management', currentUser.value?.role, COMMON_PERMISSION_CONFIGS)
  }

  return {
    currentUser,
    token,
    refreshToken,
    isLoggedIn,
    getUser,
    getToken,
    getRefreshTokenValue,
    setUser,
    setToken,
    setRefreshToken,
    clearUser,
    validateToken,
    refreshAccessToken: refreshAccessTokenAction,
    isAdmin,
    isManager,
    isDepartmentManager,
    isSupervisor,
    isWorker,
    isMaterialManager,
    canViewStatistics,
    canViewPersonnel,
    canViewSpareParts,
    canViewRepairTools,
    canViewWorkOrder,
    canApprovePeriodicInspection,
    canApproveTemporaryRepair,
    canApproveSpotWork,
    canFillMaintenanceLog,
    canViewMaintenanceLog,
    canViewAllMaintenanceLog,
    canFillWeeklyReport,
    canViewWeeklyReport,
    canViewAlerts,
    canViewSystemManagement,
    canDeletePersonnel,
    canEditPersonnelRole,
    canViewProjectManagement,
  }
})
