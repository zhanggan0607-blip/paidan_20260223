import { ref, readonly, watch } from 'vue'
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

const currentUser = ref<User | null>(null)
let heartbeatInterval: number | null = null

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

const startHeartbeat = () => {
  stopHeartbeat()
  if (currentUser.value) {
    onlineUserService.recordLogin('h5', currentUser.value.id, currentUser.value.name).catch(() => {})
  }
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

currentUser.value = loadUserFromStorage()

watch(currentUser, (newUser) => {
  if (newUser) {
    localStorage.setItem(USER_STORAGE_KEY, JSON.stringify(newUser))
  }
}, { deep: true })

if (localStorage.getItem(TOKEN_STORAGE_KEY)) {
  startHeartbeat()
}

export const userStore = {
  readonlyCurrentUser: readonly(currentUser),

  getUser(): User | null {
    return currentUser.value
  },

  setUser(user: User): void {
    if (currentUser.value && currentUser.value.id !== user.id) {
      onlineUserService.logout(currentUser.value.id, 'h5').catch(() => {})
    }
    currentUser.value = user
    localStorage.setItem(USER_STORAGE_KEY, JSON.stringify(user))
    onlineUserService.recordLogin('h5', user.id, user.name).catch(() => {})
    window.dispatchEvent(new CustomEvent('user-changed', { detail: user }))
  },

  clearUser(): void {
    stopHeartbeat()
    if (currentUser.value) {
      onlineUserService.logout(currentUser.value.id, 'h5').catch(() => {})
    }
    currentUser.value = null
    localStorage.removeItem(USER_STORAGE_KEY)
    localStorage.removeItem(TOKEN_STORAGE_KEY)
    window.dispatchEvent(new CustomEvent('user-changed', { detail: null }))
  },

  getToken(): string | null {
    return localStorage.getItem(TOKEN_STORAGE_KEY)
  },

  setToken(token: string): void {
    localStorage.setItem(TOKEN_STORAGE_KEY, token)
    startHeartbeat()
  },

  isLoggedIn(): boolean {
    return !!this.getToken()
  },

  isAdmin(): boolean {
    return isAdminRole(currentUser.value?.role)
  },

  isDepartmentManager(): boolean {
    return currentUser.value?.role === RoleCode.DEPARTMENT_MANAGER
  },

  isMaterialManager(): boolean {
    return isMaterialManager(currentUser.value?.role)
  },

  isEmployee(): boolean {
    return currentUser.value?.role === RoleCode.EMPLOYEE
  },

  canManagePersonnel(): boolean {
    return hasPermission(currentUser.value?.role, 'manage_personnel')
  },

  canManageProjects(): boolean {
    return hasPermission(currentUser.value?.role, 'manage_projects')
  },

  canManageSpareParts(): boolean {
    return hasPermission(currentUser.value?.role, 'manage_spare_parts')
  },

  canViewAllWorkOrders(): boolean {
    return hasPermission(currentUser.value?.role, 'view_all_work_orders')
  },

  canViewPersonnel(): boolean {
    return hasPermission(currentUser.value?.role, 'view_personnel')
  },

  canViewStatistics(): boolean {
    return hasPermission(currentUser.value?.role, 'view_statistics')
  },

  canViewProjectManagement(): boolean {
    return hasPermission(currentUser.value?.role, 'view_project_management')
  },

  canViewWorkOrder(): boolean {
    return !isMaterialManager(currentUser.value?.role)
  },

  canViewSparePartsInventory(): boolean {
    return hasPermission(currentUser.value?.role, 'view_spare_parts_inventory')
  },

  canViewSparePartsStock(): boolean {
    return hasPermission(currentUser.value?.role, 'view_spare_parts_stock')
  },

  canViewSparePartsIssue(): boolean {
    return hasPermission(currentUser.value?.role, 'view_spare_parts_issue')
  },

  canViewRepairToolsStock(): boolean {
    return hasPermission(currentUser.value?.role, 'view_repair_tools_stock')
  },

  canViewRepairToolsInbound(): boolean {
    return hasPermission(currentUser.value?.role, 'view_repair_tools_inbound')
  },

  canViewRepairToolsIssue(): boolean {
    return hasPermission(currentUser.value?.role, 'view_repair_tools_issue')
  },

  canViewAlerts(): boolean {
    return hasPermission(currentUser.value?.role, 'view_alerts')
  },

  canViewSystemManagement(): boolean {
    return hasPermission(currentUser.value?.role, 'view_system_management')
  },

  canViewPeriodicInspection(): boolean {
    return !isMaterialManager(currentUser.value?.role)
  },

  canApprovePeriodicInspection(): boolean {
    return hasPermission(currentUser.value?.role, 'approve_periodic_inspection')
  },

  canApproveTemporaryRepair(): boolean {
    return hasPermission(currentUser.value?.role, 'approve_temporary_repair')
  },

  canApproveSpotWork(): boolean {
    return hasPermission(currentUser.value?.role, 'approve_spot_work')
  },

  canViewTemporaryRepair(): boolean {
    return !isMaterialManager(currentUser.value?.role)
  },

  canViewSpotWork(): boolean {
    return !isMaterialManager(currentUser.value?.role)
  },

  canApplySpotWork(): boolean {
    return hasPermission(currentUser.value?.role, 'apply_spot_work')
  },

  canViewProjectInfo(): boolean {
    return true
  },

  canQuickFillSpotWork(): boolean {
    return !isMaterialManager(currentUser.value?.role)
  },

  canViewMaintenanceLog(): boolean {
    return hasPermission(currentUser.value?.role, 'view_maintenance_log')
  },

  canViewMaintenanceLogDetail(): boolean {
    return hasPermission(currentUser.value?.role, 'view_maintenance_log_detail')
  },

  canFillMaintenanceLog(): boolean {
    return hasPermission(currentUser.value?.role, 'fill_maintenance_log')
  },

  canViewAllMaintenanceLog(): boolean {
    return hasPermission(currentUser.value?.role, 'view_all_maintenance_log')
  },

  canViewDepartmentWeeklyReport(): boolean {
    return hasPermission(currentUser.value?.role, 'view_department_weekly_report')
  },

  canViewAllWeeklyReport(): boolean {
    return hasPermission(currentUser.value?.role, 'view_all_weekly_report')
  },

  canApproveWeeklyReport(): boolean {
    return hasPermission(currentUser.value?.role, 'approve_weekly_report')
  },

  canViewWorkList(): boolean {
    return !isMaterialManager(currentUser.value?.role)
  },

  canViewSignature(): boolean {
    return !isMaterialManager(currentUser.value?.role)
  },

  canCreateTemporaryRepair(): boolean {
    return hasPermission(currentUser.value?.role, 'create_temporary_repair')
  },

  isManager(): boolean {
    return isManagerRole(currentUser.value?.role)
  },

  hasPermission(permissionId: string): boolean {
    return hasPermission(currentUser.value?.role, permissionId)
  }
}
