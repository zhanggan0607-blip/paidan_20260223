/**
 * 工作计划数据模型
 */

/**
 * 工作计划
 */
export interface WorkPlan {
  id: number
  plan_id: string
  plan_name: string
  project_id: string
  project_name: string
  plan_type?: string
  plan_start_date: string
  plan_end_date: string
  status?: string
  completion_rate?: number
  filled_count?: number
  total_count?: number
  remarks?: string
  created_at: string
  updated_at: string
}

/**
 * 工作计划查询参数
 */
export interface WorkPlanQueryParams {
  page?: number
  size?: number
  project_name?: string
  plan_type?: string
  status?: string
}

/**
 * 创建工作计划请求
 */
export interface WorkPlanCreate {
  plan_name: string
  project_id: string
  plan_type?: string
  plan_start_date: string
  plan_end_date: string
  remarks?: string
}

/**
 * 更新工作计划请求
 */
export interface WorkPlanUpdate extends WorkPlanCreate {}

/**
 * 工作计划统计
 */
export interface WorkPlanStatistics {
  expiringSoon: number
  overdue: number
  yearlyCompleted: number
  periodicInspection: number
  temporaryRepair: number
  spotWork: number
}
