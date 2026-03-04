/**
 * 零星用工数据模型
 */

/**
 * 零星用工工单
 */
export interface SpotWork {
  id: number
  work_id: string
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
  work_content?: string
  photos?: string[] | string
  signature?: string
  status: string
  remarks?: string
  actual_completion_date?: string
  worker_count?: number
  work_days?: number
  workers?: SpotWorkWorker[]
  created_at: string
  updated_at: string
}

/**
 * 零星用工工人
 */
export interface SpotWorkWorker {
  id: number
  spot_work_id?: number
  project_id?: string
  project_name?: string
  start_date?: string
  end_date?: string
  name: string
  gender?: string
  birth_date?: string
  address?: string
  id_card_number?: string
  issuing_authority?: string
  valid_period?: string
  id_card_front?: string
  id_card_back?: string
  created_at?: string
  updated_at?: string
}

/**
 * 创建零星用工请求
 */
export interface SpotWorkCreate {
  work_id?: string
  plan_id?: string
  project_id: string
  project_name: string
  plan_start_date: string
  plan_end_date: string
  client_name?: string
  client_contact?: string
  client_contact_info?: string
  maintenance_personnel?: string
  work_content?: string
  photos?: string | string[]
  signature?: string
  status?: string
  remarks?: string
  worker_count?: number
}

/**
 * 更新零星用工请求
 */
export interface SpotWorkUpdate {
  work_id: string
  plan_id?: string
  project_id: string
  project_name: string
  plan_start_date: string
  plan_end_date: string
  client_name?: string
  client_contact?: string
  client_contact_info?: string
  maintenance_personnel?: string
  work_content?: string
  photos?: string[] | string
  signature?: string
  status: string
  remarks?: string
  actual_completion_date?: string
  worker_count?: number
  work_days?: number
}

/**
 * 零星用工查询参数
 */
export interface SpotWorkQueryParams {
  page?: number
  size?: number
  project_name?: string
  work_id?: string
  status?: string
}

/**
 * 快速填报请求
 */
export interface QuickFillRequest {
  project_id: string
  project_name: string
  plan_start_date: string
  plan_end_date: string
  work_content?: string
  client_contact?: string
  client_contact_info?: string
  photos?: string
  signature?: string
  worker_count?: number
  remark?: string
}

/**
 * 工人信息保存请求
 */
export interface WorkersSaveRequest {
  spot_work_id?: number
  project_id?: string
  project_name?: string
  start_date?: string
  end_date?: string
  workers: Partial<SpotWorkWorker>[]
}
