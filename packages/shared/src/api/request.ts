/**
 * 统一请求封装工厂
 * 提供创建Axios实例的工厂函数，支持自定义配置
 */
import axios, {
  type AxiosInstance,
  type AxiosResponse,
  type InternalAxiosRequestConfig,
  type AxiosError,
} from 'axios'
import type { ApiResponse, ApiError, User } from '../types/api'

interface AxiosRequestConfigWithMetadata extends InternalAxiosRequestConfig {
  metadata?: { startTime: number }
}

export interface RequestConfig {
  baseURL: string
  timeout?: number
  getToken: () => string | null
  getUser: () => User | null
  setToken?: (token: string) => void
  onUnauthorized?: () => void
  onNetworkError?: (error: ApiError) => void
  onServerError?: (error: ApiError) => void
  refreshEndpoint?: string
  enableLogger?: boolean
}

export interface RequestOptions {
  signal?: AbortSignal
}

export interface RequestInstance {
  request: AxiosInstance
  get: <T = unknown>(url: string, config?: RequestOptions) => Promise<ApiResponse<T>>
  post: <T = unknown>(
    url: string,
    data?: unknown,
    config?: RequestOptions
  ) => Promise<ApiResponse<T>>
  put: <T = unknown>(
    url: string,
    data?: unknown,
    config?: RequestOptions
  ) => Promise<ApiResponse<T>>
  patch: <T = unknown>(
    url: string,
    data?: unknown,
    config?: RequestOptions
  ) => Promise<ApiResponse<T>>
  delete: <T = unknown>(url: string, config?: RequestOptions) => Promise<ApiResponse<T>>
}

let isRefreshing = false
let refreshSubscribers: ((token: string) => void)[] = []

function subscribeTokenRefresh(callback: (token: string) => void) {
  refreshSubscribers.push(callback)
}

function onTokenRefreshed(token: string) {
  refreshSubscribers.forEach((callback) => callback(token))
  refreshSubscribers = []
}

async function refreshToken(
  axiosInstance: AxiosInstance,
  config: RequestConfig
): Promise<string | null> {
  try {
    const token = config.getToken()
    if (!token) return null

    const refreshEndpoint = config.refreshEndpoint || '/auth/refresh'
    const response = await axiosInstance.post(
      refreshEndpoint,
      {},
      {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      }
    )

    if (response.data?.code === 200 && response.data?.data?.access_token) {
      const newToken = response.data.data.access_token
      if (config.setToken) {
        config.setToken(newToken)
      }
      return newToken
    }
    return null
  } catch {
    return null
  }
}

function createApiError(error: AxiosError | Error, status?: number): ApiError {
  if (axios.isAxiosError(error)) {
    const response = error.response
    const data = response?.data as
      | { detail?: string; message?: string; data?: { errors?: string[] } }
      | undefined

    return {
      status: response?.status || 0,
      message: data?.detail || data?.message || error.message,
      errors: data?.data?.errors || [],
      data: data?.data || null,
    }
  }

  return {
    status: status || -1,
    message: error.message,
    errors: [],
    data: null,
  }
}

function logRequest(config: RequestConfig, method: string, url: string, data?: unknown) {
  if (!config.enableLogger) return
  console.log(`[API Request] ${method.toUpperCase()} ${url}`, data || '')
}

function logResponse(
  config: RequestConfig,
  method: string,
  url: string,
  response: unknown,
  duration: number
) {
  if (!config.enableLogger) return
  console.log(`[API Response] ${method.toUpperCase()} ${url} (${duration}ms)`, response)
}

function logError(config: RequestConfig, method: string, url: string, error: ApiError) {
  if (!config.enableLogger) return
  console.error(`[API Error] ${method.toUpperCase()} ${url}`, error)
}

