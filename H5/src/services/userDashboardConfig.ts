/**
 * 用户仪表盘配置服务
 * 提供用户仪表盘配置的查询和更新功能
 */
import request from '../api/request'
import { API_ENDPOINTS } from '../api/endpoints'
import type { ApiResponse } from '../types/api'

export interface DashboardItem {
  id: string
  visible: boolean
  position: number
}

export interface DashboardConfig {
  cards: DashboardItem[]
  charts: DashboardItem[]
}

export const userDashboardConfigService = {
  /**
   * 获取用户仪表盘配置
   */
  async get(): Promise<ApiResponse<DashboardConfig>> {
    return request.get(API_ENDPOINTS.USER_DASHBOARD_CONFIG.GET)
  },

  /**
   * 更新用户仪表盘配置
   */
  async update(data: DashboardConfig): Promise<ApiResponse<DashboardConfig>> {
    return request.put(API_ENDPOINTS.USER_DASHBOARD_CONFIG.UPDATE, data)
  },
}

export default userDashboardConfigService
