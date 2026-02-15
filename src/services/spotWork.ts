import apiClient from '../utils/api'

export interface SpotWork {
  id: number
  work_id: string
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

export interface SpotWorkCreate {
  work_id: string
  project_id: string
  project_name: string
  plan_start_date: string
  plan_end_date: string
  client_name: string
  maintenance_personnel: string
  status: string
  remarks?: string
}

export interface SpotWorkUpdate {
  work_id?: string
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
    content: SpotWork[]
    totalElements: number
    totalPages: number
    size: number
    number: number
    first: boolean
    last: boolean
  }
}

export const spotWorkService = {
  async getList(params?: {
    page?: number
    size?: number
    project_name?: string
    client_name?: string
    status?: string
  }): Promise<PaginatedResponse> {
    return await apiClient.get('/spot-work', { params })
  },

  async getAll(): Promise<ApiResponse<SpotWork[]>> {
    return await apiClient.get('/spot-work/all/list')
  },

  async getById(id: number): Promise<ApiResponse<SpotWork>> {
    return await apiClient.get(`/spot-work/${id}`)
  },

  async create(data: SpotWorkCreate): Promise<ApiResponse<SpotWork>> {
    return await apiClient.post('/spot-work', data)
  },

  async update(id: number, data: SpotWorkUpdate): Promise<ApiResponse<SpotWork>> {
    return await apiClient.put(`/spot-work/${id}`, data)
  },

  async delete(id: number): Promise<ApiResponse<null>> {
    return await apiClient.delete(`/spot-work/${id}`)
  }
}
