from sqlalchemy import BigInteger, Column, DateTime, Index, String
from sqlalchemy.sql import func

from app.database import Base
from app.models.mixins import SerializationMixin


class WorkOrderOperationLog(Base, SerializationMixin):
    _exclude_from_dict = {'operation_type'}
    __tablename__ = "work_order_operation_log"

    id = Column(BigInteger, primary_key=True, autoincrement=True, comment="主键ID")
    work_order_type = Column(String(50), nullable=False, comment="工单类型: periodic_inspection/temporary_repair/spot_work")
    work_order_id = Column(BigInteger, nullable=False, comment="工单ID")
    work_order_no = Column(String(50), nullable=False, comment="工单编号")
    operator_name = Column(String(100), nullable=False, comment="操作人员姓名")
    operator_id = Column(BigInteger, nullable=True, comment="操作人员ID")
    operation_type = Column(String(50), nullable=True, default=None, comment="操作类型(已废弃，请使用operation_type_code)")
    operation_type_code = Column(String(50), nullable=True, comment="操作类型编码")
    operation_type_name = Column(String(50), nullable=True, comment="操作类型名称")
    operation_remark = Column(String(500), comment="操作备注")
    created_at = Column(DateTime, server_default=func.now(), nullable=False, comment="操作时间")

    __table_args__ = (
        Index('idx_operation_log_type_id', 'work_order_type', 'work_order_id'),
        Index('idx_operation_log_work_order_no', 'work_order_no'),
        Index('idx_operation_log_created_at', 'created_at'),
        {'comment': '工单操作日志表'}
    )
