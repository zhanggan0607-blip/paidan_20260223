/**
 * 项目信息服务
 * 提供项目信息的增删改查功能
 */
import request from '../api/request'
import { API_ENDPOINTS } from '../api/endpoints'
import type { ApiResponse, PaginatedResponse } from '../types/api'
import type {
  ProjectInfo,
  ProjectInfoCreate,
  ProjectInfoUpdate,
  ProjectInfoQueryParams
} from '../types/models'

export const projectInfoService = {
  /**
   * 获取项目信息列表（分页）
   */
  async getList(params?: ProjectInfoQueryParams): Promise<PaginatedResponse<ProjectInfo>> {
    return request.get(API_ENDPOINTS.PROJECT_INFO.LIST, { params })
  },

  /**
   * 获取项目信息详情
   */
  async getById(id: number): Promise<ApiResponse<ProjectInfo>> {
    return request.get(API_ENDPOINTS.PROJECT_INFO.DETAIL(id))
  },

  /**
   * 获取所有项目信息（不分页）
   */
  async getAll(): Promise<ApiResponse<ProjectInfo[]>> {
    return request.get(API_ENDPOINTS.PROJECT_INFO.ALL)
  },

  /**
   * 创建项目信息
   */
  async create(data: ProjectInfoCreate): Promise<ApiResponse<ProjectInfo>> {
    return request.post(API_ENDPOINTS.PROJECT_INFO.LIST, data)
  },

  /**
   * 更新项目信息
   */
  async update(id: number, data: ProjectInfoUpdate): Promise<ApiResponse<ProjectInfo>> {
    return request.put(API_ENDPOINTS.PROJECT_INFO.DETAIL(id), data)
  },

  /**
   * 删除项目信息
   */
  async delete(id: number, cascade: boolean = false): Promise<ApiResponse<null>> {
    return request.delete(API_ENDPOINTS.PROJECT_INFO.DETAIL(id), { params: { cascade } })
  },
}

export default projectInfoService
