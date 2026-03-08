/**
 * 在线用户服务类型定义
 */
export interface OnlineUser {
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
