export interface ApiResponse<T = unknown> {
  code: number
  message: string
  data: T
}

export interface PaginatedResponse<T = unknown> {
  items: T[]
  total: number
  page: number
  pageSize: number
  content?: T[]
  totalElements?: number
}

export interface QueryParams {
  page: number
  pageSize: number
  user?: string
  product?: string
  project?: string
}

export interface SparePartsIssueQueryParams extends QueryParams {
  user?: string
  product?: string
  project?: string
}

export interface SparePartsStockQueryParams extends QueryParams {
  product?: string
  user?: string
}

export interface DashboardItem {
  id: string
  visible: boolean
  position: number
}

export interface DashboardConfig {
  cards: DashboardItem[]
  charts: DashboardItem[]
}

export interface DragItem {
  id: string
  visible: boolean
  position: number
}

export interface WorkByPerson {
  name: string
  value: number
}

export interface TopProject {
  name: string
  value: number
}

export interface StatisticsOverview {
  year: number
  nearExpiry: number
  overdue: number
  completed: number
  regularInspectionCount: number
  temporaryRepairCount: number
  spotWorkCount: number
  workOrderByPerson: WorkByPerson[]
  inspectionByPerson: WorkByPerson[]
  repairByPerson: WorkByPerson[]
  laborByPerson: WorkByPerson[]
  onTimeRate: number
  topProjects: TopProject[]
}

export interface ProjectInfo {
  id: number
  project_id: string
  project_name: string
  completion_date: string
  maintenance_end_date: string
  maintenance_period: string
  client_name: string
  address: string
  project_abbr?: string
  client_contact?: string
  client_contact_position?: string
  client_contact_info?: string
  created_at: string
  updated_at: string
}

export interface ProjectInfoCreate {
  project_id: string
  project_name: string
  completion_date: string
  maintenance_end_date: string
  maintenance_period: string
  client_name: string
  address: string
  project_abbr?: string
  client_contact?: string
  client_contact_position?: string
  client_contact_info?: string
}

export interface ProjectInfoUpdate extends ProjectInfoCreate {}

export interface Personnel {
  id: number
  name: string
  role: string
  phone?: string
  email?: string
  department?: string
  created_at?: string
  updated_at?: string
}

export interface PersonnelCreate {
  name: string
  role: string
  phone?: string
  email?: string
  department?: string
}

export interface PersonnelUpdate extends PersonnelCreate {}

export interface TreeNode {
  id: number
  label: string
  level: number
  parent_id?: number
  check_requirement?: string
  children?: TreeNode[]
}

export interface ToastState {
  visible: boolean
  message: string
  type: 'success' | 'error' | 'warning' | 'info'
}

export interface ApiError {
  status: number
  message: string
  errors: unknown[]
  data: unknown
}
