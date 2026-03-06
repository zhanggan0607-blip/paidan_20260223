/**
 * 临时维修服务
 * 提供临时维修工单的增删改查、提交、审批等功能
 */
import request from '../api/request'
import { API_ENDPOINTS } from '../api/endpoints'
import type { ApiResponse, PaginatedResponse } from '../types/api'
import type {
  TemporaryRepair,
  TemporaryRepairCreate,
  TemporaryRepairUpdate,
  TemporaryRepairQueryParams,
} from '../types/models'

export const temporaryRepairService = {
  /**
   * 获取临时维修列表（分页）
   */
  async getList(params?: TemporaryRepairQueryParams): Promise<PaginatedResponse<TemporaryRepair>> {
    return request.get(API_ENDPOINTS.TEMPORARY_REPAIR.LIST, { params })
  },

  /**
   * 获取临时维修详情
   */
  async getById(id: number): Promise<ApiResponse<TemporaryRepair>> {
    return request.get(API_ENDPOINTS.TEMPORARY_REPAIR.DETAIL(id))
  },

  /**
   * 获取所有临时维修（不分页）
   */
  async getAll(): Promise<ApiResponse<TemporaryRepair[]>> {
    return request.get(API_ENDPOINTS.TEMPORARY_REPAIR.ALL)
  },

  /**
   * 创建临时维修
   */
  async create(data: TemporaryRepairCreate): Promise<ApiResponse<TemporaryRepair>> {
    return request.post(API_ENDPOINTS.TEMPORARY_REPAIR.LIST, data)
  },

  /**
   * 更新临时维修
   */
  async update(id: number, data: TemporaryRepairUpdate): Promise<ApiResponse<TemporaryRepair>> {
    return request.put(API_ENDPOINTS.TEMPORARY_REPAIR.DETAIL(id), data)
  },

  /**
   * 部分更新临时维修
   */
  async patch(
    id: number,
    data: Partial<TemporaryRepairUpdate>
  ): Promise<ApiResponse<TemporaryRepair>> {
    return request.patch(API_ENDPOINTS.TEMPORARY_REPAIR.DETAIL(id), data)
  },

  /**
   * 提交临时维修
   */
  async submit(id: number): Promise<ApiResponse<TemporaryRepair>> {
    return request.post(API_ENDPOINTS.TEMPORARY_REPAIR.SUBMIT(id))
  },

  /**
   * 审批通过
   */
  async approve(id: number, remark?: string): Promise<ApiResponse<TemporaryRepair>> {
    return request.post(API_ENDPOINTS.TEMPORARY_REPAIR.APPROVE(id), { remark })
  },

  /**
   * 审批退回
   */
  async reject(id: number, remark: string): Promise<ApiResponse<TemporaryRepair>> {
    return request.post(API_ENDPOINTS.TEMPORARY_REPAIR.REJECT(id), { remark })
  },

  /**
   * 删除临时维修
   */
  async delete(id: number): Promise<ApiResponse<null>> {
    return request.delete(API_ENDPOINTS.TEMPORARY_REPAIR.DETAIL(id))
  },
}

export default temporaryRepairService
