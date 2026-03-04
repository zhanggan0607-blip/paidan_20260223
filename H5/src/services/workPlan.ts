/**
 * 工作计划服务
 * 提供工作计划的增删改查功能
 */
import request from '../api/request'
import { API_ENDPOINTS } from '../api/endpoints'
import type { ApiResponse, PaginatedResponse } from '../types/api'
import type { WorkPlan, WorkPlanQueryParams, WorkPlanCreate, WorkPlanUpdate, WorkPlanStatistics } from '../types/models'

export const workPlanService = {
  /**
   * 获取工作计划列表（分页）
   */
  async getList(params?: WorkPlanQueryParams): Promise<PaginatedResponse<WorkPlan>> {
    return request.get(API_ENDPOINTS.WORK_PLAN.LIST, { params })
  },

  /**
   * 获取工作计划详情
   */
  async getById(id: number): Promise<ApiResponse<WorkPlan>> {
    return request.get(API_ENDPOINTS.WORK_PLAN.DETAIL(id))
  },

  /**
   * 获取所有工作计划（不分页）
   */
  async getAll(): Promise<ApiResponse<WorkPlan[]>> {
    return request.get(API_ENDPOINTS.WORK_PLAN.ALL)
  },

  /**
   * 创建工作计划
   */
  async create(data: WorkPlanCreate): Promise<ApiResponse<WorkPlan>> {
    return request.post(API_ENDPOINTS.WORK_PLAN.LIST, data)
  },

  /**
   * 更新工作计划
   */
  async update(id: number, data: WorkPlanUpdate): Promise<ApiResponse<WorkPlan>> {
    return request.put(API_ENDPOINTS.WORK_PLAN.DETAIL(id), data)
  },

  /**
   * 删除工作计划
   */
  async delete(id: number): Promise<ApiResponse<null>> {
    return request.delete(API_ENDPOINTS.WORK_PLAN.DETAIL(id))
  },

  /**
   * 获取统计数据
   */
  async getStatistics(): Promise<ApiResponse<WorkPlanStatistics>> {
    return request.get(API_ENDPOINTS.WORK_PLAN.STATISTICS)
  },
}

export default workPlanService
