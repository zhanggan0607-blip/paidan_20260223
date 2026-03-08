/**
 * 项目信息服务
 * 提供项目信息的增删改查等功能
 */
import request from '../api/request'
import { API_ENDPOINTS } from '../api/endpoints'
import type { ApiResponse, PaginatedData } from '@sstcp/shared'

export interface ProjectInfo {
  id: number
  project_id: string
  project_name: string
  completion_date: string
  maintenance_end_date: string
  maintenance_period: string
  client_name: string
  address: string
  project_abbr?: string
  project_manager?: string
  client_contact?: string
  client_contact_position?: string
  client_contact_info?: string
  created_at: string
  updated_at: string
}

export interface ProjectInfoCreate {
  project_id: string
  project_name: string
  completion_date: string
  maintenance_end_date: string
  maintenance_period: string
  client_name: string
  address: string
  project_abbr?: string
  project_manager?: string
  client_contact?: string
  client_contact_position?: string
  client_contact_info?: string
}

export interface ProjectInfoUpdate {
  project_id: string
  project_name: string
  completion_date: string
  maintenance_end_date: string
  maintenance_period: string
  client_name: string
  address: string
  project_abbr?: string
  project_manager?: string
  client_contact?: string
  client_contact_position?: string
  client_contact_info?: string
}

export const projectInfoService = {
  /**
   * 获取项目列表（分页）
   */
  async getList(params?: {
    page?: number
    size?: number
    project_name?: string
    client_name?: string
  }): Promise<ApiResponse<PaginatedData<ProjectInfo>>> {
    return await request.get(API_ENDPOINTS.PROJECT_INFO.LIST, { params })
  },

  /**
   * 获取项目详情
   */
  async getById(id: number): Promise<ApiResponse<ProjectInfo>> {
    return await request.get(API_ENDPOINTS.PROJECT_INFO.DETAIL(id))
  },

  /**
   * 创建项目
   */
  async create(data: ProjectInfoCreate): Promise<ApiResponse<ProjectInfo>> {
    return await request.post(API_ENDPOINTS.PROJECT_INFO.LIST, data)
  },

  /**
   * 更新项目
   */
  async update(id: number, data: ProjectInfoUpdate): Promise<ApiResponse<ProjectInfo>> {
    return await request.put(API_ENDPOINTS.PROJECT_INFO.DETAIL(id), data)
  },

  /**
   * 删除项目
   */
  async delete(id: number, cascade: boolean = false): Promise<ApiResponse<null>> {
    return await request.delete(API_ENDPOINTS.PROJECT_INFO.DETAIL(id), { params: { cascade } })
  },

  /**
   * 获取所有项目（不分页）
   */
  async getAll(): Promise<ApiResponse<ProjectInfo[]>> {
    return await request.get(API_ENDPOINTS.PROJECT_INFO.ALL)
  },
}
