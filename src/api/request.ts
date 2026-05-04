import { createRequest, type RequestInstance, createSortInterceptor } from '@sstcp/shared'
import { API_CONFIG } from '../config/constants'
import { useUserStore } from '../stores/userStore'
import router from '../router'

const LOGIN_PATH = '/login'

function isLoginPage(): boolean {
  return router.currentRoute.value.path === LOGIN_PATH || router.currentRoute.value.path === LOGIN_PATH + '/'
}

const requestInstance: RequestInstance = createRequest({
  baseURL: API_CONFIG.BASE_URL,
  timeout: API_CONFIG.TIMEOUT,
  getToken: () => useUserStore().token,
  getRefreshToken: () => useUserStore().refreshToken,
  getUser: () => useUserStore().currentUser,
  setToken: (token: string) => useUserStore().setToken(token),
  setRefreshToken: (token: string) => useUserStore().setRefreshToken(token),
  onUnauthorized: () => {
    useUserStore().clearUser()
    if (!isLoginPage()) {
      router.replace(LOGIN_PATH)
    }
  },
  refreshEndpoint: '/auth/refresh',
  enableLogger: import.meta.env.DEV,
})

createSortInterceptor(requestInstance.request)

export const request = requestInstance

export default requestInstance
