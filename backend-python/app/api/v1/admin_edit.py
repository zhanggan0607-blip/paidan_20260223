"""
管理员编辑工单API
允许管理员在任何状态下编辑工单内容和照片
每次改动都会记录到操作日志
"""
import json
import logging
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import UserInfo, get_admin_user
from app.models.operation_type import OperationType
from app.models.spot_work import SpotWork
from app.models.temporary_repair import TemporaryRepair
from app.models.periodic_inspection import PeriodicInspection
from app.models.work_order_operation_log import WorkOrderOperationLog
from app.schemas.common import ApiResponse

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/admin-edit", tags=["Admin Edit Work Order"])


class AdminEditContentRequest(BaseModel):
    work_order_type: str
    work_order_id: int
    field_name: str
    old_value: str | None = None
    new_value: str | None = None
    remark: str | None = None


class AdminAddPhotoRequest(BaseModel):
    work_order_type: str
    work_order_id: int
    photo_url: str
    remark: str | None = None


class AdminDeletePhotoRequest(BaseModel):
    work_order_type: str
    work_order_id: int
    photo_url: str
    remark: str | None = None


WORK_ORDER_MODELS = {
    'spot_work': SpotWork,
    'temporary_repair': TemporaryRepair,
    'periodic_inspection': PeriodicInspection,
}

WORK_ORDER_ID_FIELDS = {
    'spot_work': 'work_id',
    'temporary_repair': 'repair_id',
    'periodic_inspection': 'inspection_id',
}

EDITABLE_FIELDS = {
    'spot_work': ['work_content', 'remarks', 'maintenance_personnel'],
    'temporary_repair': ['fault_description', 'solution', 'remarks', 'maintenance_personnel'],
    'periodic_inspection': ['execution_result', 'remarks', 'maintenance_personnel'],
}


def get_work_order(db: Session, work_order_type: str, work_order_id: int) -> Any:
    model = WORK_ORDER_MODELS.get(work_order_type)
    if not model:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"不支持的工单类型: {work_order_type}"
        )
    
    work_order = db.query(model).filter(model.id == work_order_id).first()
    if not work_order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="工单不存在"
        )
    
    return work_order


def create_operation_log(
    db: Session,
    work_order_type: str,
    work_order_id: int,
    work_order_no: str,
    operator_name: str,
    operator_id: int,
    operation_type_code: str,
    operation_type_name: str,
    operation_remark: str | None = None
) -> None:
    operation_type = db.query(OperationType).filter(
        OperationType.type_code == operation_type_code
    ).first()
    
    type_name = operation_type_name
    if operation_type:
        type_name = operation_type.type_name
    
    log = WorkOrderOperationLog(
        work_order_type=work_order_type,
        work_order_id=work_order_id,
        work_order_no=work_order_no,
        operator_name=operator_name,
        operator_id=operator_id,
        operation_type=operation_type_code,
        operation_type_code=operation_type_code,
        operation_type_name=type_name,
        operation_remark=operation_remark
    )
    db.add(log)


@router.post("/content", response_model=ApiResponse)
def admin_edit_content(
    dto: AdminEditContentRequest,
    db: Session = Depends(get_db),
    user_info: UserInfo = Depends(get_admin_user)
):
    """
    管理员编辑工单内容
    只允许管理员操作
    """
    editable_fields = EDITABLE_FIELDS.get(dto.work_order_type, [])
    if dto.field_name not in editable_fields:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"字段 '{dto.field_name}' 不允许编辑，可编辑字段: {editable_fields}"
        )
    
    work_order = get_work_order(db, dto.work_order_type, dto.work_order_id)
    id_field = WORK_ORDER_ID_FIELDS.get(dto.work_order_type, 'id')
    work_order_no = getattr(work_order, id_field, str(work_order.id))
    
    old_value = getattr(work_order, dto.field_name, None)
    setattr(work_order, dto.field_name, dto.new_value)
    
    field_display_names = {
        'work_content': '工作内容',
        'remarks': '备注',
        'maintenance_personnel': '运维人员',
        'fault_description': '故障描述',
        'solution': '解决方案',
        'execution_result': '发现问题',
    }
    
    field_display = field_display_names.get(dto.field_name, dto.field_name)
    remark = f"编辑字段【{field_display}】"
    if dto.remark:
        remark += f": {dto.remark}"
    
    create_operation_log(
        db=db,
        work_order_type=dto.work_order_type,
        work_order_id=dto.work_order_id,
        work_order_no=work_order_no,
        operator_name=user_info.name,
        operator_id=user_info.id,
        operation_type_code='admin_edit_content',
        operation_type_name='管理员编辑内容',
        operation_remark=remark
    )
    
    db.commit()
    db.refresh(work_order)
    
    return ApiResponse.success(work_order.to_dict(), "编辑成功")


