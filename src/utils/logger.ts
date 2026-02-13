import type { ApiError } from '@/types/api'

const isDev = import.meta.env.DEV

export const logger = {
  log: (...args: unknown[]) => {
    if (isDev) {
      console.log(...args)
    }
  },
  error: (...args: unknown[]) => {
    console.error(...args)
  },
  warn: (...args: unknown[]) => {
    if (isDev) {
      console.warn(...args)
    }
  },
  info: (...args: unknown[]) => {
    if (isDev) {
      console.info(...args)
    }
  }
}

export class AppError extends Error {
  public status: number
  public code: string
  public data: unknown

  constructor(message: string, status: number = 500, code: string = 'UNKNOWN_ERROR', data: unknown = null) {
    super(message)
    this.name = 'AppError'
    this.status = status
    this.code = code
    this.data = data
  }
}

export const errorHandler = {
  handle(error: unknown, context?: string): AppError {
    if (error instanceof AppError) {
      logger.error(`[${context || 'App'}]`, error.message)
      return error
    }

    const apiError = error as ApiError
    
    if (apiError && typeof apiError.status === 'number') {
      const message = apiError.message || '请求失败'
      logger.error(`[${context || 'API'}]`, message, apiError)
      return new AppError(message, apiError.status, 'API_ERROR', apiError.data)
    }

    if (error instanceof Error) {
      logger.error(`[${context || 'Unknown'}]`, error.message)
      return new AppError(error.message, 500, 'RUNTIME_ERROR')
    }

    logger.error(`[${context || 'Unknown'}]`, '未知错误', error)
    return new AppError('未知错误', 500, 'UNKNOWN_ERROR')
  },

  getErrorMessage(error: unknown): string {
    if (error instanceof AppError) {
      return error.message
    }
    if (error instanceof Error) {
      return error.message
    }
    return '操作失败，请稍后重试'
  }
}

export const toastHelper = {
  success(message: string): { visible: boolean; message: string; type: 'success' } {
    return { visible: true, message, type: 'success' }
  },
  error(message: string): { visible: boolean; message: string; type: 'error' } {
    return { visible: true, message, type: 'error' }
  },
  warning(message: string): { visible: boolean; message: string; type: 'warning' } {
    return { visible: true, message, type: 'warning' }
  },
  info(message: string): { visible: boolean; message: string; type: 'info' } {
    return { visible: true, message, type: 'info' }
  }
}
