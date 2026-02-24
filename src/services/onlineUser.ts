/**
 * 在线用户服务
 * 提供在线用户统计和心跳功能
 */
import api from '@/utils/api'

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
    const response = await api.get('/online/count')
    return response.data
  },

  /**
   * 获取在线用户列表
   */
  async getOnlineUsers(deviceType?: string): Promise<OnlineUser[]> {
    const params = deviceType ? { device_type: deviceType } : {}
    const response = await api.get('/online/users', { params })
    return response.data
  },

  /**
   * 获取在线用户详细统计
   */
  async getOnlineStatistics(): Promise<OnlineStatistics> {
    const response = await api.get('/online/statistics')
    return response.data
  },

  /**
   * 发送心跳更新活跃状态
   */
  async sendHeartbeat(deviceType: string = 'pc'): Promise<void> {
    await api.post('/online/heartbeat', { device_type: deviceType })
  },

  /**
   * 记录登录
   * @param deviceType 设备类型 pc/h5
   * @param userId 用户ID（可选，用于PC端切换用户场景）
   * @param userName 用户名称（可选）
   */
  async recordLogin(deviceType: string = 'pc', userId?: number, userName?: string): Promise<void> {
    const params: any = { device_type: deviceType }
    if (userId) {
      params.user_id = userId
      params.user_name = userName
    }
    await api.post('/online/login', params)
  },

  /**
   * 记录登出
   * @param userId 用户ID（可选，用于PC端切换用户场景）
   * @param deviceType 设备类型（可选，用于PC端切换用户场景）
   */
  async logout(userId?: number, deviceType?: string): Promise<void> {
    const params: any = {}
    if (userId) {
      params.user_id = userId
    }
    if (deviceType) {
      params.device_type = deviceType
    }
    await api.post('/online/logout', params)
  }
}

export default onlineUserService
