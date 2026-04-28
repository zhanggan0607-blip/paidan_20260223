"""
临时维修API
提供临时维修工单的HTTP接口

权限说明：
- 列表查询：运维人员只能看到自己负责项目的工单，管理员可以看到所有数据
- 创建工单：部门经理创建工单时，选择项目后，工单自动分配给该项目的运维人员
- 更新工单：管理员可更新所有工单，运维人员只能更新自己负责项目的工单
- 删除工单：需要管理员或部门经理权限
"""
import logging

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import UserInfo, check_data_access, get_current_user_info, get_current_user_required, get_manager_user
from app.schemas.common import ApiResponse
from app.schemas.temporary_repair import (
    TemporaryRepairApprove,
    TemporaryRepairCreate,
    TemporaryRepairPartialUpdate,
    TemporaryRepairUpdate,
)
from app.services.temporary_repair import TemporaryRepairService
from app.utils.work_order_id_generator import generate_repair_id

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/temporary-repair", tags=["Temporary Repair Management"])


@router.get("/generate-id", response_model=ApiResponse)
def generate_temporary_repair_id(
    project_id: str = Query(..., description="项目编号"),
    db: Session = Depends(get_db),
    user_info: UserInfo = Depends(get_current_user_info)
):
    """
    生成临时维修单编号
    后端使用数据库序列保证唯一性，避免前端全量拉取数据
    """
    repair_id = generate_repair_id(db, project_id)
    return ApiResponse(
        code=200,
        message="success",
        data={"repair_id": repair_id}
    )


@router.get("/all/list", response_model=ApiResponse)
def get_all_temporary_repairs(
    db: Session = Depends(get_db),
    user_info: UserInfo = Depends(get_current_user_info)
):
    """
    获取所有临时维修（不分页）
    运维人员只能看到自己负责项目的工单，管理员可以看到所有数据
    """
    service = TemporaryRepairService(db)
    items = service.get_all_unpaginated()

    items = service.filter_by_user_access(items, user_info.name, user_info.is_manager)

    return ApiResponse(
        code=200,
        message="success",
        data=[item.to_list_dict() for item in items]
    )


@router.get("", response_model=ApiResponse)
def get_temporary_repairs_list(
    page: int = Query(0, ge=0, description="Page number, starts from 0"),
    size: int = Query(10, ge=1, le=1000, description="Page size"),
    project_name: str | None = Query(None, description="Project name (fuzzy search)"),
    repair_id: str | None = Query(None, description="Repair ID (fuzzy search)"),
    status: str | None = Query(None, description="Status"),
    db: Session = Depends(get_db),
    user_info: UserInfo = Depends(get_current_user_info)
):
    """
    分页获取临时维修列表
    运维人员只能看到自己负责项目的工单，管理员可以看到所有数据
    """
    service = TemporaryRepairService(db)
    maintenance_personnel = user_info.get_maintenance_personnel_filter()

    logger.info(f"[PC端临时维修] user={user_info.name}, is_manager={user_info.is_manager}, filter={maintenance_personnel}")

    items, total = service.get_all(
        page=page, size=size, project_name=project_name, repair_id=repair_id,
        status=status, maintenance_personnel=maintenance_personnel
    )
    items_dict = [item.to_list_dict() for item in items]
    return ApiResponse(
        code=200,
        message="success",
        data={
            'content': items_dict,
            'totalElements': total,
            'totalPages': (total + size - 1) // size,
            'size': size,
            'number': page,
            'first': page == 0,
            'last': page >= (total + size - 1) // size
        }
    )


@router.get("/{id}", response_model=ApiResponse)
def get_temporary_repair_by_id(
    id: int,
    db: Session = Depends(get_db),
    user_info: UserInfo = Depends(get_current_user_required)
):
    """
    根据ID获取临时维修详情
    管理员可查看所有工单，运维人员只能查看自己负责项目的工单
    """
    service = TemporaryRepairService(db)
    repair = service.get_by_id(id)

    logger.info(f"[临时维修详情] user_info: id={user_info.id}, name={user_info.name}, role={user_info.role}, is_manager={user_info.is_manager}")
    logger.info(f"[临时维修详情] repair: id={repair.id}, maintenance_personnel={repair.maintenance_personnel}")

    if not check_data_access(user_info, repair.maintenance_personnel):
        logger.warning(f"[临时维修详情] 权限拒绝: user={user_info.name}, maintenance_personnel={repair.maintenance_personnel}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权查看此工单"
        )

    return ApiResponse(
        code=200,
        message="success",
        data=repair.to_dict()
    )


@router.post("", response_model=ApiResponse, status_code=status.HTTP_201_CREATED)
def create_temporary_repair(
    dto: TemporaryRepairCreate,
    db: Session = Depends(get_db),
    user_info: UserInfo = Depends(get_current_user_required)
):
    """
    创建临时维修
    所有已认证用户均可创建
    """
    service = TemporaryRepairService(db)
    repair = service.create(dto, user_info.id, user_info.name)
    return ApiResponse(
        code=200,
        message="创建成功",
        data=repair.to_dict()
    )


@router.put("/{id}", response_model=ApiResponse)
def update_temporary_repair(
    id: int,
    dto: TemporaryRepairUpdate,
    db: Session = Depends(get_db),
    user_info: UserInfo = Depends(get_current_user_required)
):
    """
    更新临时维修
    管理员可更新所有工单，运维人员只能更新自己负责项目的工单

    权限说明：
    - 普通员工只能修改工单内容，不能修改状态为"已完成"或"已退回"
    - 状态审批（改为"已完成"或"已退回"）需要管理员或部门经理权限
    """
    service = TemporaryRepairService(db)
    existing = service.get_by_id(id)

    if not check_data_access(user_info, existing.maintenance_personnel):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权修改此工单"
        )

    if dto.status in ['已完成', '已退回'] and not user_info.is_manager:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="工单审批需要管理员或部门经理权限"
        )

    repair = service.update(id, dto, user_info.id, user_info.name)
    return ApiResponse(
        code=200,
        message="更新成功",
        data=repair.to_dict()
    )


