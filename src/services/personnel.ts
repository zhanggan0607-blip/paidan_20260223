/**
 * 人员管理服务模块
 * 提供人员数据的增删改查接口
 */
import request from '../api/request'
import { API_ENDPOINTS } from '../api/endpoints'

export interface Personnel {
  id: number
  name: string
  gender: string
  phone?: string
  department?: string
  role: string
  address?: string
  remarks?: string
  created_at: string
  updated_at: string
}

export interface PersonnelCreate {
  name: string
  gender: string
  phone?: string
  department?: string
  role: string
  address?: string
  remarks?: string
}

export interface PersonnelUpdate {
  name?: string
  gender?: string
  phone?: string
  department?: string
  role?: string
  address?: string
  remarks?: string
}

export interface ApiResponse<T = unknown> {
  code: number
  message: string
  data: T
}

export interface PaginatedResponse {
  code: number
  message: string
  data: {
    content: Personnel[]
    totalElements: number
    totalPages: number
    size: number
    number: number
    first: boolean
    last: boolean
  }
}

export const personnelService = {
  /**
   * 获取人员列表（分页）
   */
  async getList(params?: {
    page?: number
    size?: number
    name?: string
    employee_id?: string
    department?: string
    status?: string
    current_user_role?: string
    current_user_department?: string
  }): Promise<PaginatedResponse> {
    return await request.get(API_ENDPOINTS.PERSONNEL.LIST, { params })
  },

  /**
   * 获取人员详情
   */
  async getById(id: number): Promise<ApiResponse<Personnel>> {
    return await request.get(API_ENDPOINTS.PERSONNEL.DETAIL(id))
  },

  /**
   * 创建人员
   */
  async create(data: PersonnelCreate): Promise<ApiResponse<Personnel>> {
    return await request.post(API_ENDPOINTS.PERSONNEL.LIST, data)
  },

  /**
   * 更新人员
   */
  async update(id: number, data: PersonnelUpdate): Promise<ApiResponse<Personnel>> {
    return await request.put(API_ENDPOINTS.PERSONNEL.DETAIL(id), data)
  },

  /**
   * 删除人员
   */
  async delete(id: number): Promise<ApiResponse<null>> {
    return await request.delete(API_ENDPOINTS.PERSONNEL.DETAIL(id))
  },

  /**
   * 获取所有人员（不分页）
   */
  async getAll(): Promise<ApiResponse<Personnel[]>> {
    return await request.get(API_ENDPOINTS.PERSONNEL.ALL)
  },
}
