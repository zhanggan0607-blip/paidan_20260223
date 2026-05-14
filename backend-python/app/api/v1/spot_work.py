"""
零星用工API
提供零星用工工单的HTTP接口

权限说明：
- 列表查询：运维人员只能看到自己的数据，管理员可以看到所有数据
- 创建工单：需要管理员或部门经理权限
- 更新工单：管理员可更新所有工单，运维人员只能更新自己的工单
- 删除工单：需要管理员或部门经理权限
"""
from app.utils.logging_config import get_logger

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import UserInfo, check_data_access, get_current_user_required, get_manager_user
from app.schemas.common import ApiResponse, PaginatedResponse
from app.schemas.spot_work import SpotWorkApprove, SpotWorkCreate, SpotWorkPartialUpdate, SpotWorkUpdate, WorkerInfo, QuickFillRequest, WorkersRequest
from app.services.personnel import PersonnelService
from app.services.spot_work import SpotWorkService
from app.utils.work_order_id_generator import generate_spot_work_id

logger = get_logger(__name__)
router = APIRouter(prefix="/spot-work", tags=["Spot Work Management"])


@router.get("/generate-id", response_model=ApiResponse)
def generate_spot_work_id_endpoint(
    project_id: str = Query(..., description="项目编号"),
    db: Session = Depends(get_db),
    user_info: UserInfo = Depends(get_current_user_required)
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
    user_info: UserInfo = Depends(get_current_user_required)
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
    statuses: str | None = Query(None, description="Multiple statuses (comma-separated)"),
    db: Session = Depends(get_db),
    user_info: UserInfo = Depends(get_current_user_required)
):
    """
    分页获取零星用工列表
    普通用户只能看到自己的数据，管理员可以看到所有数据
    """
    service = SpotWorkService(db)
    maintenance_personnel = user_info.get_maintenance_personnel_filter()

    logger.info(f"[PC端零星用工] user={user_info.name}, is_manager={user_info.is_manager}, filter={maintenance_personnel}")

    status_list = None
    if statuses:
        status_list = [s.strip() for s in statuses.split(',') if s.strip()]

    items_dict, total = service.get_all_with_workers(
        page=page, size=size, project_name=project_name, work_id=work_id,
        status=status, maintenance_personnel=maintenance_personnel,
        statuses=status_list
    )

    return PaginatedResponse.success(items_dict, total, page, size)


