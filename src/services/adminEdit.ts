import { request } from '@/api/request'
import type { ApiResponse } from '@/types/api'

export interface AdminEditContentRequest {
  work_order_type: string
  work_order_id: number
  field_name: string
  old_value?: string | null
  new_value?: string | null
  remark?: string | null
}

export interface AdminAddPhotoRequest {
  work_order_type: string
  work_order_id: number
  photo_url: string
  remark?: string | null
}

export interface AdminDeletePhotoRequest {
  work_order_type: string
  work_order_id: number
  photo_url: string
  remark?: string | null
}

export interface EditableField {
  field_name: string
  display_name: string
}

export const adminEditService = {
  async editContent(data: AdminEditContentRequest): Promise<ApiResponse<unknown>> {
    const response = await request.post('/admin-edit/content', data)
    return response as unknown as ApiResponse<unknown>
  },

  async addPhoto(data: AdminAddPhotoRequest): Promise<ApiResponse<unknown>> {
    const response = await request.post('/admin-edit/photo/add', data)
    return response as unknown as ApiResponse<unknown>
  },

  async deletePhoto(data: AdminDeletePhotoRequest): Promise<ApiResponse<unknown>> {
    const response = await request.post('/admin-edit/photo/delete', data)
    return response as unknown as ApiResponse<unknown>
  },

  async getEditableFields(workOrderType: string): Promise<ApiResponse<EditableField[]>> {
    const response = await request.get(`/admin-edit/editable-fields/${workOrderType}`)
    return response as unknown as ApiResponse<EditableField[]>
  },
}
