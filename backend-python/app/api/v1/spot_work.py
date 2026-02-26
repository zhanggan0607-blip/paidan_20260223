from typing import Optional, List
import json
import logging
from fastapi import APIRouter, Depends, Query, HTTPException, status, Request
from sqlalchemy.orm import Session
from app.database import get_db
from app.services.spot_work import SpotWorkService
from app.services.personnel import PersonnelService
from app.schemas.common import ApiResponse, PaginatedResponse
from app.schemas.spot_work import SpotWorkCreate, SpotWorkUpdate, SpotWorkPartialUpdate
from app.auth import get_current_user, get_current_user_from_headers
from pydantic import BaseModel

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/spot-work", tags=["Spot Work Management"])


class WorkerInfo(BaseModel):
    name: str
    gender: Optional[str] = None
    birthDate: Optional[str] = None
    address: Optional[str] = None
    idCardNumber: str
    issuingAuthority: Optional[str] = None
    validPeriod: Optional[str] = None
    idCardFront: str
    idCardBack: str


class QuickFillRequest(BaseModel):
    project_id: str
    project_name: str
    plan_start_date: str
    plan_end_date: str
    work_content: Optional[str] = None
    remark: Optional[str] = None
    client_contact: Optional[str] = None
    client_contact_info: Optional[str] = None
    photos: Optional[str] = None
    signature: Optional[str] = None
    worker_count: Optional[int] = 0


class WorkersRequest(BaseModel):
    project_id: str
    project_name: str
    start_date: str
    end_date: str
    workers: List[WorkerInfo]


def validate_maintenance_personnel(db: Session, personnel_name: str) -> None:
    """校验运维人员必须在personnel表中存在"""
    if personnel_name:
        personnel_service = PersonnelService(db)
        if not personnel_service.validate_personnel_exists(personnel_name):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"运维人员'{personnel_name}'不存在于人员列表中，请先添加该人员"
            )


@router.get("/all/list", response_model=ApiResponse)
def get_all_spot_works(
    request: Request,
    db: Session = Depends(get_db),
    current_user: Optional[dict] = Depends(get_current_user)
):
    service = SpotWorkService(db)
    user_info = current_user or get_current_user_from_headers(request)
    user_name = None
    is_manager = False
    if user_info:
        user_name = user_info.get('sub') or user_info.get('name')
        role = user_info.get('role', '')
        is_manager = role in ['管理员', '部门经理', '主管']
    
    items = service.get_all_unpaginated()
    
    if not is_manager and user_name:
        items = [item for item in items if item.maintenance_personnel == user_name]
    
    return ApiResponse(
        code=200,
        message="success",
        data=[item.to_dict() for item in items]
    )


