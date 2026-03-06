/**
 * 上传服务
 * 提供文件上传功能
 */
import request from '../api/request'
import { API_ENDPOINTS } from '../api/endpoints'
import type { ApiResponse } from '../types/api'

export interface UploadResponse {
  url: string
  filename: string
}

export const uploadService = {
  /**
   * 上传图片（Base64）
   */
  async uploadImageBase64(
    base64Data: string,
    filename?: string
  ): Promise<ApiResponse<UploadResponse>> {
    return request.post(API_ENDPOINTS.UPLOAD.BASE64, {
      image_base64: base64Data,
      filename,
    })
  },

  /**
   * 上传文件
   */
  async uploadFile(file: File): Promise<ApiResponse<UploadResponse>> {
    const formData = new FormData()
    formData.append('file', file)
    return request.post(API_ENDPOINTS.UPLOAD.FILE, formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    })
  },
}

export default uploadService
