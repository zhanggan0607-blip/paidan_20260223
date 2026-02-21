import axios, { AxiosInstance, AxiosResponse, InternalAxiosRequestConfig } from 'axios'
import { API_CONFIG } from '../config/constants'
import { userStore } from '../stores/userStore'

let isRefreshing = false
let refreshSubscribers: ((token: string) => void)[] = []

function subscribeTokenRefresh(callback: (token: string) => void) {
  refreshSubscribers.push(callback)
}

function onTokenRefreshed(token: string) {
  refreshSubscribers.forEach(callback => callback(token))
  refreshSubscribers = []
}

async function refreshToken(): Promise<string | null> {
  try {
    const response = await axios.post(`${API_CONFIG.BASE_URL}/auth/refresh`, {}, {
      headers: {
        'Authorization': `Bearer ${userStore.getToken()}`
      }
    })
    
    if (response.data?.code === 200 && response.data?.data?.access_token) {
      const newToken = response.data.data.access_token
      userStore.setToken(newToken)
      return newToken
    }
    return null
  } catch {
    return null
  }
}

const apiClient: AxiosInstance = axios.create({
  baseURL: API_CONFIG.BASE_URL,
  timeout: API_CONFIG.TIMEOUT,
  headers: {
    'Content-Type': 'application/json',
  },
})

apiClient.interceptors.request.use(
  (config: InternalAxiosRequestConfig) => {
    const token = userStore.getToken()
    if (token) {
      config.headers = config.headers || {}
      config.headers['Authorization'] = `Bearer ${token}`
    }
    
    const currentUser = userStore.getUser()
    if (currentUser) {
      config.headers = config.headers || {}
      config.headers['X-User-Name'] = encodeURIComponent(currentUser.name)
      config.headers['X-User-Role'] = encodeURIComponent(currentUser.role)
    }
    
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

apiClient.interceptors.response.use(
  (response: AxiosResponse) => {
    return response.data
  },
  async (error) => {
    const originalRequest = error.config
    
    if (error.response) {
      const { status, data } = error.response
      
      const errorMessage = data?.detail || data?.message || error.message
      
      if (status === 401 && !originalRequest._retry) {
        if (isRefreshing) {
          return new Promise((resolve) => {
            subscribeTokenRefresh((token: string) => {
              originalRequest.headers.Authorization = `Bearer ${token}`
              resolve(apiClient(originalRequest))
            })
          })
        }
        
        originalRequest._retry = true
        isRefreshing = true
        
        const newToken = await refreshToken()
        isRefreshing = false
        
        if (newToken) {
          onTokenRefreshed(newToken)
          originalRequest.headers.Authorization = `Bearer ${newToken}`
          return apiClient(originalRequest)
        }
        
        userStore.clearUser()
        window.location.href = '/login'
        
        return Promise.reject({
          status: 401,
          message: '登录已过期，请重新登录',
          errors: [],
          data: null
        })
      }
      
      switch (status) {
        case 400:
          console.error('请求错误', errorMessage)
          break
        case 403:
          console.error('没有权限访问此资源')
          break
        case 404:
          console.error('请求的资源不存在')
          break
        case 422:
          console.error('参数验证失败', data?.detail || data?.data?.errors)
          break
        case 500:
          console.error('服务器内部错误', errorMessage)
          break
        default:
          if (status !== 401) {
            console.error('请求失败', errorMessage)
          }
      }
      
      return Promise.reject({
        status,
        message: errorMessage,
        errors: data?.data?.errors || [],
        data: data?.data || null
      })
    } else if (error.request) {
      console.error('网络错误，请检查网络连接')
      return Promise.reject({
        status: 0,
        message: '网络错误，请检查网络连接',
        errors: [],
        data: null
      })
    } else {
      console.error('请求配置错误', error.message)
      return Promise.reject({
        status: -1,
        message: error.message,
        errors: [],
        data: null
      })
    }
  }
)

export default apiClient
