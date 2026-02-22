import CryptoJS from 'crypto-js'

const SECRET_KEY = import.meta.env.VITE_STORAGE_SECRET_KEY || 'sstcp-maintenance-system-2026'

class SecureStorage {
  private key: string

  constructor(secretKey: string) {
    this.key = secretKey
  }

  encrypt(data: string): string {
    return CryptoJS.AES.encrypt(data, this.key).toString()
  }

  decrypt(encryptedData: string): string | null {
    try {
      const bytes = CryptoJS.AES.decrypt(encryptedData, this.key)
      return bytes.toString(CryptoJS.enc.Utf8)
    } catch {
      return null
    }
  }

  setItem(key: string, value: string): void {
    const encrypted = this.encrypt(value)
    localStorage.setItem(key, encrypted)
  }

  getItem(key: string): string | null {
    const encrypted = localStorage.getItem(key)
    if (!encrypted) return null
    return this.decrypt(encrypted)
  }

  removeItem(key: string): void {
    localStorage.removeItem(key)
  }

  clear(): void {
    localStorage.clear()
  }
}

const secureStorage = new SecureStorage(SECRET_KEY)

class TokenManager {
  private static readonly TOKEN_KEY = 'auth_token'
  private static readonly REFRESH_TOKEN_KEY = 'refresh_token'
  private static readonly TOKEN_EXPIRY_KEY = 'token_expiry'

  saveToken(token: string, expiresIn: number = 3600): void {
    const expiresAt = Date.now() + expiresIn * 1000
    secureStorage.setItem(TokenManager.TOKEN_KEY, token)
    secureStorage.setItem(TokenManager.TOKEN_EXPIRY_KEY, expiresAt.toString())
  }

  saveRefreshToken(refreshToken: string): void {
    secureStorage.setItem(TokenManager.REFRESH_TOKEN_KEY, refreshToken)
  }

  getToken(): string | null {
    return secureStorage.getItem(TokenManager.TOKEN_KEY)
  }

  getRefreshToken(): string | null {
    return secureStorage.getItem(TokenManager.REFRESH_TOKEN_KEY)
  }

  isTokenExpired(): boolean {
    const expiry = secureStorage.getItem(TokenManager.TOKEN_EXPIRY_KEY)
    if (!expiry) return true
    return Date.now() > parseInt(expiry)
  }

  willExpireSoon(threshold: number = 300000): boolean {
    const expiry = secureStorage.getItem(TokenManager.TOKEN_EXPIRY_KEY)
    if (!expiry) return true
    const timeUntilExpiry = parseInt(expiry) - Date.now()
    return timeUntilExpiry < threshold
  }

  clearTokens(): void {
    secureStorage.removeItem(TokenManager.TOKEN_KEY)
    secureStorage.removeItem(TokenManager.REFRESH_TOKEN_KEY)
    secureStorage.removeItem(TokenManager.TOKEN_EXPIRY_KEY)
  }

  isAuthenticated(): boolean {
    const token = this.getToken()
    return !!token && !this.isTokenExpired()
  }
}

export const tokenManager = new TokenManager()
export default secureStorage