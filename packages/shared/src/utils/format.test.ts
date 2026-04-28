/**
 * 日期时间格式化工具测试
 */
import { describe, it, expect } from 'vitest'
import {
  formatDate,
  formatDateTime,
  formatTime,
  parseDate,
  getDaysDiff,
  isOverdue,
  getWorkIdFontSize,
  getCurrentDate,
  getCurrentDateTime,
} from './format'

describe('formatDate', () => {
  it('应格式化Date对象为YYYY-MM-DD', () => {
    const date = new Date(2026, 3, 14)
    expect(formatDate(date)).toBe('2026-04-14')
  })

  it('应格式化ISO字符串为YYYY-MM-DD', () => {
    expect(formatDate('2026-04-14T10:30:00')).toBe('2026-04-14')
  })

  it('空值应返回空字符串', () => {
    expect(formatDate(null)).toBe('')
    expect(formatDate(undefined)).toBe('')
    expect(formatDate('')).toBe('')
  })

  it('无效日期应返回空字符串', () => {
    expect(formatDate('invalid')).toBe('')
    expect(formatDate(new Date('invalid'))).toBe('')
  })
})

describe('formatDateTime', () => {
  it('应格式化为YYYY-MM-DD HH:mm:ss', () => {
    const date = new Date(2026, 3, 14, 10, 30, 45)
    expect(formatDateTime(date)).toBe('2026-04-14 10:30:45')
  })

  it('空值应返回空字符串', () => {
    expect(formatDateTime(null)).toBe('')
    expect(formatDateTime(undefined)).toBe('')
  })
})

describe('formatTime', () => {
  it('应格式化为HH:mm:ss', () => {
    const date = new Date(2026, 3, 14, 10, 30, 45)
    expect(formatTime(date)).toBe('10:30:45')
  })

  it('空值应返回空字符串', () => {
    expect(formatTime(null)).toBe('')
  })
})

describe('parseDate', () => {
  it('应解析有效日期字符串', () => {
    const result = parseDate('2026-04-14')
    expect(result).not.toBeNull()
    expect(result!.getFullYear()).toBe(2026)
  })

  it('空值应返回null', () => {
    expect(parseDate(null)).toBeNull()
    expect(parseDate(undefined)).toBeNull()
    expect(parseDate('')).toBeNull()
  })

  it('无效日期应返回null', () => {
    expect(parseDate('invalid')).toBeNull()
  })
})

describe('getDaysDiff', () => {
  it('应计算两个日期之间的天数差', () => {
    expect(getDaysDiff('2026-04-14', '2026-04-16')).toBe(2)
  })

  it('同一日期差为0', () => {
    expect(getDaysDiff('2026-04-14', '2026-04-14')).toBe(0)
  })

  it('结束日期早于开始日期应为负数', () => {
    expect(getDaysDiff('2026-04-16', '2026-04-14')).toBeLessThan(0)
  })
})

describe('isOverdue', () => {
  it('过去日期应为过期', () => {
    expect(isOverdue('2020-01-01')).toBe(true)
  })

  it('未来日期应未过期', () => {
    expect(isOverdue('2099-12-31')).toBe(false)
  })

  it('空值应返回false', () => {
    expect(isOverdue(null)).toBe(false)
    expect(isOverdue(undefined)).toBe(false)
  })
})

describe('getWorkIdFontSize', () => {
  it('空值应返回14', () => {
    expect(getWorkIdFontSize('')).toBe(14)
  })

  it('短编号应返回14', () => {
    expect(getWorkIdFontSize('WX-2026-001')).toBe(14)
  })

  it('长编号应返回较小字体', () => {
    expect(getWorkIdFontSize('A'.repeat(25))).toBeLessThan(14)
  })

  it('超长编号应返回最小7', () => {
    expect(getWorkIdFontSize('A'.repeat(50))).toBe(7)
  })
})

describe('getCurrentDate / getCurrentDateTime', () => {
  it('getCurrentDate应返回YYYY-MM-DD格式', () => {
    const result = getCurrentDate()
    expect(result).toMatch(/^\d{4}-\d{2}-\d{2}$/)
  })

  it('getCurrentDateTime应返回YYYY-MM-DD HH:mm:ss格式', () => {
    const result = getCurrentDateTime()
    expect(result).toMatch(/^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}$/)
  })
})
