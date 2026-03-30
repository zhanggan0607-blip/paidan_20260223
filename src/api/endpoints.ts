/**
 * PC端API端点
 * 从shared包导入共享的API端点定义
 */
import { API_ENDPOINTS as BASE_API_ENDPOINTS } from '@sstcp/shared'

export const API_ENDPOINTS = {
  ...BASE_API_ENDPOINTS,
  PERIODIC_INSPECTION: {
    ...BASE_API_ENDPOINTS.PERIODIC_INSPECTION,
    INSPECTION_RECORDS: (inspectionId: string) =>
      `/periodic-inspection-record/inspection/${inspectionId}`,
  },
}

export default API_ENDPOINTS
