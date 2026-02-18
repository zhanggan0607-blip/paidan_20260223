import apiClient from '../utils/api'

export interface WorkOrder {
  id: number
  order_id: string
  order_type: string
  order_type_code: string
  project_id: string
  project_name: string
  client_name: string
  plan_start_date: string
  plan_end_date: string
  maintenance_personnel: string
  status: string
  remarks: string
  execution_result?: string
  signature?: string
  created_at: string
  updated_at: string
}

export interface PaginatedResponse {
  code: number
  message: string
  data: {
    content: WorkOrder[]
    totalElements: number
    totalPages: number
    size: number
    number: number
    first: boolean
    last: boolean
  }
}

export interface ApiResponse<T = any> {
  code: number
  message: string
  data: T
}

export const workOrderService = {
  async getList(params?: {
    page?: number
    size?: number
    project_name?: string
    order_id?: string
    order_type?: string
    status?: string
    maintenance_personnel?: string
  }): Promise<PaginatedResponse> {
    return await apiClient.get('/work-order', { params })
  },

  async getAll(): Promise<ApiResponse<WorkOrder[]>> {
    return await apiClient.get('/work-order/all/list')
  }
}
