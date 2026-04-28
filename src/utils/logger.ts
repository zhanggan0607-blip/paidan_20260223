/**
 * 日志工具类
 * 用于统一管理应用日志输出
 */

type LogLevel = 'debug' | 'info' | 'warn' | 'error'

class Logger {
  private isDev = import.meta.env.DEV
  private prefix = '[SSTCP]'

  private formatMessage(level: LogLevel, ..._args: unknown[]): string {
    const timestamp = new Date().toISOString()
    return `${this.prefix} [${timestamp}] [${level.toUpperCase()}]`
  }

  debug(...args: unknown[]) {
    if (this.isDev) {
      console.log(this.formatMessage('debug'), ...args)
    }
  }

  info(...args: unknown[]) {
    console.info(this.formatMessage('info'), ...args)
  }

  warn(...args: unknown[]) {
    console.warn(this.formatMessage('warn'), ...args)
  }

  error(...args: unknown[]) {
    console.error(this.formatMessage('error'), ...args)
  }

  group(label: string) {
    if (this.isDev) {
      console.group(label)
    }
  }

  groupEnd() {
    if (this.isDev) {
      console.groupEnd()
    }
  }

  time(label: string) {
    if (this.isDev) {
      console.time(label)
    }
  }

  timeEnd(label: string) {
    if (this.isDev) {
      console.timeEnd(label)
    }
  }
}

export const logger = new Logger()
