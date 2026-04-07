"""
维保周报API
提供维保周报的HTTP接口
"""
import logging
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import (
    UserInfo,
    check_data_access,
    get_current_user_info,
    get_current_user_required,
    get_manager_user,
)
from app.models.weekly_report import WeeklyReport
from app.models.work_order_operation_log import WorkOrderOperationLog
from app.schemas.common import ApiResponse
from app.schemas.weekly_report import (
    WeeklyReportApprove,
    WeeklyReportCreate,
    WeeklyReportSign,
    WeeklyReportUpdate,
)
from app.services.weekly_report import WeeklyReportService

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/weekly-report", tags=["Weekly Report Management"])


@router.get("/generate-id", response_model=ApiResponse)
def generate_report_id(
    report_date: str | None = Query(None, description="填报日期"),
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
    report_id: str | None = Query(None, description="周报编号"),
    report_date: str | None = Query(None, description="填报日期"),
    work_summary: str | None = Query(None, description="周报内容(模糊搜索)"),
    created_by: str | None = Query(None, description="创建人"),
    db: Session = Depends(get_db),
    user_info: UserInfo = Depends(get_current_user_required)
):
    """
    获取维保周报列表
    管理员可以查看所有周报，普通用户只能查看自己的周报
    """
    service = WeeklyReportService(db)

    if not user_info.is_manager:
        created_by = user_info.name

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
    user_info: UserInfo = Depends(get_current_user_required)
):
    """
    获取所有维保周报列表(不分页)
    管理员可以查看所有周报，普通用户只能查看自己的周报
    """
    service = WeeklyReportService(db)

    if user_info.is_manager:
        items = service.get_all_unpaginated()
    else:
        items = service.get_all_unpaginated(created_by=user_info.name)

    return ApiResponse(
        code=200,
        message="success",
        data=[item.to_dict() for item in items]
    )


@router.get("/{id}", response_model=ApiResponse)
def get_weekly_report_by_id(
    id: int,
    db: Session = Depends(get_db),
    user_info: UserInfo = Depends(get_current_user_required)
):
    """
    获取维保周报详情
    管理员可以查看所有周报，普通用户只能查看自己的周报
    """
    service = WeeklyReportService(db)
    report = service.get_by_id(id)

    if not check_data_access(user_info, report.created_by):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权访问此周报"
        )

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
    user_info: UserInfo = Depends(get_current_user_required)
):
    """
    更新维保周报
    管理员可更新所有周报，普通用户只能更新自己的周报
    """
    service = WeeklyReportService(db)

    existing_report = service.get_by_id(id)
    if not check_data_access(user_info, existing_report.created_by):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权修改此周报"
        )

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
    user_info: UserInfo = Depends(get_current_user_required)
):
    """
    提交维保周报
    管理员可提交所有周报，普通用户只能提交自己的周报
    """
    service = WeeklyReportService(db)

    existing_report = service.get_by_id(id)
    if not check_data_access(user_info, existing_report.created_by):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权提交此周报"
        )

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
    user_info: UserInfo = Depends(get_manager_user)
):
    """
    审核维保周报
    需要管理员或部门经理权限
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
    user_info: UserInfo = Depends(get_manager_user)
):
    """
    部门经理签字
    需要管理员或部门经理权限
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
    user_info: UserInfo = Depends(get_current_user_required)
):
    """
    删除维保周报(软删除)
    管理员可以删除所有周报，普通用户只能删除自己的周报
    """
    service = WeeklyReportService(db)
    report = service.get_by_id(id)

    if not check_data_access(user_info, report.created_by):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权删除此周报"
        )

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
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="周报不存在"
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
