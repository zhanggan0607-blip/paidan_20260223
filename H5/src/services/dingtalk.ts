/**
 * 钉钉服务
 * 提供钉钉免登认证功能
 */
import request from '../api/request'
import { API_ENDPOINTS } from '../api/endpoints'
import type { ApiResponse } from '../types'

export interface DingTalkLoginRequest {
  auth_code: string
  device_type?: string
}

export interface DingTalkLoginResponse {
  access_token: string
  token_type: string
  user: {
    id: number
    name: string
    role: string
    department: string
    phone: string
    avatar?: string
  }
}

export interface DingTalkSyncResponse {
  total: number
  added: number
  updated: number
  skipped: number
}

export const dingtalkService = {
  /**
   * 钉钉免登
   */
  async login(authCode: string): Promise<ApiResponse<DingTalkLoginResponse>> {
    return request.post(API_ENDPOINTS.DINGTALK.LOGIN, {
      auth_code: authCode,
      device_type: 'h5',
    })
  },

  /**
   * 同步钉钉通讯录
   */
  async syncUsers(): Promise<ApiResponse<DingTalkSyncResponse>> {
    return request.post(API_ENDPOINTS.DINGTALK.SYNC_USERS)
  },

  /**
   * 检查钉钉配置
   */
  async checkConfig(): Promise<ApiResponse<{ configured: boolean; has_token?: boolean }>> {
    return request.get(API_ENDPOINTS.DINGTALK.CHECK_CONFIG)
  },

  /**
   * 判断是否在钉钉环境中
   */
  isInDingTalk(): boolean {
    const ua = navigator.userAgent.toLowerCase()
    return ua.indexOf('dingtalk') > -1
  },

  /**
   * 获取钉钉免登授权码
   * 需要在钉钉环境中调用
   */
  async getAuthCode(): Promise<string> {
    return new Promise((resolve, reject) => {
      if (!this.isInDingTalk()) {
        reject(new Error('当前不在钉钉环境中'))
        return
      }

      const script = document.createElement('script')
      script.src = 'https://g.alicdn.com/dingding/dingtalk-jsapi/2.10.3/dingtalk.open.js'
      script.onload = () => {
        if ((window as any).dd) {
          const dd = (window as any).dd
          dd.runtime.permission.requestAuthCode({
            clientId: import.meta.env.VITE_DINGTALK_CLIENT_ID || '',
            onSuccess: (result: { code: string }) => {
              resolve(result.code)
            },
            onFail: (err: Error) => {
              reject(new Error(`获取钉钉授权码失败: ${err.message || JSON.stringify(err)}`))
            },
          })
        } else {
          reject(new Error('钉钉JSAPI加载失败'))
        }
      }
      script.onerror = () => {
        reject(new Error('钉钉JSAPI加载失败'))
      }
      document.head.appendChild(script)
    })
  },
}

export default dingtalkService
