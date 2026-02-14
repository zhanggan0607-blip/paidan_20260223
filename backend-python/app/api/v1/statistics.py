from typing import List
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_, case, extract
from datetime import datetime, timedelta
from app.database import get_db
from app.schemas.common import ApiResponse
from app.models.maintenance_plan import MaintenancePlan
from app.models.project_info import ProjectInfo
from app.config import OverdueAlertConfig

router = APIRouter(prefix="/statistics", tags=["Statistics"])


@router.get("/overview", response_model=ApiResponse)
def get_statistics_overview(
    year: int = Query(..., description="年度"),
    db: Session = Depends(get_db)
):
    """获取统计数据概览 - 统一使用 MaintenancePlan 表"""
    
    today = datetime.now().date()
    year_start = datetime(year, 1, 1).date()
    year_end = datetime(year, 12, 31).date()
    near_due_days = 5
    valid_statuses = OverdueAlertConfig.VALID_STATUSES
    
    near_due_count = 0
    overdue_count = 0
    year_completed_count = 0
    regular_inspection_count = 0
    temporary_repair_count = 0
    spot_work_count = 0
    
    maintenance_plans = db.query(MaintenancePlan).all()
    for plan in maintenance_plans:
        plan_end = plan.plan_end_date
        if isinstance(plan_end, datetime):
            plan_end = plan_end.date()
        
        if plan_end:
            if plan_end < today and plan.plan_status in valid_statuses:
                overdue_count += 1
            elif 0 < (plan_end - today).days <= near_due_days and plan.plan_status in valid_statuses:
                near_due_count += 1
        
        if plan.plan_status == '已完成' and plan_end:
            if plan_end >= year_start and plan_end <= year_end:
                year_completed_count += 1
        
        if plan.plan_type == '定期维保':
            regular_inspection_count += 1
        elif plan.plan_type == '临时维修':
            temporary_repair_count += 1
        elif plan.plan_type == '零星用工':
            spot_work_count += 1
    
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
    year: int = Query(..., description="年度"),
    db: Session = Depends(get_db)
):
    """获取准时完成率 - 统一使用 MaintenancePlan 表"""
    
    year_start = datetime(year, 1, 1).date()
    year_end = datetime(year, 12, 31).date()
    
    on_time_count = 0
    total_count = 0
    
    maintenance_plans = db.query(MaintenancePlan).filter(
        MaintenancePlan.plan_status == '已完成'
    ).all()
    
    for plan in maintenance_plans:
        plan_end = plan.plan_end_date
        actual_end = plan.execution_date or plan.updated_at
        if isinstance(plan_end, datetime):
            plan_end = plan_end.date()
        if isinstance(actual_end, datetime):
            actual_end = actual_end.date()
        if plan_end and actual_end:
            if plan_end >= year_start and plan_end <= year_end:
                total_count += 1
                if actual_end <= plan_end:
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
    year: int = Query(..., description="年度"),
    limit: int = Query(5, ge=1, le=10, description="返回数量"),
    db: Session = Depends(get_db)
):
    """获取年度前五项目（维保单数量）- 统一使用 MaintenancePlan 表"""
    
    year_start = datetime(year, 1, 1).date()
    year_end = datetime(year, 12, 31).date()
    
    project_stats = {}
    
    maintenance_plans = db.query(MaintenancePlan).filter(
        MaintenancePlan.plan_status == '已完成'
    ).all()
    
    for plan in maintenance_plans:
        plan_end = plan.plan_end_date
        if isinstance(plan_end, datetime):
            plan_end = plan_end.date()
        if plan_end and plan_end >= year_start and plan_end <= year_end:
            if plan.project_id:
                if plan.project_id not in project_stats:
                    project_stats[plan.project_id] = 0
                project_stats[plan.project_id] += 1
    
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
    year: int = Query(..., description="年度"),
    limit: int = Query(5, ge=1, le=10, description="返回数量"),
    db: Session = Depends(get_db)
):
    """获取临时维修单年度前五 - 按项目统计临时维修单数量"""
    
    year_start = datetime(year, 1, 1).date()
    year_end = datetime(year, 12, 31).date()
    
    project_stats = {}
    
    maintenance_plans = db.query(MaintenancePlan).filter(
        MaintenancePlan.plan_type == '临时维修',
        MaintenancePlan.plan_status == '已完成'
    ).all()
    
    for plan in maintenance_plans:
        plan_end = plan.plan_end_date
        if isinstance(plan_end, datetime):
            plan_end = plan_end.date()
        if plan_end and plan_end >= year_start and plan_end <= year_end:
            if plan.project_id:
                if plan.project_id not in project_stats:
                    project_stats[plan.project_id] = 0
                project_stats[plan.project_id] += 1
    
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
    year: int = Query(..., description="年度"),
    db: Session = Depends(get_db)
):
    """获取员工工单数量统计 - 按运维人员分组统计"""
    
    year_start = datetime(year, 1, 1).date()
    year_end = datetime(year, 12, 31).date()
    
    employee_stats = {}
    
    maintenance_plans = db.query(MaintenancePlan).all()
    for plan in maintenance_plans:
        plan_end = plan.plan_end_date
        if isinstance(plan_end, datetime):
            plan_end = plan_end.date()
        if plan_end and plan_end >= year_start and plan_end <= year_end:
            personnel = plan.responsible_person or '未知'
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
    year: int = Query(..., description="年度"),
    db: Session = Depends(get_db)
):
    """获取临时维修单完成数量统计 - 按运维人员分组统计已完成的临时维修单"""
    
    year_start = datetime(year, 1, 1).date()
    year_end = datetime(year, 12, 31).date()
    
    repair_stats = {}
    
    maintenance_plans = db.query(MaintenancePlan).filter(
        MaintenancePlan.plan_type == '临时维修',
        MaintenancePlan.plan_status == '已完成'
    ).all()
    
    for plan in maintenance_plans:
        plan_end = plan.plan_end_date
        if isinstance(plan_end, datetime):
            plan_end = plan_end.date()
        if plan_end and plan_end >= year_start and plan_end <= year_end:
            personnel = plan.responsible_person or '未知'
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
    year: int = Query(..., description="年度"),
    db: Session = Depends(get_db)
):
    """获取零星用工单完成数量统计 - 按运维人员分组统计已完成的零星用工单"""
    
    year_start = datetime(year, 1, 1).date()
    year_end = datetime(year, 12, 31).date()
    
    spotwork_stats = {}
    
    maintenance_plans = db.query(MaintenancePlan).filter(
        MaintenancePlan.plan_type == '零星用工',
        MaintenancePlan.plan_status == '已完成'
    ).all()
    
    for plan in maintenance_plans:
        plan_end = plan.plan_end_date
        if isinstance(plan_end, datetime):
            plan_end = plan_end.date()
        if plan_end and plan_end >= year_start and plan_end <= year_end:
            personnel = plan.responsible_person or '未知'
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
    year: int = Query(..., description="年度"),
    db: Session = Depends(get_db)
):
    """获取定期巡检单完成数量统计 - 按运维人员分组统计已完成的定期巡检单"""
    
    year_start = datetime(year, 1, 1).date()
    year_end = datetime(year, 12, 31).date()
    
    inspection_stats = {}
    
    maintenance_plans = db.query(MaintenancePlan).filter(
        MaintenancePlan.plan_type == '定期维保',
        MaintenancePlan.plan_status == '已完成'
    ).all()
    
    for plan in maintenance_plans:
        plan_end = plan.plan_end_date
        if isinstance(plan_end, datetime):
            plan_end = plan_end.date()
        if plan_end and plan_end >= year_start and plan_end <= year_end:
            personnel = plan.responsible_person or '未知'
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
