/**
 * API端点常量统一管理
 * 所有API路径在此文件中统一定义，便于维护和修改
 * 适用于PC端和H5端
 */

export const API_ENDPOINTS = {
  AUTH: {
    LOGIN: '/auth/login',
    LOGIN_JSON: '/auth/login-json',
    LOGOUT: '/auth/logout',
    REFRESH: '/auth/refresh',
    ME: '/auth/me',
  },

  DINGTALK: {
    LOGIN: '/dingtalk/login',
    SYNC_USERS: '/dingtalk/sync-users',
    CHECK_CONFIG: '/dingtalk/check-config',
  },

  PROJECT_INFO: {
    LIST: '/project-info',
    DETAIL: (id: number) => `/project-info/${id}`,
    ALL: '/project-info/all/list',
  },

  PERSONNEL: {
    LIST: '/personnel',
    DETAIL: (id: number) => `/personnel/${id}`,
    ALL: '/personnel/all/list',
  },

  CUSTOMER: {
    LIST: '/customer',
    DETAIL: (id: number) => `/customer/${id}`,
    ALL: '/customer/all/list',
  },

  PERIODIC_INSPECTION: {
    LIST: '/periodic-inspection',
    DETAIL: (id: number) => `/periodic-inspection/${id}`,
    ALL: '/periodic-inspection/all/list',
    RECORDS: (id: number) => `/periodic-inspection/${id}/records`,
    RECORD_DETAIL: (inspectionId: number, recordId: number) =>
      `/periodic-inspection/${inspectionId}/records/${recordId}`,
    RECORD_BY_INSPECTION: (inspectionId: string) =>
      `/periodic-inspection-record/inspection/${inspectionId}`,
    CREATE_RECORD: '/periodic-inspection-record',
    SUBMIT: (id: number) => `/periodic-inspection/${id}/submit`,
    APPROVE: (id: number) => `/periodic-inspection/${id}/approve`,
    REJECT: (id: number) => `/periodic-inspection/${id}/reject`,
  },

  TEMPORARY_REPAIR: {
    LIST: '/temporary-repair',
    DETAIL: (id: number) => `/temporary-repair/${id}`,
    ALL: '/temporary-repair/all/list',
    SUBMIT: (id: number) => `/temporary-repair/${id}/submit`,
    APPROVE: (id: number) => `/temporary-repair/${id}/approve`,
    REJECT: (id: number) => `/temporary-repair/${id}/reject`,
  },

  SPOT_WORK: {
    LIST: '/spot-work',
    DETAIL: (id: number) => `/spot-work/${id}`,
    ALL: '/spot-work/all/list',
    QUICK_FILL: '/spot-work/quick-fill',
    WORKERS: '/spot-work/workers',
    WORKER_DETAIL: (id: number) => `/spot-work/workers/${id}`,
    WORKERS_BY_PROJECT: '/spot-work/workers',
    SUBMIT: (id: number) => `/spot-work/${id}/submit`,
    APPROVE: (id: number) => `/spot-work/${id}/approve`,
    REJECT: (id: number) => `/spot-work/${id}/reject`,
  },

  WORK_ORDER: {
    LIST: '/work-order',
    DETAIL: (id: number, type: string) => `/work-order/${id}?type=${type}`,
  },

  MAINTENANCE_PLAN: {
    LIST: '/maintenance-plan',
    DETAIL: (id: number) => `/maintenance-plan/${id}`,
    ALL: '/maintenance-plan/all/list',
    BY_PLAN_ID: (planId: string) => `/maintenance-plan/plan-id/${planId}`,
    GENERATE_WORK_ORDERS: (id: number) => `/maintenance-plan/${id}/generate-work-orders`,
  },

  WORK_PLAN: {
    LIST: '/work-plan',
    DETAIL: (id: number) => `/work-plan/${id}`,
    ALL: '/work-plan/all/list',
    STATISTICS: '/work-plan/statistics',
  },

  INSPECTION_ITEM: {
    LIST: '/inspection-item',
    DETAIL: (id: number) => `/inspection-item/${id}`,
    ALL: '/inspection-item/all/list',
    TREE: '/inspection-item/tree',
  },

  SPARE_PARTS_STOCK: {
    LIST: '/spare-parts-stock/stock',
    DETAIL: (id: number) => `/spare-parts-stock/stock/${id}`,
    ALL: '/spare-parts-stock/stock',
    INBOUND_RECORDS: '/spare-parts-stock/inbound-records',
    INBOUND: '/spare-parts-stock/inbound',
    PRODUCTS: '/spare-parts-stock/products',
  },

  SPARE_PARTS_USAGE: {
    LIST: '/spare-parts/usage',
    DETAIL: (id: number) => `/spare-parts/usage/${id}`,
    ISSUE: '/spare-parts/usage',
    RETURN: (id: number) => `/spare-parts/usage/${id}/return`,
  },

  REPAIR_TOOLS_STOCK: {
    LIST: '/repair-tools/stock',
    DETAIL: (id: number) => `/repair-tools/stock/${id}`,
    ALL: '/repair-tools/stock',
    RESTOCK: (id: number) => `/repair-tools/stock/${id}/restock`,
  },

  REPAIR_TOOLS_USAGE: {
    LIST: '/repair-tools/issue',
    DETAIL: (id: number) => `/repair-tools/issue/${id}`,
    ISSUE: '/repair-tools/issue',
    RETURN: (id: number) => `/repair-tools/issue/${id}/return`,
  },

  WEEKLY_REPORT: {
    LIST: '/weekly-report',
    DETAIL: (id: number) => `/weekly-report/${id}`,
    ALL: '/weekly-report/all/list',
    MY: '/weekly-report/my',
    SUBMIT: (id: number) => `/weekly-report/${id}/submit`,
    GENERATE_ID: '/weekly-report/generate-id',
    OPERATION_LOGS: (id: number) => `/weekly-report/${id}/operation-logs`,
  },

  MAINTENANCE_LOG: {
    LIST: '/maintenance-log',
    DETAIL: (id: number) => `/maintenance-log/${id}`,
    MY: '/maintenance-log/my',
    SUBMIT: (id: number) => `/maintenance-log/${id}/submit`,
    OPERATION_LOGS: (id: number) => `/maintenance-log/${id}/operation-logs`,
  },

  DICTIONARY: {
    LIST: '/dictionary',
    DETAIL: (id: number) => `/dictionary/${id}`,
    BY_TYPE: (type: string) => `/dictionary/type/${type}`,
  },

  STATISTICS: {
    OVERVIEW: '/statistics/overview',
    WORK_BY_PERSON: '/statistics/employee-stats',
    TOP_PROJECTS: '/statistics/top-projects',
    COMPLETION_RATE: '/statistics/completion-rate',
    DETAIL: '/statistics/detail',
  },

  OVERDUE_ALERT: {
    LIST: '/overdue-alert',
  },

  EXPIRING_SOON: {
    LIST: '/expiring-soon',
  },

  ONLINE_USER: {
    COUNT: '/online/count',
    USERS: '/online/users',
    STATISTICS: '/online/statistics',
    HEARTBEAT: '/online/heartbeat',
    LOGIN: '/online/login',
    LOGOUT: '/online/logout',
  },

  WORK_ORDER_OPERATION_LOG: {
    LIST: '/work-order-operation-log',
    BY_WORK_ORDER: (workOrderId: string) => `/work-order-operation-log/work-order/${workOrderId}`,
    CREATE: '/work-order-operation-log',
  },

  UPLOAD: {
    IMAGE: '/upload/image',
    FILE: '/upload',
    BASE64: '/upload/base64',
  },

  OCR: {
    IDCARD: '/ocr/idcard',
  },

  USER_DASHBOARD_CONFIG: {
    GET: '/user-dashboard-config',
    UPDATE: '/user-dashboard-config',
  },

  OPERATION_TYPE: {
    LIST: '/operation-type',
    DETAIL: (id: number) => `/operation-type/${id}`,
    BY_CODE: (code: string) => `/operation-type/code/${code}`,
  },
} as const

export default API_ENDPOINTS
