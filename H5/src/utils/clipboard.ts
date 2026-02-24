/**
 * 剪贴板工具函数
 * 统一管理复制相关功能
 */
import { showToast } from 'vant'

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
    await navigator.clipboard.writeText(text)
    showToast(successMessage)
    return true
  } catch {
    showToast(failMessage)
    return false
  }
}

/**
 * 复制工单编号到剪贴板
 * @param orderId 工单编号
 */
export const copyOrderId = async (orderId: string): Promise<boolean> => {
  return copyToClipboard(orderId, '工单编号已复制', '复制失败')
}
