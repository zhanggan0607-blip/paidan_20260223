/**
 * 共享常量定义
 * 统一管理 PC 端和 H5 端的常量配置
 */

/**
 * API 配置
 */
export const API_CONFIG = {
  get BASE_URL(): string {
    if (typeof import.meta !== 'undefined' && import.meta.env?.PROD) {
      return '/api/v1'
    }
    if (typeof import.meta !== 'undefined' && import.meta.env?.VITE_API_BASE_URL) {
      return import.meta.env.VITE_API_BASE_URL
    }
    return '/api/v1'
  },
  TIMEOUT: 60000,
}
