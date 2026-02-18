import api from '../utils/api'

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
  async getList(params: CustomerListParams): Promise<ApiResponse<CustomerListResponse>> {
    const response = await api.get('/customer', { params })
    return response as unknown as ApiResponse<CustomerListResponse>
  },

  async getById(id: number): Promise<ApiResponse<Customer>> {
    const response = await api.get(`/customer/${id}`)
    return response as unknown as ApiResponse<Customer>
  },

  async create(data: CustomerCreate): Promise<ApiResponse<Customer>> {
    const response = await api.post('/customer', data)
    return response as unknown as ApiResponse<Customer>
  },

  async update(id: number, data: CustomerUpdate): Promise<ApiResponse<Customer>> {
    const response = await api.put(`/customer/${id}`, data)
    return response as unknown as ApiResponse<Customer>
  },

  async delete(id: number, cascade: boolean = false): Promise<ApiResponse<void>> {
    const response = await api.delete(`/customer/${id}`, { params: { cascade } })
    return response as unknown as ApiResponse<void>
  }
}
