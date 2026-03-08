"""
零星用工API
提供零星用工工单的HTTP接口

权限说明：
- 列表查询：运维人员只能看到自己的数据，管理员可以看到所有数据
- 创建工单：需要管理员或部门经理权限
- 更新工单：管理员可更新所有工单，运维人员只能更新自己的工单
- 删除工单：需要管理员或部门经理权限
"""
import logging

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import UserInfo, check_data_access, get_current_user_info, get_manager_user
from app.schemas.common import ApiResponse
from app.schemas.spot_work import SpotWorkCreate, SpotWorkPartialUpdate, SpotWorkUpdate
from app.services.personnel import PersonnelService
from app.services.spot_work import SpotWorkService

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/spot-work", tags=["Spot Work Management"])


class WorkerInfo(BaseModel):
    name: str
    gender: str | None = None
    birthDate: str | None = None
    address: str | None = None
    idCardNumber: str
    issuingAuthority: str | None = None
    validPeriod: str | None = None
    idCardFront: str
    idCardBack: str


class QuickFillRequest(BaseModel):
    project_id: str
    project_name: str
    plan_start_date: str
    plan_end_date: str
    work_content: str | None = None
    remark: str | None = None
    client_contact: str | None = None
    client_contact_info: str | None = None
    photos: str | None = None
    signature: str | None = None
    worker_count: int | None = 0


class WorkersRequest(BaseModel):
    project_id: str
    project_name: str
    start_date: str
    end_date: str
    workers: list[WorkerInfo]


@router.get("/all/list", response_model=ApiResponse)
def get_all_spot_works(
    db: Session = Depends(get_db),
    user_info: UserInfo = Depends(get_current_user_info)
):
    """
    获取所有零星用工（不分页）
    普通用户只能看到自己的数据，管理员可以看到所有数据
    """
    service = SpotWorkService(db)
    items = service.get_all_unpaginated()

    if not user_info.is_manager and user_info.name:
        items = [item for item in items if item.maintenance_personnel == user_info.name]

    return ApiResponse(
        code=200,
        message="success",
        data=[item.to_dict() for item in items]
    )


@router.get("", response_model=ApiResponse)
def get_spot_works_list(
    page: int = Query(0, ge=0, description="Page number, starts from 0"),
    size: int = Query(10, ge=1, le=1000, description="Page size"),
    project_name: str | None = Query(None, description="Project name (fuzzy search)"),
    work_id: str | None = Query(None, description="Work ID (fuzzy search)"),
    status: str | None = Query(None, description="Status"),
    db: Session = Depends(get_db),
    user_info: UserInfo = Depends(get_current_user_info)
):
    """
    分页获取零星用工列表
    普通用户只能看到自己的数据，管理员可以看到所有数据
    """
    service = SpotWorkService(db)
    maintenance_personnel = user_info.get_maintenance_personnel_filter()

    logger.info(f"[PC端零星用工] user={user_info.name}, is_manager={user_info.is_manager}, filter={maintenance_personnel}")

    items_dict, total = service.get_all_with_workers(
        page=page, size=size, project_name=project_name, work_id=work_id,
        status=status, maintenance_personnel=maintenance_personnel
    )

    return ApiResponse(
        code=200,
        message="success",
        data={
            'content': items_dict,
            'totalElements': total,
            'totalPages': (total + size - 1) // size if size > 0 else 0,
            'size': size,
            'number': page,
            'first': page == 0,
            'last': page >= (total + size - 1) // size if size > 0 else True
        }
    )


@router.post("/quick-fill", response_model=ApiResponse, status_code=status.HTTP_201_CREATED)
def quick_fill_spot_work(
    dto: QuickFillRequest,
    db: Session = Depends(get_db),
    user_info: UserInfo = Depends(get_current_user_info)
):
    """
    快速填报零星用工
    自动生成工单编号：YG-项目编号-年月日-序号
    """
    service = SpotWorkService(db)

    work = service.quick_fill(
        project_id=dto.project_id,
        project_name=dto.project_name,
        plan_start_date=dto.plan_start_date,
        plan_end_date=dto.plan_end_date,
        work_content=dto.work_content,
        remark=dto.remark,
        client_contact=dto.client_contact,
        client_contact_info=dto.client_contact_info,
        photos=dto.photos,
        signature=dto.signature,
        maintenance_personnel=user_info.name,
        operator_id=user_info.id,
        operator_name=user_info.name
    )

    return ApiResponse(
        code=200,
        message="提交成功",
        data={"work_id": work.work_id}
    )


@router.get("/workers", response_model=ApiResponse)
def get_workers(
    project_id: str = Query(..., description="项目编号"),
    start_date: str = Query(..., description="开始日期"),
    end_date: str = Query(..., description="结束日期"),
    db: Session = Depends(get_db)
):
    """
    获取施工人员列表
    使用日期部分比较，避免时间部分导致的匹配问题
    """
    service = SpotWorkService(db)
    workers = service.get_workers_by_project_and_date(project_id, start_date, end_date)

    return ApiResponse(
        code=200,
        message="success",
        data=[w.to_dict() for w in workers]
    )


