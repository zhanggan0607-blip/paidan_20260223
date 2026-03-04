/**
 * 统一请求封装工厂
 * 提供创建Axios实例的工厂函数，支持自定义配置
 */
import axios, { type AxiosInstance, type AxiosResponse, type InternalAxiosRequestConfig, type AxiosError } from 'axios'
import type { ApiResponse, ApiError, User } from '../types/api'

export interface RequestConfig {
  baseURL: string
  timeout?: number
  getToken: () => string | null
  getUser: () => User | null
  setToken?: (token: string) => void
  onUnauthorized?: () => void
  refreshEndpoint?: string
}

export interface RequestInstance {
  request: AxiosInstance
  get: <T = unknown>(url: string, config?: object) => Promise<ApiResponse<T>>
  post: <T = unknown>(url: string, data?: unknown, config?: object) => Promise<ApiResponse<T>>
  put: <T = unknown>(url: string, data?: unknown, config?: object) => Promise<ApiResponse<T>>
  patch: <T = unknown>(url: string, data?: unknown, config?: object) => Promise<ApiResponse<T>>
  delete: <T = unknown>(url: string, config?: object) => Promise<ApiResponse<T>>
}

let isRefreshing = false
let refreshSubscribers: ((token: string) => void)[] = []

function subscribeTokenRefresh(callback: (token: string) => void) {
  refreshSubscribers.push(callback)
}

function onTokenRefreshed(token: string) {
  refreshSubscribers.forEach(callback => callback(token))
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
    const response = await axiosInstance.post(refreshEndpoint, {}, {
      headers: {
        'Authorization': `Bearer ${token}`
      }
    })
    
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
    const data = response?.data as { detail?: string; message?: string; data?: { errors?: string[] } } | undefined
    
    return {
      status: response?.status || 0,
      message: data?.detail || data?.message || error.message,
      errors: data?.data?.errors || [],
      data: data?.data || null
    }
  }
  
  return {
    status: status || -1,
    message: error.message,
    errors: [],
    data: null
  }
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
      const user = config.getUser()
      if (user) {
        axiosConfig.headers['X-User-Name'] = encodeURIComponent(user.name || '')
        axiosConfig.headers['X-User-Role'] = encodeURIComponent(user.role || '')
      }
      return axiosConfig
    },
    (error) => Promise.reject(error)
  )

  instance.interceptors.response.use(
    (response: AxiosResponse) => {
      return response.data
    },
    async (error: AxiosError) => {
      const originalRequest = error.config as InternalAxiosRequestConfig & { _retry?: boolean }
      
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
          data: null
        } as ApiError)
      }
      
      return Promise.reject(createApiError(error))
    }
  )

  function addAuthHeaders(requestConfig: InternalAxiosRequestConfig | object): object {
    const token = config.getToken()
    const user = config.getUser()
    const headers: Record<string, string> = {}
    
    if (token) {
      headers['Authorization'] = `Bearer ${token}`
    }
    if (user) {
      headers['X-User-Name'] = encodeURIComponent(user.name || '')
      headers['X-User-Role'] = encodeURIComponent(user.role || '')
    }
    
    return {
      ...requestConfig,
      headers: {
        ...headers,
        ...('headers' in requestConfig ? requestConfig.headers : {})
      }
    }
  }

  return {
    request: instance,
    get: <T = unknown>(url: string, requestConfig?: object) => 
      instance.get(url, addAuthHeaders(requestConfig || {})) as Promise<ApiResponse<T>>,
    post: <T = unknown>(url: string, data?: unknown, requestConfig?: object) => 
      instance.post(url, data, addAuthHeaders(requestConfig || {})) as Promise<ApiResponse<T>>,
    put: <T = unknown>(url: string, data?: unknown, requestConfig?: object) => 
      instance.put(url, data, addAuthHeaders(requestConfig || {})) as Promise<ApiResponse<T>>,
    patch: <T = unknown>(url: string, data?: unknown, requestConfig?: object) => 
      instance.patch(url, data, addAuthHeaders(requestConfig || {})) as Promise<ApiResponse<T>>,
    delete: <T = unknown>(url: string, requestConfig?: object) => 
      instance.delete(url, addAuthHeaders(requestConfig || {})) as Promise<ApiResponse<T>>,
  }
}

export default createRequest
