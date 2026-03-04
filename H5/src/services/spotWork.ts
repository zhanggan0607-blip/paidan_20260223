/**
 * 零星用工服务
 * 提供零星用工工单的增删改查、快速填报、工人管理等功能
 */
import request from '../api/request'
import { API_ENDPOINTS } from '../api/endpoints'
import type { ApiResponse, PaginatedResponse } from '../types/api'
import type {
  SpotWork,
  SpotWorkWorker,
  SpotWorkCreate,
  SpotWorkUpdate,
  SpotWorkQueryParams,
  QuickFillRequest,
  WorkersSaveRequest
} from '../types/models'

export const spotWorkService = {
  /**
   * 获取零星用工列表（分页）
   */
  async getList(params?: SpotWorkQueryParams): Promise<PaginatedResponse<SpotWork>> {
    return request.get(API_ENDPOINTS.SPOT_WORK.LIST, { params })
  },

  /**
   * 获取零星用工详情
   */
  async getById(id: number): Promise<ApiResponse<SpotWork>> {
    return request.get(API_ENDPOINTS.SPOT_WORK.DETAIL(id))
  },

  /**
   * 获取所有零星用工（不分页）
   */
  async getAll(): Promise<ApiResponse<SpotWork[]>> {
    return request.get(API_ENDPOINTS.SPOT_WORK.ALL)
  },

  /**
   * 快速填报零星用工
   */
  async quickFill(data: QuickFillRequest): Promise<ApiResponse<SpotWork>> {
    return request.post(API_ENDPOINTS.SPOT_WORK.QUICK_FILL, data)
  },

  /**
   * 创建零星用工
   */
  async create(data: SpotWorkCreate): Promise<ApiResponse<SpotWork>> {
    return request.post(API_ENDPOINTS.SPOT_WORK.LIST, data)
  },

  /**
   * 更新零星用工
   */
  async update(id: number, data: SpotWorkUpdate): Promise<ApiResponse<SpotWork>> {
    return request.put(API_ENDPOINTS.SPOT_WORK.DETAIL(id), data)
  },

  /**
   * 部分更新零星用工
   */
  async patch(id: number, data: Partial<SpotWorkUpdate>): Promise<ApiResponse<SpotWork>> {
    return request.patch(API_ENDPOINTS.SPOT_WORK.DETAIL(id), data)
  },

  /**
   * 保存工人信息
   */
  async saveWorkers(data: WorkersSaveRequest): Promise<ApiResponse<SpotWorkWorker[]>> {
    return request.post(API_ENDPOINTS.SPOT_WORK.WORKERS, data)
  },

  /**
   * 获取工人详情
   */
  async getWorkerById(id: number): Promise<ApiResponse<SpotWorkWorker>> {
    return request.get(API_ENDPOINTS.SPOT_WORK.WORKER_DETAIL(id))
  },

  /**
   * 根据项目ID获取工人列表
   */
  async getWorkersByProject(projectId: string, startDate: string, endDate: string): Promise<ApiResponse<SpotWorkWorker[]>> {
    return request.get(API_ENDPOINTS.SPOT_WORK.WORKERS_BY_PROJECT, {
      params: {
        project_id: projectId,
        start_date: startDate,
        end_date: endDate
      }
    })
  },

  /**
   * 更新工人信息
   */
  async updateWorker(id: number, data: Partial<SpotWorkWorker>): Promise<ApiResponse<SpotWorkWorker>> {
    return request.put(API_ENDPOINTS.SPOT_WORK.WORKER_DETAIL(id), data)
  },

  /**
   * 提交零星用工
   */
  async submit(id: number): Promise<ApiResponse<SpotWork>> {
    return request.post(API_ENDPOINTS.SPOT_WORK.SUBMIT(id))
  },

  /**
   * 审批通过
   */
  async approve(id: number, remark?: string): Promise<ApiResponse<SpotWork>> {
    return request.post(API_ENDPOINTS.SPOT_WORK.APPROVE(id), { remark })
  },

  /**
   * 审批退回
   */
  async reject(id: number, remark: string): Promise<ApiResponse<SpotWork>> {
    return request.post(API_ENDPOINTS.SPOT_WORK.REJECT(id), { remark })
  },

  /**
   * 删除零星用工
   */
  async delete(id: number): Promise<ApiResponse<null>> {
    return request.delete(API_ENDPOINTS.SPOT_WORK.DETAIL(id))
  },

  /**
   * 获取工人列表
   */
  async getWorkers(params: { project_id: string; start_date: string; end_date: string }): Promise<ApiResponse<SpotWorkWorker[]>> {
    return request.get(API_ENDPOINTS.SPOT_WORK.WORKERS, { params })
  },
}

export default spotWorkService
