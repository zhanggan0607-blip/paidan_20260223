import axios, { AxiosInstance, AxiosRequestConfig, AxiosResponse, InternalAxiosRequestConfig } from 'axios'

const API_BASE_URL = 'http://localhost:8080/api/v1'

const apiClient: AxiosInstance = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
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
    
    console.log('📤 API请求:', {
      url: `${config.baseURL}${config.url}`,
      method: config.method?.toUpperCase(),
      headers: config.headers,
      data: config.data
    })
    
    return config
  },
  (error) => {
    console.error('❌ 请求拦截器错误:', error)
    return Promise.reject(error)
  }
)

apiClient.interceptors.response.use(
  (response: AxiosResponse) => {
    console.log('✅ API响应:', {
      status: response.status,
      statusText: response.statusText,
      data: response.data
    })
    return response.data
  },
  (error) => {
    console.error('❌ 响应拦截器错误:', {
      message: error.message,
      status: error.response?.status,
      data: error.response?.data
    })
    
    if (error.response) {
      const { status, data } = error.response
      
      switch (status) {
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
          console.error('参数验证失败', data?.data?.errors)
          break
        case 500:
          console.error('服务器内部错误', data?.message)
          break
        default:
          console.error('请求失败', data?.message || error.message)
      }
      
      return Promise.reject({
        status,
        message: data?.message || error.message,
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