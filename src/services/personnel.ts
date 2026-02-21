import apiClient from '../utils/api'

/**
 * 人员管理服务模块
 * 提供人员数据的增删改查接口
 */

/** 人员信息接口 */
export interface Personnel {
  /** 人员ID */
  id: number
  /** 姓名 */
  name: string
  /** 性别 */
  gender: string
  /** 联系电话 */
  phone?: string
  /** 所属部门 */
  department?: string
  /** 角色 */
  role: string
  /** 地址 */
  address?: string
  /** 备注 */
  remarks?: string
  /** 创建时间 */
  created_at: string
  /** 更新时间 */
  updated_at: string
}

/** 人员创建数据接口 */
export interface PersonnelCreate {
  /** 姓名 */
  name: string
  /** 性别 */
  gender: string
  /** 联系电话 */
  phone?: string
  /** 所属部门 */
  department?: string
  /** 角色 */
  role: string
  /** 地址 */
  address?: string
  /** 备注 */
  remarks?: string
}

/** 人员更新数据接口 */
export interface PersonnelUpdate {
  /** 姓名 */
  name?: string
  /** 性别 */
  gender?: string
  /** 联系电话 */
  phone?: string
  /** 所属部门 */
  department?: string
  /** 角色 */
  role?: string
  /** 地址 */
  address?: string
  /** 备注 */
  remarks?: string
}

/** 通用API响应接口 */
export interface ApiResponse<T = any> {
  /** 响应状态码 */
  code: number
  /** 响应消息 */
  message: string
  /** 响应数据 */
  data: T
}

/** 分页响应接口 */
export interface PaginatedResponse {
  /** 响应状态码 */
  code: number
  /** 响应消息 */
  message: string
  /** 分页数据 */
  data: {
    /** 数据列表 */
    content: Personnel[]
    /** 总记录数 */
    totalElements: number
    /** 总页数 */
    totalPages: number
    /** 每页大小 */
    size: number
    /** 当前页码 */
    number: number
    /** 是否第一页 */
    first: boolean
    /** 是否最后一页 */
    last: boolean
  }
}

/**
 * 人员服务对象
 * 提供人员管理的所有API调用方法
 */
export const personnelService = {
  /**
   * 分页获取人员列表
   * @param params 查询参数
   * @returns 分页响应数据
   */
  async getList(params?: {
    page?: number
    size?: number
    name?: string
    employee_id?: string
    department?: string
    status?: string
    current_user_role?: string
    current_user_department?: string
  }): Promise<PaginatedResponse> {
    return await apiClient.get('/personnel', { params })
  },

  /**
   * 根据ID获取人员详情
   * @param id 人员ID
   * @returns 人员详情数据
   */
  async getById(id: number): Promise<ApiResponse<Personnel>> {
    return await apiClient.get(`/personnel/${id}`)
  },

  /**
   * 创建新人员
   * @param data 人员创建数据
   * @returns 创建成功的人员数据
   */
  async create(data: PersonnelCreate): Promise<ApiResponse<Personnel>> {
    return await apiClient.post('/personnel', data)
  },

  /**
   * 更新人员信息
   * @param id 人员ID
   * @param data 人员更新数据
   * @returns 更新后的人员数据
   */
  async update(id: number, data: PersonnelUpdate): Promise<ApiResponse<Personnel>> {
    return await apiClient.put(`/personnel/${id}`, data)
  },

  /**
   * 删除人员
   * @param id 人员ID
   * @returns 删除结果
   */
  async delete(id: number): Promise<ApiResponse<null>> {
    return await apiClient.delete(`/personnel/${id}`)
  },

  /**
   * 获取所有人员列表（不分页）
   * @returns 所有人员数据
   */
  async getAll(): Promise<ApiResponse<Personnel[]>> {
    return await apiClient.get('/personnel/all/list')
  }
}
