/**
 * 备件服务
 * 提供备件库存、领用、归还、入库等功能
 */
import request from '../api/request'
import { API_ENDPOINTS } from '../api/endpoints'
import type { ApiResponse } from '../types/api'
import type {
  SparePartsStock,
  SparePartsUsage,
  SparePartsInbound,
  SparePartsIssueRequest,
  SparePartsInboundRequest,
  SparePartsStockQueryParams,
  SparePartsUsageQueryParams
} from '../types/models'

export const sparePartsService = {
  /**
   * 获取备件库存列表
   */
  async getStockList(params?: SparePartsStockQueryParams): Promise<ApiResponse<{ items: SparePartsStock[]; total: number }>> {
    return request.get(API_ENDPOINTS.SPARE_PARTS_STOCK.LIST, { params })
  },

  /**
   * 获取备件库存详情
   */
  async getStockById(id: number): Promise<ApiResponse<SparePartsStock>> {
    return request.get(API_ENDPOINTS.SPARE_PARTS_STOCK.DETAIL(id))
  },

  /**
   * 获取所有备件库存
   */
  async getAllStock(): Promise<ApiResponse<SparePartsStock[]>> {
    return request.get(API_ENDPOINTS.SPARE_PARTS_STOCK.ALL)
  },

  /**
   * 获取入库记录列表
   */
  async getInboundRecords(params?: { page?: number; size?: number; pageSize?: number; tool_name?: string; user_name?: string }): Promise<ApiResponse<{ items: SparePartsInbound[]; total: number }>> {
    return request.get(API_ENDPOINTS.SPARE_PARTS_STOCK.INBOUND_RECORDS, { params })
  },

  /**
   * 备件入库
   */
  async inbound(data: SparePartsInboundRequest): Promise<ApiResponse<null>> {
    return request.post(API_ENDPOINTS.SPARE_PARTS_STOCK.INBOUND, data)
  },

  /**
   * 获取备件使用记录列表
   */
  async getUsageList(params?: SparePartsUsageQueryParams): Promise<ApiResponse<{ items: SparePartsUsage[]; total: number }>> {
    return request.get(API_ENDPOINTS.SPARE_PARTS_USAGE.LIST, { params })
  },

  /**
   * 获取备件使用记录详情
   */
  async getUsageById(id: number): Promise<ApiResponse<SparePartsUsage>> {
    return request.get(API_ENDPOINTS.SPARE_PARTS_USAGE.DETAIL(id))
  },

  /**
   * 领用备件
   */
  async issue(data: SparePartsIssueRequest): Promise<ApiResponse<null>> {
    return request.post(API_ENDPOINTS.SPARE_PARTS_USAGE.ISSUE, data)
  },

  /**
   * 归还备件
   */
  async returnSpare(id: number, data: { return_quantity: number; remark?: string }): Promise<ApiResponse<null>> {
    return request.put(API_ENDPOINTS.SPARE_PARTS_USAGE.RETURN(id), data)
  },
}

export default sparePartsService
