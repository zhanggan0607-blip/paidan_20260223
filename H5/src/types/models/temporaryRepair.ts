/**
 * 临时维修数据模型
 */

/**
 * 临时维修
 */
export interface TemporaryRepair {
  id: number
  repair_id: string
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
  remarks?: string
  fault_description?: string
  solution?: string
  photos?: string[]
  signature?: string
  customer_signature?: string
  execution_date?: string
  actual_completion_date?: string
  created_at: string
  updated_at: string
}

/**
 * 创建临时维修请求
 */
export interface TemporaryRepairCreate {
  repair_id?: string
  plan_id?: string
  project_id: string
  project_name: string
  plan_start_date: string
  plan_end_date: string
  client_name?: string
  client_contact?: string
  client_contact_info?: string
  maintenance_personnel?: string
  fault_description?: string
  solution?: string
  photos?: string[]
  signature?: string
  customer_signature?: string
  execution_date?: string
  status?: string
  remarks?: string
}

/**
 * 更新临时维修请求
 */
export interface TemporaryRepairUpdate {
  repair_id: string
  plan_id?: string
  project_id: string
  project_name: string
  plan_start_date: string
  plan_end_date: string
  client_name?: string
  client_contact?: string
  client_contact_info?: string
  maintenance_personnel?: string
  fault_description?: string
  solution?: string
  photos?: string[]
  signature?: string
  customer_signature?: string
  execution_date?: string
  status: string
  remarks?: string
}

/**
 * 临时维修查询参数
 */
export interface TemporaryRepairQueryParams {
  page?: number
  size?: number
  project_name?: string
  client_name?: string
  repair_id?: string
  status?: string
}
