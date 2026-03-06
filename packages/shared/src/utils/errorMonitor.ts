/**
 * 前端错误监控工具
 * 提供统一的错误捕获、上报和处理功能
 */

interface ErrorReport {
  message: string
  stack?: string
  url: string
  line?: number
  column?: number
  timestamp: string
  userAgent: string
  userId?: string
  userRole?: string
  extra?: Record<string, unknown>
}

interface ErrorMonitorConfig {
  enabled: boolean
  endpoint?: string
  userId?: () => string | undefined
  userRole?: () => string | undefined
  onerror?: (error: ErrorReport) => void
  sampleRate?: number
}

let config: ErrorMonitorConfig = {
  enabled: true,
  sampleRate: 1.0,
}

function shouldSample(): boolean {
  return Math.random() < (config.sampleRate || 1.0)
}

function createErrorReport(
  message: string,
  stack?: string,
  url?: string,
  line?: number,
  column?: number,
  extra?: Record<string, unknown>
): ErrorReport {
  return {
    message,
    stack,
    url: url || window.location.href,
    line,
    column,
    timestamp: new Date().toISOString(),
    userAgent: navigator.userAgent,
    userId: config.userId?.(),
    userRole: config.userRole?.(),
    extra,
  }
}

async function reportError(report: ErrorReport): Promise<void> {
  if (!config.enabled || !shouldSample()) {
    return
  }

  config.onerror?.(report)

  if (config.endpoint) {
    try {
      await fetch(config.endpoint, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(report),
      })
    } catch {
      console.error('[ErrorMonitor] Failed to report error')
    }
  }
}

function handleGlobalError(event: ErrorEvent): boolean {
  const report = createErrorReport(
    event.message,
    event.error?.stack,
    event.filename,
    event.lineno,
    event.colno
  )
  reportError(report)
  return false
}

function handleUnhandledRejection(event: PromiseRejectionEvent): boolean {
  const error = event.reason
  const report = createErrorReport(
    error?.message || 'Unhandled Promise Rejection',
    error?.stack,
    undefined,
    undefined,
    undefined,
    { reason: error }
  )
  reportError(report)
  return false
}

function handleVueError(err: Error, vm: unknown, info: string): void {
  const report = createErrorReport(err.message, err.stack, undefined, undefined, undefined, {
    componentInfo: info,
    componentName: (vm as { $options?: { name?: string } })?.$options?.name,
  })
  reportError(report)
}

export function initErrorMonitor(userConfig: Partial<ErrorMonitorConfig> = {}): void {
  config = { ...config, ...userConfig }

  if (!config.enabled) {
    return
  }

  window.addEventListener('error', handleGlobalError)
  window.addEventListener('unhandledrejection', handleUnhandledRejection)

  console.log('[ErrorMonitor] Initialized')
}

export function destroyErrorMonitor(): void {
  window.removeEventListener('error', handleGlobalError)
  window.removeEventListener('unhandledrejection', handleUnhandledRejection)
}

export function captureError(error: Error | string, extra?: Record<string, unknown>): void {
  const message = typeof error === 'string' ? error : error.message
  const stack = typeof error === 'string' ? undefined : error.stack
  const report = createErrorReport(message, stack, undefined, undefined, undefined, extra)
  reportError(report)
}

export function captureMessage(
  message: string,
  level: 'info' | 'warning' | 'error' = 'info',
  extra?: Record<string, unknown>
): void {
  const report = createErrorReport(
    `[${level.toUpperCase()}] ${message}`,
    undefined,
    undefined,
    undefined,
    undefined,
    { level, ...extra }
  )
  reportError(report)
}

export const vueErrorHandler = {
  install(app: {
    config: { errorHandler: (err: Error, vm: unknown, info: string) => void }
  }): void {
    app.config.errorHandler = handleVueError
  },
}

export default {
  init: initErrorMonitor,
  destroy: destroyErrorMonitor,
  captureError,
  captureMessage,
  vueErrorHandler,
}
