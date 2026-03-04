/**
 * 临时维修服务
 * 提供临时维修工单的增删改查等功能
 */
import request from '../api/request'
import { API_ENDPOINTS } from '../api/endpoints'
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
  /**
   * 获取临时维修列表（分页）
   */
  async getList(params?: {
    page?: number
    size?: number
    project_name?: string
    repair_id?: string
    status?: string
  }): Promise<TemporaryRepairPaginatedResponse> {
    return await request.get(API_ENDPOINTS.TEMPORARY_REPAIR.LIST, { params })
  },

  /**
   * 获取所有临时维修（不分页）
   */
  async getAll(): Promise<ApiResponse<TemporaryRepair[]>> {
    return await request.get(API_ENDPOINTS.TEMPORARY_REPAIR.ALL)
  },

  /**
   * 获取临时维修详情
   */
  async getById(id: number): Promise<ApiResponse<TemporaryRepair>> {
    return await request.get(API_ENDPOINTS.TEMPORARY_REPAIR.DETAIL(id))
  },

  /**
   * 创建临时维修
   */
  async create(data: TemporaryRepairCreate): Promise<ApiResponse<TemporaryRepair>> {
    return await request.post(API_ENDPOINTS.TEMPORARY_REPAIR.LIST, data)
  },

  /**
   * 更新临时维修
   */
  async update(id: number, data: TemporaryRepairUpdate): Promise<ApiResponse<TemporaryRepair>> {
    return await request.put(API_ENDPOINTS.TEMPORARY_REPAIR.DETAIL(id), data)
  },

  /**
   * 删除临时维修
   */
  async delete(id: number): Promise<ApiResponse<null>> {
    return await request.delete(API_ENDPOINTS.TEMPORARY_REPAIR.DETAIL(id))
  }
}
