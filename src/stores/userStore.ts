import { ref, readonly } from 'vue'
import {
  RoleCode,
  hasPermission,
  isManagerRole,
  isAdminRole,
  canShowMenu
} from '../config/permission'
import onlineUserService from '../services/onlineUser'

export interface User {
  id: number
  name: string
  role: string
  department?: string
  email?: string
  phone?: string
}

const TOKEN_KEY = 'token'
const USER_KEY = 'user'

const currentUser = ref<User | null>(null)
const token = ref<string | null>(null)
let heartbeatInterval: number | null = null

const loadStoredUser = () => {
  const storedToken = localStorage.getItem(TOKEN_KEY)
  const storedUser = localStorage.getItem(USER_KEY)
  
  if (storedToken) {
    token.value = storedToken
  }
  
  if (storedUser) {
    try {
      currentUser.value = JSON.parse(storedUser)
    } catch {
      currentUser.value = null
    }
  }
}

const startHeartbeat = () => {
  stopHeartbeat()
  if (currentUser.value) {
    onlineUserService.recordLogin('pc', currentUser.value.id, currentUser.value.name).catch(() => {})
  }
  onlineUserService.sendHeartbeat('pc').catch(() => {})
  heartbeatInterval = window.setInterval(() => {
    if (token.value) {
      onlineUserService.sendHeartbeat('pc').catch(() => {})
    }
  }, 1 * 60 * 1000)
}

const stopHeartbeat = () => {
  if (heartbeatInterval) {
    clearInterval(heartbeatInterval)
    heartbeatInterval = null
  }
}

loadStoredUser()

if (token.value) {
  startHeartbeat()
}

export const userStore = {
  readonlyCurrentUser: readonly(currentUser),
  readonlyToken: readonly(token),
  
  getUser: (): User | null => {
    return currentUser.value
  },
  
  getToken: (): string | null => {
    return token.value
  },
  
  setUser: (user: User) => {
    if (currentUser.value && currentUser.value.id !== user.id) {
      onlineUserService.logout(currentUser.value.id, 'pc').catch(() => {})
    }
    currentUser.value = user
    localStorage.setItem(USER_KEY, JSON.stringify(user))
    onlineUserService.recordLogin('pc', user.id, user.name).catch(() => {})
    window.dispatchEvent(new CustomEvent('user-changed', { detail: user }))
  },
  
  setToken: (newToken: string) => {
    token.value = newToken
    localStorage.setItem(TOKEN_KEY, newToken)
    startHeartbeat()
  },
  
  clearUser: () => {
    stopHeartbeat()
    if (currentUser.value) {
      onlineUserService.logout(currentUser.value.id, 'pc').catch(() => {})
    }
    currentUser.value = null
    token.value = null
    localStorage.removeItem(TOKEN_KEY)
    localStorage.removeItem(USER_KEY)
    window.dispatchEvent(new CustomEvent('user-changed', { detail: null }))
  },
  
  isAdmin: (): boolean => {
    return isAdminRole(currentUser.value?.role)
  },
  
  isDepartmentManager: (): boolean => {
    return currentUser.value?.role === RoleCode.DEPARTMENT_MANAGER
  },
  
  isMaterialManager: (): boolean => {
    return currentUser.value?.role === RoleCode.MATERIAL_MANAGER
  },
  
  isMaterialManagerOnly: (): boolean => {
    return currentUser.value?.role === RoleCode.MATERIAL_MANAGER
  },
  
  isEmployee: (): boolean => {
    return currentUser.value?.role === RoleCode.EMPLOYEE
  },
  
  canViewStatistics: (): boolean => {
    return hasPermission(currentUser.value?.role, 'view_statistics')
  },
  
  canViewProjectManagement: (): boolean => {
    return hasPermission(currentUser.value?.role, 'view_project_management')
  },
  
  canViewAlerts: (): boolean => {
    return hasPermission(currentUser.value?.role, 'view_alerts')
  },
  
  canViewPersonnel: (): boolean => {
    return hasPermission(currentUser.value?.role, 'view_personnel')
  },
  
  canViewSystemManagement: (): boolean => {
    return hasPermission(currentUser.value?.role, 'view_system_management')
  },
  
  canViewWorkOrder: (): boolean => {
    return hasPermission(currentUser.value?.role, 'view_work_order')
  },
  
  canViewSparePartsStock: (): boolean => {
    return hasPermission(currentUser.value?.role, 'view_spare_parts_stock')
  },
  
  canViewSparePartsIssue: (): boolean => {
    return hasPermission(currentUser.value?.role, 'view_spare_parts_issue')
  },
  
  canViewRepairToolsInbound: (): boolean => {
    return hasPermission(currentUser.value?.role, 'view_repair_tools_stock')
  },
  
  canViewRepairToolsIssue: (): boolean => {
    return hasPermission(currentUser.value?.role, 'view_repair_tools_issue')
  },
  
  canFillMaintenanceLog: (): boolean => {
    return hasPermission(currentUser.value?.role, 'fill_maintenance_log')
  },
  
  canViewMaintenanceLog: (): boolean => {
    return hasPermission(currentUser.value?.role, 'view_maintenance_log')
  },
  
  canViewAllMaintenanceLog: (): boolean => {
    return hasPermission(currentUser.value?.role, 'view_all_maintenance_log')
  },
  
  canFillWeeklyReport: (): boolean => {
    return hasPermission(currentUser.value?.role, 'fill_weekly_report')
  },
  
  canViewWeeklyReport: (): boolean => {
    return hasPermission(currentUser.value?.role, 'view_weekly_report')
  },
  
  canApproveWeeklyReport: (): boolean => {
    return hasPermission(currentUser.value?.role, 'view_weekly_report')
  },
  
  canApprovePeriodicInspection: (): boolean => {
    return hasPermission(currentUser.value?.role, 'approve_periodic_inspection')
  },
  
  canApproveTemporaryRepair: (): boolean => {
    return hasPermission(currentUser.value?.role, 'approve_temporary_repair')
  },
  
  canApproveSpotWork: (): boolean => {
    return hasPermission(currentUser.value?.role, 'approve_spot_work')
  },
  
  canDeletePersonnel: (): boolean => {
    return hasPermission(currentUser.value?.role, 'delete_personnel')
  },
  
  canEditPersonnelRole: (): boolean => {
    return hasPermission(currentUser.value?.role, 'edit_personnel_role')
  },
  
  canShowMenu: (menuId: string): boolean => {
    return canShowMenu(menuId, currentUser.value?.role)
  },
  
  isManager: (): boolean => {
    return isManagerRole(currentUser.value?.role)
  },
  
  hasPermission: (permissionId: string): boolean => {
    return hasPermission(currentUser.value?.role, permissionId)
  }
}
