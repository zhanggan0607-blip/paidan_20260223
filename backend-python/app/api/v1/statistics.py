from typing import List, Optional
from fastapi import APIRouter, Depends, Query, HTTPException, Request
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_, case, extract
from datetime import datetime, timedelta
from app.database import get_db
from app.schemas.common import ApiResponse
from app.models.periodic_inspection import PeriodicInspection
from app.models.temporary_repair import TemporaryRepair
from app.models.spot_work import SpotWork
from app.models.project_info import ProjectInfo
from app.config import OverdueAlertConfig
from app.auth import get_current_user, get_current_user_from_headers

router = APIRouter(prefix="/statistics", tags=["Statistics"])


def _apply_user_filter(query, model, user_name: Optional[str], is_manager: bool):
    """应用用户数据过滤"""
    if not is_manager and user_name:
        if hasattr(model, 'maintenance_personnel'):
            query = query.filter(model.maintenance_personnel == user_name)
    return query


def _get_user_info(request: Request, current_user: Optional[dict]):
    """
    获取用户信息并判断是否为管理员
    返回: (user_name, is_manager)
    """
    user_info = current_user or get_current_user_from_headers(request)
    if not user_info:
        return None, False
    
    user_name = user_info.get('sub') or user_info.get('name')
    role = user_info.get('role', '')
    is_manager = role in ['管理员', '部门经理', '主管']
    
    return user_name, is_manager


@router.get("/overview", response_model=ApiResponse)
def get_statistics_overview(
    request: Request,
    year: int = Query(..., description="年度"),
    db: Session = Depends(get_db),
    current_user: Optional[dict] = Depends(get_current_user)
):
    """
    获取统计数据概览 - 从三种工单表获取数据
    年份过滤统一使用 plan_start_date
    本年完成使用 actual_completion_date 判断
    """
    
    user_name, is_manager = _get_user_info(request, current_user)
    
    today = datetime.now().date()
    current_year = today.year
    year_start = datetime(year, 1, 1).date()
    year_end = datetime(year, 12, 31).date()
    near_due_days = 7
    valid_statuses = OverdueAlertConfig.VALID_STATUSES
    completed_statuses = OverdueAlertConfig.COMPLETED_STATUSES
    
    near_due_count = 0
    overdue_count = 0
    year_completed_count = 0
    regular_inspection_count = 0
    temporary_repair_count = 0
    spot_work_count = 0
    
    inspection_query = db.query(PeriodicInspection)
    inspection_query = _apply_user_filter(inspection_query, PeriodicInspection, user_name, is_manager)
    
    for inspection in inspection_query.all():
        plan_start = inspection.plan_start_date
        plan_end = inspection.plan_end_date
        actual_completion = inspection.actual_completion_date
        if isinstance(plan_start, datetime):
            plan_start = plan_start.date()
        if isinstance(plan_end, datetime):
            plan_end = plan_end.date()
        if isinstance(actual_completion, datetime):
            actual_completion = actual_completion.date()
        
        if plan_start:
            if plan_start >= year_start and plan_start <= year_end:
                regular_inspection_count += 1
            
            if inspection.status in valid_statuses:
                days_from_today = (plan_start - today).days
                if 0 <= days_from_today <= near_due_days:
                    near_due_count += 1
        
        if plan_end:
            check_date = today if year == current_year else year_end
            if plan_end < check_date and inspection.status in valid_statuses:
                overdue_count += 1
        
        if inspection.status in completed_statuses and actual_completion:
            if actual_completion >= year_start and actual_completion <= year_end:
                year_completed_count += 1
    
    repair_query = db.query(TemporaryRepair)
    repair_query = _apply_user_filter(repair_query, TemporaryRepair, user_name, is_manager)
    
    for repair in repair_query.all():
        plan_start = repair.plan_start_date
        plan_end = repair.plan_end_date
        actual_completion = repair.actual_completion_date
        if isinstance(plan_start, datetime):
            plan_start = plan_start.date()
        if isinstance(plan_end, datetime):
            plan_end = plan_end.date()
        if isinstance(actual_completion, datetime):
            actual_completion = actual_completion.date()
        
        if plan_start:
            if plan_start >= year_start and plan_start <= year_end:
                temporary_repair_count += 1
            
            if repair.status in valid_statuses:
                days_from_today = (plan_start - today).days
                if 0 <= days_from_today <= near_due_days:
                    near_due_count += 1
        
        if plan_end:
            check_date = today if year == current_year else year_end
            if plan_end < check_date and repair.status in valid_statuses:
                overdue_count += 1
        
        if repair.status in completed_statuses and actual_completion:
            if actual_completion >= year_start and actual_completion <= year_end:
                year_completed_count += 1
    
    work_query = db.query(SpotWork)
    work_query = _apply_user_filter(work_query, SpotWork, user_name, is_manager)
    
    for work in work_query.all():
        plan_start = work.plan_start_date
        plan_end = work.plan_end_date
        actual_completion = work.actual_completion_date
        if isinstance(plan_start, datetime):
            plan_start = plan_start.date()
        if isinstance(plan_end, datetime):
            plan_end = plan_end.date()
        if isinstance(actual_completion, datetime):
            actual_completion = actual_completion.date()
        
        if plan_start:
            if plan_start >= year_start and plan_start <= year_end:
                spot_work_count += 1
            
            if work.status in valid_statuses:
                days_from_today = (plan_start - today).days
                if 0 <= days_from_today <= near_due_days:
                    near_due_count += 1
        
        if plan_end:
            check_date = today if year == current_year else year_end
            if plan_end < check_date and work.status in valid_statuses:
                overdue_count += 1
        
        if work.status in completed_statuses and actual_completion:
            if actual_completion >= year_start and actual_completion <= year_end:
                year_completed_count += 1
    
    total_work_orders = regular_inspection_count + temporary_repair_count + spot_work_count
    
    return ApiResponse.success({
        'year': year,
        'totalWorkOrders': total_work_orders,
        'regularInspectionCount': regular_inspection_count,
        'temporaryRepairCount': temporary_repair_count,
        'spotWorkCount': spot_work_count,
        'nearDueCount': near_due_count,
        'overdueCount': overdue_count,
        'yearCompletedCount': year_completed_count
    })


