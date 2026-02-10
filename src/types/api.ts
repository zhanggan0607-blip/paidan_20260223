/**
 * API 响应通用接口
 */
export interface ApiResponse<T> {
  code: number
  message: string
  data: T
}

/**
 * 分页响应接口
 */
export interface PaginatedResponse<T> {
  items: T[]
  total: number
  page: number
  pageSize: number
}

/**
 * 查询参数接口
 */
export interface QueryParams {
  page: number
  pageSize: number
  user?: string
  product?: string
  project?: string
}

/**
 * 备品备件领用查询参数接口
 */
export interface SparePartsIssueQueryParams extends QueryParams {
  user?: string
  product?: string
  project?: string
}

/**
 * 备品备件入库查询参数接口
 */
export interface SparePartsStockQueryParams extends QueryParams {
  product?: string
  user?: string
}
