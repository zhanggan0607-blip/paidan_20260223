/**
 * OCR服务
 * 提供身份证OCR识别功能
 */
import request from '../api/request'
import { API_ENDPOINTS } from '../api/endpoints'
import type { ApiResponse } from '../types/api'
import type { IDCardOCRResult } from '../types/models'

export interface IDCardOCRRequest {
  imageBase64: string
  side: 'face' | 'back'
}

export const ocrService = {
  /**
   * 身份证OCR识别
   */
  async recognizeIDCard(data: IDCardOCRRequest): Promise<ApiResponse<IDCardOCRResult>> {
    return request.post(API_ENDPOINTS.OCR.IDCARD, data)
  },
}

export default ocrService
