/**
 * 统计数据模型
 */

/**
 * 统计概览
 */
export interface StatisticsOverview {
  year: number
  nearExpiry: number
  overdue: number
  completed: number
  regularInspectionCount: number
  temporaryRepairCount: number
  spotWorkCount: number
  workOrderByPerson: { name: string; value: number }[]
  inspectionByPerson: { name: string; value: number }[]
  repairByPerson: { name: string; value: number }[]
  laborByPerson: { name: string; value: number }[]
  onTimeRate: number
  topProjects: { name: string; value: number }[]
}

/**
 * 按人员统计工单
 */
export interface WorkByPerson {
  name: string
  value: number
}

/**
 * 项目排名
 */
export interface TopProject {
  name: string
  value: number
}
