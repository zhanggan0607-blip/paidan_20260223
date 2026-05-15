import axios, {
  type AxiosInstance,
  type AxiosResponse,
  type InternalAxiosRequestConfig,
  type AxiosError,
  type AxiosRequestConfig,
} from 'axios'
import type { ApiResponse, ApiError, User } from '../types/api'
import { decodeJwtPayload as _decodeJwt, shouldRefreshToken as _shouldRefresh } from '../utils/jwt'

interface AxiosRequestConfigWithMetadata extends InternalAxiosRequestConfig {
  metadata?: { startTime: number }
}

export interface RequestConfig {
  baseURL: string
  timeout?: number
  getToken: () => string | null
  getRefreshToken?: () => string | null
  getUser: () => User | null
  setToken?: (token: string) => void
  setRefreshToken?: (token: string) => void
  onUnauthorized?: () => void
  onNetworkError?: (error: ApiError) => void
  onServerError?: (error: ApiError) => void
  onRateLimited?: (error: ApiError) => void
  refreshEndpoint?: string
  enableLogger?: boolean
  proactiveRefreshBufferMinutes?: number
  onRequestInterceptor?: (config: InternalAxiosRequestConfig) => InternalAxiosRequestConfig
  onResponseInterceptor?: (response: any) => any
}

