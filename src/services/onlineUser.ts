/**
 * 在线用户服务
 * 提供在线用户统计和心跳功能
 */
import request from '../api/request'
import { API_ENDPOINTS } from '../api/endpoints'

export interface OnlineUser {
  id: number
  user_id: number
  user_name: string
  department: string | null
  role: string | null
  login_time: string
  last_activity: string
  ip_address: string | null
  device_type: string
  is_active: boolean
}

export interface OnlineCount {
  total: number
  pc_count: number
  h5_count: number
}

export interface OnlineStatistics {
  total: number
  pc_count: number
  h5_count: number
  pc_users: OnlineUser[]
  h5_users: OnlineUser[]
}

export interface LoginRequest {
  device_type?: string
  user_id?: number
  user_name?: string
}

export interface LogoutRequest {
  user_id?: number
  device_type?: string
}

export const onlineUserService = {
  /**
   * 获取在线用户数量统计
   */
  async getOnlineCount(): Promise<OnlineCount> {
    const response = await request.get(API_ENDPOINTS.ONLINE_USER.COUNT)
    return response.data
  },

  /**
   * 获取在线用户列表
   */
  async getOnlineUsers(deviceType?: string): Promise<OnlineUser[]> {
    const params = deviceType ? { device_type: deviceType } : {}
    const response = await request.get(API_ENDPOINTS.ONLINE_USER.USERS, { params })
    return response.data
  },

  /**
   * 获取在线用户详细统计
   */
  async getOnlineStatistics(): Promise<OnlineStatistics> {
    const response = await request.get(API_ENDPOINTS.ONLINE_USER.STATISTICS)
    return response.data
  },

  /**
   * 发送心跳更新活跃状态
   */
  async sendHeartbeat(deviceType: string = 'pc'): Promise<void> {
    await request.post(API_ENDPOINTS.ONLINE_USER.HEARTBEAT, { device_type: deviceType })
  },

  /**
   * 记录登录
   */
  async recordLogin(deviceType: string = 'pc', userId?: number, userName?: string): Promise<void> {
    const params: Record<string, unknown> = { device_type: deviceType }
    if (userId) {
      params.user_id = userId
      params.user_name = userName
    }
    await request.post(API_ENDPOINTS.ONLINE_USER.LOGIN, params)
  },

  /**
   * 记录登出
   */
  async logout(userId?: number, deviceType?: string): Promise<void> {
    const params: Record<string, unknown> = {}
    if (userId) {
      params.user_id = userId
    }
    if (deviceType) {
      params.device_type = deviceType
    }
    await request.post(API_ENDPOINTS.ONLINE_USER.LOGOUT, params)
  }
}

export default onlineUserService