@router.post("/workers", response_model=ApiResponse, status_code=status.HTTP_201_CREATED)
def save_workers(
    dto: WorkersRequest,
    db: Session = Depends(get_db)
):
    """
    保存施工人员信息
    根据身份证号码+项目编号+日期范围判断是否已存在，避免重复保存
    包含身份证号码强认证
    """
    logger.info(f"收到施工人员保存请求: project_id={dto.project_id}, workers_count={len(dto.workers)}")
    for i, w in enumerate(dto.workers):
        logger.info(f"工人{i+1}: name={w.name}, idCardNumber={w.idCardNumber}, idCardFront={bool(w.idCardFront)}, idCardBack={bool(w.idCardBack)}")

    service = SpotWorkService(db)

    workers_data = [w.model_dump() for w in dto.workers]

    saved_count, skipped_count = service.save_workers(
        project_id=dto.project_id,
        project_name=dto.project_name,
        start_date=dto.start_date,
        end_date=dto.end_date,
        workers_data=workers_data
    )

    return ApiResponse(
        code=200,
        message=f"保存成功，新增{saved_count}人，跳过{skipped_count}人重复数据",
        data={"saved_count": saved_count, "skipped_count": skipped_count}
    )


@router.get("/{id}", response_model=ApiResponse)
def get_spot_work_by_id(
    id: int,
    db: Session = Depends(get_db),
    user_info: UserInfo = Depends(get_current_user_info)
):
    """
    根据ID获取零星用工详情（包含工人信息）
    管理员可查看所有工单，运维人员只能查看自己的工单
    """
    service = SpotWorkService(db)
    work = service.get_by_id(id)

    if not check_data_access(user_info, work.maintenance_personnel):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权查看此工单"
        )

    work_dict = service.get_by_id_with_workers(id)

    return ApiResponse(
        code=200,
        message="success",
        data=work_dict
    )


@router.post("", response_model=ApiResponse, status_code=status.HTTP_201_CREATED)
def create_spot_work(
    dto: SpotWorkCreate,
    db: Session = Depends(get_db),
    user_info: UserInfo = Depends(get_manager_user)
):
    """
    创建零星用工
    需要管理员或部门经理权限
    """
    if dto.maintenance_personnel:
        personnel_service = PersonnelService(db)
        if not personnel_service.validate_personnel_exists(dto.maintenance_personnel):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"运维人员'{dto.maintenance_personnel}'不存在于人员列表中，请先添加该人员"
            )

    service = SpotWorkService(db)
    work = service.create(dto, user_info.id, user_info.name)

    return ApiResponse(
        code=200,
        message="Created successfully",
        data=work.to_dict()
    )


@router.put("/{id}", response_model=ApiResponse)
def update_spot_work(
    id: int,
    dto: SpotWorkUpdate,
    db: Session = Depends(get_db),
    user_info: UserInfo = Depends(get_current_user_info)
):
    """
    更新零星用工
    管理员可更新所有工单，运维人员只能更新自己的工单

    权限说明：
    - 普通员工只能修改工单内容，不能修改状态为"已完成"或"已退回"
    - 状态审批（改为"已完成"或"已退回"）需要管理员或部门经理权限
    """
    if dto.maintenance_personnel:
        personnel_service = PersonnelService(db)
        if not personnel_service.validate_personnel_exists(dto.maintenance_personnel):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"运维人员'{dto.maintenance_personnel}'不存在于人员列表中，请先添加该人员"
            )

    service = SpotWorkService(db)
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

    work = service.update(id, dto)
    return ApiResponse(
        code=200,
        message="Updated successfully",
        data=work.to_dict()
    )


@router.patch("/{id}", response_model=ApiResponse)
def partial_update_spot_work(
    id: int,
    dto: SpotWorkPartialUpdate,
    db: Session = Depends(get_db),
    user_info: UserInfo = Depends(get_current_user_info)
):
    """
    部分更新零星用工
    管理员可更新所有工单，运维人员只能更新自己的工单

    权限说明：
    - 普通员工只能修改工单内容，不能修改状态为"已完成"或"已退回"
    - 状态审批（改为"已完成"或"已退回"）需要管理员或部门经理权限
    """
    if dto.maintenance_personnel:
        personnel_service = PersonnelService(db)
        if not personnel_service.validate_personnel_exists(dto.maintenance_personnel):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"运维人员'{dto.maintenance_personnel}'不存在于人员列表中，请先添加该人员"
            )

    service = SpotWorkService(db)
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

    work = service.partial_update(id, dto)
    return ApiResponse(
        code=200,
        message="Updated successfully",
        data=work.to_dict()
    )


@router.delete("/{id}", response_model=ApiResponse)
def delete_spot_work(
    id: int,
    db: Session = Depends(get_db),
    user_info: UserInfo = Depends(get_manager_user)
):
    """
    删除零星用工（软删除）
    需要管理员或部门经理权限
    """
    service = SpotWorkService(db)
    service.delete(id, user_info.id, user_info.name)

    return ApiResponse(
        code=200,
        message="Deleted successfully",
        data=None
    )
