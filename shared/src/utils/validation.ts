export interface ValidationRule {
  required?: boolean
  minLength?: number
  maxLength?: number
  pattern?: RegExp
  custom?: (value: any) => boolean | string
}

export interface ValidationResult {
  valid: boolean
  message?: string
}

export function validateRequired(value: any): ValidationResult {
  const isValid = value !== null && value !== undefined && value !== ''
  return {
    valid: isValid,
    message: isValid ? undefined : '此字段为必填项'
  }
}

export function validateLength(value: string, min?: number, max?: number): ValidationResult {
  if (!value) return { valid: true }

  if (min && value.length < min) {
    return {
      valid: false,
      message: `长度不能少于${min}个字符`
    }
  }

  if (max && value.length > max) {
    return {
      valid: false,
      message: `长度不能超过${max}个字符`
    }
  }

  return { valid: true }
}

export function validatePattern(value: string, pattern: RegExp, message: string): ValidationResult {
  if (!value) return { valid: true }

  const isValid = pattern.test(value)
  return {
    valid: isValid,
    message: isValid ? undefined : message
  }
}

export function validateEmail(email: string): ValidationResult {
  const emailPattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
  return validatePattern(email, emailPattern, '请输入有效的邮箱地址')
}

export function validatePhone(phone: string): ValidationResult {
  const phonePattern = /^1[3-9]\d{9}$/
  return validatePattern(phone, phonePattern, '请输入有效的手机号码')
}

export function validateIdCard(idCard: string): ValidationResult {
  const idCardPattern = /(^\d{15}$)|(^\d{18}$)|(^\d{17}(\d|X|x)$)/
  return validatePattern(idCard, idCardPattern, '请输入有效的身份证号码')
}

export function validateField(value: any, rules: ValidationRule): ValidationResult {
  if (rules.required) {
    const result = validateRequired(value)
    if (!result.valid) return result
  }

  if (typeof value === 'string') {
    if (rules.minLength || rules.maxLength) {
      const result = validateLength(value, rules.minLength, rules.maxLength)
      if (!result.valid) return result
    }

    if (rules.pattern) {
      const result = validatePattern(value, rules.pattern, '格式不正确')
      if (!result.valid) return result
    }
  }

  if (rules.custom) {
    const customResult = rules.custom(value)
    if (typeof customResult === 'boolean') {
      return { valid: customResult }
    } else if (typeof customResult === 'string') {
      return { valid: false, message: customResult }
    }
  }

  return { valid: true }
}

export function validateForm(data: Record<string, any>, rules: Record<string, ValidationRule>): Record<string, ValidationResult> {
  const results: Record<string, ValidationResult> = {}

  for (const field in rules) {
    results[field] = validateField(data[field], rules[field])
  }

  return results
}

export function isFormValid(results: Record<string, ValidationResult>): boolean {
  return Object.values(results).every(result => result.valid)
}