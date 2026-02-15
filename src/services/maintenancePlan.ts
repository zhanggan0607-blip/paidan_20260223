import apiClient from '../utils/api'

export interface MaintenancePlan {
  id: number
  plan_id: string
  plan_name: string
  project_id: string
  project_name?: string
  plan_type: string
  equipment_id: string
  equipment_name: string
  equipment_model?: string
  equipment_location?: string
  plan_start_date: string
  plan_end_date: string
  execution_date?: string
  next_maintenance_date?: string
  responsible_person: string
  responsible_department?: string
  contact_info?: string
  maintenance_content: string
  maintenance_requirements?: string
  maintenance_standard?: string
  plan_status: string
  execution_status: string
  completion_rate?: number
  remarks?: string
  created_at: string
  updated_at: string
}

export interface MaintenancePlanDisplay {
  id: string
  planId: string
  projectName: string
  startDate: string
  endDate: string
  planCount: number
  clientName: string
  address: string
  originalData: MaintenancePlan
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
  responsible_person: string
  responsible_department?: string
  contact_info?: string
  maintenance_content: string
  maintenance_requirements?: string
  maintenance_standard?: string
  plan_status: string
  execution_status: string
  completion_rate?: number
  remarks?: string
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
  responsible_person: string
  responsible_department?: string
  contact_info?: string
  maintenance_content: string
  maintenance_requirements?: string
  maintenance_standard?: string
  plan_status: string
  execution_status: string
  completion_rate?: number
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
    content: MaintenancePlan[]
    totalElements: number
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
    return await apiClient.get('/maintenance-plan', { params })
  },

  async getById(id: number): Promise<ApiResponse<MaintenancePlan>> {
    return await apiClient.get(`/maintenance-plan/${id}`)
  },

  async create(data: MaintenancePlanCreate): Promise<ApiResponse<MaintenancePlan>> {
    return await apiClient.post('/maintenance-plan', data)
  },

  async update(id: number, data: MaintenancePlanUpdate): Promise<ApiResponse<MaintenancePlan>> {
    return await apiClient.put(`/maintenance-plan/${id}`, data)
  },

  async delete(id: number): Promise<ApiResponse<null>> {
    return await apiClient.delete(`/maintenance-plan/${id}`)
  },

  async getAll(): Promise<ApiResponse<MaintenancePlan[]>> {
    return await apiClient.get('/maintenance-plan/all/list')
  },

  async getByProjectId(projectId: string): Promise<ApiResponse<MaintenancePlan[]>> {
    return await apiClient.get(`/maintenance-plan/project/${projectId}`)
  },

  async getUpcoming(days: number = 7): Promise<ApiResponse<MaintenancePlan[]>> {
    return await apiClient.get('/maintenance-plan/upcoming/list', { params: { days } })
  },

  async updateStatus(id: number, status: string): Promise<ApiResponse<MaintenancePlan>> {
    return await apiClient.patch(`/maintenance-plan/${id}/status`, null, { params: { status } })
  },

  async updateCompletionRate(id: number, rate: number): Promise<ApiResponse<MaintenancePlan>> {
    return await apiClient.patch(`/maintenance-plan/${id}/completion-rate`, null, { params: { rate } })
  },

  async getByDateRange(startDate: string, endDate: string): Promise<ApiResponse<MaintenancePlan[]>> {
    return await apiClient.get('/maintenance-plan/date-range/list', {
      params: {
        start_date: startDate,
        end_date: endDate
      }
    })
  }
}
