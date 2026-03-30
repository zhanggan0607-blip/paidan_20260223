/**
 * 工单数据模型
 */

/**
 * 工单项
 */
export interface WorkOrderItem {
  id: number
  work_order_id: string
  work_order_type: string
  project_id: string
  project_name: string
  client_name?: string
  plan_start_date: string
  plan_end_date: string
  status: string
  maintenance_personnel?: string
  created_at: string
  updated_at: string
}

/**
 * 工单查询参数
 */
export interface WorkOrderQueryParams {
  page?: number
  size?: number
  project_name?: string
  client_name?: string
  work_order_type?: string
  status?: string
}
