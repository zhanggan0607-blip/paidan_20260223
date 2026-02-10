import apiClient from '../utils/api'

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

export interface ApiResponse<T = any> {
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
    return await apiClient.get('/personnel', { params })
  },

  async getById(id: number): Promise<ApiResponse<Personnel>> {
    return await apiClient.get(`/personnel/${id}`)
  },

  async create(data: PersonnelCreate): Promise<ApiResponse<Personnel>> {
    return await apiClient.post('/personnel', data)
  },

  async update(id: number, data: PersonnelUpdate): Promise<ApiResponse<Personnel>> {
    return await apiClient.put(`/personnel/${id}`, data)
  },

  async delete(id: number): Promise<ApiResponse<null>> {
    return await apiClient.delete(`/personnel/${id}`)
  },

  async getAll(): Promise<ApiResponse<Personnel[]>> {
    return await apiClient.get('/personnel/all/list')
  }
}
