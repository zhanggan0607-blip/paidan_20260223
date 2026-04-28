/**
 * API端点常量测试
 */
import { describe, it, expect } from 'vitest'
import { API_ENDPOINTS } from './endpoints'

describe('API_ENDPOINTS', () => {
  it('AUTH端点应完整', () => {
    expect(API_ENDPOINTS.AUTH.LOGIN).toBe('/auth/login')
    expect(API_ENDPOINTS.AUTH.LOGIN_JSON).toBe('/auth/login-json')
    expect(API_ENDPOINTS.AUTH.LOGOUT).toBe('/auth/logout')
    expect(API_ENDPOINTS.AUTH.REFRESH).toBe('/auth/refresh')
    expect(API_ENDPOINTS.AUTH.ME).toBe('/auth/me')
  })

  it('PROJECT_INFO端点应完整', () => {
    expect(API_ENDPOINTS.PROJECT_INFO.LIST).toBe('/project-info')
    expect(API_ENDPOINTS.PROJECT_INFO.ALL).toBe('/project-info/all/list')
    expect(typeof API_ENDPOINTS.PROJECT_INFO.DETAIL).toBe('function')
    expect(API_ENDPOINTS.PROJECT_INFO.DETAIL(1)).toBe('/project-info/1')
  })

  it('PERSONNEL端点应完整', () => {
    expect(API_ENDPOINTS.PERSONNEL.LIST).toBe('/personnel')
    expect(API_ENDPOINTS.PERSONNEL.ALL).toBe('/personnel/all/list')
    expect(API_ENDPOINTS.PERSONNEL.DETAIL(5)).toBe('/personnel/5')
  })

  it('TEMPORARY_REPAIR端点应完整', () => {
    expect(API_ENDPOINTS.TEMPORARY_REPAIR.LIST).toBe('/temporary-repair')
    expect(API_ENDPOINTS.TEMPORARY_REPAIR.GENERATE_ID).toBe('/temporary-repair/generate-id')
    expect(API_ENDPOINTS.TEMPORARY_REPAIR.SUBMIT(1)).toBe('/temporary-repair/1/submit')
    expect(API_ENDPOINTS.TEMPORARY_REPAIR.APPROVE(1)).toBe('/temporary-repair/1/approve')
  })

  it('SPOT_WORK端点应完整', () => {
    expect(API_ENDPOINTS.SPOT_WORK.LIST).toBe('/spot-work')
    expect(API_ENDPOINTS.SPOT_WORK.QUICK_FILL).toBe('/spot-work/quick-fill')
    expect(API_ENDPOINTS.SPOT_WORK.WORKERS).toBe('/spot-work/workers')
    expect(API_ENDPOINTS.SPOT_WORK.CHECK_ID_CARD).toBe('/spot-work/workers/check-id-card')
  })

  it('PERIODIC_INSPECTION端点应完整', () => {
    expect(API_ENDPOINTS.PERIODIC_INSPECTION.LIST).toBe('/periodic-inspection')
    expect(API_ENDPOINTS.PERIODIC_INSPECTION.RECORD_BY_INSPECTION('insp-1')).toBe(
      '/periodic-inspection-record/inspection/insp-1'
    )
  })

  it('所有端点路径应以/开头', () => {
    function checkPaths(obj: Record<string, any>, prefix = '') {
      for (const [key, value] of Object.entries(obj)) {
        if (typeof value === 'string') {
          expect(value.startsWith('/'), `${prefix}.${key} = "${value}" should start with /`).toBe(true)
        } else if (typeof value === 'function') {
          const result = value(1)
          if (typeof result === 'string') {
            expect(result.startsWith('/'), `${prefix}.${key}(1) = "${result}" should start with /`).toBe(true)
          }
        } else if (typeof value === 'object' && value !== null) {
          checkPaths(value, `${prefix}.${key}`)
        }
      }
    }
    checkPaths(API_ENDPOINTS)
  })

  it('动态端点函数应正确拼接ID', () => {
    expect(API_ENDPOINTS.PROJECT_INFO.DETAIL(42)).toBe('/project-info/42')
    expect(API_ENDPOINTS.PERSONNEL.DETAIL(99)).toBe('/personnel/99')
    expect(API_ENDPOINTS.TEMPORARY_REPAIR.DETAIL(123)).toBe('/temporary-repair/123')
  })
})
