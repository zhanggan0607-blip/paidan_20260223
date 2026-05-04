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

export interface BatchUploadResponse {
  success: UploadResponse[]
  failed: { filename: string; error: string }[]
}

export const uploadService = {
  async uploadImageBase64(
    base64Data: string,
    filename?: string
  ): Promise<ApiResponse<UploadResponse>> {
    return request.post(API_ENDPOINTS.UPLOAD.BASE64, {
      data: base64Data,
      filename,
    })
  },

  async uploadFile(file: File): Promise<ApiResponse<UploadResponse>> {
    const formData = new FormData()
    formData.append('file', file)
    return request.post(API_ENDPOINTS.UPLOAD.FILE, formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    })
  },

  async uploadFiles(files: File[]): Promise<ApiResponse<BatchUploadResponse>> {
    const formData = new FormData()
    files.forEach((file) => {
      formData.append('files', file)
    })
    return request.post(API_ENDPOINTS.UPLOAD.BATCH, formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    })
  },
}

export default uploadService
