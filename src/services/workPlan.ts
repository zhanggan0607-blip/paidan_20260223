/**
 * 工作计划服务
 * 提供工作计划的增删改查等功能
 */
import request from '../api/request'
import { API_ENDPOINTS } from '../api/endpoints'
import { PLAN_TYPE_LIST, PLAN_TYPES } from '../config/constants'

export type PlanType = typeof PLAN_TYPE_LIST[number]

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

export interface ApiResponse<T = unknown> {
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
  /**
   * 获取工作计划列表（分页）
   */
  async getList(params?: {
    page?: number
    size?: number
    plan_type?: PlanType
    project_name?: string
    client_name?: string
    status?: string
  }): Promise<PaginatedResponse> {
    return await request.get(API_ENDPOINTS.WORK_PLAN.LIST, { params })
  },

  /**
   * 获取所有工作计划（不分页）
   */
  async getAll(params?: {
    plan_type?: PlanType
  }): Promise<ApiResponse<WorkPlan[]>> {
    return await request.get(API_ENDPOINTS.WORK_PLAN.ALL, { params })
  },

  /**
   * 获取工作计划详情
   */
  async getById(id: number): Promise<ApiResponse<WorkPlan>> {
    return await request.get(API_ENDPOINTS.WORK_PLAN.DETAIL(id))
  },

  /**
   * 创建工作计划
   */
  async create(data: WorkPlanCreate): Promise<ApiResponse<WorkPlan>> {
    return await request.post(API_ENDPOINTS.WORK_PLAN.LIST, data)
  },

  /**
   * 更新工作计划
   */
  async update(id: number, data: WorkPlanUpdate): Promise<ApiResponse<WorkPlan>> {
    return await request.put(API_ENDPOINTS.WORK_PLAN.DETAIL(id), data)
  },

  /**
   * 删除工作计划
   */
  async delete(id: number): Promise<ApiResponse<null>> {
    return await request.delete(API_ENDPOINTS.WORK_PLAN.DETAIL(id))
  }
}
