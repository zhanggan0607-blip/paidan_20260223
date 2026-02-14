import apiClient from '@/utils/api'

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

export const statisticsService = {
  async getStatisticsOverview(year: number): Promise<StatisticsOverview> {
    const response = await apiClient.get('/statistics/overview', { params: { year } })
    return response.data
  },

  async getCompletionRate(year: number): Promise<CompletionRate> {
    const response = await apiClient.get('/statistics/completion-rate', { params: { year } })
    return response.data
  },

  async getTopProjects(year: number, limit: number = 5): Promise<TopProject[]> {
    const response = await apiClient.get('/statistics/top-projects', { params: { year, limit } })
    return response.data
  },

  async getTopRepairs(year: number, limit: number = 5): Promise<TopProject[]> {
    const response = await apiClient.get('/statistics/top-repairs', { params: { year, limit } })
    return response.data
  },

  async getEmployeeStats(year: number): Promise<EmployeeStats> {
    const response = await apiClient.get('/statistics/employee-stats', { params: { year } })
    return response.data
  },

  async getInspectionStats(year: number): Promise<EmployeeStats> {
    const response = await apiClient.get('/statistics/inspection-stats', { params: { year } })
    return response.data
  },

  async getRepairStats(year: number): Promise<EmployeeStats> {
    const response = await apiClient.get('/statistics/repair-stats', { params: { year } })
    return response.data
  },

  async getSpotworkStats(year: number): Promise<EmployeeStats> {
    const response = await apiClient.get('/statistics/spotwork-stats', { params: { year } })
    return response.data
  }
}
