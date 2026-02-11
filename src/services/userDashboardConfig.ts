import apiClient from '../utils/api'

export interface DashboardConfig {
  cards: Array<{
    id: string
    visible: boolean
    position: number
  }>
  charts: Array<{
    id: string
    visible: boolean
    position: number
  }>
  layout: 'grid' | 'list'
}

export interface ApiResponse<T = any> {
  code: number
  message: string
  data: T
}

export const userDashboardConfigService = {
  async getConfig(dashboardType: string, userId?: string): Promise<ApiResponse<DashboardConfig>> {
    const params = userId ? { user_id: userId } : {}
    return await apiClient.get(`/user-dashboard-config/${dashboardType}`, { params })
  },

  async saveConfig(dashboardType: string, config: DashboardConfig, userId?: string): Promise<ApiResponse<DashboardConfig>> {
    const params = userId ? { user_id: userId, dashboard_type: dashboardType } : { dashboard_type: dashboardType }
    return await apiClient.post('/user-dashboard-config', config, { params })
  },

  async deleteConfig(dashboardType: string, userId?: string): Promise<ApiResponse<null>> {
    const params = userId ? { user_id: userId, dashboard_type: dashboardType } : { dashboard_type: dashboardType }
    return await apiClient.delete(`/user-dashboard-config/${dashboardType}`, { params })
  },

  async getAllConfigs(userId: string): Promise<ApiResponse<DashboardConfig[]>> {
    return await apiClient.get(`/user-dashboard-config/all/${userId}`)
  }
}
