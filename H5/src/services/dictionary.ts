/**
 * 数据字典服务
 * 提供数据字典的查询功能
 */
import request from '../api/request'
import { API_ENDPOINTS } from '../api/endpoints'
import type { ApiResponse } from '../types/api'
import type { DictionaryItem } from '../types/models'

export const dictionaryService = {
  /**
   * 获取字典列表
   */
  async getList(params?: { type?: string }): Promise<ApiResponse<DictionaryItem[]>> {
    return request.get(API_ENDPOINTS.DICTIONARY.LIST, { params })
  },

  /**
   * 获取字典详情
   */
  async getById(id: number): Promise<ApiResponse<DictionaryItem>> {
    return request.get(API_ENDPOINTS.DICTIONARY.DETAIL(id))
  },

  /**
   * 按类型获取字典项
   */
  async getByType(type: string): Promise<ApiResponse<DictionaryItem[]>> {
    return request.get(API_ENDPOINTS.DICTIONARY.BY_TYPE(type))
  },
}

export default dictionaryService
