/**
 * 维保日志服务
 * 提供维保日志的增删改查、提交等功能
 */
import request from '../api/request'
import { API_ENDPOINTS } from '../api/endpoints'
import type { ApiResponse, PaginatedResponse } from '../types/api'
import type { MaintenanceLog, MaintenanceLogQueryParams, MaintenanceLogCreate, MaintenanceLogUpdate, OperationLog } from '../types/models'

export const maintenanceLogService = {
  /**
   * 获取维保日志列表
   */
  async getList(params?: MaintenanceLogQueryParams): Promise<PaginatedResponse<MaintenanceLog>> {
    return request.get(API_ENDPOINTS.MAINTENANCE_LOG.LIST, { params })
  },

  /**
   * 获取维保日志详情
   */
  async getById(id: number): Promise<ApiResponse<MaintenanceLog>> {
    return request.get(API_ENDPOINTS.MAINTENANCE_LOG.DETAIL(id))
  },

  /**
   * 获取我的维保日志
   */
  async getMy(params?: MaintenanceLogQueryParams): Promise<PaginatedResponse<MaintenanceLog>> {
    return request.get(API_ENDPOINTS.MAINTENANCE_LOG.MY, { params })
  },

  /**
   * 创建维保日志
   */
  async create(data: MaintenanceLogCreate): Promise<ApiResponse<MaintenanceLog>> {
    return request.post(API_ENDPOINTS.MAINTENANCE_LOG.LIST, data)
  },

  /**
   * 更新维保日志
   */
  async update(id: number, data: MaintenanceLogUpdate): Promise<ApiResponse<MaintenanceLog>> {
    return request.put(API_ENDPOINTS.MAINTENANCE_LOG.DETAIL(id), data)
  },

  /**
   * 提交维保日志
   */
  async submit(id: number): Promise<ApiResponse<MaintenanceLog>> {
    return request.post(API_ENDPOINTS.MAINTENANCE_LOG.SUBMIT(id))
  },

  /**
   * 删除维保日志
   */
  async delete(id: number): Promise<ApiResponse<null>> {
    return request.delete(API_ENDPOINTS.MAINTENANCE_LOG.DETAIL(id))
  },

  /**
   * 获取维保日志操作日志
   */
  async getOperationLogs(id: number): Promise<ApiResponse<OperationLog[]>> {
    return request.get(API_ENDPOINTS.MAINTENANCE_LOG.OPERATION_LOGS(id))
  },
}

export default maintenanceLogService
