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

export interface User {
  id: number
  name: string
  role: string
  department: string
  phone: string
}

export interface LoginRequest {
  username: string
  password: string
}

export interface LoginResponse {
  access_token: string
  token_type: string
  user: User
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
  project_manager?: string
  client_contact?: string
  client_contact_position?: string
  client_contact_info?: string
  created_at: string
  updated_at: string
}

export interface Personnel {
  id: number
  name: string
  gender?: string
  phone?: string
  department?: string
  role?: string
  address?: string
  remarks?: string
  created_at?: string
  updated_at?: string
}

export interface SpotWork {
  id: number
  work_id: string
  plan_id?: string
  project_id: string
  project_name: string
  plan_start_date: string
  plan_end_date: string
  client_name?: string
  client_contact?: string
  client_contact_info?: string
  address?: string
  client_contact_position?: string
  maintenance_personnel?: string
  work_content?: string
  photos?: string[]
  signature?: string
  status: string
  remarks?: string
  actual_completion_date?: string
  worker_count?: number
  work_days?: number
  workers?: SpotWorkWorker[]
  created_at: string
  updated_at: string
}

export interface SpotWorkWorker {
  id: number
  spot_work_id?: number
  project_id: string
  project_name?: string
  start_date?: string
  end_date?: string
  name: string
  gender?: string
  birth_date?: string
  address?: string
  id_card_number?: string
  issuing_authority?: string
  valid_period?: string
  id_card_front?: string
  id_card_back?: string
  created_at?: string
  updated_at?: string
}

export interface PeriodicInspection {
  id: number
  inspection_id: string
  plan_id?: string
  project_id: string
  project_name: string
  plan_start_date: string
  plan_end_date: string
  client_name?: string
  client_contact?: string
  client_contact_info?: string
  address?: string
  client_contact_position?: string
  maintenance_personnel?: string
  status: string
  filled_count: number
  total_count: number
  execution_result?: string
  remarks?: string
  signature?: string
  actual_completion_date?: string
  created_at: string
  updated_at: string
}

export interface PeriodicInspectionRecord {
  id: number
  inspection_id: string
  item_id: string
  item_name: string
  inspection_item?: string
  inspection_content?: string
  check_content?: string
  brief_description?: string
  equipment_name?: string
  equipment_location?: string
  inspected: boolean
  photos?: string[]
  inspection_result?: string
  created_at: string
  updated_at: string
}

export interface TemporaryRepair {
  id: number
  repair_id: string
  plan_id?: string
  project_id: string
  project_name: string
  plan_start_date: string
  plan_end_date: string
  client_name?: string
  client_contact?: string
  client_contact_info?: string
  address?: string
  client_contact_position?: string
  maintenance_personnel?: string
  status: string
  remarks?: string
  fault_description?: string
  solution?: string
  photos?: string[]
  signature?: string
  execution_date?: string
  actual_completion_date?: string
  created_at: string
  updated_at: string
}

export interface SparePartsStock {
  id: number
  product_name: string
  brand?: string
  model?: string
  unit: string
  quantity: number
  status: string
  created_at: string
  updated_at: string
}

export interface SparePartsUsage {
  id: number
  product_name: string
  brand?: string
  model?: string
  quantity: number
  user_name: string
  issue_time: string
  unit: string
  project_id?: string
  project_name?: string
  stock_id?: number
  status: string
  created_at: string
  updated_at: string
}

export interface SparePartsInbound {
  id: number
  inbound_no: string
  product_name: string
  brand?: string
  model?: string
  quantity: number
  supplier?: string
  unit: string
  user_name: string
  remarks?: string
  created_at: string
}

export interface InspectionItem {
  id: number
  item_code: string
  item_name: string
  item_type?: string
  level: number
  parent_id?: number
  check_content?: string
  check_standard?: string
  sort_order?: number
  created_at: string
  updated_at: string
}

export interface MaintenancePlan {
  id: number
  plan_id: string
  plan_name: string
  project_id: string
  project_name: string
  plan_type?: string
  equipment_id?: string
  equipment_name?: string
  equipment_model?: string
  equipment_location?: string
  plan_start_date: string
  plan_end_date: string
  execution_date?: string
  next_maintenance_date?: string
  maintenance_personnel?: string
  responsible_department?: string
  contact_info?: string
  maintenance_content?: string
  maintenance_requirements?: string
  maintenance_standard?: string
  plan_status?: string
  status?: string
  completion_rate?: number
  filled_count?: number
  total_count?: number
  remarks?: string
  inspection_items?: string
  created_at: string
  updated_at: string
}

export interface WeeklyReport {
  id: number
  report_id: string
  project_id: string
  project_name: string
  report_date: string
  report_content?: string
  status: string
  created_at: string
  updated_at: string
}

export interface MaintenanceLog {
  id: number
  log_id: string
  project_id: string
  project_name: string
  log_date: string
  log_content?: string
  status: string
  created_at: string
  updated_at: string
}

export interface RepairToolsStock {
  id: number
  tool_name: string
  tool_model?: string
  unit: string
  quantity: number
  status: string
  created_at: string
  updated_at: string
}

export interface OperationLog {
  id: number
  work_order_id: string
  work_order_type: string
  operation_type: string
  operator?: string
  operator_role?: string
  remark?: string
  created_at: string
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