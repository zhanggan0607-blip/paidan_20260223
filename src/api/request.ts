/**
 * PC端HTTP请求封装
 * 基于 @sstcp/shared 的 createRequest 工厂函数
 *
 * 功能：
 * - 自动注入JWT Token到Authorization头
 * - 401响应自动刷新Token（带并发请求排队机制）
 * - 刷新失败自动清除用户状态并跳转登录页
 * - 主动Token刷新：请求前检查token是否即将过期，提前刷新避免401
 *
 * FIXME: X-User-Name/X-User-Role 请求头后端已不再使用，应移除以减少带宽
 */
import { createRequest, type RequestInstance, createSortInterceptor } from '@sstcp/shared'
import { API_CONFIG } from '../config/constants'
import { userStore } from '../stores/userStore'

const LOGIN_PATH = '/login'

function isLoginPage(): boolean {
  const pathname = window.location.pathname
  return pathname === LOGIN_PATH || pathname === LOGIN_PATH + '/'
}

const requestInstance: RequestInstance = createRequest({
  baseURL: API_CONFIG.BASE_URL,
  timeout: API_CONFIG.TIMEOUT,
  getToken: () => userStore.getToken(),
  getRefreshToken: () => userStore.getRefreshToken(),
  getUser: () => userStore.getUser(),
  setToken: (token: string) => userStore.setToken(token),
  setRefreshToken: (token: string) => userStore.setRefreshToken(token),
  onUnauthorized: () => {
    userStore.clearUser()
    if (!isLoginPage()) {
      window.location.href = LOGIN_PATH
    }
  },
  refreshEndpoint: '/auth/refresh',
  enableLogger: import.meta.env.DEV,
  onRequestInterceptor: (config) => {
    const user = userStore.getUser()
    if (user) {
      if (!config.headers) {
        config.headers = {} as any
      }
      config.headers['X-User-Name'] = encodeURIComponent(user.name || '')
      config.headers['X-User-Role'] = encodeURIComponent(user.role || '')
    }
    return config
  },
})

// 注册全局排序拦截器
createSortInterceptor(requestInstance.request)

export const request = requestInstance

export default requestInstance
