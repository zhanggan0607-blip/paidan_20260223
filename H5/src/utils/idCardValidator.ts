/**
 * 身份证号码强认证工具
 * 包含格式验证、校验码验证、出生日期验证、性别验证
 */

// TODO: 身份证验证 - 考虑加入有效期验证
// FIXME: 目前只支持18位身份证，15位的需要兼容
// TODO: 考虑加入港澳台身份证验证

export interface IdCardValidationResult {
  valid: boolean
  message: string
  birthDate?: string
  gender?: string
}

const WEIGHTS = [7, 9, 10, 5, 8, 4, 2, 1, 6, 3, 7, 9, 10, 5, 8, 4, 2]
const CHECK_CODES = ['1', '0', 'X', '9', '8', '7', '6', '5', '4', '3', '2']

/**
 * 验证身份证号码
 * @param idCard 身份证号码
 * @returns 验证结果，包含是否有效、错误信息、出生日期、性别
 */
export function validateIdCard(idCard: string): IdCardValidationResult {
  if (!idCard) {
    return { valid: false, message: '身份证号码不能为空' }
  }

  const idCardUpper = idCard.toUpperCase().trim()

  if (idCardUpper.length !== 18) {
    return { valid: false, message: '身份证号码必须为18位' }
  }

  if (!/^\d{17}[\dX]$/.test(idCardUpper)) {
    return { valid: false, message: '身份证号码格式不正确，前17位必须为数字，最后一位可以是数字或X' }
  }

  let sum = 0
  for (let i = 0; i < 17; i++) {
    sum += parseInt(idCardUpper[i]!, 10) * WEIGHTS[i]!
  }
  const checkCode = CHECK_CODES[sum % 11]
  
  if (idCardUpper[17] !== checkCode) {
    return { valid: false, message: '身份证号码校验码错误，请检查是否输入正确' }
  }

  const year = parseInt(idCardUpper.substring(6, 10), 10)
  const month = parseInt(idCardUpper.substring(10, 12), 10)
  const day = parseInt(idCardUpper.substring(12, 14), 10)

  const birthDate = `${year}-${month.toString().padStart(2, '0')}-${day.toString().padStart(2, '0')}`

  if (month < 1 || month > 12) {
    return { valid: false, message: '身份证号码中月份无效，应为01-12' }
  }

  const daysInMonth = new Date(year, month, 0).getDate()
  if (day < 1 || day > daysInMonth) {
    return { valid: false, message: `身份证号码中日期无效，${year}年${month}月没有${day}日` }
  }

  const birthDateObj = new Date(year, month - 1, day)
  const today = new Date()
  today.setHours(0, 0, 0, 0)
  
  if (birthDateObj > today) {
    return { valid: false, message: '身份证号码中出生日期不能晚于今天' }
  }

  const minYear = 1900
  if (year < minYear) {
    return { valid: false, message: `身份证号码中出生年份不能早于${minYear}年` }
  }

  const genderCode = parseInt(idCardUpper.substring(16, 17), 10)
  const gender = genderCode % 2 === 1 ? '男' : '女'

  return {
    valid: true,
    message: '身份证号码验证通过',
    birthDate,
    gender
  }
}

/**
 * 从身份证号码提取出生日期
 * @param idCard 身份证号码
 * @returns 出生日期字符串 (YYYY-MM-DD格式)
 */
export function extractBirthDate(idCard: string): string | null {
  if (!idCard || idCard.length !== 18) {
    return null
  }
  
  const year = idCard.substring(6, 10)
  const month = idCard.substring(10, 12)
  const day = idCard.substring(12, 14)
  
  return `${year}-${month}-${day}`
}

/**
 * 从身份证号码提取性别
 * @param idCard 身份证号码
 * @returns 性别 ('男' 或 '女')
 */
export function extractGender(idCard: string): string | null {
  if (!idCard || idCard.length !== 18) {
    return null
  }
  
  const genderCode = parseInt(idCard.substring(16, 17), 10)
  return genderCode % 2 === 1 ? '男' : '女'
}

/**
 * 计算年龄
 * @param birthDate 出生日期字符串 (YYYY-MM-DD格式)
 * @returns 年龄
 */
export function calculateAge(birthDate: string): number | null {
  if (!birthDate) {
    return null
  }
  
  const birth = new Date(birthDate)
  const today = new Date()
  
  let age = today.getFullYear() - birth.getFullYear()
  const monthDiff = today.getMonth() - birth.getMonth()
  
  if (monthDiff < 0 || (monthDiff === 0 && today.getDate() < birth.getDate())) {
    age--
  }
  
  return age >= 0 ? age : null
}

/**
 * 获取身份证号码所属地区码（前6位）
 * @param idCard 身份证号码
 * @returns 地区码
 */
export function getRegionCode(idCard: string): string | null {
  if (!idCard || idCard.length < 6) {
    return null
  }
  return idCard.substring(0, 6)
}
