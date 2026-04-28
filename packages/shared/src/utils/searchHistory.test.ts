/**
 * 搜索历史管理测试
 */
import { describe, it, expect, beforeEach } from 'vitest'
import {
  getSearchHistory,
  addSearchHistory,
  removeSearchHistory,
  clearSearchHistory,
  getRecentKeywords,
  saveSearchHistory,
  loadSearchHistory,
  clearFieldSearchHistory,
  filterHistoryByKeyword,
} from './searchHistory'

describe('搜索历史（全局）', () => {
  beforeEach(() => {
    localStorage.clear()
  })

  it('初始应为空', () => {
    expect(getSearchHistory()).toEqual([])
  })

  it('添加后应能获取', () => {
    addSearchHistory('测试关键词')
    const history = getSearchHistory()
    expect(history.length).toBe(1)
    expect(history[0].keyword).toBe('测试关键词')
  })

  it('重复关键词应移到最前面', () => {
    addSearchHistory('关键词A')
    addSearchHistory('关键词B')
    addSearchHistory('关键词A')

    const history = getSearchHistory()
    expect(history[0].keyword).toBe('关键词A')
    expect(history.length).toBe(2)
  })

  it('空关键词不应添加', () => {
    addSearchHistory('')
    addSearchHistory('   ')
    expect(getSearchHistory()).toEqual([])
  })

  it('删除指定关键词', () => {
    addSearchHistory('关键词A')
    addSearchHistory('关键词B')
    removeSearchHistory('关键词A')
    const history = getSearchHistory()
    expect(history.length).toBe(1)
    expect(history[0].keyword).toBe('关键词B')
  })

  it('清空全部搜索历史', () => {
    addSearchHistory('A')
    addSearchHistory('B')
    clearSearchHistory()
    expect(getSearchHistory()).toEqual([])
  })

  it('按类型清空', () => {
    addSearchHistory('A', 'type1')
    addSearchHistory('B', 'type2')
    clearSearchHistory('type1')
    const history = getSearchHistory()
    expect(history.length).toBe(1)
    expect(history[0].keyword).toBe('B')
  })

  it('getRecentKeywords应限制数量', () => {
    for (let i = 0; i < 15; i++) {
      addSearchHistory(`关键词${i}`)
    }
    const keywords = getRecentKeywords(5)
    expect(keywords.length).toBe(5)
  })

  it('按类型过滤', () => {
    addSearchHistory('A', 'type1')
    addSearchHistory('B', 'type2')
    const result = getSearchHistory('type1')
    expect(result.length).toBe(1)
    expect(result[0].keyword).toBe('A')
  })
})

describe('搜索历史（按字段键）', () => {
  beforeEach(() => {
    localStorage.clear()
  })

  it('saveSearchHistory和loadSearchHistory', () => {
    saveSearchHistory('project_name', '测试项目')
    const history = loadSearchHistory('project_name')
    expect(history).toContain('测试项目')
  })

  it('重复值应移到最前面', () => {
    saveSearchHistory('field', 'A')
    saveSearchHistory('field', 'B')
    saveSearchHistory('field', 'A')
    const history = loadSearchHistory('field')
    expect(history[0]).toBe('A')
    expect(history.length).toBe(2)
  })

  it('空值不应保存', () => {
    saveSearchHistory('field', '')
    saveSearchHistory('field', '   ')
    expect(loadSearchHistory('field')).toEqual([])
  })

  it('clearFieldSearchHistory应清除指定字段', () => {
    saveSearchHistory('field1', 'A')
    saveSearchHistory('field2', 'B')
    clearFieldSearchHistory('field1')
    expect(loadSearchHistory('field1')).toEqual([])
    expect(loadSearchHistory('field2')).toContain('B')
  })

  it('filterHistoryByKeyword应过滤', () => {
    const history = ['测试项目A', '测试项目B', '其他项目']
    expect(filterHistoryByKeyword(history, '测试')).toHaveLength(2)
    expect(filterHistoryByKeyword(history, '')).toHaveLength(3)
  })
})
