import apiClient from '../utils/api'
import type { SpotWork as SpotWorkType, SpotWorkWorker, ApiResponse, PaginatedResponse } from '../types/api'

export type SpotWork = SpotWorkType

export interface SpotWorkCreate {
  work_id: string
  plan_id?: string
  project_id: string
  project_name: string
  plan_start_date: string
  plan_end_date: string
  client_name?: string
  client_contact?: string
  client_contact_info?: string
  maintenance_personnel?: string
  work_content?: string
  photos?: string
  signature?: string
  status?: string
  remarks?: string
}

export interface SpotWorkUpdate {
  work_id?: string
  plan_id?: string
  project_id?: string
  project_name?: string
  plan_start_date?: string
  plan_end_date?: string
  client_name?: string
  client_contact?: string
  client_contact_info?: string
  maintenance_personnel?: string
  work_content?: string
  photos?: string
  signature?: string
  status?: string
  remarks?: string
}

export interface SpotWorkPaginatedResponse {
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
    work_id?: string
    status?: string
  }): Promise<SpotWorkPaginatedResponse> {
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
