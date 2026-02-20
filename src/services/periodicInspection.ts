import apiClient from '../utils/api'
import type { PeriodicInspection as PeriodicInspectionType, ApiResponse } from '../types/api'

export type PeriodicInspection = PeriodicInspectionType

export interface PeriodicInspectionCreate {
  inspection_id: string
  plan_id?: string
  project_id: string
  project_name: string
  plan_start_date: string
  plan_end_date: string
  client_name?: string
  maintenance_personnel?: string
  status?: string
  filled_count?: number
  total_count?: number
  execution_result?: string
  remarks?: string
  signature?: string
}

export interface PeriodicInspectionUpdate {
  inspection_id: string
  plan_id?: string
  project_id: string
  project_name: string
  plan_start_date: string
  plan_end_date: string
  client_name?: string
  maintenance_personnel?: string
  status: string
  filled_count?: number
  total_count?: number
  execution_result?: string
  remarks?: string
  signature?: string
}

export interface PeriodicInspectionPaginatedResponse {
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
    inspection_id?: string
    status?: string
  }): Promise<PeriodicInspectionPaginatedResponse> {
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
