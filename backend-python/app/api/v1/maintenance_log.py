import json
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import (
    UserInfo,
    check_data_access,
    get_current_user_required,
    get_manager_user,
)
from app.models.maintenance_log import MaintenanceLog
from app.models.personnel import Personnel
from app.models.work_order_operation_log import WorkOrderOperationLog
from app.schemas.common import ApiResponse

router = APIRouter(prefix="/maintenance-log", tags=["Maintenance Log Management"])


class MaintenanceLogCreate(BaseModel):
    project_id: str
    project_name: str
    log_type: str = "maintenance"
    log_date: str
    work_content: str | None = None
    images: list[str] | None = None
    remark: str | None = None


def get_log_type_prefix(log_type: str) -> str:
    """
    获取日志类型前缀
    维修日志前缀为WX
    """
    prefix_map = {
        'maintenance': 'WX'
    }
    return prefix_map.get(log_type, 'WX')


def generate_log_id(project_id: str, log_type: str, db: Session) -> str:
    """
    生成日志编号
    格式: 前缀-项目编号-年月日-序号
    示例: WX-TQ2023423-20251123-01
    """
    prefix = get_log_type_prefix(log_type)
    today = datetime.now().strftime("%Y%m%d")
    base_id = f"{prefix}-{project_id}-{today}"

    count = db.query(MaintenanceLog).filter(
        MaintenanceLog.log_id.like(f"{base_id}%")
    ).count()

    sequence = str(count + 1).zfill(2)
    return f"{base_id}-{sequence}"


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
        operation_type=operation_type_code,
        operation_type_code=operation_type_code,
        operation_type_name=operation_type_name,
        operation_remark=operation_remark
    )

    db.add(log)
    db.commit()


@router.get("", response_model=ApiResponse)
def get_maintenance_logs(
    request: Request,
    page: int = Query(0, ge=0, description="页码，从0开始"),
    size: int = Query(10, ge=1, le=1000, description="每页数量"),
    project_name: str | None = Query(None, description="项目名称(模糊搜索)"),
    log_type: str | None = Query(None, description="日志类型"),
    log_date: str | None = Query(None, description="日志日期"),
    created_by: str | None = Query(None, description="创建者"),
    created_by_role: str | None = Query(None, description="创建者角色"),
    db: Session = Depends(get_db),
    user_info: UserInfo = Depends(get_current_user_required)
):
    """
    获取维保日志列表
    管理员可以查看所有日志，普通用户只能查看自己的日志
    """
    query = db.query(MaintenanceLog).filter(MaintenanceLog.is_deleted == False)

    if not user_info.is_manager:
        query = query.filter(MaintenanceLog.created_by == user_info.name)
    elif created_by:
        query = query.filter(MaintenanceLog.created_by == created_by)

    if project_name:
        query = query.filter(MaintenanceLog.project_name.ilike(f"%{project_name}%"))
    if log_type:
        query = query.filter(MaintenanceLog.log_type == log_type)
    if log_date:
        query = query.filter(MaintenanceLog.log_date == log_date)

    if created_by_role:
        subquery = db.query(Personnel.name).filter(Personnel.role == created_by_role).subquery()
        query = query.filter(MaintenanceLog.created_by.in_(subquery))

    total = query.count()
    items = query.order_by(MaintenanceLog.created_at.desc()).offset(page * size).limit(size).all()

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
def get_all_maintenance_logs(
    request: Request,
    db: Session = Depends(get_db),
    user_info: UserInfo = Depends(get_current_user_required)
):
    """
    获取所有维保日志列表(不分页)
    管理员可以查看所有日志，普通用户只能查看自己的日志
    """
    query = db.query(MaintenanceLog).filter(MaintenanceLog.is_deleted == False)

    if not user_info.is_manager:
        query = query.filter(MaintenanceLog.created_by == user_info.name)

    items = query.order_by(MaintenanceLog.created_at.desc()).all()

    return ApiResponse(
        code=200,
        message="success",
        data=[item.to_dict() for item in items]
    )


@router.get("/my", response_model=ApiResponse)
def get_my_maintenance_logs(
    request: Request,
    page: int = Query(0, ge=0, description="页码，从0开始"),
    size: int = Query(10, ge=1, le=1000, description="每页数量"),
    project_name: str | None = Query(None, description="项目名称(模糊搜索)"),
    log_type: str | None = Query(None, description="日志类型"),
    log_date: str | None = Query(None, description="日志日期"),
    status: str | None = Query(None, description="状态"),
    db: Session = Depends(get_db),
    user_info: UserInfo = Depends(get_current_user_required)
):
    """
    获取当前用户的维保日志列表
    """
    query = db.query(MaintenanceLog).filter(MaintenanceLog.is_deleted == False)

    query = query.filter(MaintenanceLog.created_by == user_info.name)

    if project_name:
        query = query.filter(MaintenanceLog.project_name.ilike(f"%{project_name}%"))
    if log_type:
        query = query.filter(MaintenanceLog.log_type == log_type)
    if log_date:
        query = query.filter(MaintenanceLog.log_date == log_date)
    if status:
        query = query.filter(MaintenanceLog.status == status)

    total = query.count()
    items = query.order_by(MaintenanceLog.created_at.desc()).offset(page * size).limit(size).all()

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


