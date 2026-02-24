/**
 * 审批操作组合式函数
 * 统一管理工单审批通过和退回逻辑
 */
import { showLoadingToast, closeToast, showSuccessToast, showFailToast, showConfirmDialog } from 'vant'
import api from '../utils/api'
import type { ApiResponse } from '../types'

interface ApprovalOptions {
  workOrderType: 'periodic_inspection' | 'temporary_repair' | 'spot_work'
  onSuccess?: () => void
}

/**
 * 审批操作组合式函数
 * @param options 配置选项
 * @returns 审批相关的方法
 */
export const useApproval = (options: ApprovalOptions) => {
  const { workOrderType, onSuccess } = options

  /**
   * 获取API端点
   * @param workOrderId 工单ID
   * @returns API端点路径
   */
  const getEndpoint = (workOrderId: number): string => {
    const endpoints: Record<string, string> = {
      'periodic_inspection': `/periodic-inspection/${workOrderId}`,
      'temporary_repair': `/temporary-repair/${workOrderId}`,
      'spot_work': `/spot-work/${workOrderId}`
    }
    return endpoints[workOrderType] || ''
  }

  /**
   * 审批通过
   * @param workOrderId 工单ID
   * @param operationLogCallback 操作日志回调函数
   */
  const approvePass = async (workOrderId: number, operationLogCallback?: () => Promise<void>) => {
    try {
      await showConfirmDialog({
        title: '审批确认',
        message: '确认审批通过该工单吗？'
      })
      
      showLoadingToast({ message: '处理中...', forbidClick: true })
      
      const response = await api.patch<unknown, ApiResponse<any>>(getEndpoint(workOrderId), {
        status: '已确认'
      })
      
      if (response.code === 200) {
        if (operationLogCallback) {
          await operationLogCallback()
        }
        showSuccessToast('审批通过')
        if (onSuccess) {
          onSuccess()
        }
        return true
      }
      return false
    } catch (error) {
      if (error !== 'cancel') {
        console.error('Failed to approve:', error)
        showFailToast('审批失败')
      }
      return false
    } finally {
      closeToast()
    }
  }

  /**
   * 审批退回
   * @param workOrderId 工单ID
   * @param operationLogCallback 操作日志回调函数
   */
  const approveReject = async (workOrderId: number, operationLogCallback?: () => Promise<void>) => {
    try {
      await showConfirmDialog({
        title: '退回确认',
        message: '确认退回该工单吗？退回后员工需重新填写。',
        confirmButtonText: '确认退回',
        confirmButtonColor: '#ee0a24'
      })
      
      showLoadingToast({ message: '处理中...', forbidClick: true })
      
      const response = await api.patch<unknown, ApiResponse<any>>(getEndpoint(workOrderId), {
        status: '已退回'
      })
      
      if (response.code === 200) {
        if (operationLogCallback) {
          await operationLogCallback()
        }
        showSuccessToast('已退回')
        if (onSuccess) {
          onSuccess()
        }
        return true
      }
      return false
    } catch (error) {
      if (error !== 'cancel') {
        console.error('Failed to reject:', error)
        showFailToast('退回失败')
      }
      return false
    } finally {
      closeToast()
    }
  }

  return {
    approvePass,
    approveReject
  }
}