@router.get("/completion-rate", response_model=ApiResponse)
def get_completion_rate(
    request: Request,
    year: int = Query(..., description="年度"),
    db: Session = Depends(get_db),
    current_user: Optional[dict] = Depends(get_current_user)
):
    """
    获取准时完成率 - 从三种工单表获取数据
    使用 actual_completion_date 判断实际完成时间
    使用 plan_start_date 过滤年份
    """
    
    user_name, is_manager = _get_user_info(request, current_user)
    
    year_start = datetime(year, 1, 1).date()
    year_end = datetime(year, 12, 31).date()
    completed_statuses = OverdueAlertConfig.COMPLETED_STATUSES
    
    on_time_count = 0
    total_count = 0
    
    inspection_query = db.query(PeriodicInspection).filter(PeriodicInspection.status.in_(completed_statuses))
    inspection_query = _apply_user_filter(inspection_query, PeriodicInspection, user_name, is_manager)
    
    for inspection in inspection_query.all():
        plan_start = inspection.plan_start_date
        plan_end = inspection.plan_end_date
        actual_completion = inspection.actual_completion_date
        if isinstance(plan_start, datetime):
            plan_start = plan_start.date()
        if isinstance(plan_end, datetime):
            plan_end = plan_end.date()
        if isinstance(actual_completion, datetime):
            actual_completion = actual_completion.date()
        
        if plan_start and actual_completion:
            if plan_start >= year_start and plan_start <= year_end:
                total_count += 1
                if actual_completion <= plan_end:
                    on_time_count += 1
    
    repair_query = db.query(TemporaryRepair).filter(TemporaryRepair.status.in_(completed_statuses))
    repair_query = _apply_user_filter(repair_query, TemporaryRepair, user_name, is_manager)
    
    for repair in repair_query.all():
        plan_start = repair.plan_start_date
        plan_end = repair.plan_end_date
        actual_completion = repair.actual_completion_date
        if isinstance(plan_start, datetime):
            plan_start = plan_start.date()
        if isinstance(plan_end, datetime):
            plan_end = plan_end.date()
        if isinstance(actual_completion, datetime):
            actual_completion = actual_completion.date()
        
        if plan_start and actual_completion:
            if plan_start >= year_start and plan_start <= year_end:
                total_count += 1
                if actual_completion <= plan_end:
                    on_time_count += 1
    
    work_query = db.query(SpotWork).filter(SpotWork.status.in_(completed_statuses))
    work_query = _apply_user_filter(work_query, SpotWork, user_name, is_manager)
    
    for work in work_query.all():
        plan_start = work.plan_start_date
        plan_end = work.plan_end_date
        actual_completion = work.actual_completion_date
        if isinstance(plan_start, datetime):
            plan_start = plan_start.date()
        if isinstance(plan_end, datetime):
            plan_end = plan_end.date()
        if isinstance(actual_completion, datetime):
            actual_completion = actual_completion.date()
        
        if plan_start and actual_completion:
            if plan_start >= year_start and plan_start <= year_end:
                total_count += 1
                if actual_completion <= plan_end:
                    on_time_count += 1
    
    delayed_count = total_count - on_time_count
    on_time_rate = on_time_count / total_count if total_count > 0 else 0
    
    return ApiResponse.success({
        'year': year,
        'onTimeRate': round(on_time_rate, 4),
        'onTimeCount': on_time_count,
        'delayedCount': delayed_count,
        'totalCount': total_count
    })


