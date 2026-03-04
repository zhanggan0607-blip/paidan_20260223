/**
 * 周报数据模型
 */

/**
 * 周报查询参数
 */
export interface WeeklyReportQueryParams {
  page?: number
  size?: number
  project_name?: string
  report_date?: string
  status?: string
  created_by?: string
}

/**
 * 创建周报请求
 */
export interface WeeklyReportCreate {
  project_id?: string
  project_name?: string
  report_date?: string
  report_id?: string
  work_summary?: string
  next_week_plan?: string
  issues?: string
  suggestions?: string
  report_content?: string
}

/**
 * 更新周报请求
 */
export interface WeeklyReportUpdate {
  report_content?: string
  status?: string
}
