/**
 * 零星用工服务
 * 提供零星用工工单的增删改查等功能
 */
import request from '../api/request'
import { API_ENDPOINTS } from '../api/endpoints'
import type { ApiResponse, PaginatedData } from '@sstcp/shared'

export interface SpotWork {
  id: number
  work_id: string
  plan_id?: string
  plan_type?: string
  project_id: string
  project_name: string
  plan_start_date: string
  plan_end_date: string
  client_name?: string
  client_contact?: string
  client_contact_info?: string
  address?: string
  client_contact_position?: string
  maintenance_personnel?: string
  work_content?: string
  photos?: string[] | string
  signature?: string
  status: string
  remarks?: string
  actual_completion_date?: string
  worker_count?: number
  work_days?: number
  workers?: SpotWorkWorker[]
  created_at: string
  updated_at: string
}

export interface SpotWorkWorker {
  id: number
  spot_work_id?: number
  project_id?: string
  project_name?: string
  start_date?: string
  end_date?: string
  name: string
  gender?: string
  birth_date?: string
  address?: string
  id_card_number?: string
  issuing_authority?: string
  valid_period?: string
  id_card_front?: string
  id_card_back?: string
  created_at?: string
  updated_at?: string
}

export interface SpotWorkCreate {
  work_id?: string
  plan_id?: string
  project_id: string
  project_name: string
  plan_start_date: string
  plan_end_date: string
  client_name?: string
  client_contact?: string
  client_contact_info?: string
  maintenance_personnel?: string
  work_content?: string
  photos?: string
  signature?: string
  status?: string
  remarks?: string
  worker_count?: number
}

export interface SpotWorkUpdate {
  work_id?: string
  plan_id?: string
  project_id?: string
  project_name?: string
  plan_start_date?: string
  plan_end_date?: string
  client_name?: string
  client_contact?: string
  client_contact_info?: string
  maintenance_personnel?: string
  work_content?: string
  photos?: string
  signature?: string
  status?: string
  remarks?: string
  worker_count?: number
}

export const spotWorkService = {
  /**
   * 获取零星用工列表（分页）
   */
  async getList(params?: {
    page?: number
    size?: number
    project_name?: string
    work_id?: string
    status?: string
  }): Promise<ApiResponse<PaginatedData<SpotWork>>> {
    return await request.get(API_ENDPOINTS.SPOT_WORK.LIST, { params })
  },

  /**
   * 获取所有零星用工（不分页）
   */
  async getAll(): Promise<ApiResponse<SpotWork[]>> {
    return await request.get(API_ENDPOINTS.SPOT_WORK.ALL)
  },

  /**
   * 获取零星用工详情
   */
  async getById(id: number): Promise<ApiResponse<SpotWork>> {
    return await request.get(API_ENDPOINTS.SPOT_WORK.DETAIL(id))
  },

  /**
   * 创建零星用工
   */
  async create(data: SpotWorkCreate): Promise<ApiResponse<SpotWork>> {
    return await request.post(API_ENDPOINTS.SPOT_WORK.LIST, data)
  },

  /**
   * 更新零星用工
   */
  async update(id: number, data: SpotWorkUpdate): Promise<ApiResponse<SpotWork>> {
    return await request.put(API_ENDPOINTS.SPOT_WORK.DETAIL(id), data)
  },

  /**
   * 删除零星用工
   */
  async delete(id: number): Promise<ApiResponse<null>> {
    return await request.delete(API_ENDPOINTS.SPOT_WORK.DETAIL(id))
  },
}
