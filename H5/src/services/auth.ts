import { USER_ROLES } from '../config/constants'

export interface User {
  id: number
  name: string
  role: string
  department: string
  phone: string
}

export interface LoginRequest {
  username: string
  password: string
}

export interface LoginResponse {
  access_token: string
  token_type: string
  user: User
}

export interface ApiResponse<T = any> {
  code: number
  message: string
  data: T
}

const USER_STORAGE_KEY = 'user'
const TOKEN_STORAGE_KEY = 'token'

export const authService = {
  logout(): void {
    localStorage.removeItem(TOKEN_STORAGE_KEY)
    localStorage.removeItem(USER_STORAGE_KEY)
  },

  getCurrentUser(): User | null {
    const userStr = localStorage.getItem(USER_STORAGE_KEY)
    if (userStr) {
      try {
        return JSON.parse(userStr)
      } catch {
        return null
      }
    }
    return null
  },

  getToken(): string | null {
    return localStorage.getItem(TOKEN_STORAGE_KEY)
  },

  isLoggedIn(): boolean {
    return !!this.getToken()
  },

  isAdmin(user: User | null): boolean {
    return user?.role === USER_ROLES.ADMIN
  },

  isDepartmentManager(user: User | null): boolean {
    return user?.role === USER_ROLES.DEPARTMENT_MANAGER
  },

  isMaterialManager(user: User | null): boolean {
    return user?.role === USER_ROLES.MATERIAL_MANAGER
  },

  isEmployee(user: User | null): boolean {
    return user?.role === USER_ROLES.EMPLOYEE
  },

  canManagePersonnel(user: User | null): boolean {
    return this.isAdmin(user) || this.isDepartmentManager(user)
  },

  canManageProjects(user: User | null): boolean {
    return this.isAdmin(user) || this.isDepartmentManager(user)
  },

  canManageSpareParts(user: User | null): boolean {
    return this.isAdmin(user) || this.isMaterialManager(user)
  },

  canViewAllWorkOrders(user: User | null): boolean {
    return this.isAdmin(user) || this.isDepartmentManager(user)
  },

  canViewPersonnel(user: User | null): boolean {
    return this.isAdmin(user)
  },

  canViewStatistics(user: User | null): boolean {
    return this.isAdmin(user) || this.isDepartmentManager(user)
  },

  canViewProjectManagement(user: User | null): boolean {
    return this.isAdmin(user) || this.isDepartmentManager(user)
  },

  canViewWorkOrder(user: User | null): boolean {
    return !this.isMaterialManager(user)
  },

  canViewSparePartsInventory(user: User | null): boolean {
    return this.isAdmin(user) || this.isMaterialManager(user) || this.isDepartmentManager(user)
  },

  canViewSparePartsStock(user: User | null): boolean {
    return this.isAdmin(user) || this.isMaterialManager(user) || this.isDepartmentManager(user)
  },

  canViewSparePartsIssue(user: User | null): boolean {
    return this.isAdmin(user) || this.isEmployee(user) || this.isDepartmentManager(user)
  },

  canViewRepairToolsStock(user: User | null): boolean {
    return this.isAdmin(user) || this.isMaterialManager(user) || this.isDepartmentManager(user)
  },

  canViewRepairToolsInbound(user: User | null): boolean {
    return this.isAdmin(user) || this.isMaterialManager(user) || this.isDepartmentManager(user)
  },

  canViewRepairToolsIssue(user: User | null): boolean {
    return this.isAdmin(user) || this.isEmployee(user) || this.isDepartmentManager(user)
  },

  canViewAlerts(user: User | null): boolean {
    return this.isAdmin(user) || this.isEmployee(user) || this.isDepartmentManager(user)
  },

  canViewSystemManagement(user: User | null): boolean {
    return this.isAdmin(user) || this.isDepartmentManager(user)
  },

  canViewPeriodicInspection(user: User | null): boolean {
    return !this.isMaterialManager(user)
  },

  canViewTemporaryRepair(user: User | null): boolean {
    return !this.isMaterialManager(user)
  },

  canViewSpotWork(user: User | null): boolean {
    return !this.isMaterialManager(user)
  },

  canViewProjectInfo(user: User | null): boolean {
    return true
  },

  canQuickFillSpotWork(user: User | null): boolean {
    return !this.isMaterialManager(user)
  },

  updateStoredUser(user: User): void {
    localStorage.setItem(USER_STORAGE_KEY, JSON.stringify(user))
  }
}
