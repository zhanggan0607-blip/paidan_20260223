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

export interface UploadProgress {
  loaded: number
  total: number
  percent: number
}

export const uploadService = {
  async uploadImageBase64(
    base64Data: string,
    filename?: string,
    onProgress?: (progress: UploadProgress) => void
  ): Promise<ApiResponse<UploadResponse>> {
    const dataSize = base64Data.length
    if (onProgress) {
      onProgress({ loaded: 0, total: dataSize, percent: 0 })
    }

    const result = await request.post(API_ENDPOINTS.UPLOAD.BASE64, {
      data: base64Data,
      filename,
    })

    if (onProgress) {
      onProgress({ loaded: dataSize, total: dataSize, percent: 100 })
    }

    return result
  },

  async uploadFile(
    file: File,
    onProgress?: (progress: UploadProgress) => void
  ): Promise<ApiResponse<UploadResponse>> {
    const formData = new FormData()
    formData.append('file', file)
    return request.post(API_ENDPOINTS.UPLOAD.FILE, formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
      onUploadProgress: onProgress
        ? (event: any) => {
            if (event.total > 0) {
              onProgress({
                loaded: event.loaded,
                total: event.total,
                percent: Math.round((event.loaded * 100) / event.total),
              })
            }
          }
        : undefined,
    })
  },

  async uploadFiles(
    files: File[],
    onProgress?: (progress: UploadProgress, fileIndex?: number) => void
  ): Promise<ApiResponse<BatchUploadResponse>> {
    if (files.length === 1) {
      const result = await this.uploadFile(files[0], onProgress as any)
      if (result.code === 200 && result.data) {
        return {
          ...result,
          data: {
            success: [result.data as UploadResponse],
            failed: [],
          },
        } as any
      }
      return {
        ...result,
        data: {
          success: [],
          failed: [{ filename: files[0].name, error: result.message || '上传失败' }],
        },
      } as any
    }

    const CONCURRENCY = 3
    const results: UploadResponse[] = []
    const failed: { filename: string; error: string }[] = []
    let completedCount = 0

    const uploadSingle = async (file: File, index: number): Promise<void> => {
      try {
        const formData = new FormData()
        formData.append('file', file)
        const result = await request.post(API_ENDPOINTS.UPLOAD.FILE, formData, {
          headers: {
            'Content-Type': 'multipart/form-data',
          },
        })

        completedCount++
        if (onProgress) {
          onProgress(
            {
              loaded: completedCount,
              total: files.length,
              percent: Math.round((completedCount * 100) / files.length),
            },
            index
          )
        }

        if (result.code === 200 && result.data) {
          results.push(result.data as UploadResponse)
        } else {
          failed.push({ filename: file.name, error: result.message || '上传失败' })
        }
      } catch (error: any) {
        completedCount++
        failed.push({ filename: file.name, error: error.message || '上传异常' })
      }
    }

    const queue = [...files]
    const workers: Promise<void>[] = []

    for (let i = 0; i < Math.min(CONCURRENCY, queue.length); i++) {
      workers.push(
        (async () => {
          while (queue.length > 0) {
            const file = queue.shift()
            if (file) {
              await uploadSingle(file, files.indexOf(file))
            }
          }
        })()
      )
    }

    await Promise.all(workers)

    return {
      code: 200,
      message: `成功上传${results.length}张图片${failed.length > 0 ? `，${failed.length}张失败` : ''}`,
      data: {
        success: results,
        failed,
      },
    } as any
  },
}

export default uploadService
