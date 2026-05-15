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
  refresh_token: string
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

      const corpId = import.meta.env.VITE_DINGTALK_CORP_ID || ''
      const clientId = import.meta.env.VITE_DINGTALK_CLIENT_ID || ''

      if (!corpId) {
        reject(new Error('钉钉企业ID未配置'))
        return
      }

      const tryRequestAuthCode = (dd: any) => {
        if (dd.requestAuthCode) {
          dd.requestAuthCode({
            corpId,
            clientId,
            onSuccess: (result: { code: string }) => {
              resolve(result.code)
            },
            onFail: (err: any) => {
              reject(new Error(`获取钉钉授权码失败: ${err.message || err.errorMessage || JSON.stringify(err)}`))
            },
          })
        } else if (dd.runtime && dd.runtime.permission && dd.runtime.permission.requestAuthCode) {
          dd.runtime.permission.requestAuthCode({
            corpId,
            onSuccess: (result: { code: string }) => {
              resolve(result.code)
            },
            onFail: (err: any) => {
              reject(new Error(`获取钉钉授权码失败: ${err.message || err.errorMessage || JSON.stringify(err)}`))
            },
          })
        } else {
          reject(new Error('钉钉JSAPI不支持免登接口'))
        }
      }

      if ((window as any).dd) {
        tryRequestAuthCode((window as any).dd)
        return
      }

      const timeout = setTimeout(() => {
        reject(new Error('钉钉JSAPI加载超时'))
      }, 10000)

      const script = document.createElement('script')
      script.src = 'https://g.alicdn.com/dingding/dingtalk-jsapi/3.0.12/dingtalk.open.js'
      script.onload = () => {
        clearTimeout(timeout)
        if ((window as any).dd) {
          tryRequestAuthCode((window as any).dd)
        } else {
          reject(new Error('钉钉JSAPI加载失败：dd对象不可用'))
        }
      }
      script.onerror = () => {
        clearTimeout(timeout)
        reject(new Error('钉钉JSAPI脚本加载失败，请检查网络连接'))
      }
      document.head.appendChild(script)
    })
  },
}

export default dingtalkService
