"""
工单管理API - 合并定期巡检、临时维修、零星用工三种工单数据
"""
from typing import Optional
from fastapi import APIRouter, Depends, Query, Request
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.periodic_inspection import PeriodicInspection
from app.models.temporary_repair import TemporaryRepair
from app.models.spot_work import SpotWork
from app.schemas.common import ApiResponse, PaginatedResponse
from app.auth import get_current_user, get_current_user_from_headers

router = APIRouter(prefix="/work-order", tags=["Work Order Management"])


@router.get("", response_model=PaginatedResponse)
def get_work_order_list(
    request: Request,
    page: int = Query(0, ge=0, description="页码，从0开始"),
    size: int = Query(10, ge=1, le=100, description="每页数量"),
    project_name: Optional[str] = Query(None, description="项目名称(模糊搜索)"),
    client_name: Optional[str] = Query(None, description="客户名称(模糊搜索)"),
    order_type: Optional[str] = Query(None, description="工单类型: inspection/repair/spotwork"),
    status: Optional[str] = Query(None, description="状态"),
    maintenance_personnel: Optional[str] = Query(None, description="运维人员(模糊搜索)"),
    db: Session = Depends(get_db),
    current_user: Optional[dict] = Depends(get_current_user)
):
    """
    获取工单列表，合并三种工单类型的数据
    """
    user_info = current_user or get_current_user_from_headers(request)
    user_name = None
    is_manager = False
    if user_info:
        user_name = user_info.get('sub') or user_info.get('name')
        role = user_info.get('role', '')
        is_manager = role in ['管理员', '部门经理', '主管']
    
    all_orders = []
    
    if not order_type or order_type == 'inspection':
        query = db.query(PeriodicInspection)
        if project_name:
            query = query.filter(PeriodicInspection.project_name.ilike(f'%{project_name}%'))
        if client_name:
            query = query.filter(PeriodicInspection.client_name.ilike(f'%{client_name}%'))
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
                'created_at': item.created_at.isoformat() if item.created_at else None,
                'updated_at': item.updated_at.isoformat() if item.updated_at else None,
            })
    
    if not order_type or order_type == 'repair':
        query = db.query(TemporaryRepair)
        if project_name:
            query = query.filter(TemporaryRepair.project_name.ilike(f'%{project_name}%'))
        if client_name:
            query = query.filter(TemporaryRepair.client_name.ilike(f'%{client_name}%'))
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
        query = db.query(SpotWork)
        if project_name:
            query = query.filter(SpotWork.project_name.ilike(f'%{project_name}%'))
        if client_name:
            query = query.filter(SpotWork.client_name.ilike(f'%{client_name}%'))
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
    request: Request,
    db: Session = Depends(get_db),
    current_user: Optional[dict] = Depends(get_current_user)
):
    """
    获取所有工单列表（不分页）
    """
    user_info = current_user or get_current_user_from_headers(request)
    user_name = None
    is_manager = False
    if user_info:
        user_name = user_info.get('sub') or user_info.get('name')
        role = user_info.get('role', '')
        is_manager = role in ['管理员', '部门经理', '主管']
    
    all_orders = []
    
    for item in db.query(PeriodicInspection).all():
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
        })
    
    for item in db.query(TemporaryRepair).all():
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
    
    for item in db.query(SpotWork).all():
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
