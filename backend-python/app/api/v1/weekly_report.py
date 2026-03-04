"""
维保周报API
提供维保周报的HTTP接口
"""
from typing import Optional
from datetime import datetime
import logging
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.common import ApiResponse
from app.schemas.weekly_report import WeeklyReportCreate, WeeklyReportUpdate, WeeklyReportApprove, WeeklyReportSign
from app.services.weekly_report import WeeklyReportService
from app.models.weekly_report import WeeklyReport
from app.models.work_order_operation_log import WorkOrderOperationLog
from app.dependencies import get_current_user_info, UserInfo

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/weekly-report", tags=["Weekly Report Management"])


@router.get("/generate-id", response_model=ApiResponse)
def generate_report_id(
    report_date: Optional[str] = Query(None, description="填报日期"),
    db: Session = Depends(get_db)
):
    """
    生成周报编号
    格式: ZB-年月日-序号
    示例: ZB-20260220-01
    """
    today = datetime.now().strftime("%Y%m%d")
    base_id = f"ZB-{today}"
    
    count = db.query(WeeklyReport).filter(
        WeeklyReport.report_id.like(f"{base_id}%")
    ).count()
    
    sequence = str(count + 1).zfill(2)
    report_id = f"{base_id}-{sequence}"
    
    return ApiResponse(
        code=200,
        message="success",
        data={"report_id": report_id}
    )


@router.get("", response_model=ApiResponse)
def get_weekly_reports(
    page: int = Query(0, ge=0, description="页码，从0开始"),
    size: int = Query(10, ge=1, le=1000, description="每页数量"),
    report_id: Optional[str] = Query(None, description="周报编号"),
    report_date: Optional[str] = Query(None, description="填报日期"),
    work_summary: Optional[str] = Query(None, description="周报内容(模糊搜索)"),
    created_by: Optional[str] = Query(None, description="创建人"),
    db: Session = Depends(get_db),
    user_info: UserInfo = Depends(get_current_user_info)
):
    """
    获取维保周报列表
    """
    service = WeeklyReportService(db)
    items, total = service.get_all(
        page, size, report_id, report_date, work_summary, created_by
    )

    return ApiResponse(
        code=200,
        message="success",
        data={
            'content': [item.to_dict() for item in items],
            'totalElements': total,
            'totalPages': (total + size - 1) // size,
            'size': size,
            'number': page,
            'first': page == 0,
            'last': page >= (total + size - 1) // size
        }
    )


@router.get("/all/list", response_model=ApiResponse)
def get_all_weekly_reports(
    db: Session = Depends(get_db),
    user_info: UserInfo = Depends(get_current_user_info)
):
    """
    获取所有维保周报列表(不分页)
    """
    service = WeeklyReportService(db)
    items = service.get_all_unpaginated()

    return ApiResponse(
        code=200,
        message="success",
        data=[item.to_dict() for item in items]
    )


@router.get("/{id}", response_model=ApiResponse)
def get_weekly_report_by_id(
    id: int,
    db: Session = Depends(get_db)
):
    """
    获取维保周报详情
    """
    service = WeeklyReportService(db)
    report = service.get_by_id(id)
    return ApiResponse(
        code=200,
        message="success",
        data=report.to_dict()
    )


@router.post("", response_model=ApiResponse, status_code=status.HTTP_201_CREATED)
def create_weekly_report(
    dto: WeeklyReportCreate,
    db: Session = Depends(get_db),
    user_info: UserInfo = Depends(get_current_user_info)
):
    """
    创建维保周报
    """
    service = WeeklyReportService(db)
    report = service.create(dto, user_info.name)

    if user_info.name and report.id:
        log = WorkOrderOperationLog(
            work_order_type='weekly_report',
            work_order_id=report.id,
            work_order_no=report.report_id,
            operator_name=user_info.name,
            operator_id=user_info.id,
            operation_type='create',
            operation_type_code='create',
            operation_type_name='创建',
            operation_remark='创建周报'
        )
        db.add(log)
        db.commit()

    return ApiResponse(
        code=200,
        message="创建成功",
        data=report.to_dict()
    )


