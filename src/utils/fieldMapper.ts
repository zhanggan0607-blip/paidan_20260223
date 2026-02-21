/**
 * 字段命名风格转换工具
 * 统一前端使用camelCase，与后端API交互时自动转换
 */

/**
 * 将snake_case字符串转换为camelCase
 */
export function toCamelCase(str: string): string {
  return str.replace(/_([a-z])/g, (_, letter) => letter.toUpperCase())
}

/**
 * 将camelCase字符串转换为snake_case
 */
export function toSnakeCase(str: string): string {
  return str.replace(/[A-Z]/g, letter => `_${letter.toLowerCase()}`)
}

/**
 * 将对象的key从snake_case转换为camelCase
 */
export function keysToCamelCase<T>(obj: T): T {
  if (obj === null || obj === undefined) {
    return obj
  }
  
  if (Array.isArray(obj)) {
    return obj.map(item => keysToCamelCase(item)) as T
  }
  
  if (typeof obj !== 'object') {
    return obj
  }
  
  const result: Record<string, unknown> = {}
  for (const [key, value] of Object.entries(obj)) {
    const camelKey = toCamelCase(key)
    result[camelKey] = keysToCamelCase(value)
  }
  
  return result as T
}

/**
 * 将对象的key从camelCase转换为snake_case
 */
export function keysToSnakeCase<T>(obj: T): T {
  if (obj === null || obj === undefined) {
    return obj
  }
  
  if (Array.isArray(obj)) {
    return obj.map(item => keysToSnakeCase(item)) as T
  }
  
  if (typeof obj !== 'object') {
    return obj
  }
  
  const result: Record<string, unknown> = {}
  for (const [key, value] of Object.entries(obj)) {
    const snakeKey = toSnakeCase(key)
    result[snakeKey] = keysToSnakeCase(value)
  }
  
  return result as T
}

/**
 * API响应数据转换：后端snake_case -> 前端camelCase
 */
export function transformApiResponse<T>(data: T): T {
  return keysToCamelCase(data)
}

/**
 * API请求数据转换：前端camelCase -> 后端snake_case
 */
export function transformApiRequest<T>(data: T): T {
  return keysToSnakeCase(data)
}
