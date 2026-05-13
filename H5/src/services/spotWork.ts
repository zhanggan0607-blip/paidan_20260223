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
  WorkersSaveRequest,
} from '../types/api'
import { CrudService } from '@sstcp/shared'

class SpotWorkService extends CrudService<SpotWork> {
  constructor() {
    super(request, API_ENDPOINTS.SPOT_WORK.LIST)
  }

  async getAll(): Promise<ApiResponse<SpotWork[]>> {
    return request.get(API_ENDPOINTS.SPOT_WORK.ALL)
  }

  async quickFill(data: QuickFillRequest): Promise<ApiResponse<SpotWork>> {
    return request.post(API_ENDPOINTS.SPOT_WORK.QUICK_FILL, data)
  }

  async saveWorkers(data: WorkersSaveRequest): Promise<ApiResponse<SpotWorkWorker[]>> {
    return request.post(API_ENDPOINTS.SPOT_WORK.WORKERS, data)
  }

  async getWorkerById(id: number): Promise<ApiResponse<SpotWorkWorker>> {
    return request.get(API_ENDPOINTS.SPOT_WORK.WORKER_DETAIL(id))
  }

  async getWorkersByProject(
    projectId: string,
    startDate: string,
    endDate: string
  ): Promise<ApiResponse<SpotWorkWorker[]>> {
    return request.get(API_ENDPOINTS.SPOT_WORK.WORKERS_BY_PROJECT, {
      params: {
        project_id: projectId,
        start_date: startDate,
        end_date: endDate,
      },
    })
  }

  async updateWorker(
    id: number,
    data: Partial<SpotWorkWorker>
  ): Promise<ApiResponse<SpotWorkWorker>> {
    return request.put(API_ENDPOINTS.SPOT_WORK.WORKER_DETAIL(id), data)
  }

  async deleteWorker(id: number): Promise<ApiResponse<null>> {
    return request.delete(API_ENDPOINTS.SPOT_WORK.WORKER_DETAIL(id))
  }

  async submit(id: number): Promise<ApiResponse<SpotWork>> {
    return request.post(API_ENDPOINTS.SPOT_WORK.SUBMIT(id))
  }

  async recall(id: number): Promise<ApiResponse<SpotWork>> {
    return request.post(API_ENDPOINTS.SPOT_WORK.RECALL(id))
  }

  async approve(
    id: number,
    approved: boolean = true,
    rejectReason?: string
  ): Promise<ApiResponse<SpotWork>> {
    return request.post(API_ENDPOINTS.SPOT_WORK.APPROVE(id), {
      approved,
      reject_reason: rejectReason,
    })
  }

  async reject(id: number, rejectReason: string): Promise<ApiResponse<SpotWork>> {
    return request.post(API_ENDPOINTS.SPOT_WORK.APPROVE(id), {
      approved: false,
      reject_reason: rejectReason,
    })
  }

  async getWorkers(params: {
    project_id: string
    start_date: string
    end_date: string
  }): Promise<ApiResponse<SpotWorkWorker[]>> {
    return request.get(API_ENDPOINTS.SPOT_WORK.WORKERS, { params })
  }

  async checkIdCardExists(
    idCardNumber: string,
    params?: {
      project_id?: string
      start_date?: string
      end_date?: string
    }
  ): Promise<
    ApiResponse<{
      exists: boolean
      name?: string
      project_name?: string
      project_id?: string
      can_reuse?: boolean
      duplicate_in_work?: boolean
      work_id?: string
      work_status?: string
    }>
  > {
    return request.get(API_ENDPOINTS.SPOT_WORK.CHECK_ID_CARD, {
      params: { id_card_number: idCardNumber, ...params },
    })
  }

  async getAllWorkers(): Promise<
    ApiResponse<
      {
        name: string
        gender?: string
        birthDate?: string
        address?: string
        idCardNumber: string
        issuingAuthority?: string
        validPeriod?: string
        idCardFront?: string
        idCardBack?: string
      }[]
    >
  > {
    return request.get(API_ENDPOINTS.SPOT_WORK.ALL_WORKERS)
  }
}

export const spotWorkService = new SpotWorkService()

export default spotWorkService
