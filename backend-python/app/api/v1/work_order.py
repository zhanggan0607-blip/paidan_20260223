"""
工单管理API - 合并定期巡检、临时维修、零星用工三种工单数据
"""
import logging
from datetime import datetime

from fastapi import APIRouter, Depends, Query, Request
from sqlalchemy import extract, or_, func, literal_column, union_all, text
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import UserInfo, get_current_user_info
from app.models.periodic_inspection import PeriodicInspection
from app.models.spot_work import SpotWork
from app.models.temporary_repair import TemporaryRepair
from app.schemas.common import ApiResponse, PaginatedResponse

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/work-order", tags=["Work Order Management"])


@router.get("", response_model=PaginatedResponse)
def get_work_order_list(
    request: Request,
    page: int = Query(0, ge=0, description="页码，从0开始"),
    size: int = Query(10, ge=1, le=1000, description="每页数量"),
    project_name: str | None = Query(None, description="项目名称(模糊搜索)"),
    order_id: str | None = Query(None, description="工单编号(模糊搜索)"),
    order_type: str | None = Query(None, description="工单类型: inspection/repair/spotwork"),
    status: str | None = Query(None, description="状态"),
    maintenance_personnel: str | None = Query(None, description="运维人员(模糊搜索)"),
    db: Session = Depends(get_db),
    user_info: UserInfo = Depends(get_current_user_info)
):
    """
    获取工单列表，合并三种工单类型的数据
    """
    user_name = user_info.name
    is_manager = user_info.is_manager

    logger.info(f"📋 [工单列表] user_name={user_name}, is_manager={is_manager}")

    all_orders = []

    if not order_type or order_type == 'inspection':
        query = db.query(PeriodicInspection).filter(PeriodicInspection.is_deleted == False)
        if project_name:
            query = query.filter(PeriodicInspection.project_name.ilike(f'%{project_name}%'))
        if order_id:
            query = query.filter(PeriodicInspection.inspection_id.ilike(f'%{order_id}%'))
        if status:
            query = query.filter(PeriodicInspection.status == status)
        if maintenance_personnel:
            query = query.filter(PeriodicInspection.maintenance_personnel.ilike(f'%{maintenance_personnel}%'))
        if not is_manager and user_name:
            query = query.filter(PeriodicInspection.maintenance_personnel == user_name)

        for item in query.all():
            all_orders.append({
                'id': item.id,
                'order_id': item.inspection_id,
                'order_type': '定期巡检单',
                'order_type_code': 'inspection',
                'project_id': item.project_id,
                'project_name': item.project_name,
                'client_name': item.client_name,
                'plan_start_date': item.plan_start_date.isoformat() if item.plan_start_date else None,
                'plan_end_date': item.plan_end_date.isoformat() if item.plan_end_date else None,
                'maintenance_personnel': item.maintenance_personnel,
                'status': item.status,
                'remarks': item.remarks,
                'execution_result': item.execution_result,
                'signature': item.signature,
                'created_at': item.created_at.isoformat() if item.created_at else None,
                'updated_at': item.updated_at.isoformat() if item.updated_at else None,
            })

    if not order_type or order_type == 'repair':
        query = db.query(TemporaryRepair).filter(TemporaryRepair.is_deleted == False)
        if project_name:
            query = query.filter(TemporaryRepair.project_name.ilike(f'%{project_name}%'))
        if order_id:
            query = query.filter(TemporaryRepair.repair_id.ilike(f'%{order_id}%'))
        if status:
            query = query.filter(TemporaryRepair.status == status)
        if maintenance_personnel:
            query = query.filter(TemporaryRepair.maintenance_personnel.ilike(f'%{maintenance_personnel}%'))
        if not is_manager and user_name:
            query = query.filter(TemporaryRepair.maintenance_personnel == user_name)

        for item in query.all():
            all_orders.append({
                'id': item.id,
                'order_id': item.repair_id,
                'order_type': '临时维修单',
                'order_type_code': 'repair',
                'project_id': item.project_id,
                'project_name': item.project_name,
                'client_name': item.client_name,
                'plan_start_date': item.plan_start_date.isoformat() if item.plan_start_date else None,
                'plan_end_date': item.plan_end_date.isoformat() if item.plan_end_date else None,
                'maintenance_personnel': item.maintenance_personnel,
                'status': item.status,
                'remarks': item.remarks,
                'created_at': item.created_at.isoformat() if item.created_at else None,
                'updated_at': item.updated_at.isoformat() if item.updated_at else None,
            })

    if not order_type or order_type == 'spotwork':
        query = db.query(SpotWork).filter(SpotWork.is_deleted == False)
        if project_name:
            query = query.filter(SpotWork.project_name.ilike(f'%{project_name}%'))
        if order_id:
            query = query.filter(SpotWork.work_id.ilike(f'%{order_id}%'))
        if status:
            query = query.filter(SpotWork.status == status)
        if maintenance_personnel:
            query = query.filter(SpotWork.maintenance_personnel.ilike(f'%{maintenance_personnel}%'))
        if not is_manager and user_name:
            query = query.filter(SpotWork.maintenance_personnel == user_name)

        for item in query.all():
            all_orders.append({
                'id': item.id,
                'order_id': item.work_id,
                'order_type': '零星用工单',
                'order_type_code': 'spotwork',
                'project_id': item.project_id,
                'project_name': item.project_name,
                'client_name': item.client_name,
                'plan_start_date': item.plan_start_date.isoformat() if item.plan_start_date else None,
                'plan_end_date': item.plan_end_date.isoformat() if item.plan_end_date else None,
                'maintenance_personnel': item.maintenance_personnel,
                'status': item.status,
                'remarks': item.remarks,
                'created_at': item.created_at.isoformat() if item.created_at else None,
                'updated_at': item.updated_at.isoformat() if item.updated_at else None,
            })

    all_orders.sort(key=lambda x: x.get('created_at') or '', reverse=True)

    total = len(all_orders)
    start = page * size
    end = start + size
    paged_orders = all_orders[start:end]

    return PaginatedResponse.success(paged_orders, total, page, size)


