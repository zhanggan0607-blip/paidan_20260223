import request from '../api/request'
import { API_ENDPOINTS } from '../api/endpoints'
import type { ApiResponse, PaginatedData, SpotWork, SpotWorkWorker, SpotWorkCreate, SpotWorkUpdate } from '@sstcp/shared'
import { CrudService } from '@sstcp/shared'

export type { SpotWork, SpotWorkWorker, SpotWorkCreate, SpotWorkUpdate }

class SpotWorkService extends CrudService<SpotWork> {
  constructor() {
    super(request, API_ENDPOINTS.SPOT_WORK.LIST)
  }

  async getAll(): Promise<ApiResponse<SpotWork[]>> {
    return await this.http.get(API_ENDPOINTS.SPOT_WORK.ALL)
  }

  async generateId(projectId: string): Promise<ApiResponse<{ work_id: string }>> {
    return await this.http.get(API_ENDPOINTS.SPOT_WORK.GENERATE_ID, { params: { project_id: projectId } })
  }

  async submit(id: number): Promise<ApiResponse<SpotWork>> {
    return await this.http.post(API_ENDPOINTS.SPOT_WORK.SUBMIT(id))
  }

  async recall(id: number): Promise<ApiResponse<SpotWork>> {
    return await this.http.post(API_ENDPOINTS.SPOT_WORK.RECALL(id))
  }

  async saveWorkers(data: {
    project_id?: string
    project_name?: string
    start_date?: string
    end_date?: string
    workers: Array<{
      name: string
      gender?: string | null
      birthDate?: string | null
      address?: string | null
      idCardNumber: string
      issuingAuthority?: string | null
      validPeriod?: string | null
      idCardFront?: string | null
      idCardBack?: string | null
      id?: number | null
    }>
  }): Promise<ApiResponse<{ saved_count: number; skipped_count: number }>> {
    return await this.http.post(API_ENDPOINTS.SPOT_WORK.WORKERS, data)
  }

  async getWorkers(params: {
    project_id: string
    start_date: string
    end_date: string
  }): Promise<ApiResponse<SpotWorkWorker[]>> {
    return await this.http.get(API_ENDPOINTS.SPOT_WORK.WORKERS, { params })
  }
}

export const spotWorkService = new SpotWorkService()
