/**
 * 状态工具函数测试
 */
import { describe, it, expect } from 'vitest'
import {
  STATUS_IN_PROGRESS,
  STATUS_PENDING_CONFIRM,
  STATUS_COMPLETED,
  STATUS_REJECTED,
  ALL_STATUSES,
  WORK_STATUS,
  getStatusType,
  getStatusColor,
  getStatusClass,
  isCompletedStatus,
  isInProgressStatus,
  isPendingConfirmStatus,
  isRejectedStatus,
  isPendingStatus,
  BASE_WORK_TABS,
} from './status'

describe('状态常量', () => {
  it('应定义四种核心状态', () => {
    expect(STATUS_IN_PROGRESS).toBe('执行中')
    expect(STATUS_PENDING_CONFIRM).toBe('待确认')
    expect(STATUS_COMPLETED).toBe('已完成')
    expect(STATUS_REJECTED).toBe('已退回')
  })

  it('ALL_STATUSES应包含四种状态', () => {
    expect(ALL_STATUSES).toHaveLength(4)
    expect(ALL_STATUSES).toContain('执行中')
    expect(ALL_STATUSES).toContain('待确认')
    expect(ALL_STATUSES).toContain('已完成')
    expect(ALL_STATUSES).toContain('已退回')
  })

  it('WORK_STATUS应与常量一致', () => {
    expect(WORK_STATUS.IN_PROGRESS).toBe(STATUS_IN_PROGRESS)
    expect(WORK_STATUS.PENDING_CONFIRM).toBe(STATUS_PENDING_CONFIRM)
    expect(WORK_STATUS.COMPLETED).toBe(STATUS_COMPLETED)
    expect(WORK_STATUS.RETURNED).toBe(STATUS_REJECTED)
  })
})

describe('getStatusType', () => {
  it('执行中应返回primary', () => {
    expect(getStatusType('执行中')).toBe('primary')
  })

  it('待确认应返回warning', () => {
    expect(getStatusType('待确认')).toBe('warning')
  })

  it('已完成应返回success', () => {
    expect(getStatusType('已完成')).toBe('success')
  })

  it('已退回应返回default', () => {
    expect(getStatusType('已退回')).toBe('default')
  })

  it('未知状态应返回default', () => {
    expect(getStatusType('未知')).toBe('default')
  })
})

describe('getStatusColor', () => {
  it('执行中应返回青色', () => {
    expect(getStatusColor('执行中')).toBe('#00bcd4')
  })

  it('待确认应返回橙色', () => {
    expect(getStatusColor('待确认')).toBe('#ff976a')
  })

  it('已完成应返回绿色', () => {
    expect(getStatusColor('已完成')).toBe('#07c160')
  })

  it('已退回应返回灰色', () => {
    expect(getStatusColor('已退回')).toBe('#969799')
  })

  it('未知状态应返回灰色', () => {
    expect(getStatusColor('未知')).toBe('#969799')
  })
})

describe('getStatusClass', () => {
  it('执行中应返回status-in-progress', () => {
    expect(getStatusClass('执行中')).toBe('status-in-progress')
  })

  it('待确认应返回status-waiting', () => {
    expect(getStatusClass('待确认')).toBe('status-waiting')
  })

  it('已完成应返回status-completed', () => {
    expect(getStatusClass('已完成')).toBe('status-completed')
  })

  it('已退回应返回status-returned', () => {
    expect(getStatusClass('已退回')).toBe('status-returned')
  })

  it('未知状态应返回空字符串', () => {
    expect(getStatusClass('未知')).toBe('')
  })
})

describe('状态判断函数', () => {
  it('isCompletedStatus', () => {
    expect(isCompletedStatus('已完成')).toBe(true)
    expect(isCompletedStatus('执行中')).toBe(false)
  })

  it('isInProgressStatus', () => {
    expect(isInProgressStatus('执行中')).toBe(true)
    expect(isInProgressStatus('已完成')).toBe(false)
  })

  it('isPendingConfirmStatus', () => {
    expect(isPendingConfirmStatus('待确认')).toBe(true)
    expect(isPendingConfirmStatus('执行中')).toBe(false)
  })

  it('isRejectedStatus', () => {
    expect(isRejectedStatus('已退回')).toBe(true)
    expect(isRejectedStatus('执行中')).toBe(false)
  })

  it('isPendingStatus应包含执行中和已退回', () => {
    expect(isPendingStatus('执行中')).toBe(true)
    expect(isPendingStatus('已退回')).toBe(true)
    expect(isPendingStatus('待确认')).toBe(false)
    expect(isPendingStatus('已完成')).toBe(false)
  })
})

describe('BASE_WORK_TABS', () => {
  it('应包含3个Tab', () => {
    expect(BASE_WORK_TABS).toHaveLength(3)
  })

  it('每个Tab应有key/title/statuses/color', () => {
    for (const tab of BASE_WORK_TABS) {
      expect(tab.key).toBeTruthy()
      expect(tab.title).toBeTruthy()
      expect(Array.isArray(tab.statuses)).toBe(true)
      expect(tab.statuses.length).toBeGreaterThan(0)
      expect(tab.color).toBeTruthy()
    }
  })
})
