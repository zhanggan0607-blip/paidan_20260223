from typing import Optional
from sqlalchemy.orm import Session
from app.models.work_order_operation_log import WorkOrderOperationLog


class WorkOrderOperationLogService:
    """
    工单操作日志服务
    """
    
    def __init__(self, db: Session):
        self.db = db
    
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
        log = WorkOrderOperationLog(
            work_order_type=work_order_type,
            work_order_id=work_order_id,
            work_order_no=work_order_no,
            operator_name=operator_name,
            operator_id=operator_id,
            operation_type_code=operation_type_code,
            operation_type_name=operation_type_name,
            operation_remark=operation_remark
        )
        self.db.add(log)
        self.db.flush()
        return log
    
    def get_logs_by_work_order(
        self,
        work_order_type: str,
        work_order_id: int
    ) -> list[WorkOrderOperationLog]:
        """
        获取指定工单的操作日志列表
        
        Args:
            work_order_type: 工单类型
            work_order_id: 工单ID
        
        Returns:
            list[WorkOrderOperationLog]: 操作日志列表
        """
        return self.db.query(WorkOrderOperationLog).filter(
            WorkOrderOperationLog.work_order_type == work_order_type,
            WorkOrderOperationLog.work_order_id == work_order_id
        ).order_by(WorkOrderOperationLog.created_at.asc()).all()
    
    def get_logs_by_work_order_no(
        self,
        work_order_type: str,
        work_order_no: str
    ) -> list[WorkOrderOperationLog]:
        """
        根据工单编号获取操作日志列表
        
        Args:
            work_order_type: 工单类型
            work_order_no: 工单编号
        
        Returns:
            list[WorkOrderOperationLog]: 操作日志列表
        """
        return self.db.query(WorkOrderOperationLog).filter(
            WorkOrderOperationLog.work_order_type == work_order_type,
            WorkOrderOperationLog.work_order_no == work_order_no
        ).order_by(WorkOrderOperationLog.created_at.asc()).all()
