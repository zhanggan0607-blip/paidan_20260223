import apiClient from '@/utils/api'

export interface StatisticsOverview {
  year: number
  regularInspectionCount: number
  temporaryRepairCount: number
  spotWorkCount: number
  maintenancePlanCount: number
}

export interface WorkByPerson {
  name: string
  value: number
}

export interface CompletionRate {
  year: number
  onTimeRate: number
}

export interface TopProject {
  name: string
  value: number
}

export const statisticsService = {
  async getStatisticsOverview(year: number): Promise<StatisticsOverview> {
    const response = await apiClient.get('/statistics/overview', { params: { year } })
    return response.data
  },

  async getWorkByPerson(year: number): Promise<WorkByPerson[]> {
    const response = await apiClient.get('/statistics/work-by-person', { params: { year } })
    return response.data
  },

  async getCompletionRate(year: number): Promise<CompletionRate> {
    const response = await apiClient.get('/statistics/completion-rate', { params: { year } })
    return response.data
  },

  async getTopProjects(year: number, limit: number = 5): Promise<TopProject[]> {
    const response = await apiClient.get('/statistics/top-projects', { params: { year, limit } })
    return response.data
  }
}