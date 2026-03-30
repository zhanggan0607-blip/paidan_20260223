/**
 * 人员数据模型
 */

/**
 * 人员信息
 */
export interface Personnel {
  id: number
  name: string
  gender?: string
  phone?: string
  department?: string
  role?: string
  address?: string
  remarks?: string
  last_login_at?: string
  created_at?: string
  updated_at?: string
}

/**
 * 创建人员请求
 */
export interface PersonnelCreate {
  name: string
  gender?: string
  phone?: string
  department?: string
  role?: string
  address?: string
  remarks?: string
}

/**
 * 更新人员请求
 */
export interface PersonnelUpdate extends PersonnelCreate {}

/**
 * 人员查询参数
 */
export interface PersonnelQueryParams {
  page?: number
  size?: number
  name?: string
  department?: string
  role?: string
}
