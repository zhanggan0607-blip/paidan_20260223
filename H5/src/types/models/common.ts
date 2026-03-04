/**
 * 其他数据模型
 */

/**
 * 维保计划
 */
export interface MaintenancePlan {
  id: number
  plan_id: string
  plan_name: string
  project_id: string
  project_name: string
  plan_type?: string
  equipment_id?: string
  equipment_name?: string
  equipment_model?: string
  equipment_location?: string
  plan_start_date: string
  plan_end_date: string
  execution_date?: string
  next_maintenance_date?: string
  maintenance_personnel?: string
  responsible_department?: string
  contact_info?: string
  maintenance_content?: string
  maintenance_requirements?: string
  maintenance_standard?: string
  plan_status?: string
  status?: string
  completion_rate?: number
  filled_count?: number
  total_count?: number
  remarks?: string
  inspection_items?: string
  created_at: string
  updated_at: string
}

/**
 * 巡检事项
 */
export interface InspectionItem {
  id: number
  item_code: string
  item_name: string
  item_type?: string
  level: number
  parent_id?: number
  check_content?: string
  check_standard?: string
  sort_order?: number
  created_at: string
  updated_at: string
}

/**
 * 周报
 */
export interface WeeklyReport {
  id: number
  report_id: string
  project_id: string
  project_name: string
  week_start_date?: string
  week_end_date?: string
  report_date: string
  work_summary?: string
  work_content?: string
  next_week_plan?: string
  issues?: string
  suggestions?: string
  report_content?: string
  images?: string[] | string
  status: string
  created_by?: string
  manager_signature?: string
  manager_sign_time?: string
  approved_by?: string
  approved_at?: string
  reject_reason?: string
  created_at: string
  updated_at: string
}

/**
 * 维保日志
 */
export interface MaintenanceLog {
  id: number
  log_id: string
  project_id: string
  project_name: string
  log_type?: string
  log_date: string
  work_content?: string
  images?: string | null
  remark?: string
  status: string
  created_by?: string
  created_at: string
  updated_at: string
}

/**
 * 操作日志
 */
export interface OperationLog {
  id: number
  work_order_type: string
  work_order_id: number
  work_order_no?: string
  operator_name?: string
  operator_id?: number | null
  operation_type?: string
  operation_type_code?: string
  operation_type_name?: string
  operation_remark?: string | null
  remark?: string | null
  color_code?: string
  created_at: string
}

/**
 * 超期提醒项
 */
export interface OverdueAlertItem {
  id: string
  workOrderNo: string
  project_id: string
  projectName: string
  customerName: string
  workOrderType: string
  planStartDate?: string
  planEndDate: string
  workOrderStatus: string
  overdueDays: number
  daysRemaining?: number
  executor: string
}

/**
 * 在线用户
 */
export interface OnlineUser {
  id: number
  user_id: number
  user_name: string
  department: string | null
  role: string | null
  login_time: string
  last_activity: string
  ip_address: string | null
  device_type: string
  is_active: boolean
}

/**
 * 在线用户统计
 */
export interface OnlineCount {
  total: number
  pc_count: number
  h5_count: number
}

/**
 * 在线用户详细统计
 */
export interface OnlineStatistics {
  total: number
  pc_count: number
  h5_count: number
  pc_users: OnlineUser[]
  h5_users: OnlineUser[]
}

/**
 * 数据字典项
 */
export interface DictionaryItem {
  id: number
  type: string
  code: string
  name: string
  sort_order?: number
  parent_code?: string
  created_at: string
  updated_at: string
}

/**
 * 客户信息
 */
export interface Customer {
  id: number
  customer_name: string
  name?: string
  contact_person?: string
  contact_phone?: string
  phone?: string
  contact_position?: string
  address?: string
  remarks?: string
  created_at: string
  updated_at: string
}

/**
 * OCR身份证识别结果
 */
export interface IDCardOCRResult {
  name: string
  gender: string
  nationality: string
  birth_date: string
  address: string
  id_card_number: string
  issuing_authority?: string
  valid_period?: string
}
