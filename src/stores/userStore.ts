import { defineStore } from 'pinia'
import { ref, computed, watch } from 'vue'
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

function decodeJwtPayload(token: string): { exp?: number; [key: string]: unknown } | null {
  try {
    const parts = token.split('.')
    if (parts.length !== 3) return null
    const base64 = parts[1].replace(/-/g, '+').replace(/_/g, '/')
    const jsonStr = decodeURIComponent(
      atob(base64)
        .split('')
        .map((c) => '%' + ('00' + c.charCodeAt(0).toString(16)).slice(-2))
        .join('')
    )
    return JSON.parse(jsonStr)
  } catch {
    return null
  }
}

function isTokenExpired(token: string): boolean {
  const payload = decodeJwtPayload(token)
  if (!payload || !payload.exp) return true
  return Date.now() >= payload.exp * 1000
}

async function fetchCurrentUser(tokenValue: string): Promise<User | null> {
  if (isTokenExpired(tokenValue)) return null
  try {
    const response = await fetch('/api/v1/auth/me', {
      headers: { Authorization: `Bearer ${tokenValue}` },
    })
    if (!response.ok) return null
    const result = await response.json()
    if (result.code === 200 && result.data) {
      return {
        id: result.data.id,
        name: result.data.name,
        role: result.data.role,
        department: result.data.department,
        phone: result.data.phone,
        must_change_password: result.data.must_change_password,
      } as User
    }
    return null
  } catch (_e) {
    return null
  }
}

export const useUserStore = defineStore('user', () => {
  const storedToken = localStorage.getItem(TOKEN_KEY)
  const storedUser = localStorage.getItem(USER_KEY)
  const storedRefreshToken = localStorage.getItem(REFRESH_TOKEN_KEY)

  const currentUser = ref<User | null>(storedUser ? (() => {
    try { return JSON.parse(storedUser) } catch (_e) { return null }
  })() : null)
  const token = ref<string | null>(storedToken)
  const refreshToken = ref<string | null>(storedRefreshToken)

  watch(currentUser, (newUser) => {
    if (newUser) {
      localStorage.setItem(USER_KEY, JSON.stringify(newUser))
    } else {
      localStorage.removeItem(USER_KEY)
    }
    window.dispatchEvent(new CustomEvent('user-changed', { detail: newUser }))
  }, { deep: true, flush: 'sync' })

  watch(token, (newToken) => {
    if (newToken) {
      localStorage.setItem(TOKEN_KEY, newToken)
    } else {
      localStorage.removeItem(TOKEN_KEY)
    }
  }, { flush: 'sync' })

  watch(refreshToken, (newRefreshToken) => {
    if (newRefreshToken) {
      localStorage.setItem(REFRESH_TOKEN_KEY, newRefreshToken)
    } else {
      localStorage.removeItem(REFRESH_TOKEN_KEY)
    }
  }, { flush: 'sync' })

  window.addEventListener('storage', (e: StorageEvent) => {
    if (e.key === TOKEN_KEY) {
      token.value = e.newValue
    }
    if (e.key === USER_KEY) {
      if (e.newValue) {
        try {
          currentUser.value = JSON.parse(e.newValue)
        } catch (_e) {
          currentUser.value = null
        }
      } else {
        currentUser.value = null
      }
    }
    if (e.key === REFRESH_TOKEN_KEY) {
      refreshToken.value = e.newValue
    }
  })

  const isLoggedIn = computed(() => !!token.value && !!currentUser.value)

  function getUser(): User | null {
    return currentUser.value
  }

  function getToken(): string | null {
    return token.value
  }

  function getRefreshToken(): string | null {
    return refreshToken.value
  }

  function setUser(user: User) {
    currentUser.value = user
  }

  function setToken(newToken: string) {
    token.value = newToken
  }

  function setRefreshToken(newRefreshToken: string) {
    refreshToken.value = newRefreshToken
  }

  function clearUser() {
    currentUser.value = null
    token.value = null
    refreshToken.value = null
  }

  async function validateToken(): Promise<boolean> {
    if (!token.value) {
      clearUser()
      return false
    }
    const user = await fetchCurrentUser(token.value)
    if (user) {
      currentUser.value = user
      return true
    }
    clearUser()
    return false
  }

  function isAdmin(): boolean {
    return isAdminRole(currentUser.value?.role)
  }

  function isDepartmentManager(): boolean {
    return currentUser.value?.role === RoleCode.DEPARTMENT_MANAGER
  }

  function canDeleteWorkOrder(): boolean {
    return canDeleteWorkOrderPermission(currentUser.value?.role)
  }

  function canShowMenuAction(menuId: string): boolean {
    return canShowMenu(menuId, currentUser.value?.role)
  }

  function isManager(): boolean {
    return isManagerRole(currentUser.value?.role)
  }

  function isMaterialManager(): boolean {
    const role = currentUser.value?.role
    return role === RoleCode.ADMIN || role === RoleCode.DEPARTMENT_MANAGER || role === RoleCode.MATERIAL_MANAGER
  }

  return {
    currentUser,
    token,
    refreshToken,
    isLoggedIn,
    getUser,
    getToken,
    getRefreshToken,
    setUser,
    setToken,
    setRefreshToken,
    clearUser,
    validateToken,
    isAdmin,
    isDepartmentManager,
    canDeleteWorkOrder,
    canShowMenu: canShowMenuAction,
    isManager,
    isMaterialManager,
  }
})
