import { defineStore } from 'pinia'
import { ref, computed, watch } from 'vue'
import type { User } from '@sstcp/shared'
import { decodeJwtPayload, isTokenExpired, fetchCurrentUser, refreshAccessToken } from '@sstcp/shared'
import { hasPermission as sharedHasPermission } from '@sstcp/shared'
import { PERMISSION_CONFIGS } from '../config/permission'

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
    return currentUser.value?.role === '运维人员'
  }

  function isMaterialManager(): boolean {
    return currentUser.value?.role === '材料员'
  }

  function canViewStatistics(): boolean {
    return sharedHasPermission(currentUser.value?.role, 'view_statistics', PERMISSION_CONFIGS)
  }

  function canViewPersonnel(): boolean {
    return sharedHasPermission(currentUser.value?.role, 'view_personnel', PERMISSION_CONFIGS)
  }

  function canViewSpareParts(): boolean {
    return sharedHasPermission(currentUser.value?.role, 'view_spare_parts_stock', PERMISSION_CONFIGS)
  }

  function canViewRepairTools(): boolean {
    return sharedHasPermission(currentUser.value?.role, 'view_repair_tools_stock', PERMISSION_CONFIGS)
  }

  function canViewWorkOrder(): boolean {
    return sharedHasPermission(currentUser.value?.role, 'view_work_order', PERMISSION_CONFIGS)
  }

  function canApprovePeriodicInspection(): boolean {
    return sharedHasPermission(currentUser.value?.role, 'approve_periodic_inspection', PERMISSION_CONFIGS)
  }

  function canApproveTemporaryRepair(): boolean {
    return sharedHasPermission(currentUser.value?.role, 'approve_temporary_repair', PERMISSION_CONFIGS)
  }

  function canApproveSpotWork(): boolean {
    return sharedHasPermission(currentUser.value?.role, 'approve_spot_work', PERMISSION_CONFIGS)
  }

  function canFillMaintenanceLog(): boolean {
    return sharedHasPermission(currentUser.value?.role, 'fill_maintenance_log', PERMISSION_CONFIGS)
  }

  function canViewMaintenanceLog(): boolean {
    return sharedHasPermission(currentUser.value?.role, 'view_maintenance_log', PERMISSION_CONFIGS)
  }

  function canViewAllMaintenanceLog(): boolean {
    return sharedHasPermission(currentUser.value?.role, 'view_all_maintenance_log', PERMISSION_CONFIGS)
  }

  function canFillWeeklyReport(): boolean {
    return sharedHasPermission(currentUser.value?.role, 'fill_weekly_report', PERMISSION_CONFIGS)
  }

  function canViewWeeklyReport(): boolean {
    return sharedHasPermission(currentUser.value?.role, 'view_weekly_report', PERMISSION_CONFIGS)
  }

  function canViewAlerts(): boolean {
    return sharedHasPermission(currentUser.value?.role, 'view_alerts', PERMISSION_CONFIGS)
  }

  function canViewSystemManagement(): boolean {
    return sharedHasPermission(currentUser.value?.role, 'view_system_management', PERMISSION_CONFIGS)
  }

  function canDeletePersonnel(): boolean {
    return sharedHasPermission(currentUser.value?.role, 'delete_personnel', PERMISSION_CONFIGS)
  }

  function canEditPersonnelRole(): boolean {
    return sharedHasPermission(currentUser.value?.role, 'edit_personnel_role', PERMISSION_CONFIGS)
  }

  function canViewProjectManagement(): boolean {
    return sharedHasPermission(currentUser.value?.role, 'view_project_management', PERMISSION_CONFIGS)
  }

  function canViewPeriodicInspection(): boolean {
    return sharedHasPermission(currentUser.value?.role, 'view_periodic_inspection', PERMISSION_CONFIGS)
  }

  function canViewTemporaryRepair(): boolean {
    return sharedHasPermission(currentUser.value?.role, 'view_temporary_repair', PERMISSION_CONFIGS)
  }

  function canViewSpotWork(): boolean {
    return sharedHasPermission(currentUser.value?.role, 'view_spot_work', PERMISSION_CONFIGS)
  }

  function canApplySpotWork(): boolean {
    return sharedHasPermission(currentUser.value?.role, 'apply_spot_work', PERMISSION_CONFIGS)
  }

  function canQuickFillSpotWork(): boolean {
    return sharedHasPermission(currentUser.value?.role, 'quick_fill_spot_work', PERMISSION_CONFIGS)
  }

  function canViewProjectInfo(): boolean {
    return sharedHasPermission(currentUser.value?.role, 'view_project_info', PERMISSION_CONFIGS)
  }

  function canViewWorkList(): boolean {
    return sharedHasPermission(currentUser.value?.role, 'view_work_list', PERMISSION_CONFIGS)
  }

  function canViewSignature(): boolean {
    return sharedHasPermission(currentUser.value?.role, 'view_signature', PERMISSION_CONFIGS)
  }

  function canViewMaintenanceLogDetail(): boolean {
    return sharedHasPermission(currentUser.value?.role, 'view_maintenance_log_detail', PERMISSION_CONFIGS)
  }

  function canViewDepartmentWeeklyReport(): boolean {
    return sharedHasPermission(currentUser.value?.role, 'view_department_weekly_report', PERMISSION_CONFIGS)
  }

  function canViewAllWeeklyReport(): boolean {
    return sharedHasPermission(currentUser.value?.role, 'view_all_weekly_report', PERMISSION_CONFIGS)
  }

  function canViewAllWorkOrders(): boolean {
    return sharedHasPermission(currentUser.value?.role, 'view_all_work_orders', PERMISSION_CONFIGS)
  }

  function canCreateTemporaryRepair(): boolean {
    return sharedHasPermission(currentUser.value?.role, 'create_temporary_repair', PERMISSION_CONFIGS)
  }

  function canViewSparePartsIssue(): boolean {
    return sharedHasPermission(currentUser.value?.role, 'view_spare_parts_issue', PERMISSION_CONFIGS)
  }

  function canViewSparePartsStock(): boolean {
    return sharedHasPermission(currentUser.value?.role, 'view_spare_parts_stock', PERMISSION_CONFIGS)
  }

  function canViewRepairToolsIssue(): boolean {
    return sharedHasPermission(currentUser.value?.role, 'view_repair_tools_issue', PERMISSION_CONFIGS)
  }

  function canViewRepairToolsInbound(): boolean {
    return sharedHasPermission(currentUser.value?.role, 'view_repair_tools_inbound', PERMISSION_CONFIGS)
  }

  function canViewRepairToolsStock(): boolean {
    return sharedHasPermission(currentUser.value?.role, 'view_repair_tools_stock', PERMISSION_CONFIGS)
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
    canViewPeriodicInspection,
    canViewTemporaryRepair,
    canViewSpotWork,
    canApplySpotWork,
    canQuickFillSpotWork,
    canViewProjectInfo,
    canViewWorkList,
    canViewSignature,
    canViewMaintenanceLogDetail,
    canViewDepartmentWeeklyReport,
    canViewAllWeeklyReport,
    canViewAllWorkOrders,
    canCreateTemporaryRepair,
    canViewSparePartsIssue,
    canViewSparePartsStock,
    canViewRepairToolsIssue,
    canViewRepairToolsInbound,
    canViewRepairToolsStock,
  }
})
