/**
 * 统计服务
 * 提供统计数据查询功能
 */
import request from '../api/request'
import { API_ENDPOINTS } from '../api/endpoints'
import type { ApiResponse } from '../types/api'
import type { StatisticsOverview, WorkByPerson, TopProject } from '../types/models'

export const statisticsService = {
  /**
   * 获取统计数据概览
   */
  async getOverview(year: number): Promise<ApiResponse<StatisticsOverview>> {
    return request.get(API_ENDPOINTS.STATISTICS.OVERVIEW, { params: { year } })
  },

  /**
   * 获取按人员统计的工单数据
   */
  async getWorkByPerson(year: number): Promise<ApiResponse<WorkByPerson[]>> {
    return request.get(API_ENDPOINTS.STATISTICS.WORK_BY_PERSON, { params: { year } })
  },

  /**
   * 获取项目排名数据
   */
  async getTopProjects(year: number): Promise<ApiResponse<TopProject[]>> {
    return request.get(API_ENDPOINTS.STATISTICS.TOP_PROJECTS, { params: { year } })
  },
}

export default statisticsService