@router.put("/{id}", response_model=ApiResponse)
def update_weekly_report(
    id: int,
    dto: WeeklyReportUpdate,
    db: Session = Depends(get_db),
    user_info: UserInfo = Depends(get_current_user_info)
):
    """
    更新维保周报
    """
    service = WeeklyReportService(db)
    report = service.update(id, dto, user_info.id, user_info.name)

    return ApiResponse(
        code=200,
        message="更新成功",
        data=report.to_dict()
    )


@router.post("/{id}/submit", response_model=ApiResponse)
def submit_weekly_report(
    id: int,
    db: Session = Depends(get_db),
    user_info: UserInfo = Depends(get_current_user_info)
):
    """
    提交维保周报
    """
    service = WeeklyReportService(db)
    report = service.submit(id, user_info.id, user_info.name)

    if user_info.name and report.id:
        log = WorkOrderOperationLog(
            work_order_type='weekly_report',
            work_order_id=report.id,
            work_order_no=report.report_id,
            operator_name=user_info.name,
            operator_id=user_info.id,
            operation_type='submit',
            operation_type_code='submit',
            operation_type_name='提交',
            operation_remark='提交周报'
        )
        db.add(log)
        db.commit()

    return ApiResponse(
        code=200,
        message="提交成功",
        data=report.to_dict()
    )


@router.post("/{id}/approve", response_model=ApiResponse)
def approve_weekly_report(
    id: int,
    dto: WeeklyReportApprove,
    db: Session = Depends(get_db),
    user_info: UserInfo = Depends(get_current_user_info)
):
    """
    审核维保周报
    """
    service = WeeklyReportService(db)
    if dto.approved:
        report = service.approve(id, user_info.name, user_info.id, user_info.name)
        message = "审核通过"
        if user_info.name and report.id:
            log = WorkOrderOperationLog(
                work_order_type='weekly_report',
                work_order_id=report.id,
                work_order_no=report.report_id,
                operator_name=user_info.name,
                operator_id=user_info.id,
                operation_type='approve',
                operation_type_code='approve',
                operation_type_name='审批通过',
                operation_remark='审核通过'
            )
            db.add(log)
            db.commit()
    else:
        report = service.reject(id, dto.reject_reason or "无原因", user_info.id, user_info.name)
        message = "已退回"
        if user_info.name and report.id:
            log = WorkOrderOperationLog(
                work_order_type='weekly_report',
                work_order_id=report.id,
                work_order_no=report.report_id,
                operator_name=user_info.name,
                operator_id=user_info.id,
                operation_type='reject',
                operation_type_code='reject',
                operation_type_name='审批退回',
                operation_remark=f'退回原因: {dto.reject_reason}'
            )
            db.add(log)
            db.commit()

    return ApiResponse(
        code=200,
        message=message,
        data=report.to_dict()
    )


@router.post("/{id}/sign", response_model=ApiResponse)
def sign_weekly_report(
    id: int,
    dto: WeeklyReportSign,
    db: Session = Depends(get_db),
    user_info: UserInfo = Depends(get_current_user_info)
):
    """
    部门经理签字
    """
    service = WeeklyReportService(db)
    report = service.sign(id, dto.manager_signature, user_info.id, user_info.name)

    return ApiResponse(
        code=200,
        message="签字成功",
        data=report.to_dict()
    )


@router.delete("/{id}", response_model=ApiResponse)
def delete_weekly_report(
    id: int,
    db: Session = Depends(get_db),
    user_info: UserInfo = Depends(get_current_user_info)
):
    """
    删除维保周报(软删除)
    """
    service = WeeklyReportService(db)
    service.delete(id, user_info.id, user_info.name)

    return ApiResponse(
        code=200,
        message="删除成功",
        data=None
    )


@router.get("/{id}/operation-logs", response_model=ApiResponse)
def get_weekly_report_operation_logs(
    id: int,
    db: Session = Depends(get_db)
):
    """
    获取周报操作日志
    """
    service = WeeklyReportService(db)
    report = service.get_by_id(id)
    if not report:
        return ApiResponse(
            code=404,
            message="周报不存在",
            data=None
        )
    
    operation_logs = db.query(WorkOrderOperationLog).filter(
        WorkOrderOperationLog.work_order_type == 'weekly_report',
        WorkOrderOperationLog.work_order_id == id
    ).order_by(WorkOrderOperationLog.created_at.desc()).all()
    
    return ApiResponse(
        code=200,
        message="success",
        data=[log.to_dict() for log in operation_logs]
    )
