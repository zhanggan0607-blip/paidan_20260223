import apiClient from '../utils/api'

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
  client_contact?: string
  client_contact_position?: string
  client_contact_info?: string
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
    content: ProjectInfo[]
    totalElements: number
    totalPages: number
    size: number
    number: number
    first: boolean
    last: boolean
  }
}

export const projectInfoService = {
  async getList(params?: {
    page?: number
    size?: number
    project_name?: string
    client_name?: string
  }): Promise<PaginatedResponse> {
    return await apiClient.get('/project-info', { params })
  },

  async getById(id: number): Promise<ApiResponse<ProjectInfo>> {
    return await apiClient.get(`/project-info/${id}`)
  },

  async create(data: ProjectInfoCreate): Promise<ApiResponse<ProjectInfo>> {
    return await apiClient.post('/project-info', data)
  },

  async update(id: number, data: ProjectInfoUpdate): Promise<ApiResponse<ProjectInfo>> {
    return await apiClient.put(`/project-info/${id}`, data)
  },

  async delete(id: number): Promise<ApiResponse<null>> {
    return await apiClient.delete(`/project-info/${id}`)
  },

  async getAll(): Promise<ApiResponse<ProjectInfo[]>> {
    return await apiClient.get('/project-info/all/list')
  }
}