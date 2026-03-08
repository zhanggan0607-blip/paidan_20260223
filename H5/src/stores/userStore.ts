/**
 * 用户状态管理
 * 提供两种导出方式：
 * 1. userStore - 兼容旧代码的对象式API
 * 2. useUserStore - Pinia Composition API
 */
import { ref, readonly, watch } from 'vue'
import {
  RoleCode,
  hasPermission,
  isManagerRole,
  isAdminRole,
  isMaterialManager,
} from '../config/permission'

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

currentUser.value = loadUserFromStorage()

if (typeof window !== 'undefined') {
  window.addEventListener('user-changed', ((event: CustomEvent<User | null>) => {
    currentUser.value = event.detail
  }) as EventListener)
}

watch(
  currentUser,
  (newUser) => {
    if (newUser) {
      localStorage.setItem(USER_STORAGE_KEY, JSON.stringify(newUser))
    }
  },
  { deep: true }
)

export const userStore = {
  readonlyCurrentUser: readonly(currentUser),

  getUser(): User | null {
    return currentUser.value
  },

  setUser(user: User): void {
    currentUser.value = user
    localStorage.setItem(USER_STORAGE_KEY, JSON.stringify(user))
    window.dispatchEvent(new CustomEvent('user-changed', { detail: user }))
  },

  clearUser(): void {
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
  },
}
