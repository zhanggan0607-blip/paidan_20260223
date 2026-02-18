import apiClient from '../utils/api'

export interface PeriodicInspection {
  id: number
  inspection_id: string
  project_id: string
  project_name: string
  plan_start_date: string
  plan_end_date: string
  client_name?: string
  client_contact?: string
  client_contact_info?: string
  client_contact_position?: string
  address?: string
  maintenance_personnel?: string
  status: string
  remarks?: string
  created_at: string
  updated_at: string
}

export interface PeriodicInspectionCreate {
  inspection_id: string
  project_id: string
  project_name: string
  plan_start_date: string
  plan_end_date: string
  client_name?: string
  maintenance_personnel?: string
  status: string
  remarks?: string
}

export interface PeriodicInspectionUpdate {
  inspection_id: string
  project_id: string
  project_name: string
  plan_start_date: string
  plan_end_date: string
  client_name?: string
  maintenance_personnel?: string
  status: string
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
    content: PeriodicInspection[]
    totalElements: number
    totalPages: number
    size: number
    number: number
    first: boolean
    last: boolean
  }
}

export const periodicInspectionService = {
  async getList(params?: {
    page?: number
    size?: number
    project_name?: string
    client_name?: string
    status?: string
  }): Promise<PaginatedResponse> {
    return await apiClient.get('/periodic-inspection', { params })
  },

  async getById(id: number): Promise<ApiResponse<PeriodicInspection>> {
    return await apiClient.get(`/periodic-inspection/${id}`)
  },

  async create(data: PeriodicInspectionCreate): Promise<ApiResponse<PeriodicInspection>> {
    return await apiClient.post('/periodic-inspection', data)
  },

  async update(id: number, data: PeriodicInspectionUpdate): Promise<ApiResponse<PeriodicInspection>> {
    return await apiClient.put(`/periodic-inspection/${id}`, data)
  },

  async delete(id: number): Promise<ApiResponse<null>> {
    return await apiClient.delete(`/periodic-inspection/${id}`)
  },

  async getAll(): Promise<ApiResponse<PeriodicInspection[]>> {
    return await apiClient.get('/periodic-inspection/all/list')
  }
}

