import request from '../api/request'
import { API_ENDPOINTS } from '../api/endpoints'
import type { TopProject as BaseTopProject } from '@sstcp/shared'

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

export type TopProject = BaseTopProject

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
  async getStatisticsOverview(year: number): Promise<StatisticsOverview> {
    const response = await request.get<StatisticsOverview>(
      API_ENDPOINTS.STATISTICS.OVERVIEW,
      { params: { year } }
    )
    return response.data
  },

  async getCompletionRate(year: number): Promise<CompletionRate> {
    const response = await request.get<CompletionRate>(
      API_ENDPOINTS.STATISTICS.COMPLETION_RATE,
      { params: { year } }
    )
    return response.data
  },

  async getTopProjects(year: number, limit: number = 5): Promise<TopProject[]> {
    const response = await request.get<TopProject[]>(
      API_ENDPOINTS.STATISTICS.TOP_PROJECTS,
      { params: { year, limit } }
    )
    return response.data
  },

  async getTopRepairs(year: number, limit: number = 5): Promise<TopProject[]> {
    const response = await request.get<TopProject[]>('/statistics/top-repairs', {
      params: { year, limit },
    })
    return response.data
  },

  async getEmployeeStats(year: number): Promise<EmployeeStats> {
    const response = await request.get<EmployeeStats>(
      API_ENDPOINTS.STATISTICS.WORK_BY_PERSON,
      { params: { year } }
    )
    return response.data
  },

  async getInspectionStats(year: number): Promise<EmployeeStats> {
    const response = await request.get<EmployeeStats>('/statistics/inspection-stats', {
      params: { year },
    })
    return response.data
  },

  async getRepairStats(year: number): Promise<EmployeeStats> {
    const response = await request.get<EmployeeStats>('/statistics/repair-stats', {
      params: { year },
    })
    return response.data
  },

  async getSpotworkStats(year: number): Promise<EmployeeStats> {
    const response = await request.get<EmployeeStats>('/statistics/spotwork-stats', {
      params: { year },
    })
    return response.data
  },

  async getStatisticsDetail(params: DetailParams): Promise<DetailResponse> {
    const response = await request.get<DetailResponse>(
      API_ENDPOINTS.STATISTICS.DETAIL,
      { params }
    )
    return response.data
  },
}
