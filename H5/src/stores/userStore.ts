/**
 * H5端用户状态管理 - Pinia Store
 * 使用标准的Pinia Store模式，支持DevTools调试和持久化
 *
 * 状态存储：localStorage (token/refresh_token/user)
 * 登录判断：isLoggedIn = !!token && !!currentUser
 *
 * TODO: 启动时应调用 /auth/me 验证token有效性，避免过期token仍显示已登录
 * TODO: 后端应支持Token黑名单机制，登出/改密码时使旧token失效
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

export const userStore = {
  get readonlyCurrentUser() {
    const store = useUserStore()
    return store.currentUser
  },

  getUser(): User | null {
    return useUserStore().currentUser
  },

  setUser(user: User): void {
    useUserStore().setUser(user)
  },

  clearUser(): void {
    useUserStore().clearUser()
  },

  getToken(): string | null {
    return useUserStore().token
  },

  setToken(token: string): void {
    useUserStore().setToken(token)
  },

  getRefreshToken(): string | null {
    return useUserStore().refreshToken
  },

  setRefreshToken(refreshToken: string): void {
    useUserStore().setRefreshToken(refreshToken)
  },

  isLoggedIn(): boolean {
    return useUserStore().isLoggedIn
  },

  isAdmin(): boolean {
    return useUserStore().isAdmin
  },

  isDepartmentManager(): boolean {
    return useUserStore().isDepartmentManager
  },

  isMaterialManager(): boolean {
    return useUserStore().isMaterialManagerRole
  },

  isEmployee(): boolean {
    return useUserStore().isEmployee
  },

  canViewAllWorkOrders(): boolean {
    return useUserStore().canViewAllWorkOrders()
  },

  canViewPersonnel(): boolean {
    return useUserStore().canViewPersonnel()
  },

  canViewStatistics(): boolean {
    return useUserStore().canViewStatistics()
  },

  canViewProjectManagement(): boolean {
    return useUserStore().canViewProjectManagement()
  },

  canViewWorkOrder(): boolean {
    return useUserStore().canViewWorkOrder()
  },

  canViewSparePartsInventory(): boolean {
    return useUserStore().canViewSparePartsInventory()
  },

  canViewSparePartsStock(): boolean {
    return useUserStore().canViewSparePartsStock()
  },

  canViewSparePartsIssue(): boolean {
    return useUserStore().canViewSparePartsIssue()
  },

  canViewRepairToolsStock(): boolean {
    return useUserStore().canViewRepairToolsStock()
  },

  canViewRepairToolsInbound(): boolean {
    return useUserStore().canViewRepairToolsInbound()
  },

  canViewRepairToolsIssue(): boolean {
    return useUserStore().canViewRepairToolsIssue()
  },

  canViewAlerts(): boolean {
    return useUserStore().canViewAlerts()
  },

  canViewSystemManagement(): boolean {
    return useUserStore().canViewSystemManagement()
  },

  canViewPeriodicInspection(): boolean {
    return useUserStore().canViewPeriodicInspection()
  },

  canApprovePeriodicInspection(): boolean {
    return useUserStore().canApprovePeriodicInspection()
  },

  canApproveTemporaryRepair(): boolean {
    return useUserStore().canApproveTemporaryRepair()
  },

  canApproveSpotWork(): boolean {
    return useUserStore().canApproveSpotWork()
  },

  canViewTemporaryRepair(): boolean {
    return useUserStore().canViewTemporaryRepair()
  },

  canViewSpotWork(): boolean {
    return useUserStore().canViewSpotWork()
  },

  canApplySpotWork(): boolean {
    return useUserStore().canApplySpotWork()
  },

  canViewProjectInfo(): boolean {
    return useUserStore().canViewProjectInfo()
  },

  canQuickFillSpotWork(): boolean {
    return useUserStore().canQuickFillSpotWork()
  },

  canViewMaintenanceLog(): boolean {
    return useUserStore().canViewMaintenanceLog()
  },

  canViewMaintenanceLogDetail(): boolean {
    return useUserStore().canViewMaintenanceLogDetail()
  },

  canFillMaintenanceLog(): boolean {
    return useUserStore().canFillMaintenanceLog()
  },

  canViewAllMaintenanceLog(): boolean {
    return useUserStore().canViewAllMaintenanceLog()
  },

  canViewDepartmentWeeklyReport(): boolean {
    return useUserStore().canViewDepartmentWeeklyReport()
  },

  canViewAllWeeklyReport(): boolean {
    return useUserStore().canViewAllWeeklyReport()
  },

  canApproveWeeklyReport(): boolean {
    return useUserStore().canApproveWeeklyReport()
  },

  canViewWorkList(): boolean {
    return useUserStore().canViewWorkList()
  },

  canViewSignature(): boolean {
    return useUserStore().canViewSignature()
  },

  isManager(): boolean {
    return useUserStore().isManager
  },

  hasPermission(permissionId: string): boolean {
    return useUserStore().checkPermission(permissionId)
  },
}
