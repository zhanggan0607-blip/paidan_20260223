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
  async login(username: string, password: string): Promise<ApiResponse<LoginResponse>> {
    const response = await fetch(`${import.meta.env.VITE_API_BASE_URL || 'http://localhost:8080/api/v1'}/auth/login-json`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ username, password })
    })
    const result: ApiResponse<LoginResponse> = await response.json()
    
    if (result.code === 200 && result.data) {
      localStorage.setItem(TOKEN_STORAGE_KEY, result.data.access_token)
      localStorage.setItem(USER_STORAGE_KEY, JSON.stringify(result.data.user))
    }
    
    return result
  },

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
    return this.isAdmin(user) || this.isDepartmentManager(user)
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
    return this.isAdmin(user) || this.isMaterialManager(user) || this.isEmployee(user) || this.isDepartmentManager(user)
  },

  canViewRepairToolsStock(user: User | null): boolean {
    return this.isAdmin(user) || this.isMaterialManager(user) || this.isDepartmentManager(user)
  },

  canViewRepairToolsInbound(user: User | null): boolean {
    return this.isAdmin(user) || this.isMaterialManager(user) || this.isDepartmentManager(user)
  },

  canViewRepairToolsIssue(user: User | null): boolean {
    return this.isAdmin(user) || this.isMaterialManager(user) || this.isEmployee(user) || this.isDepartmentManager(user)
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

  canApprovePeriodicInspection(user: User | null): boolean {
    return this.isAdmin(user) || this.isDepartmentManager(user)
  },

  canApproveTemporaryRepair(user: User | null): boolean {
    return this.isAdmin(user) || this.isDepartmentManager(user)
  },

  canApproveSpotWork(user: User | null): boolean {
    return this.isAdmin(user) || this.isDepartmentManager(user)
  },

  canViewTemporaryRepair(user: User | null): boolean {
    return !this.isMaterialManager(user)
  },

  canViewSpotWork(user: User | null): boolean {
    return !this.isMaterialManager(user)
  },

  canApplySpotWork(user: User | null): boolean {
    return !this.isMaterialManager(user)
  },

  canViewProjectInfo(_user: User | null): boolean {
    return true
  },

  canQuickFillSpotWork(user: User | null): boolean {
    return !this.isMaterialManager(user)
  },

  canViewMaintenanceLog(user: User | null): boolean {
    return this.isEmployee(user)
  },

  canViewMaintenanceLogDetail(user: User | null): boolean {
    return this.isAdmin(user) || this.isDepartmentManager(user) || this.isEmployee(user)
  },

  canFillMaintenanceLog(user: User | null): boolean {
    return this.isEmployee(user)
  },

  canViewAllMaintenanceLog(user: User | null): boolean {
    return this.isAdmin(user) || this.isDepartmentManager(user)
  },

  canViewDepartmentWeeklyReport(user: User | null): boolean {
    return this.isAdmin(user) || this.isDepartmentManager(user)
  },

  canViewAllWeeklyReport(user: User | null): boolean {
    return this.isAdmin(user) || this.isDepartmentManager(user)
  },

  canViewWorkList(user: User | null): boolean {
    return !this.isMaterialManager(user)
  },

  canViewSignature(user: User | null): boolean {
    return !this.isMaterialManager(user)
  },

  updateStoredUser(user: User): void {
    localStorage.setItem(USER_STORAGE_KEY, JSON.stringify(user))
  }
}
