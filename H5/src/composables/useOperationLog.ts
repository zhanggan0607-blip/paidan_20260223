/**
 * 操作日志组合式函数
 * 统一管理工单操作日志记录
 */
import api from '../utils/api'
import { userStore } from '../stores/userStore'

interface OperationLogParams {
  workOrderType: 'periodic_inspection' | 'temporary_repair' | 'spot_work'
  workOrderId: number
  workOrderNo: string
}

/**
 * 操作日志组合式函数
 * @param params 基础参数
 * @returns 操作日志相关的方法
 */
export const useOperationLog = (params: OperationLogParams) => {
  const { workOrderType, workOrderId, workOrderNo } = params

  /**
   * 添加操作日志
   * @param operationTypeCode 操作类型编码
   * @param operationRemark 操作备注
   * @returns 是否成功
   */
  const addLog = async (operationTypeCode: string, operationRemark?: string): Promise<boolean> => {
    const user = userStore.getUser()
    if (!user) return false

    try {
      await api.post('/work-order-operation-log', {
        work_order_type: workOrderType,
        work_order_id: workOrderId,
        work_order_no: workOrderNo,
        operator_name: user.name,
        operator_id: user.id,
        operation_type_code: operationTypeCode,
        operation_remark: operationRemark
      })
      return true
    } catch (error) {
      console.error('Failed to add operation log:', error)
      return false
    }
  }

  /**
   * 记录提交操作
   */
  const logSubmit = async (): Promise<boolean> => {
    return addLog('submit', '员工提交工单')
  }

  /**
   * 记录保存操作
   */
  const logSave = async (): Promise<boolean> => {
    return addLog('save', '员工保存工单')
  }

  /**
   * 记录审批通过操作
   */
  const logApprove = async (): Promise<boolean> => {
    return addLog('approve', '部门经理审批通过')
  }

  /**
   * 记录退回操作
   */
  const logReject = async (): Promise<boolean> => {
    return addLog('reject', '部门经理退回工单')
  }

  /**
   * 记录删除操作
   */
  const logDelete = async (): Promise<boolean> => {
    return addLog('delete', `删除工单 ${workOrderNo}`)
  }

  return {
    addLog,
    logSubmit,
    logSave,
    logApprove,
    logReject,
    logDelete
  }
}