@router.get("/top-projects", response_model=ApiResponse)
def get_top_projects(
    request: Request,
    year: int = Query(..., description="年度"),
    limit: int = Query(5, ge=1, le=10, description="返回数量"),
    db: Session = Depends(get_db),
    current_user: Optional[dict] = Depends(get_current_user)
):
    """
    获取年度前五项目（工单数量）- 从三种工单表获取数据
    使用 plan_start_date 过滤年份
    """
    
    user_name, is_manager = _get_user_info(request, current_user)
    
    year_start = datetime(year, 1, 1).date()
    year_end = datetime(year, 12, 31).date()
    completed_statuses = OverdueAlertConfig.COMPLETED_STATUSES
    
    project_stats = {}
    
    inspection_query = db.query(PeriodicInspection).filter(PeriodicInspection.status.in_(completed_statuses))
    inspection_query = _apply_user_filter(inspection_query, PeriodicInspection, user_name, is_manager)
    
    for inspection in inspection_query.all():
        plan_start = inspection.plan_start_date
        if isinstance(plan_start, datetime):
            plan_start = plan_start.date()
        if plan_start and plan_start >= year_start and plan_start <= year_end:
            if inspection.project_id:
                if inspection.project_id not in project_stats:
                    project_stats[inspection.project_id] = 0
                project_stats[inspection.project_id] += 1
    
    repair_query = db.query(TemporaryRepair).filter(TemporaryRepair.status.in_(completed_statuses))
    repair_query = _apply_user_filter(repair_query, TemporaryRepair, user_name, is_manager)
    
    for repair in repair_query.all():
        plan_start = repair.plan_start_date
        if isinstance(plan_start, datetime):
            plan_start = plan_start.date()
        if plan_start and plan_start >= year_start and plan_start <= year_end:
            if repair.project_id:
                if repair.project_id not in project_stats:
                    project_stats[repair.project_id] = 0
                project_stats[repair.project_id] += 1
    
    work_query = db.query(SpotWork).filter(SpotWork.status.in_(completed_statuses))
    work_query = _apply_user_filter(work_query, SpotWork, user_name, is_manager)
    
    for work in work_query.all():
        plan_start = work.plan_start_date
        if isinstance(plan_start, datetime):
            plan_start = plan_start.date()
        if plan_start and plan_start >= year_start and plan_start <= year_end:
            if work.project_id:
                if work.project_id not in project_stats:
                    project_stats[work.project_id] = 0
                project_stats[work.project_id] += 1
    
    projects = db.query(ProjectInfo).all()
    project_dict = {p.project_id: p.project_name for p in projects}
    
    sorted_projects = sorted(project_stats.items(), key=lambda x: x[1], reverse=True)[:limit]
    
    result = []
    for project_id, value in sorted_projects:
        project_name = project_dict.get(project_id, project_id)
        result.append({
            'name': project_name,
            'value': value
        })
    
    return ApiResponse.success(result)