@router.get("/all/list", response_model=ApiResponse)
def get_all_work_orders(
    db: Session = Depends(get_db),
    user_info: UserInfo = Depends(get_current_user_info)
):
    """
    获取所有工单列表（不分页）
    """
    user_name = user_info.name
    is_manager = user_info.is_manager

    all_orders = []

    for item in db.query(PeriodicInspection).filter(PeriodicInspection.is_deleted == False).all():
        if not is_manager and user_name and item.maintenance_personnel != user_name:
            continue
        all_orders.append({
            'id': item.id,
            'order_id': item.inspection_id,
            'order_type': '定期巡检单',
            'order_type_code': 'inspection',
            'project_id': item.project_id,
            'project_name': item.project_name,
            'client_name': item.client_name,
            'plan_start_date': item.plan_start_date.isoformat() if item.plan_start_date else None,
            'plan_end_date': item.plan_end_date.isoformat() if item.plan_end_date else None,
            'maintenance_personnel': item.maintenance_personnel,
            'status': item.status,
            'remarks': item.remarks,
            'execution_result': item.execution_result,
            'signature': item.signature,
        })

    for item in db.query(TemporaryRepair).filter(TemporaryRepair.is_deleted == False).all():
        if not is_manager and user_name and item.maintenance_personnel != user_name:
            continue
        all_orders.append({
            'id': item.id,
            'order_id': item.repair_id,
            'order_type': '临时维修单',
            'order_type_code': 'repair',
            'project_id': item.project_id,
            'project_name': item.project_name,
            'client_name': item.client_name,
            'plan_start_date': item.plan_start_date.isoformat() if item.plan_start_date else None,
            'plan_end_date': item.plan_end_date.isoformat() if item.plan_end_date else None,
            'maintenance_personnel': item.maintenance_personnel,
            'status': item.status,
            'remarks': item.remarks,
        })

    for item in db.query(SpotWork).filter(SpotWork.is_deleted == False).all():
        if not is_manager and user_name and item.maintenance_personnel != user_name:
            continue
        all_orders.append({
            'id': item.id,
            'order_id': item.work_id,
            'order_type': '零星用工单',
            'order_type_code': 'spotwork',
            'project_id': item.project_id,
            'project_name': item.project_name,
            'client_name': item.client_name,
            'plan_start_date': item.plan_start_date.isoformat() if item.plan_start_date else None,
            'plan_end_date': item.plan_end_date.isoformat() if item.plan_end_date else None,
            'maintenance_personnel': item.maintenance_personnel,
            'status': item.status,
            'remarks': item.remarks,
        })

    all_orders.sort(key=lambda x: x.get('created_at') or '', reverse=True)

    return ApiResponse.success(all_orders)


