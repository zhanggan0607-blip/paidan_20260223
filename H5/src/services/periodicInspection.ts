/**
 * 定期巡检服务
 * 提供定期巡检工单的增删改查、提交、审批等功能
 */
import request from '../api/request'
import { API_ENDPOINTS } from '../api/endpoints'
import type { ApiResponse, PaginatedResponse } from '../types/api'
import type {
  PeriodicInspection,
  PeriodicInspectionRecord,
  PeriodicInspectionCreate,
  PeriodicInspectionUpdate,
  PeriodicInspectionQueryParams
} from '../types/models'

export const periodicInspectionService = {
  /**
   * 获取定期巡检列表（分页）
   */
  async getList(params?: PeriodicInspectionQueryParams): Promise<PaginatedResponse<PeriodicInspection>> {
    return request.get(API_ENDPOINTS.PERIODIC_INSPECTION.LIST, { params })
  },

  /**
   * 获取定期巡检详情
   */
  async getById(id: number): Promise<ApiResponse<PeriodicInspection>> {
    return request.get(API_ENDPOINTS.PERIODIC_INSPECTION.DETAIL(id))
  },

  /**
   * 获取所有定期巡检（不分页）
   */
  async getAll(): Promise<ApiResponse<PeriodicInspection[]>> {
    return request.get(API_ENDPOINTS.PERIODIC_INSPECTION.ALL)
  },

  /**
   * 获取巡检记录列表
   */
  async getRecords(inspectionId: number): Promise<ApiResponse<PeriodicInspectionRecord[]>> {
    return request.get(API_ENDPOINTS.PERIODIC_INSPECTION.RECORDS(inspectionId))
  },

  /**
   * 根据巡检单ID获取巡检记录
   */
  async getRecordsByInspectionId(inspectionId: string): Promise<ApiResponse<PeriodicInspectionRecord[]>> {
    return request.get(API_ENDPOINTS.PERIODIC_INSPECTION.RECORD_BY_INSPECTION(inspectionId))
  },

  /**
   * 创建巡检记录
   */
  async createRecord(data: Partial<PeriodicInspectionRecord>): Promise<ApiResponse<PeriodicInspectionRecord>> {
    return request.post(API_ENDPOINTS.PERIODIC_INSPECTION.CREATE_RECORD, data)
  },

  /**
   * 获取巡检记录详情
   */
  async getRecordDetail(inspectionId: number, recordId: number): Promise<ApiResponse<PeriodicInspectionRecord>> {
    return request.get(API_ENDPOINTS.PERIODIC_INSPECTION.RECORD_DETAIL(inspectionId, recordId))
  },

  /**
   * 更新巡检记录
   */
  async updateRecord(inspectionId: number, recordId: number, data: Partial<PeriodicInspectionRecord>): Promise<ApiResponse<PeriodicInspectionRecord>> {
    return request.put(API_ENDPOINTS.PERIODIC_INSPECTION.RECORD_DETAIL(inspectionId, recordId), data)
  },

  /**
   * 创建定期巡检
   */
  async create(data: PeriodicInspectionCreate): Promise<ApiResponse<PeriodicInspection>> {
    return request.post(API_ENDPOINTS.PERIODIC_INSPECTION.LIST, data)
  },

  /**
   * 更新定期巡检
   */
  async update(id: number, data: PeriodicInspectionUpdate): Promise<ApiResponse<PeriodicInspection>> {
    return request.put(API_ENDPOINTS.PERIODIC_INSPECTION.DETAIL(id), data)
  },

  /**
   * 部分更新定期巡检
   */
  async patch(id: number, data: Partial<PeriodicInspectionUpdate>): Promise<ApiResponse<PeriodicInspection>> {
    return request.patch(API_ENDPOINTS.PERIODIC_INSPECTION.DETAIL(id), data)
  },

  /**
   * 提交定期巡检
   */
  async submit(id: number): Promise<ApiResponse<PeriodicInspection>> {
    return request.post(API_ENDPOINTS.PERIODIC_INSPECTION.SUBMIT(id))
  },

  /**
   * 审批通过
   */
  async approve(id: number, remark?: string): Promise<ApiResponse<PeriodicInspection>> {
    return request.post(API_ENDPOINTS.PERIODIC_INSPECTION.APPROVE(id), { remark })
  },

  /**
   * 审批退回
   */
  async reject(id: number, remark: string): Promise<ApiResponse<PeriodicInspection>> {
    return request.post(API_ENDPOINTS.PERIODIC_INSPECTION.REJECT(id), { remark })
  },

  /**
   * 删除定期巡检
   */
  async delete(id: number): Promise<ApiResponse<null>> {
    return request.delete(API_ENDPOINTS.PERIODIC_INSPECTION.DETAIL(id))
  },
}

export default periodicInspectionService
