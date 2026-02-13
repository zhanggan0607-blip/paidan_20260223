import apiClient from '../utils/api'

export const PLAN_TYPES = ['定期巡检', '临时维修', '零星用工'] as const
export type PlanType = typeof PLAN_TYPES[number]

export interface WorkPlan {
  id: number
  plan_id: string
  plan_type: PlanType
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

export interface WorkPlanCreate {
  plan_id: string
  plan_type: PlanType
  project_id: string
  project_name: string
  plan_start_date: string
  plan_end_date: string
  client_name: string
  maintenance_personnel: string
  status: string
  remarks?: string
}

export interface WorkPlanUpdate {
  plan_id?: string
  plan_type?: PlanType
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
    content: WorkPlan[]
    totalElements: number
    totalPages: number
    size: number
    number: number
    first: boolean
    last: boolean
  }
}

export const workPlanService = {
  async getList(params?: {
    page?: number
    size?: number
    plan_type?: PlanType
    project_name?: string
    client_name?: string
    status?: string
  }): Promise<PaginatedResponse> {
    return await apiClient.get('/work-plan', { params })
  },

  async getAll(params?: {
    plan_type?: PlanType
  }): Promise<ApiResponse<WorkPlan[]>> {
    return await apiClient.get('/work-plan/all/list', { params })
  },

  async getById(id: number): Promise<ApiResponse<WorkPlan>> {
    return await apiClient.get(`/work-plan/${id}`)
  },

  async create(data: WorkPlanCreate): Promise<ApiResponse<WorkPlan>> {
    return await apiClient.post('/work-plan', data)
  },

  async update(id: number, data: WorkPlanUpdate): Promise<ApiResponse<WorkPlan>> {
    return await apiClient.put(`/work-plan/${id}`, data)
  },

  async delete(id: number): Promise<ApiResponse<null>> {
    return await apiClient.delete(`/work-plan/${id}`)
  }
}
