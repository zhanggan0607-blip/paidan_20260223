/**
 * 维保计划服务
 * 提供维保计划的增删改查功能
 */
import request from '../api/request'
import { API_ENDPOINTS } from '../api/endpoints'
import type { ApiResponse, PaginatedResponse } from '../types/api'
import type { MaintenancePlan } from '../types/models'

export interface MaintenancePlanQueryParams {
  page?: number
  size?: number
  project_name?: string
  plan_type?: string
  status?: string
}

export interface MaintenancePlanCreate {
  plan_name: string
  project_id: string
  plan_type?: string
  equipment_id?: string
  equipment_name?: string
  equipment_model?: string
  equipment_location?: string
  plan_start_date: string
  plan_end_date: string
  maintenance_personnel?: string
  responsible_department?: string
  contact_info?: string
  maintenance_content?: string
  maintenance_requirements?: string
  maintenance_standard?: string
  remarks?: string
  inspection_items?: string
}

export interface MaintenancePlanUpdate extends MaintenancePlanCreate {}

export const maintenancePlanService = {
  /**
   * 获取维保计划列表（分页）
   */
  async getList(params?: MaintenancePlanQueryParams): Promise<PaginatedResponse<MaintenancePlan>> {
    return request.get(API_ENDPOINTS.MAINTENANCE_PLAN.LIST, { params })
  },

  /**
   * 获取维保计划详情
   */
  async getById(id: number): Promise<ApiResponse<MaintenancePlan>> {
    return request.get(API_ENDPOINTS.MAINTENANCE_PLAN.DETAIL(id))
  },

  /**
   * 根据计划ID获取维保计划详情
   */
  async getByPlanId(planId: string): Promise<ApiResponse<MaintenancePlan>> {
    return request.get(API_ENDPOINTS.MAINTENANCE_PLAN.BY_PLAN_ID(planId))
  },

  /**
   * 获取所有维保计划（不分页）
   */
  async getAll(): Promise<ApiResponse<MaintenancePlan[]>> {
    return request.get(API_ENDPOINTS.MAINTENANCE_PLAN.ALL)
  },

  /**
   * 创建维保计划
   */
  async create(data: MaintenancePlanCreate): Promise<ApiResponse<MaintenancePlan>> {
    return request.post(API_ENDPOINTS.MAINTENANCE_PLAN.LIST, data)
  },

  /**
   * 更新维保计划
   */
  async update(id: number, data: MaintenancePlanUpdate): Promise<ApiResponse<MaintenancePlan>> {
    return request.put(API_ENDPOINTS.MAINTENANCE_PLAN.DETAIL(id), data)
  },

  /**
   * 删除维保计划
   */
  async delete(id: number): Promise<ApiResponse<null>> {
    return request.delete(API_ENDPOINTS.MAINTENANCE_PLAN.DETAIL(id))
  },

  /**
   * 生成工单
   */
  async generateWorkOrders(id: number): Promise<ApiResponse<unknown>> {
    return request.post(API_ENDPOINTS.MAINTENANCE_PLAN.GENERATE_WORK_ORDERS(id))
  },
}

export default maintenancePlanService
