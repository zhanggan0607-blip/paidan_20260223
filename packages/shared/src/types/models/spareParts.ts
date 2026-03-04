/**
 * 备件数据模型
 */

/**
 * 备件库存
 */
export interface SparePartsStock {
  id: number
  product_name: string
  productName?: string
  brand?: string
  model?: string
  unit: string
  quantity: number
  stock?: number
  status: string
  created_at: string
  updated_at: string
}

/**
 * 备件使用记录
 */
export interface SparePartsUsage {
  id: number
  product_name: string
  productName?: string
  brand?: string
  model?: string
  quantity: number
  return_quantity?: number
  user_name: string
  userName?: string
  issue_time: string
  issueTime?: string
  unit: string
  project_id?: string
  project_name?: string
  projectName?: string
  stock_id?: number | null
  status: string
  created_at: string
  updated_at: string
}

/**
 * 备件入库记录
 */
export interface SparePartsInbound {
  id: number
  inbound_no: string
  inboundNo?: string
  product_name: string
  productName?: string
  brand?: string
  model?: string
  quantity: number
  supplier?: string
  unit: string
  user_name: string
  userName?: string
  remarks?: string
  inbound_time?: string
  inboundTime?: string
  created_at: string
}

/**
 * 备件领用请求
 */
export interface SparePartsIssueRequest {
  stock_id?: number
  product_name?: string
  brand?: string | null
  model?: string | null
  quantity: number
  user_name?: string
  issue_time?: string
  unit?: string
  project_id?: string | null
  project_name?: string | null
}

/**
 * 备件归还请求
 */
export interface SparePartsReturnRequest {
  usage_id: number
  quantity: number
}

/**
 * 备件入库请求
 */
export interface SparePartsInboundRequest {
  product_name: string
  brand?: string
  model?: string
  quantity: number
  supplier?: string
  unit: string
  user_name?: string
  remarks?: string
}

/**
 * 备件库存查询参数
 */
export interface SparePartsStockQueryParams {
  page?: number
  size?: number
  pageSize?: number
  product_name?: string
  brand?: string
}

/**
 * 备件使用查询参数
 */
export interface SparePartsUsageQueryParams {
  page?: number
  size?: number
  pageSize?: number
  product_name?: string
  user_name?: string
  project_name?: string
  status?: string
}
