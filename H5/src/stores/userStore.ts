import { ref, readonly, watch } from 'vue'
import { USER_ROLES } from '../config/constants'

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

watch(currentUser, (newUser) => {
  if (newUser) {
    localStorage.setItem(USER_STORAGE_KEY, JSON.stringify(newUser))
  }
}, { deep: true })

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
    return currentUser.value?.role === USER_ROLES.ADMIN
  },

  isDepartmentManager(): boolean {
    return currentUser.value?.role === USER_ROLES.DEPARTMENT_MANAGER
  },

  isMaterialManager(): boolean {
    return currentUser.value?.role === USER_ROLES.MATERIAL_MANAGER
  },

  isEmployee(): boolean {
    return currentUser.value?.role === USER_ROLES.EMPLOYEE
  },

  canManagePersonnel(): boolean {
    return this.isAdmin() || this.isDepartmentManager()
  },

  canManageProjects(): boolean {
    return this.isAdmin() || this.isDepartmentManager()
  },

  canManageSpareParts(): boolean {
    return this.isAdmin() || this.isMaterialManager()
  },

  canViewAllWorkOrders(): boolean {
    return this.isAdmin() || this.isDepartmentManager()
  },

  canViewPersonnel(): boolean {
    return this.isAdmin() || this.isDepartmentManager()
  },

  canViewStatistics(): boolean {
    return this.isAdmin() || this.isDepartmentManager()
  },

  canViewProjectManagement(): boolean {
    return this.isAdmin() || this.isDepartmentManager()
  },

  canViewWorkOrder(): boolean {
    return !this.isMaterialManager()
  },

  canViewSparePartsInventory(): boolean {
    return this.isAdmin() || this.isMaterialManager() || this.isDepartmentManager()
  },

  canViewSparePartsStock(): boolean {
    return this.isAdmin() || this.isMaterialManager() || this.isDepartmentManager()
  },

  canViewSparePartsIssue(): boolean {
    return this.isAdmin() || this.isMaterialManager() || this.isEmployee() || this.isDepartmentManager()
  },

  canViewRepairToolsStock(): boolean {
    return this.isAdmin() || this.isMaterialManager() || this.isDepartmentManager()
  },

  canViewRepairToolsInbound(): boolean {
    return this.isAdmin() || this.isMaterialManager() || this.isDepartmentManager()
  },

  canViewRepairToolsIssue(): boolean {
    return this.isAdmin() || this.isMaterialManager() || this.isEmployee() || this.isDepartmentManager()
  },

  canViewAlerts(): boolean {
    return this.isAdmin() || this.isEmployee() || this.isDepartmentManager()
  },

  canViewSystemManagement(): boolean {
    return this.isAdmin() || this.isDepartmentManager()
  },

  canViewPeriodicInspection(): boolean {
    return !this.isMaterialManager()
  },

  canApprovePeriodicInspection(): boolean {
    return this.isAdmin() || this.isDepartmentManager()
  },

  canApproveTemporaryRepair(): boolean {
    return this.isAdmin() || this.isDepartmentManager()
  },

  canApproveSpotWork(): boolean {
    return this.isAdmin() || this.isDepartmentManager()
  },

  canViewTemporaryRepair(): boolean {
    return !this.isMaterialManager()
  },

  canViewSpotWork(): boolean {
    return !this.isMaterialManager()
  },

  canApplySpotWork(): boolean {
    return !this.isMaterialManager()
  },

  canViewProjectInfo(): boolean {
    return true
  },

  canQuickFillSpotWork(): boolean {
    return !this.isMaterialManager()
  },

  canViewMaintenanceLog(): boolean {
    return this.isEmployee()
  },

  canViewMaintenanceLogDetail(): boolean {
    return this.isAdmin() || this.isDepartmentManager() || this.isEmployee()
  },

  canFillMaintenanceLog(): boolean {
    return this.isEmployee()
  },

  canViewAllMaintenanceLog(): boolean {
    return this.isAdmin() || this.isDepartmentManager()
  },

  canViewDepartmentWeeklyReport(): boolean {
    return this.isAdmin() || this.isDepartmentManager() || this.isEmployee()
  },

  canViewAllWeeklyReport(): boolean {
    return this.isAdmin() || this.isDepartmentManager()
  },

  canApproveWeeklyReport(): boolean {
    return this.isAdmin() || this.isDepartmentManager()
  },

  canViewWorkList(): boolean {
    return !this.isMaterialManager()
  },

  canViewSignature(): boolean {
    return !this.isMaterialManager()
  }
}