@router.get("/completed-this-year", response_model=PaginatedResponse)
def get_completed_this_year(
    request: Request,
    page: int = Query(0, ge=0, description="页码，从0开始"),
    size: int = Query(20, ge=1, le=100, description="每页数量"),
    db: Session = Depends(get_db),
    user_info: UserInfo = Depends(get_current_user_info)
):
    """
    获取本年已完成的工单列表
    
    优化：使用SQL UNION ALL合并查询，在数据库层面分页
    """
    user_name = user_info.name
    is_manager = user_info.is_manager
    current_year = datetime.now().year
    
    logger.info(f"✅ [本年完成] user_name={user_name}, is_manager={is_manager}, year={current_year}")
    
    base_filter = "status = '已完成' AND EXTRACT(YEAR FROM actual_completion_date) = :year"
    if not is_manager and user_name:
        base_filter += " AND maintenance_personnel = :user_name"
    
    count_sql = text(f"""
        SELECT COUNT(*) as total FROM (
            SELECT id FROM periodic_inspection WHERE {base_filter} AND is_deleted = false
            UNION ALL
            SELECT id FROM temporary_repair WHERE {base_filter} AND is_deleted = false
            UNION ALL
            SELECT id FROM spot_work WHERE {base_filter} AND is_deleted = false
        ) AS combined
    """)
    
    count_params = {'year': current_year}
    if not is_manager and user_name:
        count_params['user_name'] = user_name
    
    total_result = db.execute(count_sql, count_params).scalar()
    total = total_result or 0
    
    offset = page * size
    
    data_sql = text(f"""
        SELECT * FROM (
            SELECT 
                id,
                inspection_id as order_id,
                '定期巡检单' as order_type,
                'inspection' as order_type_code,
                '定期巡检' as plan_type,
                project_id,
                project_name,
                client_name,
                plan_start_date,
                plan_end_date,
                actual_completion_date,
                maintenance_personnel,
                status,
                remarks,
                created_at,
                updated_at
            FROM periodic_inspection 
            WHERE {base_filter} AND is_deleted = false
            
            UNION ALL
            
            SELECT 
                id,
                repair_id as order_id,
                '临时维修单' as order_type,
                'repair' as order_type_code,
                '临时维修' as plan_type,
                project_id,
                project_name,
                client_name,
                plan_start_date,
                plan_end_date,
                actual_completion_date,
                maintenance_personnel,
                status,
                remarks,
                created_at,
                updated_at
            FROM temporary_repair 
            WHERE {base_filter} AND is_deleted = false
            
            UNION ALL
            
            SELECT 
                id,
                work_id as order_id,
                '零星用工单' as order_type,
                'spotwork' as order_type_code,
                '零星用工' as plan_type,
                project_id,
                project_name,
                client_name,
                plan_start_date,
                plan_end_date,
                actual_completion_date,
                maintenance_personnel,
                status,
                remarks,
                created_at,
                updated_at
            FROM spot_work 
            WHERE {base_filter} AND is_deleted = false
        ) AS combined
        ORDER BY actual_completion_date DESC NULLS LAST, updated_at DESC
        LIMIT :limit OFFSET :offset
    """)
    
    data_params = {'year': current_year, 'limit': size, 'offset': offset}
    if not is_manager and user_name:
        data_params['user_name'] = user_name
    
    results = db.execute(data_sql, data_params).fetchall()
    
    all_orders = []
    for row in results:
        all_orders.append({
            'id': row.id,
            'order_id': row.order_id,
            'order_type': row.order_type,
            'order_type_code': row.order_type_code,
            'plan_type': row.plan_type,
            'project_id': row.project_id,
            'project_name': row.project_name,
            'client_name': row.client_name,
            'plan_start_date': row.plan_start_date.isoformat() if row.plan_start_date else None,
            'plan_end_date': row.plan_end_date.isoformat() if row.plan_end_date else None,
            'actual_completion_date': row.actual_completion_date.isoformat() if row.actual_completion_date else None,
            'maintenance_personnel': row.maintenance_personnel,
            'status': row.status,
            'remarks': row.remarks,
            'created_at': row.created_at.isoformat() if row.created_at else None,
            'updated_at': row.updated_at.isoformat() if row.updated_at else None,
        })
    
    return PaginatedResponse.success(all_orders, total, page, size)
