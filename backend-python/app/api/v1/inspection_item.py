
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import UserInfo, get_manager_user
from app.schemas.common import ApiResponse, PaginatedResponse
from app.schemas.inspection_item import InspectionItemCreate, InspectionItemUpdate
from app.services.inspection_item import InspectionItemService

router = APIRouter(prefix="/inspection-item", tags=["巡检事项管理"])

@router.get("/tree", response_model=ApiResponse)
def get_inspection_item_tree(
    db: Session = Depends(get_db)
):
    service = InspectionItemService(db)
    tree = service.get_tree()
    return ApiResponse(code=200, message="获取成功", data=tree)

@router.get("/all/list", response_model=ApiResponse)
def get_all_inspection_items(
    db: Session = Depends(get_db)
):
    service = InspectionItemService(db)
    items = service.get_all_items()
    return ApiResponse(code=200, message="获取成功", data=[item.to_dict() for item in items])

@router.get("", response_model=PaginatedResponse)
def get_inspection_item_list(
    page: int = 0,
    size: int = 10,
    keyword: str | None = None,
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
            "content": [item.to_dict() for item in paginated_items],
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
    return ApiResponse(code=200, message="获取成功", data=item.to_dict())

@router.post("", response_model=ApiResponse, status_code=status.HTTP_201_CREATED)
def create_inspection_item(
    item_data: InspectionItemCreate,
    db: Session = Depends(get_db),
    user_info: UserInfo = Depends(get_manager_user)
):
    """
    创建巡检事项
    需要管理员或部门经理权限
    """
    service = InspectionItemService(db)
    try:
        item = service.create_item(item_data)
        return ApiResponse(code=200, message="创建成功", data=item.to_dict())
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)) from e

@router.put("/{id}", response_model=ApiResponse)
def update_inspection_item(
    id: int,
    item_data: InspectionItemUpdate,
    db: Session = Depends(get_db),
    user_info: UserInfo = Depends(get_manager_user)
):
    """
    更新巡检事项
    需要管理员或部门经理权限
    """
    service = InspectionItemService(db)
    try:
        item = service.update_item(id, item_data)
        if not item:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="巡检事项不存在")
        return ApiResponse(code=200, message="更新成功", data=item.to_dict())
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)) from e

@router.delete("/{id}", response_model=ApiResponse)
def delete_inspection_item(
    id: int,
    db: Session = Depends(get_db),
    user_info: UserInfo = Depends(get_manager_user)
):
    """
    删除巡检事项
    需要管理员或部门经理权限
    """
    service = InspectionItemService(db)
    success = service.delete_item(id)
    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="巡检事项不存在")
    return ApiResponse(code=200, message="删除成功", data=None)