@router.get("", response_model=ApiResponse)
def get_spot_works_list(
    request: Request,
    page: int = Query(0, ge=0, description="Page number, starts from 0"),
    size: int = Query(10, ge=1, le=100, description="Page size"),
    project_name: Optional[str] = Query(None, description="Project name (fuzzy search)"),
    work_id: Optional[str] = Query(None, description="Work ID (fuzzy search)"),
    status: Optional[str] = Query(None, description="Status"),
    db: Session = Depends(get_db),
    current_user: Optional[dict] = Depends(get_current_user)
):
    from app.models.spot_work_worker import SpotWorkWorker
    from sqlalchemy import func as sql_func, or_
    
    service = SpotWorkService(db)
    user_info = current_user or get_current_user_from_headers(request)
    user_name = None
    is_manager = False
    if user_info:
        user_name = user_info.get('sub') or user_info.get('name')
        role = user_info.get('role', '')
        is_manager = role in ['管理员', '部门经理', '主管']
    
    maintenance_personnel = None if is_manager else user_name
    
    logger.info(f"[PC端零星用工] user_info={user_info}, user_name={user_name}, is_manager={is_manager}, maintenance_personnel={maintenance_personnel}")
    
    items, total = service.get_all(
        page=page, size=size, project_name=project_name, work_id=work_id, 
        status=status, maintenance_personnel=maintenance_personnel
    )
    
    if not items:
        return ApiResponse(
            code=200,
            message="success",
            data={
                'content': [],
                'totalElements': total,
                'totalPages': (total + size - 1) // size if size > 0 else 0,
                'size': size,
                'number': page,
                'first': page == 0,
                'last': page >= (total + size - 1) // size if size > 0 else True
            }
        )
    
    project_ids = [item.project_id for item in items]
    start_dates = [item.plan_start_date.date() for item in items if item.plan_start_date]
    end_dates = [item.plan_end_date.date() for item in items if item.plan_end_date]
    
    workers_query = db.query(SpotWorkWorker).filter(
        SpotWorkWorker.project_id.in_(project_ids)
    )
    
    if start_dates or end_dates:
        date_filters = []
        for item in items:
            if item.plan_start_date and item.plan_end_date:
                date_filters.append(
                    sql_func.and_(
                        SpotWorkWorker.project_id == item.project_id,
                        sql_func.date(SpotWorkWorker.start_date) == item.plan_start_date.date(),
                        sql_func.date(SpotWorkWorker.end_date) == item.plan_end_date.date()
                    )
                )
            elif item.plan_start_date:
                date_filters.append(
                    sql_func.and_(
                        SpotWorkWorker.project_id == item.project_id,
                        sql_func.date(SpotWorkWorker.start_date) == item.plan_start_date.date()
                    )
                )
        if date_filters:
            workers_query = db.query(SpotWorkWorker).filter(or_(*date_filters))
    
    all_workers = workers_query.all()
    
    worker_map = {}
    for worker in all_workers:
        key = (worker.project_id, 
               worker.start_date.date() if worker.start_date else None,
               worker.end_date.date() if worker.end_date else None)
        if key not in worker_map:
            worker_map[key] = []
        worker_map[key].append(worker)
    
    items_dict = []
    for item in items:
        item_dict = item.to_dict()
        
        key = (
            item.project_id,
            item.plan_start_date.date() if item.plan_start_date else None,
            item.plan_end_date.date() if item.plan_end_date else None
        )
        workers = worker_map.get(key, [])
        worker_count = len(workers)
        
        days = 0
        if item.plan_start_date and item.plan_end_date:
            delta = (item.plan_end_date - item.plan_start_date).days + 1
            days = max(0, delta)
        
        item_dict['worker_count'] = worker_count
        item_dict['work_days'] = days * worker_count
        items_dict.append(item_dict)
    
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
    request: Request,
    db: Session = Depends(get_db),
    current_user: Optional[dict] = Depends(get_current_user)
):
    """
    快速填报零星用工
    自动生成工单编号：YG-项目编号-年月日-序号
    """
    from app.services.spot_work import SpotWorkCreate
    from app.models.spot_work import SpotWork
    from app.models.work_order_operation_log import WorkOrderOperationLog
    from datetime import datetime
    
    service = SpotWorkService(db)
    
    user_info = current_user or get_current_user_from_headers(request)
    maintenance_personnel = None
    operator_name = None
    operator_id = None
    if user_info:
        maintenance_personnel = user_info.get('sub') or user_info.get('name')
        operator_name = user_info.get('name') or user_info.get('sub')
        operator_id = user_info.get('id')
    
    today = datetime.now().strftime("%Y%m%d")
    prefix = f"YG-{dto.project_id}-{today}"
    
    count = db.query(SpotWork).filter(SpotWork.work_id.like(f"{prefix}%")).count()
    sequence = str(count + 1).zfill(2)
    work_id = f"{prefix}-{sequence}"
    
    photos_list = None
    if dto.photos:
        try:
            photos_list = json.loads(dto.photos) if isinstance(dto.photos, str) else dto.photos
        except:
            photos_list = None
    
    create_dto = SpotWorkCreate(
        work_id=work_id,
        project_id=dto.project_id,
        project_name=dto.project_name,
        plan_start_date=dto.plan_start_date,
        plan_end_date=dto.plan_end_date,
        client_name='',
        client_contact=dto.client_contact,
        client_contact_info=dto.client_contact_info,
        maintenance_personnel=maintenance_personnel,
        work_content=dto.work_content,
        photos=photos_list,
        signature=dto.signature,
        status='待确认',
        remarks=dto.remark
    )
    
    work = service.create(create_dto)
    
    if operator_name and work.id:
        operation_log = WorkOrderOperationLog(
            work_order_type='spot_work',
            work_order_id=work.id,
            work_order_no=work.work_id,
            operator_name=operator_name,
            operator_id=operator_id,
            operation_type='submit',
            operation_type_code='submit',
            operation_type_name='提交',
            operation_remark='员工提交工单'
        )
        db.add(operation_log)
        db.commit()
    
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
    """
    from app.models.spot_work_worker import SpotWorkWorker
    from datetime import datetime
    
    try:
        start = datetime.strptime(start_date, '%Y-%m-%d') if start_date else None
        end = datetime.strptime(end_date, '%Y-%m-%d') if end_date else None
    except:
        start = None
        end = None
    
    query = db.query(SpotWorkWorker).filter(SpotWorkWorker.project_id == project_id)
    
    if start:
        query = query.filter(SpotWorkWorker.start_date == start)
    if end:
        query = query.filter(SpotWorkWorker.end_date == end)
    
    workers = query.all()
    
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
    import logging
    from app.models.spot_work_worker import SpotWorkWorker
    from app.utils.id_card_validator import validate_id_card
    from datetime import datetime
    
    logger = logging.getLogger(__name__)
    logger.info(f"收到施工人员保存请求: project_id={dto.project_id}, workers_count={len(dto.workers)}")
    
    try:
        start = datetime.strptime(dto.start_date, '%Y-%m-%d') if dto.start_date else None
        end = datetime.strptime(dto.end_date, '%Y-%m-%d') if dto.end_date else None
    except Exception as e:
        logger.error(f"日期解析错误: {e}")
        start = None
        end = None
    
    saved_count = 0
    skipped_count = 0
    
    for worker_data in dto.workers:
        is_valid, id_card_msg, birth_date_from_id, gender_from_id = validate_id_card(worker_data.idCardNumber)
        if not is_valid:
            logger.warning(f"身份证验证失败: name={worker_data.name}, id_card={worker_data.idCardNumber}, msg={id_card_msg}")
            return ApiResponse(
                code=400,
                message=f"施工人员'{worker_data.name}'的身份证号码无效: {id_card_msg}",
                data=None
            )
        
        if birth_date_from_id and worker_data.birthDate and worker_data.birthDate != birth_date_from_id:
            return ApiResponse(
                code=400,
                message=f"施工人员'{worker_data.name}'的身份证号码与出生日期不匹配，根据身份证应为{birth_date_from_id}",
                data=None
            )
        
        if gender_from_id and worker_data.gender and worker_data.gender != gender_from_id:
            return ApiResponse(
                code=400,
                message=f"施工人员'{worker_data.name}'的身份证号码与性别不匹配，根据身份证应为{gender_from_id}",
                data=None
            )
        
        existing = db.query(SpotWorkWorker).filter(
            SpotWorkWorker.project_id == dto.project_id,
            SpotWorkWorker.id_card_number == worker_data.idCardNumber,
            SpotWorkWorker.start_date == start,
            SpotWorkWorker.end_date == end
        ).first()
        
        if existing:
            logger.info(f"施工人员已存在，跳过: name={worker_data.name}, id_card={worker_data.idCardNumber}")
            skipped_count += 1
            continue
        
        logger.info(f"保存施工人员: name={worker_data.name}, id_card={worker_data.idCardNumber}")
        worker = SpotWorkWorker(
            project_id=dto.project_id,
            project_name=dto.project_name,
            start_date=start,
            end_date=end,
            name=worker_data.name,
            gender=worker_data.gender,
            birth_date=worker_data.birthDate,
            address=worker_data.address,
            id_card_number=worker_data.idCardNumber,
            issuing_authority=worker_data.issuingAuthority,
            valid_period=worker_data.validPeriod,
            id_card_front=worker_data.idCardFront,
            id_card_back=worker_data.idCardBack
        )
        db.add(worker)
        saved_count += 1
    
    try:
        db.commit()
        logger.info(f"施工人员保存成功，新增 {saved_count} 条，跳过 {skipped_count} 条重复数据")
    except Exception as e:
        logger.error(f"保存施工人员失败: {e}")
        db.rollback()
        return ApiResponse(code=500, message=f"保存失败: {str(e)}", data=None)
    
    return ApiResponse(
        code=200,
        message=f"保存成功，新增{saved_count}人，跳过{skipped_count}人重复数据",
        data={"saved_count": saved_count, "skipped_count": skipped_count}
    )


@router.get("/{id}", response_model=ApiResponse)
def get_spot_work_by_id(
    id: int,
    db: Session = Depends(get_db)
):
    from app.models.spot_work_worker import SpotWorkWorker
    from datetime import datetime
    from sqlalchemy import func as sql_func
    
    service = SpotWorkService(db)
    work = service.get_by_id(id)
    work_dict = work.to_dict()
    
    query = db.query(SpotWorkWorker).filter(
        SpotWorkWorker.project_id == work.project_id
    )
    
    if work.plan_start_date:
        query = query.filter(
            sql_func.date(SpotWorkWorker.start_date) == work.plan_start_date.date()
        )
    if work.plan_end_date:
        query = query.filter(
            sql_func.date(SpotWorkWorker.end_date) == work.plan_end_date.date()
        )
    
    workers = query.all()
    
    worker_count = len(workers)
    
    days = 0
    if work.plan_start_date and work.plan_end_date:
        delta = (work.plan_end_date - work.plan_start_date).days + 1
        days = max(0, delta)
    
    work_days = days * worker_count
    
    work_dict['worker_count'] = worker_count
    work_dict['work_days'] = work_days
    work_dict['workers'] = [w.to_dict() for w in workers]
    
    return ApiResponse(
        code=200,
        message="success",
        data=work_dict
    )


@router.post("", response_model=ApiResponse, status_code=status.HTTP_201_CREATED)
def create_spot_work(
    dto: SpotWorkCreate,
    request: Request,
    db: Session = Depends(get_db),
    current_user: Optional[dict] = Depends(get_current_user)
):
    from app.models.work_order_operation_log import WorkOrderOperationLog
    
    if dto.maintenance_personnel:
        validate_maintenance_personnel(db, dto.maintenance_personnel)
    service = SpotWorkService(db)
    work = service.create(dto)
    
    user_info = current_user or get_current_user_from_headers(request)
    operator_name = None
    operator_id = None
    if user_info:
        operator_name = user_info.get('name') or user_info.get('sub')
        operator_id = user_info.get('id')
    
    if operator_name and work.id:
        operation_log = WorkOrderOperationLog(
            work_order_type='spot_work',
            work_order_id=work.id,
            work_order_no=work.work_id,
            operator_name=operator_name,
            operator_id=operator_id,
            operation_type='create',
            operation_type_code='create',
            operation_type_name='创建',
            operation_remark='创建零星用工工单'
        )
        db.add(operation_log)
        db.commit()
    
    return ApiResponse(
        code=200,
        message="Created successfully",
        data=work.to_dict()
    )


@router.put("/{id}", response_model=ApiResponse)
def update_spot_work(
    id: int,
    dto: SpotWorkUpdate,
    db: Session = Depends(get_db)
):
    if dto.maintenance_personnel:
        validate_maintenance_personnel(db, dto.maintenance_personnel)
    service = SpotWorkService(db)
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
    db: Session = Depends(get_db)
):
    if dto.maintenance_personnel:
        validate_maintenance_personnel(db, dto.maintenance_personnel)
    service = SpotWorkService(db)
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
    current_user: Optional[dict] = Depends(get_current_user)
):
    from app.models.work_order_operation_log import WorkOrderOperationLog
    service = SpotWorkService(db)
    work = service.get_by_id(id)
    work_id = work.work_id
    
    user_id = current_user.get('id') if current_user else None
    operator_name = current_user.get('name', '系统') if current_user else '系统'
    
    log = WorkOrderOperationLog(
        work_order_type='spot_work',
        work_order_id=id,
        work_order_no=work_id,
        operator_name=operator_name,
        operator_id=user_id,
        operation_type='delete',
        operation_type_code='delete',
        operation_type_name='删除',
        operation_remark=f'删除零星用工单 {work_id}'
    )
    db.add(log)
    
    service.delete(id, user_id)
    return ApiResponse(
        code=200,
        message="Deleted successfully",
        data=None
    )
