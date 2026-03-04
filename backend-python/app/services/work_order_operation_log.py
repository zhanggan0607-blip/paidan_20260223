"""
工单操作日志服务
提供工单操作日志业务逻辑处理
"""
from typing import List, Optional
from sqlalchemy.orm import Session
from app.models.work_order_operation_log import WorkOrderOperationLog
from app.repositories.work_order_operation_log import WorkOrderOperationLogRepository


class WorkOrderOperationLogService:
    """
    工单操作日志服务
    提供工单操作日志的增删查等业务逻辑
    """
    
    def __init__(self, db: Session):
        self.repository = WorkOrderOperationLogRepository(db)
    
    def add_log(
        self,
        work_order_type: str,
        work_order_id: int,
        work_order_no: str,
        operator_name: str,
        operation_type_code: str,
        operation_type_name: str,
        operator_id: Optional[int] = None,
        operation_remark: Optional[str] = None
    ) -> WorkOrderOperationLog:
        """
        添加操作日志
        
        Args:
            work_order_type: 工单类型 (periodic_inspection/temporary_repair/spot_work)
            work_order_id: 工单ID
            work_order_no: 工单编号
            operator_name: 操作人员姓名
            operation_type_code: 操作类型编码 (submit/approve/reject等)
            operation_type_name: 操作类型名称 (提交/审批通过/审批退回等)
            operator_id: 操作人员ID (可选)
            operation_remark: 操作备注 (可选)
        
        Returns:
            WorkOrderOperationLog: 创建的操作日志记录
        """
        return self.repository.create_log(
            work_order_type=work_order_type,
            work_order_id=work_order_id,
            work_order_no=work_order_no,
            operator_name=operator_name,
            operation_type_code=operation_type_code,
            operation_type_name=operation_type_name,
            operator_id=operator_id,
            operation_remark=operation_remark
        )
    
    def add_log_flush(
        self,
        work_order_type: str,
        work_order_id: int,
        work_order_no: str,
        operator_name: str,
        operation_type_code: str,
        operation_type_name: str,
        operator_id: Optional[int] = None,
        operation_remark: Optional[str] = None
    ) -> WorkOrderOperationLog:
        """
        添加操作日志（使用flush而非commit，用于事务中）
        
        Args:
            work_order_type: 工单类型
            work_order_id: 工单ID
            work_order_no: 工单编号
            operator_name: 操作人员姓名
            operation_type_code: 操作类型编码
            operation_type_name: 操作类型名称
            operator_id: 操作人员ID (可选)
            operation_remark: 操作备注 (可选)
        
        Returns:
            WorkOrderOperationLog: 创建的操作日志记录
        """
        return self.repository.add_log_flush(
            work_order_type=work_order_type,
            work_order_id=work_order_id,
            work_order_no=work_order_no,
            operator_name=operator_name,
            operation_type_code=operation_type_code,
            operation_type_name=operation_type_name,
            operator_id=operator_id,
            operation_remark=operation_remark
        )
    
    def get_logs_by_work_order(
        self,
        work_order_type: str,
        work_order_id: int
    ) -> List[WorkOrderOperationLog]:
        """
        获取指定工单的操作日志列表
        
        Args:
            work_order_type: 工单类型
            work_order_id: 工单ID
        
        Returns:
            list[WorkOrderOperationLog]: 操作日志列表
        """
        return self.repository.find_by_work_order(work_order_type, work_order_id)
    
    def get_logs_by_work_order_no(
        self,
        work_order_type: str,
        work_order_no: str
    ) -> List[WorkOrderOperationLog]:
        """
        根据工单编号获取操作日志列表
        
        Args:
            work_order_type: 工单类型
            work_order_no: 工单编号
        
        Returns:
            list[WorkOrderOperationLog]: 操作日志列表
        """
        return self.repository.find_by_work_order_no(work_order_type, work_order_no)
