/**
 * 统计服务
 * 提供统计数据查询等功能
 */
import request from '../api/request'
import { API_ENDPOINTS } from '../api/endpoints'

export interface StatisticsOverview {
  year: number
  totalWorkOrders: number
  regularInspectionCount: number
  temporaryRepairCount: number
  spotWorkCount: number
  nearDueCount: number
  overdueCount: number
  yearCompletedCount: number
}

export interface CompletionRate {
  year: number
  onTimeRate: number
  onTimeCount: number
  delayedCount: number
  totalCount: number
}

export interface TopProject {
  name: string
  value: number
}

export interface EmployeeStats {
  year: number
  employees: Array<{ name: string; count: number }>
  total: number
}

export interface WorkOrderDetail {
  id: number
  orderType: string
  orderNumber: string
  projectName: string
  maintenancePersonnel: string
  planStartDate: string
  planEndDate: string
  status: string
  content: string
}

export interface DetailResponse {
  total: number
  page: number
  pageSize: number
  data: WorkOrderDetail[]
}

export interface DetailParams {
  year: number
  data_type: string
  employee_name?: string
  project_name?: string
  order_type?: string
  page?: number
  page_size?: number
}

export const statisticsService = {
  /**
   * 获取统计概览
   */
  async getStatisticsOverview(year: number): Promise<StatisticsOverview> {
    const response = await request.get(API_ENDPOINTS.STATISTICS.OVERVIEW, { params: { year } })
    return response.data
  },

  /**
   * 获取完成率统计
   */
  async getCompletionRate(year: number): Promise<CompletionRate> {
    const response = await request.get(API_ENDPOINTS.STATISTICS.COMPLETION_RATE, {
      params: { year },
    })
    return response.data
  },

  /**
   * 获取项目排行
   */
  async getTopProjects(year: number, limit: number = 5): Promise<TopProject[]> {
    const response = await request.get(API_ENDPOINTS.STATISTICS.TOP_PROJECTS, {
      params: { year, limit },
    })
    return response.data
  },

  /**
   * 获取维修排行
   */
  async getTopRepairs(year: number, limit: number = 5): Promise<TopProject[]> {
    const response = await request.get('/statistics/top-repairs', { params: { year, limit } })
    return response.data
  },

  /**
   * 获取员工统计
   */
  async getEmployeeStats(year: number): Promise<EmployeeStats> {
    const response = await request.get(API_ENDPOINTS.STATISTICS.WORK_BY_PERSON, {
      params: { year },
    })
    return response.data
  },

  /**
   * 获取巡检统计
   */
  async getInspectionStats(year: number): Promise<EmployeeStats> {
    const response = await request.get('/statistics/inspection-stats', { params: { year } })
    return response.data
  },

  /**
   * 获取维修统计
   */
  async getRepairStats(year: number): Promise<EmployeeStats> {
    const response = await request.get('/statistics/repair-stats', { params: { year } })
    return response.data
  },

  /**
   * 获取零星用工统计
   */
  async getSpotworkStats(year: number): Promise<EmployeeStats> {
    const response = await request.get('/statistics/spotwork-stats', { params: { year } })
    return response.data
  },

  /**
   * 获取统计详情
   */
  async getStatisticsDetail(params: DetailParams): Promise<DetailResponse> {
    const response = (await request.get(API_ENDPOINTS.STATISTICS.DETAIL, {
      params,
    })) as unknown as { data: DetailResponse }
    console.log('getStatisticsDetail raw response:', response)
    return response.data as DetailResponse
  },
}
