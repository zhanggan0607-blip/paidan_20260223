/**
 * 认证服务
 * 提供用户登录、登出、Token刷新等功能
 */
import request from '../api/request'
import { API_ENDPOINTS } from '../api/endpoints'
import type {
  ApiResponse,
  LoginRequest,
  LoginResponse,
  RefreshTokenResponse,
  UserInfo,
} from '../types'

export const authService = {
  /**
   * 用户登录
   */
  async login(credentials: LoginRequest): Promise<ApiResponse<LoginResponse>> {
    return request.post(API_ENDPOINTS.AUTH.LOGIN_JSON, credentials)
  },

  /**
   * 用户登出
   */
  async logout(): Promise<ApiResponse<null>> {
    return request.post(API_ENDPOINTS.AUTH.LOGOUT)
  },

  /**
   * 刷新Token
   */
  async refreshToken(): Promise<ApiResponse<RefreshTokenResponse>> {
    return request.post(API_ENDPOINTS.AUTH.REFRESH)
  },

  /**
   * 获取当前用户信息
   */
  async getCurrentUser(): Promise<ApiResponse<UserInfo>> {
    return request.get(API_ENDPOINTS.AUTH.ME)
  },
}

export default authService