@router.post("/quick-fill", response_model=ApiResponse, status_code=status.HTTP_201_CREATED)
def quick_fill_spot_work(
    dto: QuickFillRequest,
    db: Session = Depends(get_db),
    user_info: UserInfo = Depends(get_current_user_required)
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
    db: Session = Depends(get_db),
    user_info: UserInfo = Depends(get_current_user_required)
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
    project_id: str | None = Query(None, description="项目编号（用于同工单去重检查）"),
    start_date: str | None = Query(None, description="开始日期（用于同工单去重检查）"),
    end_date: str | None = Query(None, description="结束日期（用于同工单去重检查）"),
    db: Session = Depends(get_db),
    user_info: UserInfo = Depends(get_current_user_required)
):
    """
    检查身份证号码是否已存在
    用于前端在OCR识别后立即检查，避免重复录入
    如果关联的工单已完成，则允许复用
    如果提供了project_id和日期参数，还会检查同一工单内是否已录入
    """
    from datetime import datetime as dt
    from app.repositories.spot_work import SpotWorkRepository

    repository = SpotWorkRepository(db)

    if project_id:
        start = None
        end = None
        try:
            if start_date:
                start = dt.strptime(start_date, '%Y-%m-%d').date()
            if end_date:
                end = dt.strptime(end_date, '%Y-%m-%d').date()
        except Exception:
            pass

        existing_in_work = repository.find_worker_in_same_work(
            project_id=project_id,
            id_card_number=id_card_number,
            start_date=start,
            end_date=end
        )
        if existing_in_work:
            return ApiResponse(
                code=200,
                message="该身份证号码已在本工单中录入",
                data={
                    "exists": True,
                    "can_reuse": False,
                    "duplicate_in_work": True,
                    "name": existing_in_work.name,
                    "project_name": existing_in_work.project_name,
                    "project_id": existing_in_work.project_id,
                }
            )

    reuse_check = repository.check_worker_can_be_reused(id_card_number)

    if reuse_check['exists']:
        worker_info = reuse_check['worker_info']
        return ApiResponse(
            code=200,
            message="身份证号码已存在",
            data={
                "exists": True,
                "can_reuse": reuse_check['can_reuse'],
                "duplicate_in_work": False,
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
            data={"exists": False, "can_reuse": True, "duplicate_in_work": False}
        )


@router.get("/workers/all", response_model=ApiResponse)
def get_all_workers(
    db: Session = Depends(get_db),
    user_info: UserInfo = Depends(get_current_user_required)
):
    """
    获取所有已录入的施工人员（去重）
    用于前端选择已录入人员
    """
    from sqlalchemy import func, distinct
    from app.models.spot_work_worker import SpotWorkWorker

    try:
        service = SpotWorkService(db)
        result = service.get_all_workers()
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
    db: Session = Depends(get_db),
    user_info: UserInfo = Depends(get_current_user_required)
):
    """
    保存施工人员信息
    根据身份证号码+项目编号+日期范围判断是否已存在，避免重复保存
    包含身份证号码强认证
    """
    logger.info(f"收到施工人员保存请求: project_id={dto.project_id}, workers_count={len(dto.workers)}")
    for i, w in enumerate(dto.workers):
        masked_id = f"{w.idCardNumber[:3]}****{w.idCardNumber[-4:]}" if w.idCardNumber and len(w.idCardNumber) >= 7 else "***"
        logger.info(f"工人{i+1}: name={w.name}, idCardNumber={masked_id}")

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


@router.delete("/workers/{worker_id}", response_model=ApiResponse)
def delete_worker(
    worker_id: int,
    db: Session = Depends(get_db),
    user_info: UserInfo = Depends(get_current_user_required)
):
    """
    删除施工人员
    已关联工单的施工人员不允许删除
    """
    from app.exceptions import ValidationException

    service = SpotWorkService(db)
    try:
        deleted = service.delete_worker(worker_id)
        if not deleted:
            return ApiResponse(code=404, message="施工人员不存在", data=None)
        return ApiResponse(code=200, message="删除成功", data=None)
    except ValidationException:
        raise


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

    if dto.status == '待确认' and existing.status == '执行中':
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="请使用提交接口(/submit)提交工单，不能通过更新接口直接修改状态"
        )

    if dto.status == '待确认' and existing.status == '已退回':
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="请使用提交接口(/submit)重新提交工单，不能通过更新接口直接修改状态"
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
        from app.utils.work_order_utils import validate_reject_reason
        validate_reject_reason(dto.reject_reason)

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
    from app.utils.work_order_utils import submit_work_order
    service = SpotWorkService(db)
    work = submit_work_order(id, service, user_info, SpotWorkPartialUpdate)
    return ApiResponse.success(work.to_dict(), "提交成功")


@router.post("/{id}/recall", response_model=ApiResponse)
def recall_spot_work(
    id: int,
    db: Session = Depends(get_db),
    user_info: UserInfo = Depends(get_current_user_required)
):
    from app.utils.work_order_utils import recall_work_order
    service = SpotWorkService(db)
    work = recall_work_order(id, service, user_info, SpotWorkPartialUpdate)
    return ApiResponse.success(work.to_dict(), "撤回成功")


@router.post("/{id}/approve", response_model=ApiResponse)
def approve_spot_work(
    id: int,
    dto: SpotWorkApprove,
    db: Session = Depends(get_db),
    user_info: UserInfo = Depends(get_manager_user)
):
    from app.utils.work_order_utils import approve_work_order
    service = SpotWorkService(db)
    work, message = approve_work_order(id, dto, service, user_info, SpotWorkPartialUpdate)
    return ApiResponse.success(work.to_dict(), message)


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
