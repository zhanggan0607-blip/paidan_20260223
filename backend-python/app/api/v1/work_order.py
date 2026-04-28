"""
工单管理API - 合并定期巡检、临时维修、零星用工三种工单数据
优化：使用SQL UNION ALL在数据库层面分页和排序
"""
import logging
from datetime import datetime

from fastapi import APIRouter, Depends, Query, Request
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import UserInfo, get_current_user_info
from app.schemas.common import ApiResponse, PaginatedResponse

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/work-order", tags=["Work Order Management"])


def _build_filter_conditions(
    project_name: str | None,
    order_id: str | None,
    status: str | None,
    maintenance_personnel: str | None,
    user_name: str | None,
    is_manager: bool
) -> tuple[str, dict]:
    """
    构建通用的过滤条件
    
    Returns:
        (filter_sql, params)
    """
    conditions = ["is_deleted = false"]
    params = {}
    
    if project_name:
        conditions.append("project_name ILIKE :project_name")
        params['project_name'] = f'%{project_name}%'
    
    if status:
        conditions.append("status = :status")
        params['status'] = status
    
    if maintenance_personnel:
        conditions.append("maintenance_personnel ILIKE :maintenance_personnel")
        params['maintenance_personnel'] = f'%{maintenance_personnel}%'
    
    if not is_manager and user_name:
        conditions.append("maintenance_personnel = :user_name")
        params['user_name'] = user_name
    
    filter_sql = " AND ".join(conditions)
    return filter_sql, params


