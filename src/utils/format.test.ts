import { describe, it, expect } from 'vitest'
import { formatDateTime, formatDate } from '@sstcp/shared/utils/format'

describe('format utils', () => {
  it('formatDateTime should format date correctly', () => {
    const date = new Date('2024-01-15T10:30:00')
    const result = formatDateTime(date)
    expect(result).toContain('2024')
    expect(result).toContain('01')
    expect(result).toContain('15')
  })

  it('formatDate should format date correctly', () => {
    const date = new Date('2024-01-15')
    const result = formatDate(date)
    expect(result).toBe('2024-01-15')
  })

  it('formatDate should handle string input', () => {
    const result = formatDate('2024-01-15T10:30:00')
    expect(result).toBe('2024-01-15')
  })
})
