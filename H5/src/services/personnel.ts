/**
 * 人员服务
 * 提供人员信息的增删改查功能
 */
import request from '../api/request'
import { API_ENDPOINTS } from '../api/endpoints'
import type { ApiResponse, PaginatedResponse } from '../types/api'
import type { Personnel, PersonnelQueryParams, PersonnelCreate, PersonnelUpdate } from '../types/models'

export const personnelService = {
  /**
   * 获取人员列表（分页）
   */
  async getList(params?: PersonnelQueryParams): Promise<PaginatedResponse<Personnel>> {
    return request.get(API_ENDPOINTS.PERSONNEL.LIST, { params })
  },

  /**
   * 获取人员详情
   */
  async getById(id: number): Promise<ApiResponse<Personnel>> {
    return request.get(API_ENDPOINTS.PERSONNEL.DETAIL(id))
  },

  /**
   * 获取所有人员（不分页）
   */
  async getAll(): Promise<ApiResponse<Personnel[]>> {
    return request.get(API_ENDPOINTS.PERSONNEL.ALL)
  },

  /**
   * 创建人员
   */
  async create(data: PersonnelCreate): Promise<ApiResponse<Personnel>> {
    return request.post(API_ENDPOINTS.PERSONNEL.LIST, data)
  },

  /**
   * 更新人员
   */
  async update(id: number, data: PersonnelUpdate): Promise<ApiResponse<Personnel>> {
    return request.put(API_ENDPOINTS.PERSONNEL.DETAIL(id), data)
  },

  /**
   * 删除人员
   */
  async delete(id: number): Promise<ApiResponse<null>> {
    return request.delete(API_ENDPOINTS.PERSONNEL.DETAIL(id))
  },
}

export default personnelService
