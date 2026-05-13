import type { User } from '../types/api'

export function decodeJwtPayload(token: unknown): { exp?: number; [key: string]: unknown } | null {
  if (typeof token !== 'string' || !token) return null
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

export function isTokenExpired(token: unknown): boolean {
  if (typeof token !== 'string' || !token) return true
  const payload = decodeJwtPayload(token)
  if (!payload || !payload.exp) return true
  return Date.now() >= payload.exp * 1000
}

export function shouldRefreshToken(token: unknown, bufferMinutes: number = 5): boolean {
  if (typeof token !== 'string' || !token) return false
  const payload = decodeJwtPayload(token)
  if (!payload || !payload.exp) return false
  const expiresAt = payload.exp * 1000
  const now = Date.now()
  const buffer = bufferMinutes * 60 * 1000
  return now >= expiresAt - buffer
}

export async function fetchCurrentUser(tokenValue: string, basePath: string = '/api/v1'): Promise<User | null> {
  if (isTokenExpired(tokenValue)) return null
  try {
    const response = await fetch(`${basePath}/auth/me`, {
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
  } catch {
    return null
  }
}

export async function refreshAccessToken(
  refreshTokenValue: string,
  basePath: string = '/api/v1'
): Promise<{ accessToken: string; refreshToken: string } | null> {
  try {
    const response = await fetch(`${basePath}/auth/refresh`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ refresh_token: refreshTokenValue }),
    })
    if (!response.ok) return null
    const result = await response.json()
    if (result.code === 200 && result.data?.access_token) {
      return {
        accessToken: result.data.access_token,
        refreshToken: result.data.refresh_token || refreshTokenValue,
      }
    }
    return null
  } catch {
    return null
  }
}
