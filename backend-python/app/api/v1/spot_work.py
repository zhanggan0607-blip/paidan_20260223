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
from app.dependencies import UserInfo, check_data_access, get_current_user_info, get_current_user_required, get_manager_user
from app.schemas.common import ApiResponse
from app.schemas.spot_work import SpotWorkApprove, SpotWorkCreate, SpotWorkPartialUpdate, SpotWorkUpdate
from app.services.personnel import PersonnelService
from app.services.spot_work import SpotWorkService
from app.utils.work_order_id_generator import generate_spot_work_id

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


@router.get("/generate-id", response_model=ApiResponse)
def generate_spot_work_id_endpoint(
    project_id: str = Query(..., description="项目编号"),
    db: Session = Depends(get_db),
    user_info: UserInfo = Depends(get_current_user_info)
):
    """
    生成零星用工单编号
    后端使用数据库序列保证唯一性，避免前端全量拉取数据
    """
    work_id = generate_spot_work_id(db, project_id)
    return ApiResponse(
        code=200,
        message="success",
        data={"work_id": work_id}
    )


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
        data=[item.to_list_dict() for item in items]
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


@router.get("/workers/check-id-card", response_model=ApiResponse)
def check_id_card_exists(
    id_card_number: str = Query(..., description="身份证号码"),
    db: Session = Depends(get_db)
):
    """
    检查身份证号码是否已存在
    用于前端在OCR识别后立即检查，避免重复录入
    如果关联的工单已完成，则允许复用
    """
    from app.repositories.spot_work import SpotWorkRepository

    repository = SpotWorkRepository(db)
    reuse_check = repository.check_worker_can_be_reused(id_card_number)

    if reuse_check['exists']:
        worker_info = reuse_check['worker_info']
        return ApiResponse(
            code=200,
            message="身份证号码已存在",
            data={
                "exists": True,
                "can_reuse": reuse_check['can_reuse'],
                "name": worker_info['name'],
                "project_name": worker_info['project_name'],
                "project_id": worker_info['project_id'],
                "work_status": reuse_check['work_status'],
                "work_id": reuse_check.get('work_id')
            }
        )
    else:
        return ApiResponse(
            code=200,
            message="身份证号码未录入",
            data={"exists": False, "can_reuse": True}
        )


@router.get("/workers/all", response_model=ApiResponse)
def get_all_workers(
    db: Session = Depends(get_db)
):
    """
    获取所有已录入的施工人员（去重）
    用于前端选择已录入人员
    """
    from sqlalchemy import func, distinct
    from app.models.spot_work_worker import SpotWorkWorker

    try:
        subquery = db.query(
            SpotWorkWorker.id_card_number,
            func.max(SpotWorkWorker.id).label('max_id')
        ).group_by(
            SpotWorkWorker.id_card_number
        ).subquery()

        workers = db.query(SpotWorkWorker).join(
            subquery,
            SpotWorkWorker.id == subquery.c.max_id
        ).all()

        result = []
        for w in workers:
            result.append({
                "name": w.name,
                "gender": w.gender,
                "birthDate": w.birth_date,
                "address": w.address,
                "idCardNumber": w.id_card_number,
                "issuingAuthority": w.issuing_authority,
                "validPeriod": w.valid_period,
                "idCardFront": w.id_card_front,
                "idCardBack": w.id_card_back
            })

        return ApiResponse(
            code=200,
            message="success",
            data=result
        )
    except Exception as e:
        logger.error(f"获取所有施工人员失败: {str(e)}")
        return ApiResponse(
            code=500,
            message="获取施工人员列表失败",
            data=[]
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
    user_info: UserInfo = Depends(get_current_user_required)
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
        message="创建成功",
        data=work.to_dict()
    )


@router.put("/{id}", response_model=ApiResponse)
def update_spot_work(
    id: int,
    dto: SpotWorkUpdate,
    db: Session = Depends(get_db),
    user_info: UserInfo = Depends(get_current_user_required)
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
        message="更新成功",
        data=work.to_dict()
    )


@router.patch("/{id}", response_model=ApiResponse)
def partial_update_spot_work(
    id: int,
    dto: SpotWorkPartialUpdate,
    db: Session = Depends(get_db),
    user_info: UserInfo = Depends(get_current_user_required)
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

    work = service.partial_update(id, dto)
    return ApiResponse(
        code=200,
        message="更新成功",
        data=work.to_dict()
    )


@router.post("/{id}/submit", response_model=ApiResponse)
def submit_spot_work(
    id: int,
    db: Session = Depends(get_db),
    user_info: UserInfo = Depends(get_current_user_required)
):
    """
    提交零星用工工单
    管理员可提交所有工单，运维人员只能提交自己的工单
    """
    service = SpotWorkService(db)
    existing = service.get_by_id(id)

    if not check_data_access(user_info, existing.maintenance_personnel):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权提交此工单"
        )

    work = service.partial_update(id, SpotWorkPartialUpdate(status='待确认'), user_info.id, user_info.name)
    return ApiResponse(
        code=200,
        message="提交成功",
        data=work.to_dict()
    )


@router.post("/{id}/recall", response_model=ApiResponse)
def recall_spot_work(
    id: int,
    db: Session = Depends(get_db),
    user_info: UserInfo = Depends(get_current_user_required)
):
    """
    撤回零星用工工单
    仅待确认状态可撤回，撤回后状态变为执行中
    管理员可撤回所有工单，运维人员只能撤回自己的工单
    """
    service = SpotWorkService(db)
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

    work = service.partial_update(id, SpotWorkPartialUpdate(status='执行中'), user_info.id, user_info.name)
    return ApiResponse(
        code=200,
        message="撤回成功",
        data=work.to_dict()
    )


@router.post("/{id}/approve", response_model=ApiResponse)
def approve_spot_work(
    id: int,
    dto: SpotWorkApprove,
    db: Session = Depends(get_db),
    user_info: UserInfo = Depends(get_manager_user)
):
    """
    审批零星用工工单
    需要管理员或部门经理权限
    """
    service = SpotWorkService(db)
    
    if dto.approved:
        work = service.partial_update(id, SpotWorkPartialUpdate(status='已完成'), user_info.id, user_info.name)
        message = "审批通过"
    else:
        if not dto.reject_reason or len(dto.reject_reason.strip()) < 10:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="请输入工单退回原因，至少10个字符"
            )
        work = service.partial_update(
            id, 
            SpotWorkPartialUpdate(status='已退回', reject_reason=dto.reject_reason), 
            user_info.id, 
            user_info.name
        )
        message = "已退回"

    return ApiResponse(
        code=200,
        message=message,
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
        message="删除成功",
        data=None
    )
