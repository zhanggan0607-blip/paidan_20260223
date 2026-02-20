from typing import Optional
from datetime import datetime
from fastapi import APIRouter, Depends, Query, status, Request
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.common import ApiResponse, PaginatedResponse
from app.schemas.weekly_report import WeeklyReportCreate, WeeklyReportUpdate, WeeklyReportApprove, WeeklyReportSign
from app.services.weekly_report import WeeklyReportService, WeeklyReportCreateDTO, WeeklyReportUpdateDTO
from app.models.weekly_report import WeeklyReport
from app.models.work_order_operation_log import WorkOrderOperationLog
from app.auth import get_current_user, get_current_user_from_headers

router = APIRouter(prefix="/weekly-report", tags=["Weekly Report Management"])


def record_operation_log(
    db: Session,
    work_order_type: str,
    work_order_id: int,
    work_order_no: str,
    operator_name: str,
    operation_type_code: str,
    operation_type_name: str,
    operation_remark: str = None
):
    """
    记录操作日志
    """
    log = WorkOrderOperationLog(
        work_order_type=work_order_type,
        work_order_id=work_order_id,
        work_order_no=work_order_no,
        operator_name=operator_name,
        operation_type_code=operation_type_code,
        operation_type_name=operation_type_name,
        operation_remark=operation_remark
    )
    
    db.add(log)
    db.commit()


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
    request: Request,
    page: int = Query(0, ge=0, description="页码，从0开始"),
    size: int = Query(10, ge=1, le=2000, description="每页数量"),
    report_id: Optional[str] = Query(None, description="周报编号"),
    report_date: Optional[str] = Query(None, description="填报日期"),
    work_summary: Optional[str] = Query(None, description="周报内容(模糊搜索)"),
    created_by: Optional[str] = Query(None, description="创建人"),
    db: Session = Depends(get_db),
    current_user: Optional[dict] = Depends(get_current_user)
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
    request: Request,
    db: Session = Depends(get_db),
    current_user: Optional[dict] = Depends(get_current_user)
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
    request: Request,
    db: Session = Depends(get_db),
    current_user: Optional[dict] = Depends(get_current_user)
):
    """
    创建维保周报
    """
    user_info = current_user or get_current_user_from_headers(request)
    created_by = None
    if user_info:
        created_by = user_info.get('sub') or user_info.get('name')

    service = WeeklyReportService(db)
    create_dto = WeeklyReportCreateDTO(
        report_id=dto.report_id,
        project_id=dto.project_id,
        project_name=dto.project_name,
        week_start_date=dto.week_start_date,
        week_end_date=dto.week_end_date,
        report_date=dto.report_date,
        work_summary=dto.work_summary,
        work_content=dto.work_content,
        next_week_plan=dto.next_week_plan,
        issues=dto.issues,
        suggestions=dto.suggestions,
        images=dto.images,
        manager_signature=dto.manager_signature
    )
    report = service.create(create_dto, created_by)

    if created_by:
        record_operation_log(
            db=db,
            work_order_type='weekly_report',
            work_order_id=report.id,
            work_order_no=report.report_id,
            operator_name=created_by,
            operation_type_code='create',
            operation_type_name='创建',
            operation_remark='创建周报'
        )

    return ApiResponse(
        code=200,
        message="创建成功",
        data=report.to_dict()
    )


@router.put("/{id}", response_model=ApiResponse)
def update_weekly_report(
    id: int,
    dto: WeeklyReportUpdate,
    db: Session = Depends(get_db)
):
    """
    更新维保周报
    """
    service = WeeklyReportService(db)
    update_dto = WeeklyReportUpdateDTO(
        project_id=dto.project_id,
        project_name=dto.project_name,
        week_start_date=dto.week_start_date,
        week_end_date=dto.week_end_date,
        report_date=dto.report_date,
        work_summary=dto.work_summary,
        work_content=dto.work_content,
        next_week_plan=dto.next_week_plan,
        issues=dto.issues,
        suggestions=dto.suggestions,
        images=dto.images,
        manager_signature=dto.manager_signature,
        status=dto.status
    )
    report = service.update(id, update_dto)

    return ApiResponse(
        code=200,
        message="更新成功",
        data=report.to_dict()
    )


@router.post("/{id}/submit", response_model=ApiResponse)
def submit_weekly_report(
    id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user: Optional[dict] = Depends(get_current_user)
):
    """
    提交维保周报
    """
    user_info = current_user or get_current_user_from_headers(request)
    operator_name = None
    if user_info:
        operator_name = user_info.get('sub') or user_info.get('name')

    service = WeeklyReportService(db)
    report = service.submit(id)

    if operator_name:
        record_operation_log(
            db=db,
            work_order_type='weekly_report',
            work_order_id=report.id,
            work_order_no=report.report_id,
            operator_name=operator_name,
            operation_type_code='submit',
            operation_type_name='提交',
            operation_remark='提交周报'
        )

    return ApiResponse(
        code=200,
        message="提交成功",
        data=report.to_dict()
    )


@router.post("/{id}/approve", response_model=ApiResponse)
def approve_weekly_report(
    id: int,
    dto: WeeklyReportApprove,
    request: Request,
    db: Session = Depends(get_db),
    current_user: Optional[dict] = Depends(get_current_user)
):
    """
    审核维保周报
    """
    user_info = current_user or get_current_user_from_headers(request)
    approved_by = None
    if user_info:
        approved_by = user_info.get('sub') or user_info.get('name')

    service = WeeklyReportService(db)
    if dto.approved:
        report = service.approve(id, approved_by)
        message = "审核通过"
        if approved_by:
            record_operation_log(
                db=db,
                work_order_type='weekly_report',
                work_order_id=report.id,
                work_order_no=report.report_id,
                operator_name=approved_by,
                operation_type_code='approve',
                operation_type_name='审批通过',
                operation_remark='审核通过'
            )
    else:
        report = service.reject(id, dto.reject_reason or "无原因")
        message = "已退回"
        if approved_by:
            record_operation_log(
                db=db,
                work_order_type='weekly_report',
                work_order_id=report.id,
                work_order_no=report.report_id,
                operator_name=approved_by,
                operation_type_code='reject',
                operation_type_name='审批退回',
                operation_remark=f'退回原因: {dto.reject_reason}'
            )

    return ApiResponse(
        code=200,
        message=message,
        data=report.to_dict()
    )


@router.post("/{id}/sign", response_model=ApiResponse)
def sign_weekly_report(
    id: int,
    dto: WeeklyReportSign,
    db: Session = Depends(get_db)
):
    """
    部门经理签字
    """
    service = WeeklyReportService(db)
    report = service.sign(id, dto.manager_signature)

    return ApiResponse(
        code=200,
        message="签字成功",
        data=report.to_dict()
    )


@router.delete("/{id}", response_model=ApiResponse)
def delete_weekly_report(
    id: int,
    db: Session = Depends(get_db)
):
    """
    删除维保周报(软删除)
    """
    service = WeeklyReportService(db)
    service.delete(id)

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
