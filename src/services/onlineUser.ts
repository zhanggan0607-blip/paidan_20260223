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
   */
  async recordLogin(deviceType: string = 'pc'): Promise<void> {
    await api.post('/online/login', null, { params: { device_type: deviceType } })
  },

  /**
   * 记录登出
   */
  async logout(): Promise<void> {
    await api.post('/online/logout')
  }
}

export default onlineUserService
