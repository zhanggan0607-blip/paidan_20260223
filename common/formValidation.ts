import { ref, computed, watch, type Ref, type ComputedRef } from 'vue'

export interface ValidationRule {
  required?: boolean
  message?: string
  minLength?: number
  maxLength?: number
  min?: number
  max?: number
  pattern?: RegExp
  validator?: (value: any) => boolean | string
  trigger?: 'blur' | 'change' | 'input'
}

export interface FieldValidation {
  value: Ref<any>
  error: Ref<string>
  touched: Ref<boolean>
  dirty: Ref<boolean>
  valid: ComputedRef<boolean>
  rules: ValidationRule[]
  validate: () => boolean
  reset: () => void
}

export function useFieldValidation(
  initialValue: any = '',
  rules: ValidationRule[] = []
): FieldValidation {
  const value = ref(initialValue)
  const error = ref('')
  const touched = ref(false)
  const dirty = ref(false)

  const valid = computed(() => !error.value && touched.value)

  const validate = (): boolean => {
    error.value = ''

    for (const rule of rules) {
      if (rule.required && !value.value) {
        error.value = rule.message || '此字段为必填项'
        return false
      }

      if (value.value) {
        if (typeof value.value === 'string') {
          if (rule.minLength && value.value.length < rule.minLength) {
            error.value = rule.message || `长度不能少于${rule.minLength}个字符`
            return false
          }

          if (rule.maxLength && value.value.length > rule.maxLength) {
            error.value = rule.message || `长度不能超过${rule.maxLength}个字符`
            return false
          }

          if (rule.pattern && !rule.pattern.test(value.value)) {
            error.value = rule.message || '格式不正确'
            return false
          }
        }

        if (typeof value.value === 'number') {
          if (rule.min !== undefined && value.value < rule.min) {
            error.value = rule.message || `不能小于${rule.min}`
            return false
          }

          if (rule.max !== undefined && value.value > rule.max) {
            error.value = rule.message || `不能大于${rule.max}`
            return false
          }
        }

        if (rule.validator) {
          const result = rule.validator(value.value)
          if (result !== true) {
            error.value = typeof result === 'string' ? result : rule.message || '验证失败'
            return false
          }
        }
      }
    }

    return true
  }

  const reset = () => {
    value.value = initialValue
    error.value = ''
    touched.value = false
    dirty.value = false
  }

  watch(value, () => {
    dirty.value = true
    if (touched.value) {
      validate()
    }
  })

  return {
    value,
    error,
    touched,
    dirty,
    valid,
    rules,
    validate,
    reset
  }
}

export interface FormValidation {
  fields: Record<string, FieldValidation>
  valid: ComputedRef<boolean>
  dirty: ComputedRef<boolean>
  touched: ComputedRef<boolean>
  validate: () => boolean
  reset: () => void
  getValues: () => Record<string, any>
  setValues: (values: Record<string, any>) => void
  getErrors: () => Record<string, string>
}

export function useFormValidation(
  fieldConfigs: Record<string, { initialValue?: any; rules?: ValidationRule[] }>
): FormValidation {
  const fields: Record<string, FieldValidation> = {}

  for (const [fieldName, config] of Object.entries(fieldConfigs)) {
    fields[fieldName] = useFieldValidation(config.initialValue, config.rules || [])
  }

  const valid = computed(() => 
    Object.values(fields).every(field => !field.error.value)
  )

  const dirty = computed(() =>
    Object.values(fields).some(field => field.dirty.value)
  )

  const touched = computed(() =>
    Object.values(fields).every(field => field.touched.value)
  )

  const validate = (): boolean => {
    let allValid = true
    for (const field of Object.values(fields)) {
      field.touched.value = true
      if (!field.validate()) {
        allValid = false
      }
    }
    return allValid
  }

  const reset = () => {
    for (const field of Object.values(fields)) {
      field.reset()
    }
  }

  const getValues = (): Record<string, any> => {
    const values: Record<string, any> = {}
    for (const [fieldName, field] of Object.entries(fields)) {
      values[fieldName] = field.value.value
    }
    return values
  }

  const setValues = (values: Record<string, any>) => {
    for (const [fieldName, value] of Object.entries(values)) {
      if (fields[fieldName]) {
        fields[fieldName].value.value = value
      }
    }
  }

  const getErrors = (): Record<string, string> => {
    const errors: Record<string, string> = {}
    for (const [fieldName, field] of Object.entries(fields)) {
      if (field.error.value) {
        errors[fieldName] = field.error.value
      }
    }
    return errors
  }

  return {
    fields,
    valid,
    dirty,
    touched,
    validate,
    reset,
    getValues,
    setValues,
    getErrors
  }
}

export const validators = {
  required: (message = '此字段为必填项'): ValidationRule => ({
    required: true,
    message
  }),

  email: (message = '请输入有效的邮箱地址'): ValidationRule => ({
    pattern: /^[^\s@]+@[^\s@]+\.[^\s@]+$/,
    message
  }),

  phone: (message = '请输入有效的手机号码'): ValidationRule => ({
    pattern: /^1[3-9]\d{9}$/,
    message
  }),

  idCard: (message = '请输入有效的身份证号码'): ValidationRule => ({
    pattern: /(^\d{15}$)|(^\d{18}$)|(^\d{17}(\d|X|x)$)/,
    message
  }),

  minLength: (length: number, message?: string): ValidationRule => ({
    minLength: length,
    message: message || `长度不能少于${length}个字符`
  }),

  maxLength: (length: number, message?: string): ValidationRule => ({
    maxLength: length,
    message: message || `长度不能超过${length}个字符`
  }),

  min: (value: number, message?: string): ValidationRule => ({
    min: value,
    message: message || `不能小于${value}`
  }),

  max: (value: number, message?: string): ValidationRule => ({
    max: value,
    message: message || `不能大于${value}`
  }),

  pattern: (regex: RegExp, message = '格式不正确'): ValidationRule => ({
    pattern: regex,
    message
  }),

  custom: (validator: (value: any) => boolean | string, message?: string): ValidationRule => ({
    validator,
    message
  })
}