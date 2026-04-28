import { ref, readonly, computed } from 'vue'
import type { User } from '@sstcp/shared'
import {
  RoleCode,
  isManagerRole,
  isAdminRole,
  canShowMenu,
  canDeleteWorkOrder as canDeleteWorkOrderPermission,
} from '../config/permission'

const TOKEN_KEY = 'token'
const REFRESH_TOKEN_KEY = 'refresh_token'
const USER_KEY = 'user'

const currentUser = ref<User | null>(null)
const token = ref<string | null>(null)

const loadStoredUser = () => {
  const storedToken = localStorage.getItem(TOKEN_KEY)
  const storedUser = localStorage.getItem(USER_KEY)

  if (storedToken) {
    token.value = storedToken
  }

  if (storedUser) {
    try {
      currentUser.value = JSON.parse(storedUser)
    } catch {
      currentUser.value = null
    }
  }
}

loadStoredUser()

window.addEventListener('storage', (e: StorageEvent) => {
  if (e.key === TOKEN_KEY) {
    token.value = e.newValue
  }
  if (e.key === USER_KEY) {
    if (e.newValue) {
      try {
        currentUser.value = JSON.parse(e.newValue)
      } catch {
        currentUser.value = null
      }
    } else {
      currentUser.value = null
    }
  }
})

export const userStore = {
  readonlyCurrentUser: readonly(currentUser),
  readonlyToken: readonly(token),
  isLoggedIn: computed(() => !!token.value && !!currentUser.value),

  getUser: (): User | null => {
    return currentUser.value
  },

  getToken: (): string | null => {
    return token.value
  },

  setUser: (user: User) => {
    currentUser.value = user
    localStorage.setItem(USER_KEY, JSON.stringify(user))
    window.dispatchEvent(new CustomEvent('user-changed', { detail: user }))
  },

  setToken: (newToken: string) => {
    token.value = newToken
    localStorage.setItem(TOKEN_KEY, newToken)
  },

  getRefreshToken: (): string | null => {
    return localStorage.getItem(REFRESH_TOKEN_KEY)
  },

  setRefreshToken: (refreshToken: string) => {
    localStorage.setItem(REFRESH_TOKEN_KEY, refreshToken)
  },

  clearUser: () => {
    currentUser.value = null
    token.value = null
    localStorage.removeItem(TOKEN_KEY)
    localStorage.removeItem(REFRESH_TOKEN_KEY)
    localStorage.removeItem(USER_KEY)
    window.dispatchEvent(new CustomEvent('user-changed', { detail: null }))
  },

  isAdmin: (): boolean => {
    return isAdminRole(currentUser.value?.role)
  },

  isDepartmentManager: (): boolean => {
    return currentUser.value?.role === RoleCode.DEPARTMENT_MANAGER
  },

  canDeleteWorkOrder: (): boolean => {
    return canDeleteWorkOrderPermission(currentUser.value?.role)
  },

  canShowMenu: (menuId: string): boolean => {
    return canShowMenu(menuId, currentUser.value?.role)
  },

  isManager: (): boolean => {
    return isManagerRole(currentUser.value?.role)
  },

  isMaterialManager: (): boolean => {
    const role = currentUser.value?.role
    return role === RoleCode.ADMIN || role === RoleCode.DEPARTMENT_MANAGER || role === RoleCode.MATERIAL_MANAGER
  },
}
