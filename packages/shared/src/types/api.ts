/**
 * 统一API响应类型定义
 */
export interface ApiResponse<T = unknown> {
  code: number
  message: string
  data: T
}

export interface PaginatedData<T> {
  items: T[]
  content?: T[]
  total: number
  totalElements?: number
  page: number
  size: number
  totalPages: number
  first: boolean
  last: boolean
}

export interface PaginatedResponse<T = unknown> extends ApiResponse<PaginatedData<T>> {}

export interface ApiError {
  status: number
  message: string
  errors?: unknown[]
  data?: unknown
}

export interface User {
  id: number
  name: string
  role: string
  department?: string
  phone?: string
  email?: string
  username?: string
  must_change_password?: boolean
}

export interface UserInfo extends User {
  id: number
  username: string
  name: string
  role: string
}

export interface LoginRequest {
  username: string
  password: string
  device_type?: string
}

export interface LoginResponse {
  access_token: string
  refresh_token?: string
  token_type?: string
  user?: UserInfo
}

export interface RefreshTokenResponse {
  access_token: string
  refresh_token?: string
}
