"""
工单操作日志Repository
提供工单操作日志数据访问方法
"""
import logging

from sqlalchemy.orm import Session

from app.models.work_order_operation_log import WorkOrderOperationLog
from app.repositories.base import BaseRepository

logger = logging.getLogger(__name__)


class WorkOrderOperationLogRepository(BaseRepository[WorkOrderOperationLog]):
    """
    工单操作日志Repository
    继承BaseRepository，复用通用CRUD方法
    """

    def __init__(self, db: Session):
        super().__init__(db, WorkOrderOperationLog)

    def find_by_work_order(
        self,
        work_order_type: str,
        work_order_id: int
    ) -> list[WorkOrderOperationLog]:
        """
        根据工单类型和ID查询操作日志

        Args:
            work_order_type: 工单类型 (periodic_inspection/temporary_repair/spot_work)
            work_order_id: 工单ID

        Returns:
            操作日志列表，按创建时间升序排列
        """
        try:
            return self.db.query(WorkOrderOperationLog).filter(
                WorkOrderOperationLog.work_order_type == work_order_type,
                WorkOrderOperationLog.work_order_id == work_order_id
            ).order_by(WorkOrderOperationLog.created_at.asc()).all()
        except Exception as e:
            logger.error(f"查询操作日志失败 (type={work_order_type}, id={work_order_id}): {str(e)}")
            raise

    def find_by_work_order_no(
        self,
        work_order_type: str,
        work_order_no: str
    ) -> list[WorkOrderOperationLog]:
        """
        根据工单类型和编号查询操作日志

        Args:
            work_order_type: 工单类型
            work_order_no: 工单编号

        Returns:
            操作日志列表，按创建时间升序排列
        """
        try:
            return self.db.query(WorkOrderOperationLog).filter(
                WorkOrderOperationLog.work_order_type == work_order_type,
                WorkOrderOperationLog.work_order_no == work_order_no
            ).order_by(WorkOrderOperationLog.created_at.asc()).all()
        except Exception as e:
            logger.error(f"查询操作日志失败 (type={work_order_type}, no={work_order_no}): {str(e)}")
            raise

    def create_log(
        self,
        work_order_type: str,
        work_order_id: int,
        work_order_no: str,
        operator_name: str,
        operation_type_code: str,
        operation_type_name: str,
        operator_id: int | None = None,
        operation_remark: str | None = None
    ) -> WorkOrderOperationLog:
        """
        创建操作日志

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
            创建的操作日志记录
        """
        try:
            log = WorkOrderOperationLog(
                work_order_type=work_order_type,
                work_order_id=work_order_id,
                work_order_no=work_order_no,
                operator_name=operator_name,
                operator_id=operator_id,
                operation_type=operation_type_code,
                operation_type_code=operation_type_code,
                operation_type_name=operation_type_name,
                operation_remark=operation_remark
            )
            return self.create(log)
        except Exception as e:
            logger.error(f"创建操作日志失败: {str(e)}")
            raise

    def add_log_flush(
        self,
        work_order_type: str,
        work_order_id: int,
        work_order_no: str,
        operator_name: str,
        operation_type_code: str,
        operation_type_name: str,
        operator_id: int | None = None,
        operation_remark: str | None = None
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
            创建的操作日志记录
        """
        try:
            log = WorkOrderOperationLog(
                work_order_type=work_order_type,
                work_order_id=work_order_id,
                work_order_no=work_order_no,
                operator_name=operator_name,
                operator_id=operator_id,
                operation_type=operation_type_code,
                operation_type_code=operation_type_code,
                operation_type_name=operation_type_name,
                operation_remark=operation_remark
            )
            self.db.add(log)
            self.db.flush()
            return log
        except Exception as e:
            logger.error(f"添加操作日志失败: {str(e)}")
            raise
