/**
 * 定期巡检数据模型
 */

/**
 * 定期巡检
 */
export interface PeriodicInspection {
  id: number
  inspection_id: string
  plan_id?: string
  plan_type?: string
  project_id: string
  project_name: string
  plan_start_date: string
  plan_end_date: string
  client_name?: string
  client_contact?: string
  client_contact_info?: string
  address?: string
  client_contact_position?: string
  maintenance_personnel?: string
  status: string
  filled_count: number
  total_count: number
  execution_result?: string
  remarks?: string
  signature?: string
  actual_completion_date?: string
  created_at: string
  updated_at: string
}

/**
 * 定期巡检记录
 */
export interface PeriodicInspectionRecord {
  id: number
  inspection_id: string
  item_id: string
  item_name: string
  inspection_item?: string
  inspection_content?: string
  check_content?: string
  brief_description?: string
  equipment_name?: string
  equipment_location?: string
  inspected: boolean
  photos?: string[]
  inspection_result?: string
  created_at: string
  updated_at: string
}

/**
 * 创建定期巡检请求
 */
export interface PeriodicInspectionCreate {
  inspection_id?: string
  plan_id?: string
  project_id: string
  project_name: string
  plan_start_date: string
  plan_end_date: string
  client_name?: string
  client_contact?: string
  client_contact_info?: string
  maintenance_personnel?: string
  status?: string
  filled_count?: number
  total_count?: number
  execution_result?: string
  remarks?: string
  signature?: string
}

/**
 * 更新定期巡检请求
 */
export interface PeriodicInspectionUpdate {
  inspection_id?: string
  plan_id?: string
  project_id?: string
  project_name?: string
  plan_start_date?: string
  plan_end_date?: string
  client_name?: string
  client_contact?: string
  client_contact_info?: string
  maintenance_personnel?: string
  status?: string
  filled_count?: number
  total_count?: number
  execution_result?: string
  remarks?: string
  signature?: string
}

/**
 * 定期巡检查询参数
 */
export interface PeriodicInspectionQueryParams {
  page?: number
  size?: number
  project_name?: string
  client_name?: string
  inspection_id?: string
  status?: string
}
