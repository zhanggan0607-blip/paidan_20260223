/**
 * 在线用户服务
 * 提供在线用户统计和心跳功能
 */
import request from '../api/request'
import { API_ENDPOINTS } from '../api/endpoints'
import type { ApiResponse } from '../types/api'
import type { OnlineUser, OnlineCount, OnlineStatistics } from '../types/models'

export const onlineUserService = {
  /**
   * 获取在线用户数量统计
   */
  async getOnlineCount(): Promise<ApiResponse<OnlineCount>> {
    return request.get(API_ENDPOINTS.ONLINE_USER.COUNT)
  },

  /**
   * 获取在线用户列表
   */
  async getOnlineUsers(deviceType?: string): Promise<ApiResponse<OnlineUser[]>> {
    const params = deviceType ? { device_type: deviceType } : {}
    return request.get(API_ENDPOINTS.ONLINE_USER.USERS, { params })
  },

  /**
   * 获取在线用户详细统计
   */
  async getOnlineStatistics(): Promise<ApiResponse<OnlineStatistics>> {
    return request.get(API_ENDPOINTS.ONLINE_USER.STATISTICS)
  },

  /**
   * 发送心跳更新活跃状态
   */
  async sendHeartbeat(deviceType: string = 'h5'): Promise<ApiResponse<null>> {
    return request.post(API_ENDPOINTS.ONLINE_USER.HEARTBEAT, { device_type: deviceType })
  },

  /**
   * 记录登录
   */
  async recordLogin(deviceType: string = 'h5', userId?: number, userName?: string): Promise<ApiResponse<null>> {
    const params: Record<string, unknown> = { device_type: deviceType }
    if (userId) {
      params.user_id = userId
      params.user_name = userName
    }
    return request.post(API_ENDPOINTS.ONLINE_USER.LOGIN, params)
  },

  /**
   * 记录登出
   */
  async logout(userId?: number, deviceType?: string): Promise<ApiResponse<null>> {
    const params: Record<string, unknown> = {}
    if (userId) {
      params.user_id = userId
    }
    if (deviceType) {
      params.device_type = deviceType
    }
    return request.post(API_ENDPOINTS.ONLINE_USER.LOGOUT, params)
  },
}

export default onlineUserService
