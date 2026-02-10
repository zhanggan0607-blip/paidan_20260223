import apiClient from '../utils/api'

export interface OverdueItem {
  id: string
  workOrderNo: string
  projectId: string
  projectName: string
  customerName: string
  workOrderType: string
  planEndDate: string
  workOrderStatus: string
  overdueDays: number
  executor: string
}

export interface ApiResponse<T = any> {
  code: number
  message: string
  data: T
}

export interface OverdueAlertResponse {
  items: OverdueItem[]
  total: number
}

export const overdueAlertService = {
  async getOverdueAlerts(params?: {
    project_name?: string
    client_name?: string
    work_order_type?: string
  }): Promise<ApiResponse<OverdueAlertResponse>> {
    return await apiClient.get('/overdue-alert', { params })
  }
}
