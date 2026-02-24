/**
 * 分页列表请求组合式函数
 * 统一管理列表数据加载、刷新、分页逻辑
 */
import { ref, computed } from 'vue'
import { showLoadingToast, closeToast } from 'vant'
import api from '../utils/api'
import type { ApiResponse } from '../types'

interface PaginationOptions<T> {
  endpoint: string
  pageSize?: number
  processData?: (items: T[]) => T[]
}

interface PaginatedResponse<T> {
  content: T[]
  items: T[]
  total: number
  totalElements: number
  totalPages: number
  size: number
  number: number
}

/**
 * 分页列表请求组合式函数
 * @param options 配置选项
 * @returns 分页相关的状态和方法
 */
export const usePagination = <T>(options: PaginationOptions<T>) => {
  const { endpoint, pageSize = 100, processData } = options

  const list = ref<T[]>([])
  const loading = ref(false)
  const currentPage = ref(0)
  const total = ref(0)
  const hasMore = ref(true)

  /**
   * 获取列表数据
   * @param params 额外的请求参数
   * @param reset 是否重置列表
   */
  const fetchList = async (params: Record<string, any> = {}, reset = true) => {
    if (reset) {
      currentPage.value = 0
      list.value = []
    }

    loading.value = true
    showLoadingToast({ message: '加载中...', forbidClick: true })

    try {
      const response = await api.get<unknown, ApiResponse<PaginatedResponse<T>>>(endpoint, {
        params: {
          page: currentPage.value,
          size: pageSize,
          ...params
        }
      })

      if (response.code === 200) {
        const data = response.data
        const items = data?.content || data?.items || []
        
        const processedItems = processData ? processData(items) : items
        
        if (reset) {
          list.value = processedItems as T[]
        } else {
          list.value = [...list.value, ...processedItems] as T[]
        }
        
        total.value = data?.totalElements || data?.total || 0
        hasMore.value = list.value.length < total.value
      }
    } catch (error) {
      console.error('Failed to fetch list:', error)
    } finally {
      loading.value = false
      closeToast()
    }
  }

  /**
   * 加载更多数据
   * @param params 额外的请求参数
   */
  const loadMore = async (params: Record<string, any> = {}) => {
    if (!hasMore.value || loading.value) return
    
    currentPage.value++
    await fetchList(params, false)
  }

  /**
   * 刷新列表
   * @param params 额外的请求参数
   */
  const refresh = async (params: Record<string, any> = {}) => {
    await fetchList(params, true)
  }

  /**
   * 重置列表
   */
  const reset = () => {
    list.value = []
    currentPage.value = 0
    total.value = 0
    hasMore.value = true
  }

  /**
   * 是否为空列表
   */
  const isEmpty = computed(() => !loading.value && list.value.length === 0)

  return {
    list,
    loading,
    currentPage,
    total,
    hasMore,
    isEmpty,
    fetchList,
    loadMore,
    refresh,
    reset
  }
}