@router.get("/top-repairs", response_model=ApiResponse)
def get_top_repairs(
    request: Request,
    year: int = Query(..., description="年度"),
    limit: int = Query(5, ge=1, le=10, description="返回数量"),
    db: Session = Depends(get_db),
    current_user: Optional[dict] = Depends(get_current_user)
):
    """
    获取临时维修单年度前五 - 按项目统计临时维修单数量
    使用 plan_start_date 过滤年份
    """
    
    user_name, is_manager = _get_user_info(request, current_user)
    
    year_start = datetime(year, 1, 1).date()
    year_end = datetime(year, 12, 31).date()
    completed_statuses = OverdueAlertConfig.COMPLETED_STATUSES
    
    project_stats = {}
    
    repair_query = db.query(TemporaryRepair).filter(TemporaryRepair.status.in_(completed_statuses))
    repair_query = _apply_user_filter(repair_query, TemporaryRepair, user_name, is_manager)
    
    for repair in repair_query.all():
        plan_start = repair.plan_start_date
        if isinstance(plan_start, datetime):
            plan_start = plan_start.date()
        if plan_start and plan_start >= year_start and plan_start <= year_end:
            if repair.project_id:
                if repair.project_id not in project_stats:
                    project_stats[repair.project_id] = 0
                project_stats[repair.project_id] += 1
    
    projects = db.query(ProjectInfo).all()
    project_dict = {p.project_id: p.project_name for p in projects}
    
    sorted_projects = sorted(project_stats.items(), key=lambda x: x[1], reverse=True)[:limit]
    
    result = []
    for project_id, value in sorted_projects:
        project_name = project_dict.get(project_id, project_id)
        result.append({
            'name': project_name,
            'value': value
        })
    
    return ApiResponse.success(result)


@router.get("/employee-stats", response_model=ApiResponse)
def get_employee_stats(
    request: Request,
    year: int = Query(..., description="年度"),
    db: Session = Depends(get_db),
    current_user: Optional[dict] = Depends(get_current_user)
):
    """
    获取运维人员工单数量统计 - 按运维人员分组统计
    使用 plan_start_date 过滤年份
    """
    
    user_name, is_manager = _get_user_info(request, current_user)
    
    year_start = datetime(year, 1, 1).date()
    year_end = datetime(year, 12, 31).date()
    
    employee_stats = {}
    
    inspection_query = db.query(PeriodicInspection)
    inspection_query = _apply_user_filter(inspection_query, PeriodicInspection, user_name, is_manager)
    
    for inspection in inspection_query.all():
        plan_start = inspection.plan_start_date
        if isinstance(plan_start, datetime):
            plan_start = plan_start.date()
        if plan_start and plan_start >= year_start and plan_start <= year_end:
            personnel = inspection.maintenance_personnel or '未知'
            if personnel not in employee_stats:
                employee_stats[personnel] = 0
            employee_stats[personnel] += 1
    
    repair_query = db.query(TemporaryRepair)
    repair_query = _apply_user_filter(repair_query, TemporaryRepair, user_name, is_manager)
    
    for repair in repair_query.all():
        plan_start = repair.plan_start_date
        if isinstance(plan_start, datetime):
            plan_start = plan_start.date()
        if plan_start and plan_start >= year_start and plan_start <= year_end:
            personnel = repair.maintenance_personnel or '未知'
            if personnel not in employee_stats:
                employee_stats[personnel] = 0
            employee_stats[personnel] += 1
    
    work_query = db.query(SpotWork)
    work_query = _apply_user_filter(work_query, SpotWork, user_name, is_manager)
    
    for work in work_query.all():
        plan_start = work.plan_start_date
        if isinstance(plan_start, datetime):
            plan_start = plan_start.date()
        if plan_start and plan_start >= year_start and plan_start <= year_end:
            personnel = work.maintenance_personnel or '未知'
            if personnel not in employee_stats:
                employee_stats[personnel] = 0
            employee_stats[personnel] += 1
    
    sorted_employees = sorted(employee_stats.items(), key=lambda x: x[1], reverse=True)
    
    result = []
    for name, count in sorted_employees:
        if name != '未知':
            result.append({
                'name': name,
                'count': count
            })
    
    return ApiResponse.success({
        'year': year,
        'employees': result,
        'total': len(result)
    })


