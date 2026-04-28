import request from '../api/request'
import { API_ENDPOINTS } from '../api/endpoints'
import type { ApiResponse, PaginatedData, SpotWork, SpotWorkWorker, SpotWorkCreate, SpotWorkUpdate } from '@sstcp/shared'

export type { SpotWork, SpotWorkWorker, SpotWorkCreate, SpotWorkUpdate }

export const spotWorkService = {
  async getList(params?: {
    page?: number
    size?: number
    project_name?: string
    work_id?: string
    status?: string
  }): Promise<ApiResponse<PaginatedData<SpotWork>>> {
    return await request.get(API_ENDPOINTS.SPOT_WORK.LIST, { params })
  },

  async getAll(): Promise<ApiResponse<SpotWork[]>> {
    return await request.get(API_ENDPOINTS.SPOT_WORK.ALL)
  },

  async generateId(projectId: string): Promise<ApiResponse<{ work_id: string }>> {
    return await request.get(API_ENDPOINTS.SPOT_WORK.GENERATE_ID, { params: { project_id: projectId } })
  },

  async getById(id: number): Promise<ApiResponse<SpotWork>> {
    return await request.get(API_ENDPOINTS.SPOT_WORK.DETAIL(id))
  },

  async create(data: SpotWorkCreate): Promise<ApiResponse<SpotWork>> {
    return await request.post(API_ENDPOINTS.SPOT_WORK.LIST, data)
  },

  async update(id: number, data: SpotWorkUpdate): Promise<ApiResponse<SpotWork>> {
    return await request.put(API_ENDPOINTS.SPOT_WORK.DETAIL(id), data)
  },

  async patch(id: number, data: Partial<SpotWorkUpdate>): Promise<ApiResponse<SpotWork>> {
    return await request.patch(API_ENDPOINTS.SPOT_WORK.DETAIL(id), data)
  },

  async delete(id: number): Promise<ApiResponse<null>> {
    return await request.delete(API_ENDPOINTS.SPOT_WORK.DETAIL(id))
  },

  async submit(id: number): Promise<ApiResponse<SpotWork>> {
    return await request.post(API_ENDPOINTS.SPOT_WORK.SUBMIT(id))
  },

  async recall(id: number): Promise<ApiResponse<SpotWork>> {
    return await request.post(API_ENDPOINTS.SPOT_WORK.RECALL(id))
  },

  async saveWorkers(data: {
    project_id: string
    project_name: string
    start_date: string
    end_date: string
    workers: Array<{
      name: string
      gender?: string | null
      birthDate?: string | null
      address?: string | null
      idCardNumber: string
      issuingAuthority?: string | null
      validPeriod?: string | null
      idCardFront: string
      idCardBack: string
    }>
  }): Promise<ApiResponse<{ saved_count: number; skipped_count: number }>> {
    return await request.post(API_ENDPOINTS.SPOT_WORK.WORKERS, data)
  },

  async getWorkers(params: {
    project_id: string
    start_date: string
    end_date: string
  }): Promise<ApiResponse<SpotWorkWorker[]>> {
    return await request.get(API_ENDPOINTS.SPOT_WORK.WORKERS, { params })
  },
}
