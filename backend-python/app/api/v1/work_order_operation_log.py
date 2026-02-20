from typing import Optional, List
from fastapi import APIRouter, Depends, Query, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.work_order_operation_log import WorkOrderOperationLog
from app.models.operation_type import OperationType
from app.schemas.periodic_inspection import ApiResponse


router = APIRouter(prefix="/work-order-operation-log", tags=["Work Order Operation Log"])


class OperationLogCreate(BaseModel):
    work_order_type: str
    work_order_id: int
    work_order_no: str
    operator_name: str
    operator_id: Optional[int] = None
    operation_type_code: str
    operation_remark: Optional[str] = None


@router.post("", response_model=ApiResponse)
def create_operation_log(
    dto: OperationLogCreate,
    db: Session = Depends(get_db)
):
    """
    创建操作日志
    """
    operation_type = db.query(OperationType).filter(
        OperationType.type_code == dto.operation_type_code,
        OperationType.is_active == 1
    ).first()
    
    if not operation_type:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"操作类型 '{dto.operation_type_code}' 不存在或已禁用"
        )
    
    log = WorkOrderOperationLog(
        work_order_type=dto.work_order_type,
        work_order_id=dto.work_order_id,
        work_order_no=dto.work_order_no,
        operator_name=dto.operator_name,
        operator_id=dto.operator_id,
        operation_type_code=dto.operation_type_code,
        operation_type_name=operation_type.type_name,
        operation_remark=dto.operation_remark
    )
    db.add(log)
    db.commit()
    db.refresh(log)
    return ApiResponse.success(log.to_dict(), "操作日志记录成功")


@router.get("", response_model=ApiResponse)
def get_operation_logs(
    work_order_type: str = Query(..., description="工单类型: periodic_inspection/temporary_repair/spot_work"),
    work_order_id: int = Query(..., description="工单ID"),
    db: Session = Depends(get_db)
):
    """
    获取指定工单的操作日志列表
    """
    logs = db.query(WorkOrderOperationLog).filter(
        WorkOrderOperationLog.work_order_type == work_order_type,
        WorkOrderOperationLog.work_order_id == work_order_id
    ).order_by(WorkOrderOperationLog.created_at.asc()).all()
    
    result = []
    for log in logs:
        log_dict = log.to_dict()
        operation_type = db.query(OperationType).filter(
            OperationType.type_code == log.operation_type_code
        ).first()
        if operation_type:
            log_dict['color_code'] = operation_type.color_code
        result.append(log_dict)
    
    return ApiResponse.success(result)


@router.get("/by-no", response_model=ApiResponse)
def get_operation_logs_by_no(
    work_order_type: str = Query(..., description="工单类型: periodic_inspection/temporary_repair/spot_work"),
    work_order_no: str = Query(..., description="工单编号"),
    db: Session = Depends(get_db)
):
    """
    根据工单编号获取操作日志列表
    """
    logs = db.query(WorkOrderOperationLog).filter(
        WorkOrderOperationLog.work_order_type == work_order_type,
        WorkOrderOperationLog.work_order_no == work_order_no
    ).order_by(WorkOrderOperationLog.created_at.asc()).all()
    
    result = []
    for log in logs:
        log_dict = log.to_dict()
        operation_type = db.query(OperationType).filter(
            OperationType.type_code == log.operation_type_code
        ).first()
        if operation_type:
            log_dict['color_code'] = operation_type.color_code
        result.append(log_dict)
    
    return ApiResponse.success(result)
