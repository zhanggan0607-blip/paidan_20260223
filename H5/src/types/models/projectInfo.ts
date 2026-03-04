/**
 * 项目信息数据模型
 */

/**
 * 项目信息
 */
export interface ProjectInfo {
  id: number
  project_id: string
  project_name: string
  completion_date?: string
  maintenance_end_date?: string
  maintenance_period?: string
  client_name?: string
  address?: string
  project_abbr?: string
  project_manager?: string
  client_contact?: string
  client_contact_position?: string
  client_contact_info?: string
  created_at: string
  updated_at: string
}

/**
 * 创建项目信息请求
 */
export interface ProjectInfoCreate {
  project_id: string
  project_name: string
  completion_date?: string
  maintenance_end_date?: string
  maintenance_period?: string
  client_name?: string
  address?: string
  project_abbr?: string
  project_manager?: string
  client_contact?: string
  client_contact_position?: string
  client_contact_info?: string
}

/**
 * 更新项目信息请求
 */
export interface ProjectInfoUpdate extends ProjectInfoCreate {}

/**
 * 项目信息查询参数
 */
export interface ProjectInfoQueryParams {
  page?: number
  size?: number
  project_name?: string
  client_name?: string
  project_id?: string
}
