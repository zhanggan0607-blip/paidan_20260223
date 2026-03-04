/**
 * 维修工具数据模型
 */

/**
 * 维修工具库存
 */
export interface RepairToolsStock {
  id: number
  tool_id?: string
  tool_name: string
  tool_model?: string
  specification?: string
  category?: string
  unit: string
  quantity: number
  stock?: number
  min_stock?: number
  location?: string
  last_stock_time?: string
  status: string
  created_at: string
  updated_at: string
}

/**
 * 维修工具使用记录
 */
export interface RepairToolsUsage {
  id: number
  tool_id?: string
  tool_name: string
  tool_model?: string
  specification?: string
  quantity: number
  return_quantity?: number
  user_name: string
  issue_time: string
  unit: string
  project_id?: string
  project_name?: string
  stock_id?: number | null
  status: string
  created_at: string
  updated_at: string
}

/**
 * 维修工具领用请求
 */
export interface RepairToolsIssueRequest {
  stock_id?: number | string
  tool_id?: string
  tool_name?: string
  specification?: string | null
  quantity: number
  user_name?: string
  project_id?: string | null
  project_name?: string | null
  remark?: string | null
}

/**
 * 维修工具归还请求
 */
export interface RepairToolsReturnRequest {
  usage_id: number
  quantity: number
}

/**
 * 维修工具库存查询参数
 */
export interface RepairToolsStockQueryParams {
  page?: number
  size?: number
  pageSize?: number
  tool_name?: string
  status?: string
}

/**
 * 维修工具使用查询参数
 */
export interface RepairToolsUsageQueryParams {
  page?: number
  size?: number
  tool_name?: string
  user_name?: string
  project_name?: string
  status?: string
}