export interface RequestOptions {
  signal?: AbortSignal
  params?: object
  headers?: Record<string, string>
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

type RefreshResult =
  | { success: true; token: string }
  | { success: false; reason: 'network_error' | 'auth_error' | 'no_token' }

let isRefreshing = false
let refreshSubscribers: ((token: string) => void)[] = []
let proactiveRefreshPromise: Promise<RefreshResult> | null = null

function subscribeTokenRefresh(callback: (token: string) => void) {
  refreshSubscribers.push(callback)
}

function onTokenRefreshed(token: string) {
  refreshSubscribers.forEach((callback) => callback(token))
  refreshSubscribers = []
}

function decodeJwtPayload(token: unknown): { exp?: number; [key: string]: unknown } | null {
  return _decodeJwt(token)
}

function shouldRefreshToken(token: unknown, bufferMinutes: number = 5): boolean {
  return _shouldRefresh(token, bufferMinutes)
}

async function refreshToken(
  axiosInstance: AxiosInstance,
  config: RequestConfig
): Promise<RefreshResult> {
  const refreshEndpoint = config.refreshEndpoint || '/auth/refresh'
  
  const getRefreshTokenFn = config.getRefreshToken || config.getToken
  const refreshTokenValue = getRefreshTokenFn ? getRefreshTokenFn() : null
  if (!refreshTokenValue) {
    return { success: false, reason: 'no_token' }
  }

  try {
    const fullURL = `${config.baseURL}${refreshEndpoint}`
    const response = await axios.post(
      fullURL,
      {
        refresh_token: refreshTokenValue,
      },
      {
        headers: {
          'Content-Type': 'application/json',
        },
        timeout: config.timeout || 60000,
      }
    )

    if (response.data?.code === 200 && response.data?.data?.access_token) {
      const newToken = response.data.data.access_token
      const newRefreshToken = response.data.data.refresh_token
      if (config.setToken) {
        config.setToken(newToken)
      }
      if (newRefreshToken && config.setRefreshToken) {
        config.setRefreshToken(newRefreshToken)
      }
      return { success: true, token: newToken }
    }
    return { success: false, reason: 'auth_error' }
  } catch (error) {
    if (axios.isAxiosError(error) && !error.response) {
      return { success: false, reason: 'network_error' }
    }
    if (axios.isAxiosError(error) && error.response?.status === 401) {
      return { success: false, reason: 'auth_error' }
    }
    return { success: false, reason: 'auth_error' }
  }
}

function createApiError(error: AxiosError | Error, status?: number): ApiError {
  if (axios.isAxiosError(error)) {
    const response = error.response
    const data = response?.data as
      | { detail?: string | Array<{ msg?: string; type?: string }>; message?: string; data?: { errors?: string[] } }
      | undefined

    let detailMessage: string | undefined
    if (data?.detail) {
      if (typeof data.detail === 'string') {
        detailMessage = data.detail
      } else if (Array.isArray(data.detail)) {
        detailMessage = data.detail.map((e) => e.msg || e.type || String(e)).join('; ')
      }
    }

    return {
      status: response?.status || 0,
      message: detailMessage || data?.message || error.message,
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
    async (axiosConfig: InternalAxiosRequestConfig) => {
      const token = config.getToken()
      if (token) {
        if (!axiosConfig.headers) {
          axiosConfig.headers = {} as any
        }

        const bufferMinutes = config.proactiveRefreshBufferMinutes ?? 5
        if (shouldRefreshToken(token, bufferMinutes) && !isRefreshing) {
          if (!proactiveRefreshPromise) {
            proactiveRefreshPromise = refreshToken(instance, config)
          }
          try {
            const result = await proactiveRefreshPromise
            if (result.success) {
              onTokenRefreshed(result.token)
              axiosConfig.headers['Authorization'] = `Bearer ${result.token}`
            } else if (result.reason === 'network_error') {
              axiosConfig.headers['Authorization'] = `Bearer ${token}`
            } else {
              const payload = decodeJwtPayload(token)
              const isExpired = payload?.exp ? Date.now() >= payload.exp * 1000 : true
              if (isExpired) {
                config.onUnauthorized?.()
                return Promise.reject({
                  status: 401,
                  message: '登录已过期',
                  errors: [],
                  data: null,
                } as ApiError)
              }
              axiosConfig.headers['Authorization'] = `Bearer ${token}`
            }
          } finally {
            proactiveRefreshPromise = null
          }
        } else {
          axiosConfig.headers['Authorization'] = `Bearer ${token}`
        }
      }

      ;(axiosConfig as AxiosRequestConfigWithMetadata).metadata = { startTime: Date.now() }

      if (config.onRequestInterceptor) {
        return config.onRequestInterceptor(axiosConfig)
      }

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
      
      if (config.onResponseInterceptor) {
        return config.onResponseInterceptor(response.data)
      }
      
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

      if (error.response?.status === 429) {
        config.onRateLimited?.(apiError)
      }

      if (error.response?.status === 401 && !originalRequest._retry) {
        const requestUrl = originalRequest.url || ''
        const refreshEndpoint = config.refreshEndpoint || '/auth/refresh'
        if (requestUrl.includes(refreshEndpoint)) {
          config.onUnauthorized?.()
          return Promise.reject(createApiError(error, 401))
        }

        const authEndpoints = ['/auth/login', '/auth/change-password', '/dingtalk/login']
        if (authEndpoints.some((ep) => requestUrl.includes(ep))) {
          return Promise.reject(createApiError(error, 401))
        }

        const token = config.getToken()

        if (!token) {
          return Promise.reject(createApiError(error, 401))
        }

        if (isRefreshing) {
          return new Promise<void>((resolve, reject) => {
            subscribeTokenRefresh((newToken: string) => {
              originalRequest.headers.Authorization = `Bearer ${newToken}`
              resolve()
            })
            setTimeout(() => {
              reject({
                status: 401,
                message: 'Token刷新超时',
                errors: [],
                data: null,
              } as ApiError)
            }, 30000)
          }).then(() => instance(originalRequest))
        }

        originalRequest._retry = true
        isRefreshing = true

        const result = await refreshToken(instance, config)
        isRefreshing = false

        if (result.success) {
          onTokenRefreshed(result.token)
          originalRequest.headers.Authorization = `Bearer ${result.token}`
          return instance(originalRequest)
        }

        const failedSubscribers = [...refreshSubscribers]
        refreshSubscribers = []
        failedSubscribers.forEach((callback) => {
          callback('')
        })

        if (result.reason === 'network_error') {
          return Promise.reject({
            status: 0,
            message: '网络连接失败，请检查网络后重试',
            errors: [],
            data: null,
          } as ApiError)
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

  function buildConfig(options?: RequestOptions): AxiosRequestConfig {
    const axiosConfig: AxiosRequestConfig = {}
    if (options?.signal) {
      axiosConfig.signal = options.signal
    }
    if (options?.params) {
      axiosConfig.params = options.params
    }
    if (options?.headers) {
      axiosConfig.headers = options.headers
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

export default createRequest
