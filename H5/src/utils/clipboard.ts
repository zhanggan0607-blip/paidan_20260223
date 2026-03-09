/**
 * 剪贴板工具函数
 * 统一管理复制相关功能
 */
import { showSuccessToast, showFailToast } from 'vant'

/**
 * 使用传统方式复制文本（备用方案）
 * @param text 要复制的文本
 */
const fallbackCopyText = (text: string): boolean => {
  const textArea = document.createElement('textarea')
  textArea.value = text
  
  textArea.style.position = 'fixed'
  textArea.style.left = '-9999px'
  textArea.style.top = '-9999px'
  
  document.body.appendChild(textArea)
  textArea.focus()
  textArea.select()
  
  try {
    const successful = document.execCommand('copy')
    document.body.removeChild(textArea)
    return successful
  } catch {
    document.body.removeChild(textArea)
    return false
  }
}

/**
 * 复制文本到剪贴板
 * @param text 要复制的文本
 * @param successMessage 成功提示消息
 * @param failMessage 失败提示消息
 */
export const copyToClipboard = async (
  text: string,
  successMessage: string = '已复制到剪贴板',
  failMessage: string = '复制失败'
): Promise<boolean> => {
  try {
    if (navigator.clipboard && window.isSecureContext) {
      await navigator.clipboard.writeText(text)
      showSuccessToast(successMessage)
      return true
    } else {
      const success = fallbackCopyText(text)
      if (success) {
        showSuccessToast(successMessage)
      } else {
        showFailToast(failMessage)
      }
      return success
    }
  } catch {
    const success = fallbackCopyText(text)
    if (success) {
      showSuccessToast(successMessage)
    } else {
      showFailToast(failMessage)
    }
    return success
  }
}

/**
 * 复制工单编号到剪贴板
 * @param orderId 工单编号
 */
export const copyOrderId = async (orderId: string): Promise<boolean> => {
  return copyToClipboard(orderId, '工单编号已复制', '复制失败')
}
