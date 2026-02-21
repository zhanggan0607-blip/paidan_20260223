import axios from 'axios'
import type { ApiResponse } from '../types'
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
    const response = await axios.post('/api/v1/auth/refresh', {}, {
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

const api = axios.create({
  baseURL: '/api/v1',
  timeout: 60000,
})

api.interceptors.request.use(
  (config) => {
    const token = userStore.getToken()
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    const user = userStore.getUser()
    if (user) {
      config.headers['X-User-Name'] = encodeURIComponent(user.name || '')
      config.headers['X-User-Role'] = encodeURIComponent(user.role || '')
    }
    return config
  },
  (error) => Promise.reject(error)
)

api.interceptors.response.use(
  (response): any => {
    return response.data as ApiResponse
  },
  async (error) => {
    const originalRequest = error.config
    
    if (error.response?.status === 401 && !originalRequest._retry) {
      if (isRefreshing) {
        return new Promise((resolve) => {
          subscribeTokenRefresh((token: string) => {
            originalRequest.headers.Authorization = `Bearer ${token}`
            resolve(api(originalRequest))
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
        return api(originalRequest)
      }
      
      userStore.clearUser()
      window.location.href = '/login'
      
      return Promise.reject({
        status: 401,
        message: '登录已过期，请重新登录',
        data: null
      })
    }
    
    const errorMessage = error.response?.data?.detail || error.response?.data?.message || error.message
    return Promise.reject({
      status: error.response?.status,
      message: errorMessage,
      data: error.response?.data
    })
  }
)

export default api