@router.get("/repair-stats", response_model=ApiResponse)
def get_repair_stats(
    request: Request,
    year: int = Query(..., description="年度"),
    db: Session = Depends(get_db),
    current_user: Optional[dict] = Depends(get_current_user)
):
    """
    获取临时维修单完成数量统计 - 按运维人员分组统计已完成的临时维修单
    使用 plan_start_date 过滤年份
    """
    
    user_name, is_manager = _get_user_info(request, current_user)
    
    year_start = datetime(year, 1, 1).date()
    year_end = datetime(year, 12, 31).date()
    completed_statuses = OverdueAlertConfig.COMPLETED_STATUSES
    
    repair_stats = {}
    
    repair_query = db.query(TemporaryRepair).filter(TemporaryRepair.status.in_(completed_statuses))
    repair_query = _apply_user_filter(repair_query, TemporaryRepair, user_name, is_manager)
    
    for repair in repair_query.all():
        plan_start = repair.plan_start_date
        if isinstance(plan_start, datetime):
            plan_start = plan_start.date()
        if plan_start and plan_start >= year_start and plan_start <= year_end:
            personnel = repair.maintenance_personnel or '未知'
            if personnel not in repair_stats:
                repair_stats[personnel] = 0
            repair_stats[personnel] += 1
    
    sorted_employees = sorted(repair_stats.items(), key=lambda x: x[1], reverse=True)
    
    result = []
    for name, count in sorted_employees:
        if name != '未知':
            result.append({
                'name': name,
                'count': count
            })
    
    return ApiResponse.success({
        'year': year,
        'employees': result,
        'total': len(result)
    })


@router.get("/spotwork-stats", response_model=ApiResponse)
def get_spotwork_stats(
    request: Request,
    year: int = Query(..., description="年度"),
    db: Session = Depends(get_db),
    current_user: Optional[dict] = Depends(get_current_user)
):
    """
    获取零星用工单完成数量统计 - 按运维人员分组统计已完成的零星用工单
    使用 plan_start_date 过滤年份
    """
    
    user_name, is_manager = _get_user_info(request, current_user)
    
    year_start = datetime(year, 1, 1).date()
    year_end = datetime(year, 12, 31).date()
    completed_statuses = OverdueAlertConfig.COMPLETED_STATUSES
    
    spotwork_stats = {}
    
    work_query = db.query(SpotWork).filter(SpotWork.status.in_(completed_statuses))
    work_query = _apply_user_filter(work_query, SpotWork, user_name, is_manager)
    
    for work in work_query.all():
        plan_start = work.plan_start_date
        if isinstance(plan_start, datetime):
            plan_start = plan_start.date()
        if plan_start and plan_start >= year_start and plan_start <= year_end:
            personnel = work.maintenance_personnel or '未知'
            if personnel not in spotwork_stats:
                spotwork_stats[personnel] = 0
            spotwork_stats[personnel] += 1
    
    sorted_employees = sorted(spotwork_stats.items(), key=lambda x: x[1], reverse=True)
    
    result = []
    for name, count in sorted_employees:
        if name != '未知':
            result.append({
                'name': name,
                'count': count
            })
    
    return ApiResponse.success({
        'year': year,
        'employees': result,
        'total': len(result)
    })


@router.get("/inspection-stats", response_model=ApiResponse)
def get_inspection_stats(
    request: Request,
    year: int = Query(..., description="年度"),
    db: Session = Depends(get_db),
    current_user: Optional[dict] = Depends(get_current_user)
):
    """
    获取定期巡检单完成数量统计 - 按运维人员分组统计已完成的定期巡检单
    使用 plan_start_date 过滤年份
    """
    
    user_name, is_manager = _get_user_info(request, current_user)
    
    year_start = datetime(year, 1, 1).date()
    year_end = datetime(year, 12, 31).date()
    completed_statuses = OverdueAlertConfig.COMPLETED_STATUSES
    
    inspection_stats = {}
    
    inspection_query = db.query(PeriodicInspection).filter(PeriodicInspection.status.in_(completed_statuses))
    inspection_query = _apply_user_filter(inspection_query, PeriodicInspection, user_name, is_manager)
    
    for inspection in inspection_query.all():
        plan_start = inspection.plan_start_date
        if isinstance(plan_start, datetime):
            plan_start = plan_start.date()
        if plan_start and plan_start >= year_start and plan_start <= year_end:
            personnel = inspection.maintenance_personnel or '未知'
            if personnel not in inspection_stats:
                inspection_stats[personnel] = 0
            inspection_stats[personnel] += 1
    
    sorted_employees = sorted(inspection_stats.items(), key=lambda x: x[1], reverse=True)
    
    result = []
    for name, count in sorted_employees:
        if name != '未知':
            result.append({
                'name': name,
                'count': count
            })
    
    return ApiResponse.success({
        'year': year,
        'employees': result,
        'total': len(result)
    })


