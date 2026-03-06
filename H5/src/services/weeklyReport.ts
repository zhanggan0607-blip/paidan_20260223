/**
 * 周报服务
 * 提供周报的增删改查、提交等功能
 */
import request from '../api/request'
import { API_ENDPOINTS } from '../api/endpoints'
import type { ApiResponse, PaginatedResponse } from '../types/api'
import type {
  WeeklyReport,
  OperationLog,
  WeeklyReportQueryParams,
  WeeklyReportCreate,
  WeeklyReportUpdate,
} from '../types/models'

export const weeklyReportService = {
  /**
   * 获取周报列表
   */
  async getList(
    params?: WeeklyReportQueryParams
  ): Promise<ApiResponse<{ content: WeeklyReport[] }>> {
    return request.get(API_ENDPOINTS.WEEKLY_REPORT.LIST, { params })
  },

  /**
   * 获取周报详情
   */
  async getById(id: number): Promise<ApiResponse<WeeklyReport>> {
    return request.get(API_ENDPOINTS.WEEKLY_REPORT.DETAIL(id))
  },

  /**
   * 获取所有周报
   */
  async getAll(): Promise<ApiResponse<WeeklyReport[]>> {
    return request.get(API_ENDPOINTS.WEEKLY_REPORT.ALL)
  },

  /**
   * 获取我的周报
   */
  async getMy(params?: WeeklyReportQueryParams): Promise<PaginatedResponse<WeeklyReport>> {
    return request.get(API_ENDPOINTS.WEEKLY_REPORT.MY, { params })
  },

  /**
   * 生成周报编号
   */
  async generateId(params?: { report_date?: string }): Promise<ApiResponse<{ report_id: string }>> {
    return request.get(API_ENDPOINTS.WEEKLY_REPORT.GENERATE_ID, { params })
  },

  /**
   * 创建周报
   */
  async create(data: WeeklyReportCreate): Promise<ApiResponse<null>> {
    return request.post(API_ENDPOINTS.WEEKLY_REPORT.LIST, data)
  },

  /**
   * 更新周报
   */
  async update(id: number, data: WeeklyReportUpdate): Promise<ApiResponse<WeeklyReport>> {
    return request.put(API_ENDPOINTS.WEEKLY_REPORT.DETAIL(id), data)
  },

  /**
   * 提交周报
   */
  async submit(id: number): Promise<ApiResponse<WeeklyReport>> {
    return request.post(API_ENDPOINTS.WEEKLY_REPORT.SUBMIT(id))
  },

  /**
   * 删除周报
   */
  async delete(id: number): Promise<ApiResponse<null>> {
    return request.delete(API_ENDPOINTS.WEEKLY_REPORT.DETAIL(id))
  },

  /**
   * 获取操作日志
   */
  async getOperationLogs(id: number): Promise<ApiResponse<OperationLog[]>> {
    return request.get(API_ENDPOINTS.WEEKLY_REPORT.OPERATION_LOGS(id))
  },
}

export default weeklyReportService
