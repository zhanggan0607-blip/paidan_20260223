/**
 * 维保计划服务
 * 提供维保计划的增删改查等功能
 */
import request from '../api/request'
import { API_ENDPOINTS } from '../api/endpoints'

export interface MaintenancePlan {
  id: number
  plan_id: string
  plan_name: string
  project_id: string
  project_name?: string
  client_name?: string
  client_contact?: string
  client_contact_info?: string
  client_contact_position?: string
  address?: string
  plan_type: string
  equipment_id: string
  equipment_name: string
  equipment_model?: string
  equipment_location?: string
  plan_start_date: string
  plan_end_date: string
  execution_date?: string
  next_maintenance_date?: string
  responsible_person: string
  responsible_department?: string
  contact_info?: string
  maintenance_content: string
  maintenance_requirements?: string
  maintenance_standard?: string
  plan_status: string
  status: string
  completion_rate?: number
  remarks?: string
  inspection_items?: string
  created_at: string
  updated_at: string
}

export interface MaintenancePlanDisplay {
  id: string
  planId: string
  projectName: string
  startDate: string
  endDate: string
  planCount: number
  clientName: string
  address: string
  originalData: MaintenancePlan
}

export interface MaintenancePlanCreate {
  plan_id: string
  plan_name: string
  project_id: string
  plan_type: string
  equipment_id: string
  equipment_name: string
  equipment_model?: string
  equipment_location?: string
  plan_start_date: string
  plan_end_date: string
  execution_date?: string
  next_maintenance_date?: string
  responsible_person: string
  responsible_department?: string
  contact_info?: string
  maintenance_content: string
  maintenance_requirements?: string
  maintenance_standard?: string
  plan_status: string
  status: string
  completion_rate?: number
  remarks?: string
  inspection_items?: string
}

export interface MaintenancePlanUpdate {
  plan_id: string
  plan_name: string
  project_id: string
  plan_type: string
  equipment_id: string
  equipment_name: string
  equipment_model?: string
  equipment_location?: string
  plan_start_date: string
  plan_end_date: string
  execution_date?: string
  next_maintenance_date?: string
  responsible_person: string
  responsible_department?: string
  contact_info?: string
  maintenance_content: string
  maintenance_requirements?: string
  maintenance_standard?: string
  plan_status: string
  status: string
  completion_rate?: number
  remarks?: string
  inspection_items?: string
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
    content: MaintenancePlan[]
    totalElements: number
    totalPages: number
    size: number
    number: number
    first: boolean
    last: boolean
  }
}

export const maintenancePlanService = {
  /**
   * 获取维保计划列表（分页）
   */
  async getList(params?: {
    page?: number
    size?: number
    plan_name?: string
    project_id?: string
    equipment_name?: string
    plan_status?: string
    execution_status?: string
    responsible_person?: string
    project_name?: string
    client_name?: string
    plan_type?: string
  }): Promise<PaginatedResponse> {
    return await request.get(API_ENDPOINTS.MAINTENANCE_PLAN.LIST, { params })
  },

  /**
   * 获取维保计划详情
   */
  async getById(id: number): Promise<ApiResponse<MaintenancePlan>> {
    return await request.get(API_ENDPOINTS.MAINTENANCE_PLAN.DETAIL(id))
  },

  /**
   * 创建维保计划
   */
  async create(data: MaintenancePlanCreate): Promise<ApiResponse<MaintenancePlan>> {
    return await request.post(API_ENDPOINTS.MAINTENANCE_PLAN.LIST, data)
  },

  /**
   * 更新维保计划
   */
  async update(id: number, data: MaintenancePlanUpdate): Promise<ApiResponse<MaintenancePlan>> {
    return await request.put(API_ENDPOINTS.MAINTENANCE_PLAN.DETAIL(id), data)
  },

  /**
   * 删除维保计划
   */
  async delete(id: number): Promise<ApiResponse<null>> {
    return await request.delete(API_ENDPOINTS.MAINTENANCE_PLAN.DETAIL(id))
  },

  /**
   * 获取所有维保计划
   */
  async getAll(): Promise<ApiResponse<MaintenancePlan[]>> {
    return await request.get(API_ENDPOINTS.MAINTENANCE_PLAN.ALL)
  },

  /**
   * 根据项目ID获取维保计划
   */
  async getByProjectId(projectId: string): Promise<ApiResponse<MaintenancePlan[]>> {
    return await request.get(`/maintenance-plan/project/${projectId}`)
  },

  /**
   * 获取即将到期的维保计划
   */
  async getUpcoming(days: number = 7): Promise<ApiResponse<MaintenancePlan[]>> {
    return await request.get('/maintenance-plan/upcoming/list', { params: { days } })
  },

  /**
   * 更新维保计划状态
   */
  async updateStatus(id: number, status: string): Promise<ApiResponse<MaintenancePlan>> {
    return await request.patch(`/maintenance-plan/${id}/status`, null, { params: { status } })
  },

  /**
   * 更新维保计划完成率
   */
  async updateCompletionRate(id: number, rate: number): Promise<ApiResponse<MaintenancePlan>> {
    return await request.patch(`/maintenance-plan/${id}/completion-rate`, null, {
      params: { rate },
    })
  },

  /**
   * 根据日期范围获取维保计划
   */
  async getByDateRange(
    startDate: string,
    endDate: string
  ): Promise<ApiResponse<MaintenancePlan[]>> {
    return await request.get('/maintenance-plan/date-range/list', {
      params: {
        start_date: startDate,
        end_date: endDate,
      },
    })
  },
}
