/**
 * 在线用户服务
 * 提供在线用户统计和心跳功能
 */
import request from '../utils/api'

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

export const onlineUserService = {
  /**
   * 获取在线用户数量统计
   */
  async getOnlineCount(): Promise<OnlineCount> {
    const response = await request.get('/online/count')
    return response.data
  },

  /**
   * 获取在线用户列表
   */
  async getOnlineUsers(deviceType?: string): Promise<OnlineUser[]> {
    const params = deviceType ? { device_type: deviceType } : {}
    const response = await request.get('/online/users', { params })
    return response.data
  },

  /**
   * 获取在线用户详细统计
   */
  async getOnlineStatistics(): Promise<OnlineStatistics> {
    const response = await request.get('/online/statistics')
    return response.data
  },

  /**
   * 发送心跳更新活跃状态
   */
  async sendHeartbeat(deviceType: string = 'h5'): Promise<void> {
    await request.post('/online/heartbeat', { device_type: deviceType })
  },

  /**
   * 记录登录
   * @param deviceType 设备类型 pc/h5
   * @param userId 用户ID（可选，用于PC端切换用户场景）
   * @param userName 用户名称（可选）
   */
  async recordLogin(deviceType: string = 'h5', userId?: number, userName?: string): Promise<void> {
    const params: any = { device_type: deviceType }
    if (userId) {
      params.user_id = userId
      params.user_name = userName
    }
    await request.post('/online/login', params)
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
    await request.post('/online/logout', params)
  }
}

export default onlineUserService
