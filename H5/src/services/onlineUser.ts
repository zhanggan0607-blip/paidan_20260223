/**
 * 在线用户服务
 * 提供在线用户状态记录和管理功能
 */
import request from '../api/request'
import { API_ENDPOINTS } from '../api/endpoints'
import type { ApiResponse } from '../types'

interface OnlineLoginRequest {
  device_type: string
  user_id: number
  user_name: string
}

interface OnlineUser {
  id: number
  user_id: number
  user_name: string
  department: string | null
  role: string | null
  login_time: string | null
  last_activity: string | null
  ip_address: string | null
  device_type: string
  is_active: boolean
}

interface OnlineStatistics {
  total_online: number
  h5_count: number
  pc_count: number
  today_logins: number
}

export const onlineUserService = {
  /**
   * 记录用户登录
   */
  async recordLogin(
    deviceType: string,
    userId: number,
    userName: string
  ): Promise<ApiResponse<null>> {
    const data: OnlineLoginRequest = {
      device_type: deviceType,
      user_id: userId,
      user_name: userName,
    }
    return request.post(API_ENDPOINTS.ONLINE_USER.LOGIN, data)
  },

  /**
   * 记录用户登出
   */
  async recordLogout(
    deviceType: string,
    userId: number,
    userName: string
  ): Promise<ApiResponse<null>> {
    const data: OnlineLoginRequest = {
      device_type: deviceType,
      user_id: userId,
      user_name: userName,
    }
    return request.post(API_ENDPOINTS.ONLINE_USER.LOGOUT, data)
  },

  /**
   * 心跳更新
   */
  async heartbeat(
    deviceType: string,
    userId: number,
    userName: string
  ): Promise<ApiResponse<null>> {
    const data: OnlineLoginRequest = {
      device_type: deviceType,
      user_id: userId,
      user_name: userName,
    }
    return request.post(API_ENDPOINTS.ONLINE_USER.HEARTBEAT, data)
  },

  /**
   * 获取在线用户数量
   */
  async getCount(): Promise<ApiResponse<{ count: number }>> {
    return request.get(API_ENDPOINTS.ONLINE_USER.COUNT)
  },

  /**
   * 获取在线用户列表
   */
  async getUsers(): Promise<ApiResponse<OnlineUser[]>> {
    return request.get(API_ENDPOINTS.ONLINE_USER.USERS)
  },

  /**
   * 获取在线用户统计
   */
  async getStatistics(): Promise<ApiResponse<OnlineStatistics>> {
    return request.get(API_ENDPOINTS.ONLINE_USER.STATISTICS)
  },
}

export default onlineUserService
