/**
 * 客户服务
 * 提供客户信息的增删改查功能
 */
import request from '../api/request'
import { API_ENDPOINTS } from '../api/endpoints'
import type { ApiResponse, PaginatedResponse } from '../types/api'
import type { Customer } from '../types/models'

export interface CustomerQueryParams {
  page?: number
  size?: number
  name?: string
  contact_person?: string
}

export interface CustomerCreate {
  customer_name: string
  contact_person?: string
  contact_phone?: string
  contact_position?: string
  address?: string
  remarks?: string
}

export interface CustomerUpdate extends CustomerCreate {}

export const customerService = {
  /**
   * 获取客户列表（分页）
   */
  async getList(params?: CustomerQueryParams): Promise<PaginatedResponse<Customer>> {
    return request.get(API_ENDPOINTS.CUSTOMER.LIST, { params })
  },

  /**
   * 获取客户详情
   */
  async getById(id: number): Promise<ApiResponse<Customer>> {
    return request.get(API_ENDPOINTS.CUSTOMER.DETAIL(id))
  },

  /**
   * 获取所有客户（不分页）
   */
  async getAll(): Promise<ApiResponse<Customer[]>> {
    return request.get(API_ENDPOINTS.CUSTOMER.ALL)
  },

  /**
   * 创建客户
   */
  async create(data: CustomerCreate): Promise<ApiResponse<Customer>> {
    return request.post(API_ENDPOINTS.CUSTOMER.LIST, data)
  },

  /**
   * 更新客户
   */
  async update(id: number, data: CustomerUpdate): Promise<ApiResponse<Customer>> {
    return request.put(API_ENDPOINTS.CUSTOMER.DETAIL(id), data)
  },

  /**
   * 删除客户
   */
  async delete(id: number): Promise<ApiResponse<null>> {
    return request.delete(API_ENDPOINTS.CUSTOMER.DETAIL(id))
  },
}

export default customerService
