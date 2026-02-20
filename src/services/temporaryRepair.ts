import apiClient from '../utils/api'
import type { TemporaryRepair as TemporaryRepairType, ApiResponse } from '../types/api'

export type TemporaryRepair = TemporaryRepairType

export interface TemporaryRepairCreate {
  repair_id: string
  plan_id?: string
  project_id: string
  project_name: string
  plan_start_date: string
  plan_end_date: string
  client_name?: string
  maintenance_personnel?: string
  status?: string
  remarks?: string
  fault_description?: string
  solution?: string
  photos?: string[]
  signature?: string
  execution_date?: string
}

export interface TemporaryRepairUpdate {
  repair_id?: string
  plan_id?: string
  project_id?: string
  project_name?: string
  plan_start_date?: string
  plan_end_date?: string
  client_name?: string
  maintenance_personnel?: string
  status?: string
  remarks?: string
  fault_description?: string
  solution?: string
  photos?: string[]
  signature?: string
  execution_date?: string
}

export interface TemporaryRepairPaginatedResponse {
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
  }): Promise<TemporaryRepairPaginatedResponse> {
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
