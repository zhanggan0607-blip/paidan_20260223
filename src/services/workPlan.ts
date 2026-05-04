import request from '../api/request'
import { API_ENDPOINTS } from '../api/endpoints'
import type { ApiResponse, PaginatedData } from '@sstcp/shared'
import { PLAN_TYPE_LIST } from '../config/constants'

export type PlanType = (typeof PLAN_TYPE_LIST)[number]

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

export const workPlanService = {
  async getList(params?: {
    page?: number
    size?: number
    plan_type?: PlanType | ''
    project_name?: string
    client_name?: string
    status?: string
    plan_id?: string
  }): Promise<ApiResponse<PaginatedData<WorkPlan>>> {
    return await request.get(API_ENDPOINTS.WORK_PLAN.LIST, { params })
  },

  async getAll(params?: { plan_type?: PlanType }): Promise<ApiResponse<WorkPlan[]>> {
    return await request.get(API_ENDPOINTS.WORK_PLAN.ALL, { params })
  },

  async getById(id: number): Promise<ApiResponse<WorkPlan>> {
    return await request.get(API_ENDPOINTS.WORK_PLAN.DETAIL(id))
  },

  async create(data: WorkPlanCreate): Promise<ApiResponse<WorkPlan>> {
    return await request.post(API_ENDPOINTS.WORK_PLAN.LIST, data)
  },

  async update(id: number, data: WorkPlanUpdate): Promise<ApiResponse<WorkPlan>> {
    return await request.put(API_ENDPOINTS.WORK_PLAN.DETAIL(id), data)
  },

  async delete(id: number): Promise<ApiResponse<null>> {
    return await request.delete(API_ENDPOINTS.WORK_PLAN.DETAIL(id))
  },
}
