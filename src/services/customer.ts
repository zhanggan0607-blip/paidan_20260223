import request from '../api/request'
import { API_ENDPOINTS } from '../api/endpoints'
import type { ApiResponse, Customer as BaseCustomer } from '@sstcp/shared'

export interface CustomerContact {
  id: number
  customer_id: number
  contact_person: string
  phone: string | null
  contact_position: string | null
  remarks: string | null
  created_at: string
  updated_at: string
}

export interface CustomerContactCreate {
  contact_person: string
  phone?: string
  contact_position?: string
  remarks?: string
}

export interface Customer extends BaseCustomer {
  contacts: CustomerContact[]
}

export interface CustomerCreate {
  name: string
  address?: string
  contacts?: CustomerContactCreate[]
  remarks?: string
}

export interface CustomerUpdate {
  name?: string
  address?: string
  contacts?: CustomerContactCreate[]
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

export const customerService = {
  async getList(
    params: CustomerListParams,
    signal?: AbortSignal
  ): Promise<ApiResponse<CustomerListResponse>> {
    const response = await request.get(API_ENDPOINTS.CUSTOMER.LIST, { params, signal })
    return response as unknown as ApiResponse<CustomerListResponse>
  },

  async getById(id: number, signal?: AbortSignal): Promise<ApiResponse<Customer>> {
    const response = await request.get(API_ENDPOINTS.CUSTOMER.DETAIL(id), { signal })
    return response as unknown as ApiResponse<Customer>
  },

  async create(data: CustomerCreate): Promise<ApiResponse<Customer>> {
    const response = await request.post(API_ENDPOINTS.CUSTOMER.LIST, data)
    return response as unknown as ApiResponse<Customer>
  },

  async update(id: number, data: CustomerUpdate): Promise<ApiResponse<Customer>> {
    const response = await request.put(API_ENDPOINTS.CUSTOMER.DETAIL(id), data)
    return response as unknown as ApiResponse<Customer>
  },

  async delete(id: number, cascade: boolean = false): Promise<ApiResponse<void>> {
    const response = await request.delete(API_ENDPOINTS.CUSTOMER.DETAIL(id), {
      params: { cascade },
    })
    return response as unknown as ApiResponse<void>
  },
}