@router.get("/{id}", response_model=ApiResponse)
def get_maintenance_log_by_id(
    id: int,
    db: Session = Depends(get_db),
    user_info: UserInfo = Depends(get_current_user_required)
):
    """
    获取维保日志详情
    管理员可以查看所有日志，普通用户只能查看自己的日志
    """
    log = db.query(MaintenanceLog).filter(MaintenanceLog.id == id, MaintenanceLog.is_deleted == False).first()
    if not log:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="维保日志不存在"
        )

    if not check_data_access(user_info, log.created_by):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权访问此日志"
        )

    return ApiResponse(
        code=200,
        message="success",
        data=log.to_dict()
    )


@router.post("", response_model=ApiResponse, status_code=status.HTTP_201_CREATED)
def create_maintenance_log(
    dto: MaintenanceLogCreate,
    request: Request,
    db: Session = Depends(get_db),
    user_info: UserInfo = Depends(get_current_user_required)
):
    """
    创建维保日志
    """
    log_id = generate_log_id(dto.project_id, dto.log_type, db)

    images_json = json.dumps(dto.images, ensure_ascii=False) if dto.images else None

    log = MaintenanceLog(
        log_id=log_id,
        project_id=dto.project_id,
        project_name=dto.project_name,
        log_type=dto.log_type,
        log_date=datetime.strptime(dto.log_date, "%Y-%m-%d"),
        work_content=dto.work_content,
        images=images_json,
        remark=dto.remark,
        created_by=user_info.name
    )

    db.add(log)
    db.commit()
    db.refresh(log)

    if user_info.name:
        record_operation_log(
            db=db,
            work_order_type='maintenance_log',
            work_order_id=log.id,
            work_order_no=log.log_id,
            operator_name=user_info.name,
            operation_type_code='create',
            operation_type_name='创建',
            operation_remark='创建维保日志'
        )

    return ApiResponse(
        code=200,
        message="创建成功",
        data=log.to_dict()
    )


@router.put("/{id}", response_model=ApiResponse)
def update_maintenance_log(
    id: int,
    dto: MaintenanceLogCreate,
    db: Session = Depends(get_db),
    user_info: UserInfo = Depends(get_current_user_required)
):
    """
    更新维保日志
    管理员可以更新所有日志，普通用户只能更新自己的日志
    """
    log = db.query(MaintenanceLog).filter(MaintenanceLog.id == id, MaintenanceLog.is_deleted == False).first()
    if not log:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="维保日志不存在"
        )

    if not check_data_access(user_info, log.created_by):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权修改此日志"
        )

    log.project_id = dto.project_id
    log.project_name = dto.project_name
    log.log_type = dto.log_type
    log.log_date = datetime.strptime(dto.log_date, "%Y-%m-%d")
    log.work_content = dto.work_content
    log.images = json.dumps(dto.images, ensure_ascii=False) if dto.images else None
    log.remark = dto.remark

    db.commit()
    db.refresh(log)

    return ApiResponse(
        code=200,
        message="更新成功",
        data=log.to_dict()
    )


@router.delete("/{id}", response_model=ApiResponse)
def delete_maintenance_log(
    id: int,
    db: Session = Depends(get_db),
    user_info: UserInfo = Depends(get_current_user_required)
):
    """
    删除维保日志(软删除)
    管理员可以删除所有日志，普通用户只能删除自己的日志
    """
    log = db.query(MaintenanceLog).filter(MaintenanceLog.id == id, MaintenanceLog.is_deleted == False).first()
    if not log:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="维保日志不存在"
        )

    if not check_data_access(user_info, log.created_by):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权删除此日志"
        )

    log.is_deleted = True
    db.commit()

    return ApiResponse(
        code=200,
        message="删除成功",
        data=None
    )


@router.get("/{id}/operation-logs", response_model=ApiResponse)
def get_maintenance_log_operation_logs(
    id: int,
    db: Session = Depends(get_db)
):
    """
    获取维保日志操作日志
    """
    log = db.query(MaintenanceLog).filter(MaintenanceLog.id == id, MaintenanceLog.is_deleted == False).first()
    if not log:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="维保日志不存在"
        )

    operation_logs = db.query(WorkOrderOperationLog).filter(
        WorkOrderOperationLog.work_order_type == 'maintenance_log',
        WorkOrderOperationLog.work_order_id == id
    ).order_by(WorkOrderOperationLog.created_at.desc()).all()

    return ApiResponse(
        code=200,
        message="success",
        data=[log.to_dict() for log in operation_logs]
    )


class RejectRequest(BaseModel):
    reject_reason: str


@router.post("/{id}/reject", response_model=ApiResponse)
def reject_maintenance_log(
    id: int,
    dto: RejectRequest,
    db: Session = Depends(get_db),
    user_info: UserInfo = Depends(get_manager_user)
):
    """
    退回维保日志
    需要管理员或部门经理权限
    """
    log = db.query(MaintenanceLog).filter(MaintenanceLog.id == id, MaintenanceLog.is_deleted == False).first()
    if not log:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="维保日志不存在"
        )

    operator_name = user_info.name

    log.status = 'rejected'
    log.reject_reason = dto.reject_reason

    db.commit()
    db.refresh(log)

    if operator_name:
        record_operation_log(
            db=db,
            work_order_type='maintenance_log',
            work_order_id=log.id,
            work_order_no=log.log_id,
            operator_name=operator_name,
            operation_type_code='reject',
            operation_type_name='审批退回',
            operation_remark=f'退回原因: {dto.reject_reason}'
        )

    return ApiResponse(
        code=200,
        message="退回成功",
        data=log.to_dict()
    )