@router.get("/detail", response_model=ApiResponse)
def get_statistics_detail(
    request: Request,
    year: int = Query(..., description="年度"),
    data_type: str = Query(..., description="数据类型: nearDue/overdue/yearCompleted/regularInspection/temporaryRepair/spotWork/onTime/delayed/employee/project"),
    employee_name: Optional[str] = Query(None, description="运维人员姓名(运维人员详情时使用)"),
    project_name: Optional[str] = Query(None, description="项目名称(项目详情时使用)"),
    order_type: Optional[str] = Query(None, description="工单类型(运维人员/项目详情时使用): inspection/repair/spotwork"),
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=10000, description="每页数量"),
    db: Session = Depends(get_db),
    current_user: Optional[dict] = Depends(get_current_user)
):
    """
    获取统计数据详细列表
    data_type: nearDue-临期工单, overdue-超期工单, yearCompleted-本年完成, 
               regularInspection-定期巡检单, temporaryRepair-临时维修单, spotWork-零星用工单,
               onTime-准时完成, delayed-延期完成, employee-运维人员工单详情, project-项目工单详情
    年份过滤统一使用 plan_start_date
    本年完成使用 actual_completion_date 判断
    """
    
    user_name, is_manager = _get_user_info(request, current_user)
    
    today = datetime.now().date()
    current_year = today.year
    year_start = datetime(year, 1, 1).date()
    year_end = datetime(year, 12, 31).date()
    near_due_days = 7
    valid_statuses = OverdueAlertConfig.VALID_STATUSES
    completed_statuses = OverdueAlertConfig.COMPLETED_STATUSES
    
    results = []
    total = 0
    
    projects = db.query(ProjectInfo).all()
    project_dict = {p.project_id: p.project_name for p in projects}
    
    def format_work_order(item, order_type_str: str) -> dict:
        """格式化工单数据"""
        plan_start = item.plan_start_date
        plan_end = item.plan_end_date
        if isinstance(plan_start, datetime):
            plan_start = plan_start.date()
        if isinstance(plan_end, datetime):
            plan_end = plan_end.date()
        
        order_number = ''
        if hasattr(item, 'inspection_id'):
            order_number = item.inspection_id or ''
        elif hasattr(item, 'repair_id'):
            order_number = item.repair_id or ''
        elif hasattr(item, 'work_id'):
            order_number = item.work_id or ''
        
        content = item.remarks or ''
        
        return {
            'id': item.id,
            'orderType': order_type_str,
            'orderNumber': order_number,
            'projectName': project_dict.get(item.project_id, item.project_id or ''),
            'maintenancePersonnel': item.maintenance_personnel or '',
            'planStartDate': plan_start.strftime('%Y-%m-%d') if plan_start else '',
            'planEndDate': plan_end.strftime('%Y-%m-%d') if plan_end else '',
            'status': item.status or '',
            'content': content
        }
    
    def filter_and_paginate(query, model, order_type_str: str, filter_func) -> tuple:
        """过滤并分页"""
        query = _apply_user_filter(query, model, user_name, is_manager)
        items = []
        for item in query.all():
            if filter_func(item):
                items.append(format_work_order(item, order_type_str))
        return items
    
    if data_type == 'nearDue':
        is_current_year = (year == current_year)
        if is_current_year:
            def check_near_due(item):
                plan_start = item.plan_start_date
                if isinstance(plan_start, datetime):
                    plan_start = plan_start.date()
                if plan_start and item.status in valid_statuses:
                    days_from_today = (plan_start - today).days
                    return 0 <= days_from_today <= near_due_days
                return False
            
            results.extend(filter_and_paginate(
                db.query(PeriodicInspection), PeriodicInspection, '定期巡检单', check_near_due
            ))
            results.extend(filter_and_paginate(
                db.query(TemporaryRepair), TemporaryRepair, '临时维修单', check_near_due
            ))
            results.extend(filter_and_paginate(
                db.query(SpotWork), SpotWork, '零星用工单', check_near_due
            ))
    
    elif data_type == 'overdue':
        def check_overdue(item):
            plan_end = item.plan_end_date
            if isinstance(plan_end, datetime):
                plan_end = plan_end.date()
            check_date = today if year == current_year else year_end
            if plan_end and plan_end < check_date and item.status in valid_statuses:
                return True
            return False
        
        results.extend(filter_and_paginate(
            db.query(PeriodicInspection), PeriodicInspection, '定期巡检单', check_overdue
        ))
        results.extend(filter_and_paginate(
            db.query(TemporaryRepair), TemporaryRepair, '临时维修单', check_overdue
        ))
        results.extend(filter_and_paginate(
            db.query(SpotWork), SpotWork, '零星用工单', check_overdue
        ))
    
    elif data_type == 'yearCompleted':
        def check_year_completed(item):
            actual_completion = item.actual_completion_date
            if isinstance(actual_completion, datetime):
                actual_completion = actual_completion.date()
            if item.status in completed_statuses and actual_completion:
                return year_start <= actual_completion <= year_end
            return False
        
        results.extend(filter_and_paginate(
            db.query(PeriodicInspection), PeriodicInspection, '定期巡检单', check_year_completed
        ))
        results.extend(filter_and_paginate(
            db.query(TemporaryRepair), TemporaryRepair, '临时维修单', check_year_completed
        ))
        results.extend(filter_and_paginate(
            db.query(SpotWork), SpotWork, '零星用工单', check_year_completed
        ))
    
    elif data_type == 'regularInspection':
        def check_inspection(item):
            plan_start = item.plan_start_date
            if isinstance(plan_start, datetime):
                plan_start = plan_start.date()
            if plan_start:
                return year_start <= plan_start <= year_end
            return False
        
        results = filter_and_paginate(
            db.query(PeriodicInspection), PeriodicInspection, '定期巡检单', check_inspection
        )
    
    elif data_type == 'temporaryRepair':
        def check_repair(item):
            plan_start = item.plan_start_date
            if isinstance(plan_start, datetime):
                plan_start = plan_start.date()
            if plan_start:
                return year_start <= plan_start <= year_end
            return False
        
        results = filter_and_paginate(
            db.query(TemporaryRepair), TemporaryRepair, '临时维修单', check_repair
        )
    
    elif data_type == 'spotWork':
        def check_spotwork(item):
            plan_start = item.plan_start_date
            if isinstance(plan_start, datetime):
                plan_start = plan_start.date()
            if plan_start:
                return year_start <= plan_start <= year_end
            return False
        
        results = filter_and_paginate(
            db.query(SpotWork), SpotWork, '零星用工单', check_spotwork
        )
    
    elif data_type == 'onTime':
        def check_on_time(item):
            plan_start = item.plan_start_date
            plan_end = item.plan_end_date
            actual_completion = item.actual_completion_date
            if isinstance(plan_start, datetime):
                plan_start = plan_start.date()
            if isinstance(plan_end, datetime):
                plan_end = plan_end.date()
            if isinstance(actual_completion, datetime):
                actual_completion = actual_completion.date()
            if item.status in completed_statuses and plan_start and actual_completion:
                if year_start <= plan_start <= year_end:
                    return actual_completion <= plan_end
            return False
        
        results.extend(filter_and_paginate(
            db.query(PeriodicInspection), PeriodicInspection, '定期巡检单', check_on_time
        ))
        results.extend(filter_and_paginate(
            db.query(TemporaryRepair), TemporaryRepair, '临时维修单', check_on_time
        ))
        results.extend(filter_and_paginate(
            db.query(SpotWork), SpotWork, '零星用工单', check_on_time
        ))
    
    elif data_type == 'delayed':
        def check_delayed(item):
            plan_start = item.plan_start_date
            plan_end = item.plan_end_date
            actual_completion = item.actual_completion_date
            if isinstance(plan_start, datetime):
                plan_start = plan_start.date()
            if isinstance(plan_end, datetime):
                plan_end = plan_end.date()
            if isinstance(actual_completion, datetime):
                actual_completion = actual_completion.date()
            if item.status in completed_statuses and plan_start and actual_completion:
                if year_start <= plan_start <= year_end:
                    return actual_completion > plan_end
            return False
        
        results.extend(filter_and_paginate(
            db.query(PeriodicInspection), PeriodicInspection, '定期巡检单', check_delayed
        ))
        results.extend(filter_and_paginate(
            db.query(TemporaryRepair), TemporaryRepair, '临时维修单', check_delayed
        ))
        results.extend(filter_and_paginate(
            db.query(SpotWork), SpotWork, '零星用工单', check_delayed
        ))
    
    elif data_type == 'employee' and employee_name:
        def check_employee(item, require_completed=False):
            plan_start = item.plan_start_date
            if isinstance(plan_start, datetime):
                plan_start = plan_start.date()
            if plan_start and year_start <= plan_start <= year_end:
                if item.maintenance_personnel == employee_name:
                    if require_completed:
                        return item.status in completed_statuses
                    return True
            return False
        
        if order_type == 'inspection':
            results.extend(filter_and_paginate(
                db.query(PeriodicInspection), PeriodicInspection, '定期巡检单', lambda item: check_employee(item, True)
            ))
        elif order_type == 'repair':
            results.extend(filter_and_paginate(
                db.query(TemporaryRepair), TemporaryRepair, '临时维修单', lambda item: check_employee(item, True)
            ))
        elif order_type == 'spotwork':
            results.extend(filter_and_paginate(
                db.query(SpotWork), SpotWork, '零星用工单', lambda item: check_employee(item, True)
            ))
        else:
            results.extend(filter_and_paginate(
                db.query(PeriodicInspection), PeriodicInspection, '定期巡检单', lambda item: check_employee(item, False)
            ))
            results.extend(filter_and_paginate(
                db.query(TemporaryRepair), TemporaryRepair, '临时维修单', lambda item: check_employee(item, False)
            ))
            results.extend(filter_and_paginate(
                db.query(SpotWork), SpotWork, '零星用工单', lambda item: check_employee(item, False)
            ))
    
    elif data_type == 'project' and project_name:
        project_id = None
        for pid, pname in project_dict.items():
            if pname == project_name:
                project_id = pid
                break
        
        if project_id:
            def check_project(item, require_completed=False):
                plan_start = item.plan_start_date
                if isinstance(plan_start, datetime):
                    plan_start = plan_start.date()
                if plan_start and year_start <= plan_start <= year_end:
                    if item.project_id == project_id:
                        if require_completed:
                            return item.status in completed_statuses
                        return True
                return False
            
            if order_type == 'inspection':
                results.extend(filter_and_paginate(
                    db.query(PeriodicInspection), PeriodicInspection, '定期巡检单', lambda item: check_project(item, True)
                ))
            elif order_type == 'repair':
                results.extend(filter_and_paginate(
                    db.query(TemporaryRepair), TemporaryRepair, '临时维修单', lambda item: check_project(item, True)
                ))
            elif order_type == 'spotwork':
                results.extend(filter_and_paginate(
                    db.query(SpotWork), SpotWork, '零星用工单', lambda item: check_project(item, True)
                ))
            else:
                results.extend(filter_and_paginate(
                    db.query(PeriodicInspection), PeriodicInspection, '定期巡检单', lambda item: check_project(item, False)
                ))
                results.extend(filter_and_paginate(
                    db.query(TemporaryRepair), TemporaryRepair, '临时维修单', lambda item: check_project(item, False)
                ))
                results.extend(filter_and_paginate(
                    db.query(SpotWork), SpotWork, '零星用工单', lambda item: check_project(item, False)
                ))
    
    total = len(results)
    start_idx = (page - 1) * page_size
    end_idx = start_idx + page_size
    paginated_results = results[start_idx:end_idx]
    
    return ApiResponse.success({
        'total': total,
        'page': page,
        'pageSize': page_size,
        'data': paginated_results
    })