@router.get("", response_model=PaginatedResponse)
def get_work_order_list(
    request: Request,
    page: int = Query(0, ge=0, description="页码，从0开始"),
    size: int = Query(10, ge=1, le=100, description="每页数量"),
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
    优化：使用SQL UNION ALL在数据库层面分页和排序
    """
    user_name = user_info.name
    is_manager = user_info.is_manager

    logger.info(f"📋 [工单列表] user_name={user_name}, is_manager={is_manager}")

    base_filter, base_params = _build_filter_conditions(
        project_name, order_id, status, maintenance_personnel, user_name, is_manager
    )

    inspection_filter = base_filter
    repair_filter = base_filter
    spotwork_filter = base_filter

    if order_id:
        inspection_filter += " AND inspection_id ILIKE :order_id"
        repair_filter += " AND repair_id ILIKE :order_id"
        spotwork_filter += " AND work_id ILIKE :order_id"
        base_params['order_id'] = f'%{order_id}%'

    count_subqueries = []
    data_subqueries = []

    if not order_type or order_type == 'inspection':
        count_subqueries.append(f"SELECT id FROM periodic_inspection WHERE {inspection_filter}")
        data_subqueries.append(f"""
            SELECT 
                id,
                inspection_id as order_id,
                '定期巡检单' as order_type,
                'inspection' as order_type_code,
                project_id,
                project_name,
                client_name,
                plan_start_date,
                plan_end_date,
                maintenance_personnel,
                status,
                remarks,
                execution_result,
                signature,
                created_at,
                updated_at
            FROM periodic_inspection 
            WHERE {inspection_filter}
        """)

    if not order_type or order_type == 'repair':
        count_subqueries.append(f"SELECT id FROM temporary_repair WHERE {repair_filter}")
        data_subqueries.append(f"""
            SELECT 
                id,
                repair_id as order_id,
                '临时维修单' as order_type,
                'repair' as order_type_code,
                project_id,
                project_name,
                client_name,
                plan_start_date,
                plan_end_date,
                maintenance_personnel,
                status,
                remarks,
                NULL as execution_result,
                NULL as signature,
                created_at,
                updated_at
            FROM temporary_repair 
            WHERE {repair_filter}
        """)

    if not order_type or order_type == 'spotwork':
        count_subqueries.append(f"SELECT id FROM spot_work WHERE {spotwork_filter}")
        data_subqueries.append(f"""
            SELECT 
                id,
                work_id as order_id,
                '零星用工单' as order_type,
                'spotwork' as order_type_code,
                project_id,
                project_name,
                client_name,
                plan_start_date,
                plan_end_date,
                maintenance_personnel,
                status,
                remarks,
                NULL as execution_result,
                NULL as signature,
                created_at,
                updated_at
            FROM spot_work 
            WHERE {spotwork_filter}
        """)

    count_sql = text(f"SELECT COUNT(*) as total FROM ({' UNION ALL '.join(count_subqueries)}) AS combined")
    total_result = db.execute(count_sql, base_params).scalar()
    total = total_result or 0

    offset = page * size

    data_sql = text(f"""
        SELECT * FROM (
            {' UNION ALL '.join(data_subqueries)}
        ) AS combined
        ORDER BY created_at DESC NULLS LAST, updated_at DESC
        LIMIT :limit OFFSET :offset
    """)

    data_params = {**base_params, 'limit': size, 'offset': offset}
    results = db.execute(data_sql, data_params).fetchall()

    all_orders = []
    for row in results:
        all_orders.append({
            'id': row.id,
            'order_id': row.order_id,
            'order_type': row.order_type,
            'order_type_code': row.order_type_code,
            'project_id': row.project_id,
            'project_name': row.project_name,
            'client_name': row.client_name,
            'plan_start_date': row.plan_start_date.isoformat() if row.plan_start_date else None,
            'plan_end_date': row.plan_end_date.isoformat() if row.plan_end_date else None,
            'maintenance_personnel': row.maintenance_personnel,
            'status': row.status,
            'remarks': row.remarks,
            'execution_result': row.execution_result,
            'signature': row.signature,
            'created_at': row.created_at.isoformat() if row.created_at else None,
            'updated_at': row.updated_at.isoformat() if row.updated_at else None,
        })

    return PaginatedResponse.success(all_orders, total, page, size)


@router.get("/all/list", response_model=ApiResponse)
def get_all_work_orders(
    db: Session = Depends(get_db),
    user_info: UserInfo = Depends(get_current_user_info)
):
    """
    获取所有工单列表（不分页）
    注意：此接口数据量大时可能影响性能，建议使用分页接口
    """
    user_name = user_info.name
    is_manager = user_info.is_manager

    base_filter, base_params = _build_filter_conditions(
        None, None, None, None, user_name, is_manager
    )

    data_sql = text(f"""
        SELECT * FROM (
            SELECT 
                id,
                inspection_id as order_id,
                '定期巡检单' as order_type,
                'inspection' as order_type_code,
                project_id,
                project_name,
                client_name,
                plan_start_date,
                plan_end_date,
                maintenance_personnel,
                status,
                remarks,
                execution_result,
                signature,
                created_at,
                updated_at
            FROM periodic_inspection 
            WHERE {base_filter}
            
            UNION ALL
            
            SELECT 
                id,
                repair_id as order_id,
                '临时维修单' as order_type,
                'repair' as order_type_code,
                project_id,
                project_name,
                client_name,
                plan_start_date,
                plan_end_date,
                maintenance_personnel,
                status,
                remarks,
                NULL as execution_result,
                NULL as signature,
                created_at,
                updated_at
            FROM temporary_repair 
            WHERE {base_filter}
            
            UNION ALL
            
            SELECT 
                id,
                work_id as order_id,
                '零星用工单' as order_type,
                'spotwork' as order_type_code,
                project_id,
                project_name,
                client_name,
                plan_start_date,
                plan_end_date,
                maintenance_personnel,
                status,
                remarks,
                NULL as execution_result,
                NULL as signature,
                created_at,
                updated_at
            FROM spot_work 
            WHERE {base_filter}
        ) AS combined
        ORDER BY created_at DESC NULLS LAST, updated_at DESC
    """)

    results = db.execute(data_sql, base_params).fetchall()

    all_orders = []
    for row in results:
        all_orders.append({
            'id': row.id,
            'order_id': row.order_id,
            'order_type': row.order_type,
            'order_type_code': row.order_type_code,
            'project_id': row.project_id,
            'project_name': row.project_name,
            'client_name': row.client_name,
            'plan_start_date': row.plan_start_date.isoformat() if row.plan_start_date else None,
            'plan_end_date': row.plan_end_date.isoformat() if row.plan_end_date else None,
            'maintenance_personnel': row.maintenance_personnel,
            'status': row.status,
            'remarks': row.remarks,
            'execution_result': row.execution_result,
            'signature': row.signature,
        })

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
    params = {'year': current_year}
    
    if not is_manager and user_name:
        base_filter += " AND maintenance_personnel = :user_name"
        params['user_name'] = user_name
    
    count_sql = text(f"""
        SELECT COUNT(*) as total FROM (
            SELECT id FROM periodic_inspection WHERE {base_filter} AND is_deleted = false
            UNION ALL
            SELECT id FROM temporary_repair WHERE {base_filter} AND is_deleted = false
            UNION ALL
            SELECT id FROM spot_work WHERE {base_filter} AND is_deleted = false
        ) AS combined
    """)
    
    total_result = db.execute(count_sql, params).scalar()
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
    
    data_params = {**params, 'limit': size, 'offset': offset}
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
