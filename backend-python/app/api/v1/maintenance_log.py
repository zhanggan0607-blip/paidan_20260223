import json
from typing import Optional, List
from datetime import datetime
from fastapi import APIRouter, Depends, Query, status, Request
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.maintenance_log import MaintenanceLog
from app.models.personnel import Personnel
from app.schemas.common import ApiResponse, PaginatedResponse
from app.auth import get_current_user, get_current_user_from_headers
from pydantic import BaseModel


router = APIRouter(prefix="/maintenance-log", tags=["Maintenance Log Management"])


class MaintenanceLogCreate(BaseModel):
    project_id: str
    project_name: str
    log_type: str = "spot"
    log_date: str
    work_content: Optional[str] = None
    images: Optional[List[str]] = None
    remark: Optional[str] = None


def get_log_type_prefix(log_type: str) -> str:
    """
    获取日志类型前缀
    """
    prefix_map = {
        'spot': 'YG'
    }
    return prefix_map.get(log_type, 'YG')


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


@router.get("", response_model=ApiResponse)
def get_maintenance_logs(
    request: Request,
    page: int = Query(0, ge=0, description="页码，从0开始"),
    size: int = Query(10, ge=1, le=100, description="每页数量"),
    project_name: Optional[str] = Query(None, description="项目名称(模糊搜索)"),
    log_type: Optional[str] = Query(None, description="日志类型"),
    log_date: Optional[str] = Query(None, description="日志日期"),
    created_by_role: Optional[str] = Query(None, description="创建者角色"),
    db: Session = Depends(get_db),
    current_user: Optional[dict] = Depends(get_current_user)
):
    """
    获取维保日志列表
    """
    query = db.query(MaintenanceLog).filter(MaintenanceLog.is_deleted == 0)
    
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
    current_user: Optional[dict] = Depends(get_current_user)
):
    """
    获取所有维保日志列表(不分页)
    """
    items = db.query(MaintenanceLog).filter(MaintenanceLog.is_deleted == 0).order_by(MaintenanceLog.created_at.desc()).all()
    
    return ApiResponse(
        code=200,
        message="success",
        data=[item.to_dict() for item in items]
    )


@router.get("/{id}", response_model=ApiResponse)
def get_maintenance_log_by_id(
    id: int,
    db: Session = Depends(get_db)
):
    """
    获取维保日志详情
    """
    log = db.query(MaintenanceLog).filter(MaintenanceLog.id == id, MaintenanceLog.is_deleted == 0).first()
    if not log:
        return ApiResponse(
            code=404,
            message="维保日志不存在",
            data=None
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
    current_user: Optional[dict] = Depends(get_current_user)
):
    """
    创建维保日志
    """
    user_info = current_user or get_current_user_from_headers(request)
    created_by = None
    if user_info:
        created_by = user_info.get('sub') or user_info.get('name')
    
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
        created_by=created_by
    )
    
    db.add(log)
    db.commit()
    db.refresh(log)
    
    return ApiResponse(
        code=200,
        message="创建成功",
        data=log.to_dict()
    )


@router.put("/{id}", response_model=ApiResponse)
def update_maintenance_log(
    id: int,
    dto: MaintenanceLogCreate,
    db: Session = Depends(get_db)
):
    """
    更新维保日志
    """
    log = db.query(MaintenanceLog).filter(MaintenanceLog.id == id, MaintenanceLog.is_deleted == 0).first()
    if not log:
        return ApiResponse(
            code=404,
            message="维保日志不存在",
            data=None
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
    db: Session = Depends(get_db)
):
    """
    删除维保日志(软删除)
    """
    log = db.query(MaintenanceLog).filter(MaintenanceLog.id == id, MaintenanceLog.is_deleted == 0).first()
    if not log:
        return ApiResponse(
            code=404,
            message="维保日志不存在",
            data=None
        )
    
    log.is_deleted = 1
    db.commit()
    
    return ApiResponse(
        code=200,
        message="删除成功",
        data=None
    )
