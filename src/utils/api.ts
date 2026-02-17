import axios, { AxiosInstance, AxiosRequestConfig, AxiosResponse, InternalAxiosRequestConfig } from 'axios'
import { API_CONFIG } from '../config/constants'
import { authService } from '../services/auth'

const apiClient: AxiosInstance = axios.create({
  baseURL: API_CONFIG.BASE_URL,
  timeout: API_CONFIG.TIMEOUT,
  headers: {
    'Content-Type': 'application/json',
  },
})

apiClient.interceptors.request.use(
  (config: InternalAxiosRequestConfig) => {
    const token = localStorage.getItem('token')
    if (token) {
      config.headers = config.headers || {}
      config.headers['Authorization'] = `Bearer ${token}`
    }
    
    const currentUser = authService.getCurrentUser()
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
  (error) => {
    if (error.response) {
      const { status, data } = error.response
      
      const errorMessage = data?.detail || data?.message || error.message
      
      switch (status) {
        case 400:
          console.error('请求错误', errorMessage)
          break
        case 401:
          console.error('未授权，请重新登录')
          localStorage.removeItem('token')
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
          console.error('请求失败', errorMessage)
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