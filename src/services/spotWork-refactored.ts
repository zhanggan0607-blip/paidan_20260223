/**
 * 零星用工服务 - PC端
 * 使用 shared 包的 service 工厂函数
 */
import request from '../api/request'
import { API_ENDPOINTS } from '../api/endpoints'
import { createBaseService, createSubmitApproveService } from '@sstcp/shared'
import type { ApiResponse, PaginatedData, SpotWork, SpotWorkCreate, SpotWorkUpdate } from '@sstcp/shared'

export type { SpotWork, SpotWorkCreate, SpotWorkUpdate }

const baseService = createBaseService<SpotWork, SpotWorkCreate, SpotWorkUpdate>({
  endpoints: {
    LIST: API_ENDPOINTS.SPOT_WORK.LIST,
    DETAIL: API_ENDPOINTS.SPOT_WORK.DETAIL,
    ALL: API_ENDPOINTS.SPOT_WORK.ALL,
  },
  request,
})

export const spotWorkService = {
  ...baseService,

  async getList(params?: {
    page?: number
    size?: number
    project_name?: string
    work_id?: string
    status?: string
  }): Promise<ApiResponse<PaginatedData<SpotWork>>> {
    return await request.get(API_ENDPOINTS.SPOT_WORK.LIST, { params })
  },
}
