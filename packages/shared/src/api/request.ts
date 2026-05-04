import axios, {
  type AxiosInstance,
  type AxiosResponse,
  type InternalAxiosRequestConfig,
  type AxiosError,
  type AxiosRequestConfig,
} from 'axios'
import type { ApiResponse, ApiError, User } from '../types/api'

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

let isRefreshing = false
let refreshSubscribers: ((token: string) => void)[] = []
let proactiveRefreshPromise: Promise<string | null> | null = null

function subscribeTokenRefresh(callback: (token: string) => void) {
  refreshSubscribers.push(callback)
}

function onTokenRefreshed(token: string) {
  refreshSubscribers.forEach((callback) => callback(token))
  refreshSubscribers = []
}

function decodeJwtPayload(token: string): { exp?: number; [key: string]: unknown } | null {
  try {
    const parts = token.split('.')
    if (parts.length !== 3) return null
    const base64 = parts[1].replace(/-/g, '+').replace(/_/g, '/')
    const jsonStr = decodeURIComponent(
      atob(base64)
        .split('')
        .map((c) => '%' + ('00' + c.charCodeAt(0).toString(16)).slice(-2))
        .join('')
    )
    return JSON.parse(jsonStr)
  } catch {
    return null
  }
}

function shouldRefreshToken(token: string, bufferMinutes: number = 5): boolean {
  const payload = decodeJwtPayload(token)
  if (!payload || !payload.exp) return false
  const expiresAt = payload.exp * 1000
  const now = Date.now()
  const buffer = bufferMinutes * 60 * 1000
  return now >= expiresAt - buffer
}

async function refreshToken(
  axiosInstance: AxiosInstance,
  config: RequestConfig
): Promise<string | null> {
  const refreshEndpoint = config.refreshEndpoint || '/auth/refresh'
  
  const getRefreshTokenFn = config.getRefreshToken || config.getToken
  const refreshTokenValue = getRefreshTokenFn ? getRefreshTokenFn() : null
  if (!refreshTokenValue) {
    return null
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
            const newToken = await proactiveRefreshPromise
            if (newToken) {
              onTokenRefreshed(newToken)
              axiosConfig.headers['Authorization'] = `Bearer ${newToken}`
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

        const newToken = await refreshToken(instance, config)
        isRefreshing = false

        if (newToken) {
          onTokenRefreshed(newToken)
          originalRequest.headers.Authorization = `Bearer ${newToken}`
          return instance(originalRequest)
        }

        const failedSubscribers = [...refreshSubscribers]
        refreshSubscribers = []
        failedSubscribers.forEach((callback) => {
          callback('')
        })
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
