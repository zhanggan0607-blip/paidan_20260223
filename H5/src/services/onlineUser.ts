/**
 * 在线用户服务
 * 提供在线用户状态记录和管理功能
 */
import request from '../api/request'
import { API_ENDPOINTS } from '../api/endpoints'
import type {
  ApiResponse,
  OnlineUser as OnlineUserType,
  OnlineStatistics as OnlineStatisticsType,
} from '../types'

interface OnlineLoginRequest {
  device_type: string
  user_id: number
  user_name: string
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
  async getUsers(): Promise<ApiResponse<OnlineUserType[]>> {
    return request.get(API_ENDPOINTS.ONLINE_USER.USERS)
  },

  /**
   * 获取在线用户统计
   */
  async getStatistics(): Promise<ApiResponse<OnlineStatisticsType>> {
    return request.get(API_ENDPOINTS.ONLINE_USER.STATISTICS)
  },
}

export default onlineUserService
