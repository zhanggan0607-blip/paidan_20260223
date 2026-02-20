from typing import Optional, List
from fastapi import APIRouter, Depends, Query, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.operation_type import OperationType
from app.schemas.periodic_inspection import ApiResponse


router = APIRouter(prefix="/operation-type", tags=["Operation Type"])


class OperationTypeCreate(BaseModel):
    type_code: str
    type_name: str
    color_code: Optional[str] = None
    sort_order: Optional[int] = 0
    is_active: Optional[int] = 1


class OperationTypeUpdate(BaseModel):
    type_code: Optional[str] = None
    type_name: Optional[str] = None
    color_code: Optional[str] = None
    sort_order: Optional[int] = None
    is_active: Optional[int] = None


@router.get("", response_model=ApiResponse)
def get_operation_types(
    is_active: Optional[int] = Query(None, description="是否启用: 1启用, 0禁用"),
    db: Session = Depends(get_db)
):
    """
    获取操作类型列表
    """
    query = db.query(OperationType)
    if is_active is not None:
        query = query.filter(OperationType.is_active == is_active)
    
    items = query.order_by(OperationType.sort_order.asc(), OperationType.id.asc()).all()
    return ApiResponse.success([item.to_dict() for item in items])


@router.get("/{type_code}", response_model=ApiResponse)
def get_operation_type_by_code(
    type_code: str,
    db: Session = Depends(get_db)
):
    """
    根据类型编码获取操作类型
    """
    item = db.query(OperationType).filter(OperationType.type_code == type_code).first()
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"操作类型 '{type_code}' 不存在"
        )
    return ApiResponse.success(item.to_dict())


@router.post("", response_model=ApiResponse)
def create_operation_type(
    dto: OperationTypeCreate,
    db: Session = Depends(get_db)
):
    """
    创建操作类型
    """
    existing = db.query(OperationType).filter(OperationType.type_code == dto.type_code).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"操作类型编码 '{dto.type_code}' 已存在"
        )
    
    item = OperationType(
        type_code=dto.type_code,
        type_name=dto.type_name,
        color_code=dto.color_code,
        sort_order=dto.sort_order or 0,
        is_active=dto.is_active if dto.is_active is not None else 1
    )
    db.add(item)
    db.commit()
    db.refresh(item)
    return ApiResponse.success(item.to_dict(), "创建成功")


@router.put("/{type_code}", response_model=ApiResponse)
def update_operation_type(
    type_code: str,
    dto: OperationTypeUpdate,
    db: Session = Depends(get_db)
):
    """
    更新操作类型
    """
    item = db.query(OperationType).filter(OperationType.type_code == type_code).first()
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"操作类型 '{type_code}' 不存在"
        )
    
    if dto.type_code is not None:
        item.type_code = dto.type_code
    if dto.type_name is not None:
        item.type_name = dto.type_name
    if dto.color_code is not None:
        item.color_code = dto.color_code
    if dto.sort_order is not None:
        item.sort_order = dto.sort_order
    if dto.is_active is not None:
        item.is_active = dto.is_active
    
    db.commit()
    db.refresh(item)
    return ApiResponse.success(item.to_dict(), "更新成功")


@router.delete("/{type_code}", response_model=ApiResponse)
def delete_operation_type(
    type_code: str,
    db: Session = Depends(get_db)
):
    """
    删除操作类型（软删除，设置为禁用）
    """
    item = db.query(OperationType).filter(OperationType.type_code == type_code).first()
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"操作类型 '{type_code}' 不存在"
        )
    
    item.is_active = 0
    db.commit()
    return ApiResponse.success(None, "删除成功")


@router.post("/init-default", response_model=ApiResponse)
def init_default_operation_types(
    db: Session = Depends(get_db)
):
    """
    初始化默认操作类型数据
    """
    default_types = [
        {"type_code": "create", "type_name": "创建", "color_code": "#07c160", "sort_order": 1},
        {"type_code": "save", "type_name": "保存", "color_code": "#1989fa", "sort_order": 2},
        {"type_code": "submit", "type_name": "提交", "color_code": "#ff976a", "sort_order": 3},
        {"type_code": "approve", "type_name": "审批通过", "color_code": "#07c160", "sort_order": 4},
        {"type_code": "reject", "type_name": "审批退回", "color_code": "#ee0a24", "sort_order": 5},
    ]
    
    created_count = 0
    for type_data in default_types:
        existing = db.query(OperationType).filter(OperationType.type_code == type_data["type_code"]).first()
        if not existing:
            item = OperationType(
                type_code=type_data["type_code"],
                type_name=type_data["type_name"],
                color_code=type_data["color_code"],
                sort_order=type_data["sort_order"],
                is_active=1
            )
            db.add(item)
            created_count += 1
    
    db.commit()
    return ApiResponse.success({"created_count": created_count}, f"初始化完成，新增 {created_count} 条记录")
