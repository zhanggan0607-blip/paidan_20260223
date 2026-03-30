/**
 * 维保日志数据模型
 */

/**
 * 维保日志查询参数
 */
export interface MaintenanceLogQueryParams {
  page?: number
  size?: number
  project_name?: string
  log_date?: string
  log_type?: string
  status?: string
  created_by?: string
  created_by_role?: string
}

/**
 * 创建维保日志请求
 */
export interface MaintenanceLogCreate {
  project_id: string
  project_name: string
  log_type?: string
  log_date: string
  log_content?: string
  work_content?: string
  images?: string[]
  remark?: string
}

/**
 * 更新维保日志请求
 */
export interface MaintenanceLogUpdate {
  project_id?: string
  project_name?: string
  log_type?: string
  log_date?: string
  work_content?: string
  images?: string[]
  remark?: string
  status?: string
}
