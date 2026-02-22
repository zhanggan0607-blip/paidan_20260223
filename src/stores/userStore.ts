import { ref, readonly } from 'vue'
import { USER_ROLES } from '../config/constants'

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

loadStoredUser()

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
    currentUser.value = user
    localStorage.setItem(USER_KEY, JSON.stringify(user))
    window.dispatchEvent(new CustomEvent('user-changed', { detail: user }))
  },
  
  setToken: (newToken: string) => {
    token.value = newToken
    localStorage.setItem(TOKEN_KEY, newToken)
  },
  
  clearUser: () => {
    currentUser.value = null
    token.value = null
    localStorage.removeItem(TOKEN_KEY)
    localStorage.removeItem(USER_KEY)
    window.dispatchEvent(new CustomEvent('user-changed', { detail: null }))
  },
  
  isAdmin: (): boolean => {
    return currentUser.value?.role === USER_ROLES.ADMIN
  },
  
  isDepartmentManager: (): boolean => {
    return currentUser.value?.role === USER_ROLES.DEPARTMENT_MANAGER
  },
  
  isMaterialManager: (): boolean => {
    return currentUser.value?.role === USER_ROLES.MATERIAL_MANAGER
  },
  
  isMaterialManagerOnly: (): boolean => {
    return currentUser.value?.role === USER_ROLES.MATERIAL_MANAGER
  },
  
  isEmployee: (): boolean => {
    return currentUser.value?.role === USER_ROLES.EMPLOYEE
  },
  
  canViewStatistics: (): boolean => {
    const role = currentUser.value?.role
    return role === USER_ROLES.ADMIN || role === USER_ROLES.DEPARTMENT_MANAGER || role === USER_ROLES.EMPLOYEE
  },
  
  canViewProjectManagement: (): boolean => {
    const role = currentUser.value?.role
    return role === USER_ROLES.ADMIN || role === USER_ROLES.DEPARTMENT_MANAGER
  },
  
  canViewAlerts: (): boolean => {
    const role = currentUser.value?.role
    return role === USER_ROLES.ADMIN || role === USER_ROLES.DEPARTMENT_MANAGER || role === USER_ROLES.EMPLOYEE
  },
  
  canViewPersonnel: (): boolean => {
    const role = currentUser.value?.role
    return role === USER_ROLES.ADMIN || role === USER_ROLES.DEPARTMENT_MANAGER
  },
  
  canViewSystemManagement: (): boolean => {
    const role = currentUser.value?.role
    return role === USER_ROLES.ADMIN || role === USER_ROLES.DEPARTMENT_MANAGER
  },
  
  canViewWorkOrder: (): boolean => {
    const role = currentUser.value?.role
    return role === USER_ROLES.ADMIN || role === USER_ROLES.DEPARTMENT_MANAGER || role === USER_ROLES.EMPLOYEE
  },
  
  canViewSparePartsStock: (): boolean => {
    const role = currentUser.value?.role
    return role === USER_ROLES.ADMIN || role === USER_ROLES.DEPARTMENT_MANAGER || role === USER_ROLES.MATERIAL_MANAGER
  },
  
  canViewSparePartsIssue: (): boolean => {
    const role = currentUser.value?.role
    return role === USER_ROLES.ADMIN || role === USER_ROLES.DEPARTMENT_MANAGER || role === USER_ROLES.MATERIAL_MANAGER || role === USER_ROLES.EMPLOYEE
  },
  
  canViewRepairToolsInbound: (): boolean => {
    const role = currentUser.value?.role
    return role === USER_ROLES.ADMIN || role === USER_ROLES.DEPARTMENT_MANAGER || role === USER_ROLES.MATERIAL_MANAGER
  },
  
  canViewRepairToolsIssue: (): boolean => {
    const role = currentUser.value?.role
    return role === USER_ROLES.ADMIN || role === USER_ROLES.DEPARTMENT_MANAGER || role === USER_ROLES.MATERIAL_MANAGER || role === USER_ROLES.EMPLOYEE
  },
  
  canFillMaintenanceLog: (): boolean => {
    const role = currentUser.value?.role
    return role === USER_ROLES.DEPARTMENT_MANAGER || role === USER_ROLES.EMPLOYEE
  },
  
  canViewMaintenanceLog: (): boolean => {
    const role = currentUser.value?.role
    return role === USER_ROLES.ADMIN || role === USER_ROLES.DEPARTMENT_MANAGER || role === USER_ROLES.EMPLOYEE
  },
  
  canViewAllMaintenanceLog: (): boolean => {
    const role = currentUser.value?.role
    return role === USER_ROLES.ADMIN || role === USER_ROLES.DEPARTMENT_MANAGER
  },
  
  canFillWeeklyReport: (): boolean => {
    const role = currentUser.value?.role
    return role === USER_ROLES.DEPARTMENT_MANAGER
  },
  
  canViewWeeklyReport: (): boolean => {
    const role = currentUser.value?.role
    return role === USER_ROLES.ADMIN || role === USER_ROLES.DEPARTMENT_MANAGER
  },
  
  canApproveWeeklyReport: (): boolean => {
    const role = currentUser.value?.role
    return role === USER_ROLES.ADMIN || role === USER_ROLES.DEPARTMENT_MANAGER
  },
  
  canApprovePeriodicInspection: (): boolean => {
    const role = currentUser.value?.role
    return role === USER_ROLES.ADMIN || role === USER_ROLES.DEPARTMENT_MANAGER
  },
  
  canApproveTemporaryRepair: (): boolean => {
    const role = currentUser.value?.role
    return role === USER_ROLES.ADMIN || role === USER_ROLES.DEPARTMENT_MANAGER
  },
  
  canApproveSpotWork: (): boolean => {
    const role = currentUser.value?.role
    return role === USER_ROLES.ADMIN || role === USER_ROLES.DEPARTMENT_MANAGER
  }
}
