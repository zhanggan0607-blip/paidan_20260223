import apiClient from '../utils/api'

export interface TemporaryRepair {
  id: number
  repair_id: string
  project_id: string
  project_name: string
  plan_start_date: string
  plan_end_date: string
  client_name: string
  maintenance_personnel: string
  status: string
  remarks?: string
  created_at: string
  updated_at: string
}

export interface TemporaryRepairCreate {
  repair_id: string
  project_id: string
  project_name: string
  plan_start_date: string
  plan_end_date: string
  client_name: string
  maintenance_personnel: string
  status: string
  remarks?: string
}

export interface TemporaryRepairUpdate {
  repair_id?: string
  project_id?: string
  project_name?: string
  plan_start_date?: string
  plan_end_date?: string
  client_name?: string
  maintenance_personnel?: string
  status?: string
  remarks?: string
}

export interface ApiResponse<T = any> {
  code: number
  message: string
  data: T
}

export interface PaginatedResponse {
  code: number
  message: string
  data: {
    content: TemporaryRepair[]
    totalElements: number
    totalPages: number
    size: number
    number: number
    first: boolean
    last: boolean
  }
}

export const temporaryRepairService = {
  async getList(params?: {
    page?: number
    size?: number
    project_name?: string
    repair_id?: string
    status?: string
  }): Promise<PaginatedResponse> {
    return await apiClient.get('/temporary-repair', { params })
  },

  async getAll(): Promise<ApiResponse<TemporaryRepair[]>> {
    return await apiClient.get('/temporary-repair/all/list')
  },

  async getById(id: number): Promise<ApiResponse<TemporaryRepair>> {
    return await apiClient.get(`/temporary-repair/${id}`)
  },

  async create(data: TemporaryRepairCreate): Promise<ApiResponse<TemporaryRepair>> {
    return await apiClient.post('/temporary-repair', data)
  },

  async update(id: number, data: TemporaryRepairUpdate): Promise<ApiResponse<TemporaryRepair>> {
    return await apiClient.put(`/temporary-repair/${id}`, data)
  },

  async delete(id: number): Promise<ApiResponse<null>> {
    return await apiClient.delete(`/temporary-repair/${id}`)
  }
}