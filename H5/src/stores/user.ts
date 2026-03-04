/**
 * 用户状态管理
 * 使用 Pinia 进行状态管理
 */
import { defineStore } from 'pinia'
import { ref, computed, watch } from 'vue'
import {
  RoleCode,
  hasPermission,
  isManagerRole,
  isAdminRole,
  isMaterialManager
} from '../config/permission'
import { onlineUserService } from '../services/onlineUser'

export interface User {
  id: number
  name: string
  role: string
  department: string
  phone: string
}

const USER_STORAGE_KEY = 'user'
const TOKEN_STORAGE_KEY = 'token'

let heartbeatInterval: number | null = null

const startHeartbeat = () => {
  stopHeartbeat()
  onlineUserService.sendHeartbeat('h5').catch(() => {})
  heartbeatInterval = window.setInterval(() => {
    const token = localStorage.getItem(TOKEN_STORAGE_KEY)
    if (token) {
      onlineUserService.sendHeartbeat('h5').catch(() => {})
    }
  }, 1 * 60 * 1000)
}

const stopHeartbeat = () => {
  if (heartbeatInterval) {
    clearInterval(heartbeatInterval)
    heartbeatInterval = null
  }
}

const loadUserFromStorage = (): User | null => {
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
  const user = ref<User | null>(loadUserFromStorage())
  const token = ref<string | null>(localStorage.getItem(TOKEN_STORAGE_KEY))

  watch(user, (newUser) => {
    if (newUser) {
      localStorage.setItem(USER_STORAGE_KEY, JSON.stringify(newUser))
    }
  }, { deep: true })

  const isLoggedIn = computed(() => !!token.value)
  const isAdmin = computed(() => isAdminRole(user.value?.role))
  const isDepartmentManager = computed(() => user.value?.role === RoleCode.DEPARTMENT_MANAGER)
  const isMaterialManagerRole = computed(() => isMaterialManager(user.value?.role))
  const isEmployee = computed(() => user.value?.role === RoleCode.EMPLOYEE)
  const isManager = computed(() => isManagerRole(user.value?.role))

  function setUser(newUser: User) {
    if (user.value && user.value.id !== newUser.id) {
      onlineUserService.logout(user.value.id, 'h5').catch(() => {})
    }
    user.value = newUser
    localStorage.setItem(USER_STORAGE_KEY, JSON.stringify(newUser))
    window.dispatchEvent(new CustomEvent('user-changed', { detail: newUser }))
  }

  function clearUser() {
    stopHeartbeat()
    if (user.value) {
      onlineUserService.logout(user.value.id, 'h5').catch(() => {})
    }
    user.value = null
    token.value = null
    localStorage.removeItem(USER_STORAGE_KEY)
    localStorage.removeItem(TOKEN_STORAGE_KEY)
    window.dispatchEvent(new CustomEvent('user-changed', { detail: null }))
  }

  function setToken(newToken: string) {
    token.value = newToken
    localStorage.setItem(TOKEN_STORAGE_KEY, newToken)
    startHeartbeat()
  }

  function canManagePersonnel(): boolean {
    return hasPermission(user.value?.role, 'manage_personnel')
  }

  function canManageProjects(): boolean {
    return hasPermission(user.value?.role, 'manage_projects')
  }

  function canManageSpareParts(): boolean {
    return hasPermission(user.value?.role, 'manage_spare_parts')
  }

  function canViewAllWorkOrders(): boolean {
    return hasPermission(user.value?.role, 'view_all_work_orders')
  }

  function canViewPersonnel(): boolean {
    return hasPermission(user.value?.role, 'view_personnel')
  }

  function canViewStatistics(): boolean {
    return hasPermission(user.value?.role, 'view_statistics')
  }

  function canViewProjectManagement(): boolean {
    return hasPermission(user.value?.role, 'view_project_management')
  }

  function canViewWorkOrder(): boolean {
    return !isMaterialManager(user.value?.role)
  }

  function canViewSparePartsInventory(): boolean {
    return hasPermission(user.value?.role, 'view_spare_parts_inventory')
  }

  function canViewSparePartsStock(): boolean {
    return hasPermission(user.value?.role, 'view_spare_parts_stock')
  }

  function canViewSparePartsIssue(): boolean {
    return hasPermission(user.value?.role, 'view_spare_parts_issue')
  }

  function canViewRepairToolsStock(): boolean {
    return hasPermission(user.value?.role, 'view_repair_tools_stock')
  }

  function canViewRepairToolsInbound(): boolean {
    return hasPermission(user.value?.role, 'view_repair_tools_inbound')
  }

  function canViewRepairToolsIssue(): boolean {
    return hasPermission(user.value?.role, 'view_repair_tools_issue')
  }

  function canViewAlerts(): boolean {
    return hasPermission(user.value?.role, 'view_alerts')
  }

  function canViewSystemManagement(): boolean {
    return hasPermission(user.value?.role, 'view_system_management')
  }

  function canViewPeriodicInspection(): boolean {
    return !isMaterialManager(user.value?.role)
  }

  function canApprovePeriodicInspection(): boolean {
    return hasPermission(user.value?.role, 'approve_periodic_inspection')
  }

  function canApproveTemporaryRepair(): boolean {
    return hasPermission(user.value?.role, 'approve_temporary_repair')
  }

  function canApproveSpotWork(): boolean {
    return hasPermission(user.value?.role, 'approve_spot_work')
  }

  function canViewTemporaryRepair(): boolean {
    return !isMaterialManager(user.value?.role)
  }

  function canViewSpotWork(): boolean {
    return !isMaterialManager(user.value?.role)
  }

  function canApplySpotWork(): boolean {
    return hasPermission(user.value?.role, 'apply_spot_work')
  }

  function canViewProjectInfo(): boolean {
    return true
  }

  function canQuickFillSpotWork(): boolean {
    return !isMaterialManager(user.value?.role)
  }

  function canViewMaintenanceLog(): boolean {
    return hasPermission(user.value?.role, 'view_maintenance_log')
  }

  function canViewMaintenanceLogDetail(): boolean {
    return hasPermission(user.value?.role, 'view_maintenance_log_detail')
  }

  function canFillMaintenanceLog(): boolean {
    return hasPermission(user.value?.role, 'fill_maintenance_log')
  }

  function canViewAllMaintenanceLog(): boolean {
    return hasPermission(user.value?.role, 'view_all_maintenance_log')
  }

  function canViewDepartmentWeeklyReport(): boolean {
    return hasPermission(user.value?.role, 'view_department_weekly_report')
  }

  function canViewAllWeeklyReport(): boolean {
    return hasPermission(user.value?.role, 'view_all_weekly_report')
  }

  function canApproveWeeklyReport(): boolean {
    return hasPermission(user.value?.role, 'approve_weekly_report')
  }

  function canViewWorkList(): boolean {
    return !isMaterialManager(user.value?.role)
  }

  function canViewSignature(): boolean {
    return !isMaterialManager(user.value?.role)
  }

  function canCreateTemporaryRepair(): boolean {
    return hasPermission(user.value?.role, 'create_temporary_repair')
  }

  function checkPermission(permissionId: string): boolean {
    return hasPermission(user.value?.role, permissionId)
  }

  return {
    user,
    token,
    isLoggedIn,
    isAdmin,
    isDepartmentManager,
    isMaterialManager: isMaterialManagerRole,
    isEmployee,
    isManager,
    setUser,
    clearUser,
    setToken,
    canManagePersonnel,
    canManageProjects,
    canManageSpareParts,
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
    canCreateTemporaryRepair,
    checkPermission,
  }
})
