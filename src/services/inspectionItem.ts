import apiClient from '../utils/api'

export interface InspectionItem {
  id: number
  item_code: string
  item_name: string
  item_type: string
  check_content: string | null
  check_standard: string | null
  created_at: string
  updated_at: string
}

export interface InspectionItemCreate {
  item_code: string
  item_name: string
  item_type: string
  check_content?: string
  check_standard?: string
}

export interface InspectionItemUpdate {
  item_code?: string
  item_name?: string
  item_type?: string
  check_content?: string
  check_standard?: string
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
    content: InspectionItem[]
    totalElements: number
    totalPages: number
    size: number
    number: number
    first: boolean
    last: boolean
  }
}

export const inspectionItemService = {
  async getAll(): Promise<ApiResponse<InspectionItem[]>> {
    return await apiClient.get('/inspection-item/all/list')
  },

  async getList(params?: {
    page?: number
    size?: number
    keyword?: string
  }): Promise<PaginatedResponse> {
    return await apiClient.get('/inspection-item', { params })
  },

  async getById(id: number): Promise<ApiResponse<InspectionItem>> {
    return await apiClient.get(`/inspection-item/${id}`)
  },

  async create(data: InspectionItemCreate): Promise<ApiResponse<InspectionItem>> {
    return await apiClient.post('/inspection-item', data)
  },

  async update(id: number, data: InspectionItemUpdate): Promise<ApiResponse<InspectionItem>> {
    return await apiClient.put(`/inspection-item/${id}`, data)
  },

  async delete(id: number): Promise<ApiResponse<null>> {
    return await apiClient.delete(`/inspection-item/${id}`)
  }
}
