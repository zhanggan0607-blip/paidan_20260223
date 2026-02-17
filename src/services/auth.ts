import apiClient from '../utils/api'
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

const USER_STORAGE_KEY = 'user_info'
const TOKEN_STORAGE_KEY = 'token'

export const authService = {
  async login(username: string, password: string): Promise<ApiResponse<LoginResponse>> {
    const response = await apiClient.post('/auth/login-json', {
      username,
      password
    })
    
    if (response.code === 200 && response.data) {
      localStorage.setItem(TOKEN_STORAGE_KEY, response.data.access_token)
      localStorage.setItem(USER_STORAGE_KEY, JSON.stringify(response.data.user))
    }
    
    return response
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
    return this.isAdmin(user) || this.isMaterialManager(user) || this.isDepartmentManager(user)
  },

  canViewAllWorkOrders(user: User | null): boolean {
    return this.isAdmin(user) || this.isDepartmentManager(user)
  },

  canViewPersonnel(user: User | null): boolean {
    return this.isAdmin(user) || this.isDepartmentManager(user)
  },

  canViewStatistics(user: User | null): boolean {
    return this.isAdmin(user) || this.isDepartmentManager(user) || this.isEmployee(user)
  },

  canViewProjectManagement(user: User | null): boolean {
    return this.isAdmin(user) || this.isDepartmentManager(user)
  },

  canViewWorkOrder(user: User | null): boolean {
    return !this.isMaterialManager(user)
  },

  canViewSparePartsStock(user: User | null): boolean {
    return this.isAdmin(user) || this.isMaterialManager(user) || this.isDepartmentManager(user)
  },

  canViewSparePartsIssue(user: User | null): boolean {
    return this.isAdmin(user) || this.isEmployee(user) || this.isDepartmentManager(user) || this.isMaterialManager(user)
  },

  canViewRepairToolsInbound(user: User | null): boolean {
    return this.isAdmin(user) || this.isMaterialManager(user) || this.isDepartmentManager(user)
  },

  canViewRepairToolsIssue(user: User | null): boolean {
    return this.isAdmin(user) || this.isEmployee(user) || this.isDepartmentManager(user) || this.isMaterialManager(user)
  },

  canViewAlerts(user: User | null): boolean {
    return this.isAdmin(user) || this.isEmployee(user) || this.isDepartmentManager(user)
  },

  canViewSystemManagement(user: User | null): boolean {
    return this.isAdmin(user) || this.isDepartmentManager(user)
  },

  async getCurrentUserInfo(): Promise<ApiResponse<User>> {
    return await apiClient.get('/auth/me')
  },

  updateStoredUser(user: User): void {
    localStorage.setItem(USER_STORAGE_KEY, JSON.stringify(user))
  }
}
