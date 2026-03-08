/**
 * 客户服务
 * 提供客户数据的增删改查等功能
 */
import request from '../api/request'
import { API_ENDPOINTS } from '../api/endpoints'

export interface Customer {
  id: number
  name: string
  address: string
  contact_person: string
  phone: string
  contact_position: string
  remarks: string
  created_at: string
  updated_at: string
}

export interface CustomerCreate {
  name: string
  address?: string
  contact_person: string
  phone: string
  contact_position?: string
  remarks?: string
}

export interface CustomerUpdate {
  name?: string
  address?: string
  contact_person?: string
  phone?: string
  contact_position?: string
  remarks?: string
}

export interface CustomerListParams {
  page?: number
  size?: number
  name?: string
  contact_person?: string
}

export interface CustomerListResponse {
  content: Customer[]
  totalElements: number
  totalPages: number
  size: number
  number: number
}

export interface ApiResponse<T> {
  code: number
  message: string
  data: T
}

export const customerService = {
  /**
   * 获取客户列表（分页）
   */
  async getList(
    params: CustomerListParams,
    signal?: AbortSignal
  ): Promise<ApiResponse<CustomerListResponse>> {
    const response = await request.get(API_ENDPOINTS.CUSTOMER.LIST, { params, signal })
    return response as unknown as ApiResponse<CustomerListResponse>
  },

  /**
   * 获取客户详情
   */
  async getById(id: number, signal?: AbortSignal): Promise<ApiResponse<Customer>> {
    const response = await request.get(API_ENDPOINTS.CUSTOMER.DETAIL(id), { signal })
    return response as unknown as ApiResponse<Customer>
  },

  /**
   * 创建客户
   */
  async create(data: CustomerCreate): Promise<ApiResponse<Customer>> {
    const response = await request.post(API_ENDPOINTS.CUSTOMER.LIST, data)
    return response as unknown as ApiResponse<Customer>
  },

  /**
   * 更新客户
   */
  async update(id: number, data: CustomerUpdate): Promise<ApiResponse<Customer>> {
    const response = await request.put(API_ENDPOINTS.CUSTOMER.DETAIL(id), data)
    return response as unknown as ApiResponse<Customer>
  },

  /**
   * 删除客户
   */
  async delete(id: number, cascade: boolean = false): Promise<ApiResponse<void>> {
    const response = await request.delete(API_ENDPOINTS.CUSTOMER.DETAIL(id), {
      params: { cascade },
    })
    return response as unknown as ApiResponse<void>
  },
}
