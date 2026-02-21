from typing import Optional
from fastapi import APIRouter, Depends, Query, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.services.personnel import PersonnelService
from app.schemas.personnel import (
    PersonnelCreate,
    PersonnelUpdate,
    PersonnelResponse,
    PaginatedResponse,
    ApiResponse
)

router = APIRouter(prefix="/personnel", tags=["Personnel Management"])


# TODO: 人员管理API - 考虑加入批量导入/导出接口
# FIXME: 权限校验应该统一在中间件处理

@router.get("/all/list", response_model=ApiResponse)
def get_all_personnel(
    db: Session = Depends(get_db)
):
    """
    获取所有人员列表（不分页）
    
    返回系统中所有人员的完整列表，用于下拉选择等场景
    
    Returns:
        ApiResponse: 包含所有人员列表的响应对象
    """
    service = PersonnelService(db)
    items = service.get_all_unpaginated()
    return ApiResponse.success([item.to_dict() for item in items])


@router.get("", response_model=PaginatedResponse)
def get_personnel_list(
    page: int = Query(0, ge=0, description="Page number, starts from 0"),
    size: int = Query(10, ge=1, le=2000, description="Page size"),
    name: Optional[str] = Query(None, description="Name (fuzzy search)"),
    department: Optional[str] = Query(None, description="Department (fuzzy search)"),
    current_user_role: Optional[str] = Query(None, description="Current user role"),
    current_user_department: Optional[str] = Query(None, description="Current user department"),
    db: Session = Depends(get_db)
):
    """
    分页获取人员列表
    
    支持按姓名、部门模糊查询，并根据当前用户角色进行权限过滤
    
    Args:
        page: 页码，从0开始
        size: 每页大小，默认10条
        name: 姓名模糊查询条件
        department: 部门模糊查询条件
        current_user_role: 当前用户角色，用于权限控制
        current_user_department: 当前用户部门，用于权限控制
    
    Returns:
        PaginatedResponse: 分页响应对象，包含人员列表和分页信息
    """
    service = PersonnelService(db)
    items, total = service.get_all(
        page=page, size=size, name=name, department=department,
        current_user_role=current_user_role, current_user_department=current_user_department
    )
    items_dict = [item.to_dict() for item in items]
    return PaginatedResponse.success(items_dict, total, page, size)


@router.get("/{id}", response_model=ApiResponse)
def get_personnel_by_id(
    id: int,
    db: Session = Depends(get_db)
):
    """
    根据ID获取人员详情
    
    Args:
        id: 人员ID
    
    Returns:
        ApiResponse: 包含人员详情的响应对象
    
    Raises:
        HTTPException: 人员不存在时返回404错误
    """
    service = PersonnelService(db)
    personnel = service.get_by_id(id)
    return ApiResponse.success(personnel.to_dict())


@router.post("", response_model=ApiResponse, status_code=status.HTTP_201_CREATED)
def create_personnel(
    dto: PersonnelCreate,
    db: Session = Depends(get_db)
):
    """
    创建新人员
    
    Args:
        dto: 人员创建数据传输对象
    
    Returns:
        ApiResponse: 包含创建成功的人员信息的响应对象
    
    Raises:
        HTTPException: 数据验证失败时返回400错误
    """
    service = PersonnelService(db)
    personnel = service.create(dto)
    return ApiResponse.success(personnel.to_dict(), "Created successfully")


@router.put("/{id}", response_model=ApiResponse)
def update_personnel(
    id: int,
    dto: PersonnelUpdate,
    db: Session = Depends(get_db)
):
    """
    更新人员信息
    
    Args:
        id: 人员ID
        dto: 人员更新数据传输对象
    
    Returns:
        ApiResponse: 包含更新后的人员信息的响应对象
    
    Raises:
        HTTPException: 人员不存在时返回404错误
    """
    service = PersonnelService(db)
    personnel = service.update(id, dto)
    return ApiResponse.success(personnel.to_dict(), "Updated successfully")


@router.delete("/{id}", response_model=ApiResponse)
def delete_personnel(
    id: int,
    db: Session = Depends(get_db)
):
    """
    删除人员
    
    Args:
        id: 人员ID
    
    Returns:
        ApiResponse: 删除成功的响应对象
    
    Raises:
        HTTPException: 人员不存在时返回404错误
    """
    service = PersonnelService(db)
    service.delete(id)
    return ApiResponse.success(None, "Deleted successfully")
