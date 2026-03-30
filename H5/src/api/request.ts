/**
 * Axios请求封装
 * 提供统一的HTTP请求客户端，包含请求/响应拦截器、Token刷新等功能
 */
import axios from 'axios'
import { userStore } from '../stores/userStore'

const LOGIN_PATH = '/login'

let isRefreshing = false
let refreshSubscribers: ((token: string) => void)[] = []

/**
 * 订阅Token刷新回调
 */
function subscribeTokenRefresh(callback: (token: string) => void) {
  refreshSubscribers.push(callback)
}

/**
 * Token刷新完成后通知所有订阅者
 */
function onTokenRefreshed(token: string) {
  refreshSubscribers.forEach((callback) => callback(token))
  refreshSubscribers = []
}

/**
 * 刷新访问令牌
 */
async function refreshToken(): Promise<string | null> {
  const refreshTokenValue = userStore.getRefreshToken()
  if (!refreshTokenValue) {
    return null
  }

  try {
    const response = await axios.post(
      '/api/v1/auth/refresh',
      {
        refresh_token: refreshTokenValue,
      },
      {
        headers: {
          'Content-Type': 'application/json',
        },
      }
    )

    if (response.data?.code === 200 && response.data?.data?.access_token) {
      const newToken = response.data.data.access_token
      const newRefreshToken = response.data.data.refresh_token
      userStore.setToken(newToken)
      if (newRefreshToken) {
        userStore.setRefreshToken(newRefreshToken)
      }
      return newToken
    }
    return null
  } catch {
    return null
  }
}

/**
 * Axios实例
 */
const request = axios.create({
  baseURL: '/api/v1',
  timeout: 60000,
})

/**
 * 请求拦截器
 * 自动添加Token和用户信息到请求头
 */
request.interceptors.request.use(
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
    if (config.method === 'get') {
      config.params = {
        ...config.params,
        _t: Date.now(),
      }
    }
    return config
  },
  (error) => Promise.reject(error)
)

/**
 * 响应拦截器
 * 处理响应数据和401错误自动刷新Token
 */
request.interceptors.response.use(
  (response) => {
    return response.data
  },
  async (error) => {
    const originalRequest = error.config

    if (error.response?.status === 401 && !originalRequest._retry) {
      const hasToken = !!userStore.getToken()

      if (!hasToken) {
        return Promise.reject({
          status: 401,
          message: '未登录',
          data: null,
        })
      }

      if (isRefreshing) {
        return new Promise((resolve) => {
          subscribeTokenRefresh((token: string) => {
            originalRequest.headers.Authorization = `Bearer ${token}`
            resolve(request(originalRequest))
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
        return request(originalRequest)
      }

      userStore.clearUser()
      if (window.location.pathname !== LOGIN_PATH) {
        window.location.href = LOGIN_PATH
      }

      return Promise.reject({
        status: 401,
        message: '登录已过期',
        data: null,
      })
    }

    const errorMessage =
      error.response?.data?.detail || error.response?.data?.message || error.message

    if (error.message === 'canceled' || error.name === 'CanceledError') {
      return Promise.reject({
        status: -1,
        message: '请求已取消',
        data: null,
        canceled: true,
      })
    }

    return Promise.reject({
      status: error.response?.status,
      message: errorMessage,
      data: error.response?.data,
    })
  }
)

export default request
