/**
 * 维修工具服务
 * 提供维修工具库存、领用、归还等功能
 */
import request from '../api/request'
import { API_ENDPOINTS } from '../api/endpoints'
import type { ApiResponse, PaginatedResponse } from '../types/api'
import type {
  RepairToolsStock,
  RepairToolsUsage,
  RepairToolsIssueRequest,
  RepairToolsStockQueryParams
} from '../types/models'

export const repairToolsService = {
  /**
   * 获取维修工具库存列表
   */
  async getStockList(params?: RepairToolsStockQueryParams): Promise<ApiResponse<{ items: RepairToolsStock[]; total: number }>> {
    return request.get(API_ENDPOINTS.REPAIR_TOOLS_STOCK.LIST, { params })
  },

  /**
   * 获取维修工具库存详情
   */
  async getStockById(id: number): Promise<ApiResponse<RepairToolsStock>> {
    return request.get(API_ENDPOINTS.REPAIR_TOOLS_STOCK.DETAIL(id))
  },

  /**
   * 获取所有维修工具库存
   */
  async getAllStock(): Promise<ApiResponse<RepairToolsStock[]>> {
    return request.get(API_ENDPOINTS.REPAIR_TOOLS_STOCK.ALL)
  },

  /**
   * 新增工具
   */
  async createStock(data: Partial<RepairToolsStock>): Promise<ApiResponse<null>> {
    return request.post(API_ENDPOINTS.REPAIR_TOOLS_STOCK.LIST, data)
  },

  /**
   * 编辑工具
   */
  async updateStock(id: number, data: Partial<RepairToolsStock>): Promise<ApiResponse<null>> {
    return request.put(API_ENDPOINTS.REPAIR_TOOLS_STOCK.DETAIL(id), data)
  },

  /**
   * 工具入库（增加库存）
   */
  async restock(id: number, data: { quantity: number; remark?: string }): Promise<ApiResponse<null>> {
    return request.post(API_ENDPOINTS.REPAIR_TOOLS_STOCK.RESTOCK(id), data)
  },

  /**
   * 获取领用记录列表
   */
  async getIssueList(params?: RepairToolsStockQueryParams): Promise<ApiResponse<{ items: RepairToolsUsage[]; total: number }>> {
    return request.get(API_ENDPOINTS.REPAIR_TOOLS_USAGE.LIST, { params })
  },

  /**
   * 获取领用记录详情
   */
  async getIssueById(id: number): Promise<ApiResponse<RepairToolsUsage>> {
    return request.get(API_ENDPOINTS.REPAIR_TOOLS_USAGE.DETAIL(id))
  },

  /**
   * 领用维修工具
   */
  async issue(data: RepairToolsIssueRequest): Promise<ApiResponse<null>> {
    return request.post(API_ENDPOINTS.REPAIR_TOOLS_USAGE.ISSUE, data)
  },

  /**
   * 归还维修工具
   */
  async returnTool(id: number, data: { return_quantity: number }): Promise<ApiResponse<null>> {
    return request.put(API_ENDPOINTS.REPAIR_TOOLS_USAGE.RETURN(id), data)
  },
}

export default repairToolsService
