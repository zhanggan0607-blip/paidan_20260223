import type { ApiResponse } from '../types/api'

type HttpMethods = {
  get<T = unknown>(url: string, config?: Record<string, unknown>): Promise<ApiResponse<T>>
  post<T = unknown>(url: string, data?: unknown, config?: Record<string, unknown>): Promise<ApiResponse<T>>
  put<T = unknown>(url: string, data?: unknown, config?: Record<string, unknown>): Promise<ApiResponse<T>>
  patch<T = unknown>(url: string, data?: unknown, config?: Record<string, unknown>): Promise<ApiResponse<T>>
  delete<T = unknown>(url: string, config?: Record<string, unknown>): Promise<ApiResponse<T>>
}

export class CrudService<T> {
  protected http: HttpMethods
  protected basePath: string

  constructor(http: HttpMethods, basePath: string) {
    this.http = http
    this.basePath = basePath
  }

  async getList(params?: Record<string, unknown>): Promise<ApiResponse> {
    return await this.http.get(this.basePath, { params })
  }

  async getById(id: string | number): Promise<ApiResponse> {
    return await this.http.get(`${this.basePath}/${id}`)
  }

  async create(data: Partial<T>): Promise<ApiResponse> {
    return await this.http.post(this.basePath, data)
  }

  async update(id: string | number, data: Partial<T>): Promise<ApiResponse> {
    return await this.http.put(`${this.basePath}/${id}`, data)
  }

  async patch(id: string | number, data: Partial<T>): Promise<ApiResponse> {
    return await this.http.patch(`${this.basePath}/${id}`, data)
  }

  async delete(id: string | number): Promise<ApiResponse> {
    return await this.http.delete(`${this.basePath}/${id}`)
  }
}
