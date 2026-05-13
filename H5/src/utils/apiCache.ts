export {
  ApiCache,
  getCache,
  withCache,
  createCacheKey,
  clearApiCache,
  invalidateCache,
  deduplicateRequest,
  clearPendingRequests,
  DEFAULT_CACHE_OPTIONS,
} from '@sstcp/shared'

export const apiCache = getCache()

export const CACHE_KEYS = {
  WORK_ORDER_COMPLETED: 'work_order_completed',
  OVERDUE_ALERT: 'overdue_alert',
  EXPIRING_SOON: 'expiring_soon',
  PROJECT_INFO: 'project_info',
  PERSONNEL: 'personnel',
  CUSTOMER: 'customer',
  STATISTICS: 'statistics',
  TEMPORARY_REPAIR_PENDING: 'temporary_repair_pending',
  SPOT_WORK_PENDING: 'spot_work_pending',
  PERIODIC_INSPECTION_PENDING: 'periodic_inspection_pending',
}

export const CACHE_TTL = {
  SHORT: 60000,
  MEDIUM: 180000,
  LONG: 600000,
}

export default apiCache
