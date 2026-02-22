export const USER_ROLES = {
  ADMIN: 'admin',
  DEPARTMENT_MANAGER: 'department_manager',
  MATERIAL_MANAGER: 'material_manager',
  EMPLOYEE: 'employee'
} as const

export const WORK_ORDER_STATUS = {
  PENDING: 'pending',
  IN_PROGRESS: 'in_progress',
  COMPLETED: 'completed',
  APPROVED: 'approved',
  REJECTED: 'rejected'
} as const

export const SPARE_PARTS_STATUS = {
  NORMAL: 'normal',
  LOW_STOCK: 'low_stock',
  OUT_OF_STOCK: 'out_of_stock'
} as const

export const OPERATION_TYPES = {
  CREATE: 'create',
  UPDATE: 'update',
  DELETE: 'delete',
  SUBMIT: 'submit',
  APPROVE: 'approve',
  REJECT: 'reject',
  RETURN: 'return'
} as const

export const WORK_ORDER_TYPES = {
  PERIODIC_INSPECTION: 'periodic_inspection',
  TEMPORARY_REPAIR: 'temporary_repair',
  SPOT_WORK: 'spot_work'
} as const

export const DATE_FORMAT = 'YYYY-MM-DD'
export const DATETIME_FORMAT = 'YYYY-MM-DD HH:mm:ss'

export const API_BASE_URL = 'http://localhost:8080/api/v1'

export const STORAGE_KEYS = {
  TOKEN: 'auth_token',
  REFRESH_TOKEN: 'refresh_token',
  USER: 'user',
  TOKEN_EXPIRY: 'token_expiry'
} as const

export const ERROR_CODES = {
  SUCCESS: 200,
  UNAUTHORIZED: 401,
  FORBIDDEN: 403,
  NOT_FOUND: 404,
  VALIDATION_ERROR: 422,
  INTERNAL_ERROR: 500,
  NETWORK_ERROR: 0
} as const

export const ERROR_MESSAGES = {
  [ERROR_CODES.UNAUTHORIZED]: '未授权，请重新登录',
  [ERROR_CODES.FORBIDDEN]: '无权限访问',
  [ERROR_CODES.NOT_FOUND]: '资源不存在',
  [ERROR_CODES.VALIDATION_ERROR]: '数据验证失败',
  [ERROR_CODES.INTERNAL_ERROR]: '服务器内部错误',
  [ERROR_CODES.NETWORK_ERROR]: '网络连接失败'
} as const

export const OCR_RATE_LIMIT = {
  MAX_REQUESTS: 10,
  WINDOW_MS: 60000
} as const

export const IMAGE_CONFIG = {
  MAX_SIZE: 500 * 1024,
  MAX_WIDTH: 1920,
  MAX_HEIGHT: 1920,
  QUALITY: 0.8,
  THUMBNAIL_SIZE: 200
} as const