@router.post("/photo/add", response_model=ApiResponse)
def admin_add_photo(
    dto: AdminAddPhotoRequest,
    db: Session = Depends(get_db),
    user_info: UserInfo = Depends(get_admin_user)
):
    """
    管理员添加照片
    只允许管理员操作
    """
    work_order = get_work_order(db, dto.work_order_type, dto.work_order_id)
    id_field = WORK_ORDER_ID_FIELDS.get(dto.work_order_type, 'id')
    work_order_no = getattr(work_order, id_field, str(work_order.id))
    
    photos = []
    if work_order.photos:
        try:
            photos = json.loads(work_order.photos) if isinstance(work_order.photos, str) else work_order.photos
        except (json.JSONDecodeError, TypeError):
            photos = []
    
    if dto.photo_url not in photos:
        photos.append(dto.photo_url)
        work_order.photos = photos
        
        remark = "添加照片"
        if dto.remark:
            remark += f": {dto.remark}"
        
        create_operation_log(
            db=db,
            work_order_type=dto.work_order_type,
            work_order_id=dto.work_order_id,
            work_order_no=work_order_no,
            operator_name=user_info.name,
            operator_id=user_info.id,
            operation_type_code='admin_add_photo',
            operation_type_name='管理员添加照片',
            operation_remark=remark
        )
        
        db.commit()
        db.refresh(work_order)
    
    return ApiResponse.success(work_order.to_dict(), "照片添加成功")


@router.post("/photo/delete", response_model=ApiResponse)
def admin_delete_photo(
    dto: AdminDeletePhotoRequest,
    db: Session = Depends(get_db),
    user_info: UserInfo = Depends(get_admin_user)
):
    """
    管理员删除照片
    只允许管理员操作
    """
    work_order = get_work_order(db, dto.work_order_type, dto.work_order_id)
    id_field = WORK_ORDER_ID_FIELDS.get(dto.work_order_type, 'id')
    work_order_no = getattr(work_order, id_field, str(work_order.id))
    
    photos = []
    if work_order.photos:
        try:
            photos = json.loads(work_order.photos) if isinstance(work_order.photos, str) else work_order.photos
        except (json.JSONDecodeError, TypeError):
            photos = []
    
    if dto.photo_url in photos:
        photos.remove(dto.photo_url)
        work_order.photos = photos if photos else None
        
        remark = "删除照片"
        if dto.remark:
            remark += f": {dto.remark}"
        
        create_operation_log(
            db=db,
            work_order_type=dto.work_order_type,
            work_order_id=dto.work_order_id,
            work_order_no=work_order_no,
            operator_name=user_info.name,
            operator_id=user_info.id,
            operation_type_code='admin_delete_photo',
            operation_type_name='管理员删除照片',
            operation_remark=remark
        )
        
        db.commit()
        db.refresh(work_order)
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="照片不存在"
        )
    
    return ApiResponse.success(work_order.to_dict(), "照片删除成功")


@router.get("/editable-fields/{work_order_type}", response_model=ApiResponse)
def get_editable_fields(
    work_order_type: str,
    user_info: UserInfo = Depends(get_admin_user)
):
    """
    获取指定工单类型的可编辑字段
    """
    fields = EDITABLE_FIELDS.get(work_order_type, [])
    
    field_display_names = {
        'work_content': '工作内容',
        'remarks': '备注',
        'maintenance_personnel': '运维人员',
        'fault_description': '故障描述',
        'solution': '解决方案',
        'execution_result': '发现问题',
    }
    
    result = [
        {"field_name": f, "display_name": field_display_names.get(f, f)}
        for f in fields
    ]
    
    return ApiResponse.success(result)
