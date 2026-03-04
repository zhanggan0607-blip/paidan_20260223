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
  total: number
  page: number
  pageSize: number
  content?: T[]
  totalElements?: number
  totalPages?: number
  size?: number
  number?: number
  first?: boolean
  last?: boolean
}

export interface PaginatedResponse<T = unknown> extends ApiResponse<PaginatedData<T>> {}

export interface LegacyPaginatedResponse<T = unknown> {
  items: T[]
  total: number
  page: number
  pageSize: number
  content?: T[]
  totalElements?: number
  totalPages?: number
  size?: number
  number?: number
  first?: boolean
  last?: boolean
}

export interface QueryParams {
  page: number
  size?: number
  pageSize?: number
}

export interface ListQueryParams extends QueryParams {
  project_name?: string
  client_name?: string
  status?: string
}

export interface ApiError {
  status: number
  message: string
  errors?: unknown[]
  data?: unknown
}

export interface User {
  id?: number
  name: string
  role: string
  department?: string
  phone?: string
  email?: string
  username?: string
}

export interface UserInfo extends User {
  id: number
  username: string
  name: string
  role: string
}

export interface TokenPayload {
  access_token: string
  token_type: string
  expires_in?: number
  refresh_token?: string
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
