from typing import List
from fastapi import APIRouter, Depends, Query, HTTPException
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

router = APIRouter(prefix="/statistics", tags=["Statistics"])


@router.get("/overview", response_model=ApiResponse)
def get_statistics_overview(
    year: int = Query(..., description="年度"),
    db: Session = Depends(get_db)
):
    """获取统计数据概览 - 从三种工单表获取数据"""
    
    today = datetime.now().date()
    current_year = today.year
    year_start = datetime(year, 1, 1).date()
    year_end = datetime(year, 12, 31).date()
    near_due_days = 3
    valid_statuses = OverdueAlertConfig.VALID_STATUSES
    
    near_due_count = 0
    overdue_count = 0
    year_completed_count = 0
    regular_inspection_count = 0
    temporary_repair_count = 0
    spot_work_count = 0
    
    is_current_year = (year == current_year)
    
    for inspection in db.query(PeriodicInspection).all():
        plan_start = inspection.plan_start_date
        plan_end = inspection.plan_end_date
        if isinstance(plan_start, datetime):
            plan_start = plan_start.date()
        if isinstance(plan_end, datetime):
            plan_end = plan_end.date()
        
        if plan_start:
            if plan_start >= year_start and plan_start <= year_end:
                regular_inspection_count += 1
        
        if is_current_year and plan_start:
            days_from_today = (plan_start - today).days
            if 0 <= days_from_today <= near_due_days:
                near_due_count += 1
        
        if plan_end:
            check_date = today if is_current_year else year_end
            if plan_end < check_date and inspection.status in valid_statuses:
                overdue_count += 1
        
        if inspection.status == '已完成' and plan_end:
            if plan_end >= year_start and plan_end <= year_end:
                year_completed_count += 1
    
    for repair in db.query(TemporaryRepair).all():
        plan_start = repair.plan_start_date
        plan_end = repair.plan_end_date
        if isinstance(plan_start, datetime):
            plan_start = plan_start.date()
        if isinstance(plan_end, datetime):
            plan_end = plan_end.date()
        
        if plan_start:
            if plan_start >= year_start and plan_start <= year_end:
                temporary_repair_count += 1
        
        if is_current_year and plan_start:
            days_from_today = (plan_start - today).days
            if 0 <= days_from_today <= near_due_days:
                near_due_count += 1
        
        if plan_end:
            check_date = today if is_current_year else year_end
            if plan_end < check_date and repair.status in valid_statuses:
                overdue_count += 1
        
        if repair.status == '已完成' and plan_end:
            if plan_end >= year_start and plan_end <= year_end:
                year_completed_count += 1
    
    for work in db.query(SpotWork).all():
        plan_start = work.plan_start_date
        plan_end = work.plan_end_date
        if isinstance(plan_start, datetime):
            plan_start = plan_start.date()
        if isinstance(plan_end, datetime):
            plan_end = plan_end.date()
        
        if plan_start:
            if plan_start >= year_start and plan_start <= year_end:
                spot_work_count += 1
        
        if is_current_year and plan_start:
            days_from_today = (plan_start - today).days
            if 0 <= days_from_today <= near_due_days:
                near_due_count += 1
        
        if plan_end:
            check_date = today if is_current_year else year_end
            if plan_end < check_date and work.status in valid_statuses:
                overdue_count += 1
        
        if work.status == '已完成' and plan_end:
            if plan_end >= year_start and plan_end <= year_end:
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
    year: int = Query(..., description="年度"),
    db: Session = Depends(get_db)
):
    """获取准时完成率 - 从三种工单表获取数据"""
    
    year_start = datetime(year, 1, 1).date()
    year_end = datetime(year, 12, 31).date()
    
    on_time_count = 0
    total_count = 0
    
    for inspection in db.query(PeriodicInspection).filter(PeriodicInspection.status == '已完成').all():
        plan_end = inspection.plan_end_date
        actual_end = inspection.updated_at
        if isinstance(plan_end, datetime):
            plan_end = plan_end.date()
        if isinstance(actual_end, datetime):
            actual_end = actual_end.date()
        if plan_end and actual_end:
            if plan_end >= year_start and plan_end <= year_end:
                total_count += 1
                if actual_end <= plan_end:
                    on_time_count += 1
    
    for repair in db.query(TemporaryRepair).filter(TemporaryRepair.status == '已完成').all():
        plan_end = repair.plan_end_date
        actual_end = repair.updated_at
        if isinstance(plan_end, datetime):
            plan_end = plan_end.date()
        if isinstance(actual_end, datetime):
            actual_end = actual_end.date()
        if plan_end and actual_end:
            if plan_end >= year_start and plan_end <= year_end:
                total_count += 1
                if actual_end <= plan_end:
                    on_time_count += 1
    
    for work in db.query(SpotWork).filter(SpotWork.status == '已完成').all():
        plan_end = work.plan_end_date
        actual_end = work.updated_at
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
    """获取年度前五项目（工单数量）- 从三种工单表获取数据"""
    
    year_start = datetime(year, 1, 1).date()
    year_end = datetime(year, 12, 31).date()
    
    project_stats = {}
    
    for inspection in db.query(PeriodicInspection).filter(PeriodicInspection.status == '已完成').all():
        plan_end = inspection.plan_end_date
        if isinstance(plan_end, datetime):
            plan_end = plan_end.date()
        if plan_end and plan_end >= year_start and plan_end <= year_end:
            if inspection.project_id:
                if inspection.project_id not in project_stats:
                    project_stats[inspection.project_id] = 0
                project_stats[inspection.project_id] += 1
    
    for repair in db.query(TemporaryRepair).filter(TemporaryRepair.status == '已完成').all():
        plan_end = repair.plan_end_date
        if isinstance(plan_end, datetime):
            plan_end = plan_end.date()
        if plan_end and plan_end >= year_start and plan_end <= year_end:
            if repair.project_id:
                if repair.project_id not in project_stats:
                    project_stats[repair.project_id] = 0
                project_stats[repair.project_id] += 1
    
    for work in db.query(SpotWork).filter(SpotWork.status == '已完成').all():
        plan_end = work.plan_end_date
        if isinstance(plan_end, datetime):
            plan_end = plan_end.date()
        if plan_end and plan_end >= year_start and plan_end <= year_end:
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
    year: int = Query(..., description="年度"),
    limit: int = Query(5, ge=1, le=10, description="返回数量"),
    db: Session = Depends(get_db)
):
    """获取临时维修单年度前五 - 按项目统计临时维修单数量"""
    
    year_start = datetime(year, 1, 1).date()
    year_end = datetime(year, 12, 31).date()
    
    project_stats = {}
    
    for repair in db.query(TemporaryRepair).filter(TemporaryRepair.status == '已完成').all():
        plan_end = repair.plan_end_date
        if isinstance(plan_end, datetime):
            plan_end = plan_end.date()
        if plan_end and plan_end >= year_start and plan_end <= year_end:
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
    year: int = Query(..., description="年度"),
    db: Session = Depends(get_db)
):
    """获取员工工单数量统计 - 按运维人员分组统计"""
    
    year_start = datetime(year, 1, 1).date()
    year_end = datetime(year, 12, 31).date()
    
    employee_stats = {}
    
    for inspection in db.query(PeriodicInspection).all():
        plan_end = inspection.plan_end_date
        if isinstance(plan_end, datetime):
            plan_end = plan_end.date()
        if plan_end and plan_end >= year_start and plan_end <= year_end:
            personnel = inspection.maintenance_personnel or '未知'
            if personnel not in employee_stats:
                employee_stats[personnel] = 0
            employee_stats[personnel] += 1
    
    for repair in db.query(TemporaryRepair).all():
        plan_end = repair.plan_end_date
        if isinstance(plan_end, datetime):
            plan_end = plan_end.date()
        if plan_end and plan_end >= year_start and plan_end <= year_end:
            personnel = repair.maintenance_personnel or '未知'
            if personnel not in employee_stats:
                employee_stats[personnel] = 0
            employee_stats[personnel] += 1
    
    for work in db.query(SpotWork).all():
        plan_end = work.plan_end_date
        if isinstance(plan_end, datetime):
            plan_end = plan_end.date()
        if plan_end and plan_end >= year_start and plan_end <= year_end:
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
    year: int = Query(..., description="年度"),
    db: Session = Depends(get_db)
):
    """获取临时维修单完成数量统计 - 按运维人员分组统计已完成的临时维修单"""
    
    year_start = datetime(year, 1, 1).date()
    year_end = datetime(year, 12, 31).date()
    
    repair_stats = {}
    
    for repair in db.query(TemporaryRepair).filter(TemporaryRepair.status == '已完成').all():
        plan_end = repair.plan_end_date
        if isinstance(plan_end, datetime):
            plan_end = plan_end.date()
        if plan_end and plan_end >= year_start and plan_end <= year_end:
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
    year: int = Query(..., description="年度"),
    db: Session = Depends(get_db)
):
    """获取零星用工单完成数量统计 - 按运维人员分组统计已完成的零星用工单"""
    
    year_start = datetime(year, 1, 1).date()
    year_end = datetime(year, 12, 31).date()
    
    spotwork_stats = {}
    
    for work in db.query(SpotWork).filter(SpotWork.status == '已完成').all():
        plan_end = work.plan_end_date
        if isinstance(plan_end, datetime):
            plan_end = plan_end.date()
        if plan_end and plan_end >= year_start and plan_end <= year_end:
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
    year: int = Query(..., description="年度"),
    db: Session = Depends(get_db)
):
    """获取定期巡检单完成数量统计 - 按运维人员分组统计已完成的定期巡检单"""
    
    year_start = datetime(year, 1, 1).date()
    year_end = datetime(year, 12, 31).date()
    
    inspection_stats = {}
    
    for inspection in db.query(PeriodicInspection).filter(PeriodicInspection.status == '已完成').all():
        plan_end = inspection.plan_end_date
        if isinstance(plan_end, datetime):
            plan_end = plan_end.date()
        if plan_end and plan_end >= year_start and plan_end <= year_end:
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
