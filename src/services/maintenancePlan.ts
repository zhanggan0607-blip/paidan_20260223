import request from '../api/request'
import { API_ENDPOINTS } from '../api/endpoints'
import type { ApiResponse, MaintenancePlan as BaseMaintenancePlan } from '@sstcp/shared'

export type MaintenancePlan = BaseMaintenancePlan

export interface MaintenancePlanDisplay {
  project_id: string
  project_name: string
  plan_start_date: string
  plan_end_date: string
  plan_count: number
  client_name: string
  address: string
  plans: MaintenancePlan[]
}

export interface MaintenancePlanCreate {
  plan_id: string
  plan_name: string
  project_id: string
  plan_type: string
  equipment_id: string
  equipment_name: string
  equipment_model?: string
  equipment_location?: string
  plan_start_date: string
  plan_end_date: string
  execution_date?: string
  next_maintenance_date?: string
  maintenance_personnel?: string
  responsible_department?: string
  contact_info?: string
  maintenance_content: string
  maintenance_requirements?: string
  maintenance_standard?: string
  plan_status: string
  status: string
  completion_rate?: number
  remarks?: string
  inspection_items?: string
}

export interface MaintenancePlanUpdate {
  plan_id: string
  plan_name: string
  project_id: string
  plan_type: string
  equipment_id: string
  equipment_name: string
  equipment_model?: string
  equipment_location?: string
  plan_start_date: string
  plan_end_date: string
  execution_date?: string
  next_maintenance_date?: string
  maintenance_personnel?: string
  responsible_department?: string
  contact_info?: string
  maintenance_content: string
  maintenance_requirements?: string
  maintenance_standard?: string
  plan_status: string
  status: string
  completion_rate?: number
  remarks?: string
  inspection_items?: string
}

export interface PaginatedResponse {
  code: number
  message: string
  data: {
    content: MaintenancePlan[]
    items: MaintenancePlan[]
    totalElements: number
    total: number
    totalPages: number
    size: number
    number: number
    first: boolean
    last: boolean
  }
}

export const maintenancePlanService = {
  async getList(params?: {
    page?: number
    size?: number
    plan_name?: string
    project_id?: string
    equipment_name?: string
    plan_status?: string
    execution_status?: string
    responsible_person?: string
    project_name?: string
    client_name?: string
    plan_type?: string
  }): Promise<PaginatedResponse> {
    return await request.get(API_ENDPOINTS.MAINTENANCE_PLAN.LIST, { params })
  },

  async getById(id: number): Promise<ApiResponse<MaintenancePlan>> {
    return await request.get(API_ENDPOINTS.MAINTENANCE_PLAN.DETAIL(id))
  },

  async create(data: MaintenancePlanCreate): Promise<ApiResponse<MaintenancePlan>> {
    return await request.post(API_ENDPOINTS.MAINTENANCE_PLAN.LIST, data)
  },

  async update(id: number, data: MaintenancePlanUpdate): Promise<ApiResponse<MaintenancePlan>> {
    return await request.put(API_ENDPOINTS.MAINTENANCE_PLAN.DETAIL(id), data)
  },

  async delete(id: number): Promise<ApiResponse<null>> {
    return await request.delete(API_ENDPOINTS.MAINTENANCE_PLAN.DETAIL(id))
  },

  async getAll(): Promise<ApiResponse<MaintenancePlan[]>> {
    return await request.get(API_ENDPOINTS.MAINTENANCE_PLAN.ALL)
  },

  async getByProjectId(projectId: string): Promise<ApiResponse<MaintenancePlan[]>> {
    return await request.get(`/maintenance-plan/project/${projectId}`)
  },

  async getUpcoming(days: number = 7): Promise<ApiResponse<MaintenancePlan[]>> {
    return await request.get('/maintenance-plan/upcoming/list', { params: { days } })
  },

  async updateStatus(id: number, status: string): Promise<ApiResponse<MaintenancePlan>> {
    return await request.patch(`/maintenance-plan/${id}/status`, null, { params: { status } })
  },

  async updateCompletionRate(id: number, rate: number): Promise<ApiResponse<MaintenancePlan>> {
    return await request.patch(`/maintenance-plan/${id}/completion-rate`, null, {
      params: { rate },
    })
  },

  async getByDateRange(
    startDate: string,
    endDate: string
  ): Promise<ApiResponse<MaintenancePlan[]>> {
    return await request.get('/maintenance-plan/date-range/list', {
      params: {
        start_date: startDate,
        end_date: endDate,
      },
    })
  },
}