@router.patch("/{id}", response_model=ApiResponse)
def partial_update_temporary_repair(
    id: int,
    dto: TemporaryRepairPartialUpdate,
    db: Session = Depends(get_db),
    user_info: UserInfo = Depends(get_current_user_required)
):
    """
    部分更新临时维修
    管理员可更新所有工单，运维人员只能更新自己负责项目的工单

    权限说明：
    - 普通员工只能修改工单内容，不能修改状态为"已完成"或"已退回"
    - 状态审批（改为"已完成"或"已退回"）需要管理员或部门经理权限
    """
    logger.info(f"=== PATCH临时维修工单 id={id} ===")
    logger.info(f"用户: {user_info.name}, is_manager: {user_info.is_manager}")
    logger.info(f"DTO类型: {type(dto)}")
    logger.info(f"DTO photos字段: {getattr(dto, 'photos', 'NO ATTR')}")
    logger.info(f"DTO所有字段: {dto.model_dump()}")
    logger.info(f"DTO非空字段: {dto.model_dump(exclude_none=True)}")
    logger.info(f"DTO已设置字段: {dto.model_dump(exclude_unset=True)}")
    
    service = TemporaryRepairService(db)
    existing = service.get_by_id(id)
    
    logger.info(f"现有工单photos: {existing.photos}")

    if not check_data_access(user_info, existing.maintenance_personnel):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权修改此工单"
        )

    if dto.status in ['已完成', '已退回'] and not user_info.is_manager:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="工单审批需要管理员或部门经理权限"
        )

    if dto.status == '已退回':
        if not dto.reject_reason or len(dto.reject_reason.strip()) < 10:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="请输入工单退回原因，至少10个字符"
            )
        if len(dto.reject_reason.strip()) > 500:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="退回原因不能超过500个字符"
            )

    repair = service.partial_update(id, dto, user_info.id, user_info.name)
    logger.info(f"更新后工单photos: {repair.photos}")
    return ApiResponse(
        code=200,
        message="更新成功",
        data=repair.to_dict()
    )


@router.post("/{id}/submit", response_model=ApiResponse)
def submit_temporary_repair(
    id: int,
    db: Session = Depends(get_db),
    user_info: UserInfo = Depends(get_current_user_required)
):
    """
    提交临时维修工单
    管理员可提交所有工单，运维人员只能提交自己的工单
    """
    service = TemporaryRepairService(db)
    existing = service.get_by_id(id)

    if not check_data_access(user_info, existing.maintenance_personnel):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权提交此工单"
        )

    repair = service.partial_update(id, TemporaryRepairPartialUpdate(status='待确认'), user_info.id, user_info.name)
    return ApiResponse(
        code=200,
        message="提交成功",
        data=repair.to_dict()
    )


@router.post("/{id}/recall", response_model=ApiResponse)
def recall_temporary_repair(
    id: int,
    db: Session = Depends(get_db),
    user_info: UserInfo = Depends(get_current_user_required)
):
    """
    撤回临时维修工单
    仅待确认状态可撤回，撤回后状态变为执行中
    管理员可撤回所有工单，运维人员只能撤回自己的工单
    """
    service = TemporaryRepairService(db)
    existing = service.get_by_id(id)

    if not existing:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="工单不存在"
        )

    if existing.status != '待确认':
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="只有待确认状态的工单才能撤回"
        )

    if not check_data_access(user_info, existing.maintenance_personnel):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权撤回此工单"
        )

    repair = service.partial_update(id, TemporaryRepairPartialUpdate(status='执行中'), user_info.id, user_info.name)
    return ApiResponse(
        code=200,
        message="撤回成功",
        data=repair.to_dict()
    )


@router.post("/{id}/approve", response_model=ApiResponse)
def approve_temporary_repair(
    id: int,
    dto: TemporaryRepairApprove,
    db: Session = Depends(get_db),
    user_info: UserInfo = Depends(get_manager_user)
):
    """
    审批临时维修工单
    需要管理员或部门经理权限
    """
    service = TemporaryRepairService(db)
    
    if dto.approved:
        repair = service.partial_update(id, TemporaryRepairPartialUpdate(status='已完成'), user_info.id, user_info.name)
        message = "审批通过"
    else:
        if not dto.reject_reason or len(dto.reject_reason.strip()) < 10:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="请输入工单退回原因，至少10个字符"
            )
        repair = service.partial_update(
            id, 
            TemporaryRepairPartialUpdate(status='已退回', reject_reason=dto.reject_reason), 
            user_info.id, 
            user_info.name
        )
        message = "已退回"

    return ApiResponse(
        code=200,
        message=message,
        data=repair.to_dict()
    )


@router.delete("/{id}", response_model=ApiResponse)
def delete_temporary_repair(
    id: int,
    db: Session = Depends(get_db),
    user_info: UserInfo = Depends(get_manager_user)
):
    """
    删除临时维修（软删除）
    需要管理员或部门经理权限
    """
    service = TemporaryRepairService(db)
    service.delete(id, user_info.id, user_info.name)
    return ApiResponse(
        code=200,
        message="删除成功",
        data=None
    )
