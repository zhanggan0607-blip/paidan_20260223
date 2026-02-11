from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Optional
from app.database import get_db
from app.schemas.inspection_item import InspectionItemCreate, InspectionItemUpdate, InspectionItem
from app.services.inspection_item import InspectionItemService
from app.schemas.common import ApiResponse, PaginatedResponse

router = APIRouter(prefix="/inspection-item", tags=["巡检事项管理"])

@router.get("/all/list", response_model=ApiResponse)
def get_all_inspection_items(
    db: Session = Depends(get_db)
):
    service = InspectionItemService(db)
    items = service.get_all_items()
    return ApiResponse(code=200, message="获取成功", data=items)

@router.get("", response_model=PaginatedResponse)
def get_inspection_item_list(
    page: int = 0,
    size: int = 10,
    keyword: Optional[str] = None,
    db: Session = Depends(get_db)
):
    service = InspectionItemService(db)
    if keyword:
        items = service.search_items(keyword)
        total = len(items)
        start_idx = page * size
        paginated_items = items[start_idx:start_idx + size]
    else:
        items, total = service.get_paginated_items(skip=page * size, limit=size)
        paginated_items = items

    return PaginatedResponse(
        code=200,
        message="获取成功",
        data={
            "content": paginated_items,
            "totalElements": total,
            "totalPages": (total + size - 1) // size,
            "size": size,
            "number": page,
            "first": page == 0,
            "last": (page + 1) * size >= total
        }
    )

@router.get("/{id}", response_model=ApiResponse)
def get_inspection_item_by_id(
    id: int,
    db: Session = Depends(get_db)
):
    service = InspectionItemService(db)
    item = service.get_item_by_id(id)
    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="巡检事项不存在")
    return ApiResponse(code=200, message="获取成功", data=item)

@router.post("", response_model=ApiResponse, status_code=status.HTTP_201_CREATED)
def create_inspection_item(
    item_data: InspectionItemCreate,
    db: Session = Depends(get_db)
):
    service = InspectionItemService(db)
    try:
        item = service.create_item(item_data)
        return ApiResponse(code=200, message="创建成功", data=item)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.put("/{id}", response_model=ApiResponse)
def update_inspection_item(
    id: int,
    item_data: InspectionItemUpdate,
    db: Session = Depends(get_db)
):
    service = InspectionItemService(db)
    try:
        item = service.update_item(id, item_data)
        if not item:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="巡检事项不存在")
        return ApiResponse(code=200, message="更新成功", data=item)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.delete("/{id}", response_model=ApiResponse)
def delete_inspection_item(
    id: int,
    db: Session = Depends(get_db)
):
    service = InspectionItemService(db)
    success = service.delete_item(id)
    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="巡检事项不存在")
    return ApiResponse(code=200, message="删除成功", data=None)
