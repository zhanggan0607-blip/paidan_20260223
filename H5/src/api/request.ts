import { createRequest, type RequestInstance, createSortInterceptor } from '@sstcp/shared'
import { userStore } from '../stores/userStore'

function getBaseURL(): string {
  if (import.meta.env.PROD) {
    return '/api/v1'
  }
  return import.meta.env.VITE_API_BASE_URL || '/api/v1'
}

const LOGIN_PATH = '/login'

function isLoginPage(): boolean {
  const pathname = window.location.pathname
  return pathname === LOGIN_PATH || pathname === LOGIN_PATH + '/'
}

const requestInstance: RequestInstance = createRequest({
  baseURL: getBaseURL(),
  timeout: 60000,
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
})

// 注册全局排序拦截器
createSortInterceptor(requestInstance.request)

export const request = requestInstance

export default requestInstance