export function createRequest(config: RequestConfig): RequestInstance {
  const instance: AxiosInstance = axios.create({
    baseURL: config.baseURL,
    timeout: config.timeout || 60000,
    headers: {
      'Content-Type': 'application/json',
    },
  })

  instance.interceptors.request.use(
    (axiosConfig: InternalAxiosRequestConfig) => {
      const token = config.getToken()
      if (token) {
        axiosConfig.headers = axiosConfig.headers || {}
        axiosConfig.headers['Authorization'] = `Bearer ${token}`
      }

      ;(axiosConfig as AxiosRequestConfigWithMetadata).metadata = { startTime: Date.now() }

      return axiosConfig
    },
    (error) => Promise.reject(error)
  )

  instance.interceptors.response.use(
    (response: AxiosResponse) => {
      const metadata = (response.config as AxiosRequestConfigWithMetadata).metadata
      const duration = Date.now() - (metadata?.startTime || 0)
      logResponse(
        config,
        response.config.method || 'get',
        response.config.url || '',
        response.data,
        duration
      )
      return response.data
    },
    async (error: AxiosError) => {
      if (error.name === 'CanceledError' || error.code === 'ERR_CANCELED') {
        return Promise.reject({
          status: 0,
          message: '请求已取消',
          errors: [],
          data: null,
        } as ApiError)
      }

      const originalRequest = error.config as InternalAxiosRequestConfig & { _retry?: boolean }
      const apiError = createApiError(error)

      logError(config, originalRequest?.method || 'get', originalRequest?.url || '', apiError)

      if (!error.response) {
        config.onNetworkError?.(apiError)
        return Promise.reject(apiError)
      }

      if (error.response.status >= 500) {
        config.onServerError?.(apiError)
      }

      if (error.response?.status === 401 && !originalRequest._retry) {
        const token = config.getToken()

        if (!token) {
          config.onUnauthorized?.()
          return Promise.reject(createApiError(error, 401))
        }

        if (isRefreshing) {
          return new Promise((resolve) => {
            subscribeTokenRefresh((newToken: string) => {
              originalRequest.headers.Authorization = `Bearer ${newToken}`
              resolve(instance(originalRequest))
            })
          })
        }

        originalRequest._retry = true
        isRefreshing = true

        const newToken = await refreshToken(instance, config)
        isRefreshing = false

        if (newToken) {
          onTokenRefreshed(newToken)
          originalRequest.headers.Authorization = `Bearer ${newToken}`
          return instance(originalRequest)
        }

        config.onUnauthorized?.()
        return Promise.reject({
          status: 401,
          message: '登录已过期',
          errors: [],
          data: null,
        } as ApiError)
      }

      return Promise.reject(createApiError(error))
    }
  )

  function buildConfig(options?: RequestOptions): object {
    const axiosConfig: { signal?: AbortSignal } = {}
    if (options?.signal) {
      axiosConfig.signal = options.signal
    }
    return axiosConfig
  }

  return {
    request: instance,
    get: <T = unknown>(url: string, options?: RequestOptions) => {
      logRequest(config, 'get', url)
      return instance.get(url, buildConfig(options)) as Promise<ApiResponse<T>>
    },
    post: <T = unknown>(url: string, data?: unknown, options?: RequestOptions) => {
      logRequest(config, 'post', url, data)
      return instance.post(url, data, buildConfig(options)) as Promise<ApiResponse<T>>
    },
    put: <T = unknown>(url: string, data?: unknown, options?: RequestOptions) => {
      logRequest(config, 'put', url, data)
      return instance.put(url, data, buildConfig(options)) as Promise<ApiResponse<T>>
    },
    patch: <T = unknown>(url: string, data?: unknown, options?: RequestOptions) => {
      logRequest(config, 'patch', url, data)
      return instance.patch(url, data, buildConfig(options)) as Promise<ApiResponse<T>>
    },
    delete: <T = unknown>(url: string, options?: RequestOptions) => {
      logRequest(config, 'delete', url)
      return instance.delete(url, buildConfig(options)) as Promise<ApiResponse<T>>
    },
  }
}

export const handleApiError = (error: unknown, defaultMessage: string = '操作失败'): string => {
  if (error && typeof error === 'object' && 'message' in error) {
    return (error as ApiError).message || defaultMessage
  }
  return defaultMessage
}

export const isApiError = (error: unknown): error is ApiError => {
  return error !== null && typeof error === 'object' && 'status' in error && 'message' in error
}

export default createRequest
