from typing import Optional
import logging
from fastapi import APIRouter, Depends, Query, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.services.project_info import ProjectInfoService
from app.schemas.project_info import (
    ProjectInfoCreate,
    ProjectInfoUpdate,
    ProjectInfoResponse,
    PaginatedResponse,
    ApiResponse
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/project-info", tags=["项目信息管理"])


@router.get("", response_model=PaginatedResponse)
def get_project_info_list(
    page: int = Query(0, ge=0, description="页码，从0开始"),
    size: int = Query(10, ge=1, le=100, description="每页大小"),
    project_name: Optional[str] = Query(None, description="项目名称（模糊查询）"),
    client_name: Optional[str] = Query(None, description="客户名称（模糊查询）"),
    db: Session = Depends(get_db)
):
    """
    获取项目信息列表，支持分页和条件查询
    """
    service = ProjectInfoService(db)
    items, total = service.get_all(page, size, project_name, client_name)
    items_dict = [item.to_dict() for item in items]
    return PaginatedResponse.success(items_dict, total, page, size)


@router.get("/{id}", response_model=ApiResponse)
def get_project_info_by_id(
    id: int,
    db: Session = Depends(get_db)
):
    """
    根据ID获取项目信息
    """
    service = ProjectInfoService(db)
    project_info = service.get_by_id(id)
    return ApiResponse.success(project_info.to_dict())


@router.post("", response_model=ApiResponse, status_code=status.HTTP_201_CREATED)
def create_project_info(
    dto: ProjectInfoCreate,
    db: Session = Depends(get_db)
):
    """
    创建新的项目信息
    """
    logger.info(f"📥 [创建项目] 接收到的数据: {dto.model_dump_json()}")

    service = ProjectInfoService(db)
    project_info = service.create(dto)

    logger.info(f"✅ [创建项目] 创建成功: id={project_info.id}, project_id={project_info.project_id}")
    return ApiResponse.success(project_info.to_dict(), "创建成功")


@router.put("/{id}", response_model=ApiResponse)
def update_project_info(
    id: int,
    dto: ProjectInfoUpdate,
    db: Session = Depends(get_db)
):
    """
    根据ID更新项目信息
    """
    service = ProjectInfoService(db)
    project_info = service.update(id, dto)
    return ApiResponse.success(project_info.to_dict(), "更新成功")


@router.delete("/{id}", response_model=ApiResponse)
def delete_project_info(
    id: int,
    cascade: bool = Query(False, description="是否级联删除关联数据"),
    db: Session = Depends(get_db)
):
    """
    根据ID删除项目信息
    
    参数:
    - cascade: 是否级联删除关联数据（工作计划、定期巡检、临时维修、零星用工、维保计划）
    """
    service = ProjectInfoService(db)
    result = service.delete(id, cascade=cascade)
    
    if result.get('deleted_related'):
        deleted_info = []
        for key, count in result['deleted_related'].items():
            name_map = {
                'work_plan': '工作计划',
                'periodic_inspection': '定期巡检',
                'temporary_repair': '临时维修',
                'spot_work': '零星用工',
                'maintenance_plan': '维保计划'
            }
            deleted_info.append(f"{count} 条{name_map.get(key, key)}")
        message = f"已删除项目【{result['project_name']}】及其关联的 {', '.join(deleted_info)}"
    else:
        message = "删除成功"
    
    return ApiResponse.success(None, message)


@router.get("/all/list", response_model=ApiResponse)
def get_all_project_info(
    db: Session = Depends(get_db)
):
    """
    获取所有项目信息列表，不分页
    """
    service = ProjectInfoService(db)
    items = service.get_all_unpaginated()
    return ApiResponse.success([item.to_dict() for item in items])
