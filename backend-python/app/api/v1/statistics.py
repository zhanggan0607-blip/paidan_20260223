from typing import List
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_, case
from datetime import datetime, timedelta
from app.database import get_db
from app.schemas.common import ApiResponse
from app.models.periodic_inspection import PeriodicInspection
from app.models.temporary_repair import TemporaryRepair
from app.models.spot_work import SpotWork
from app.models.maintenance_plan import MaintenancePlan
from app.models.personnel import Personnel
from app.config import OverdueAlertConfig

router = APIRouter(prefix="/statistics", tags=["Statistics"])


@router.get("/overview", response_model=ApiResponse)
def get_statistics_overview(
    year: int = Query(..., description="年度"),
    db: Session = Depends(get_db)
):
    """获取统计数据概览"""
    
    today = datetime.now()
    near_expiry_date = today + timedelta(days=7)
    
    # 临期工单：临时维修单中，状态为未完成且7天内到期的
    near_expiry_repairs = db.query(TemporaryRepair).filter(
        TemporaryRepair.status.in_(OverdueAlertConfig.VALID_STATUSES),
        TemporaryRepair.plan_end_date >= today,
        TemporaryRepair.plan_end_date <= near_expiry_date
    ).all()
    near_expiry_count = len(near_expiry_repairs)
    
    # 超期工单：项目超期提醒汇总数量（定期巡检、临时维修、零星用工中已超期的）
    overdue_inspections = db.query(PeriodicInspection).filter(
        PeriodicInspection.status.in_(OverdueAlertConfig.VALID_STATUSES),
        PeriodicInspection.plan_end_date < today
    ).all()
    
    overdue_repairs = db.query(TemporaryRepair).filter(
        TemporaryRepair.status.in_(OverdueAlertConfig.VALID_STATUSES),
        TemporaryRepair.plan_end_date < today
    ).all()
    
    overdue_spot_works = db.query(SpotWork).filter(
        SpotWork.status.in_(OverdueAlertConfig.VALID_STATUSES),
        SpotWork.plan_end_date < today
    ).all()
    
    overdue_count = len(overdue_inspections) + len(overdue_repairs) + len(overdue_spot_works)
    
    # 本年完成：定期巡检单中本年度已完成的数量
    completed_inspections = db.query(PeriodicInspection).filter(
        func.extract('year', PeriodicInspection.created_at) == year,
        PeriodicInspection.status == '已完成'
    ).all()
    completed_count = len(completed_inspections)
    
    # 定期巡检单：本年度定期巡检单总数
    regular_inspections = db.query(PeriodicInspection).filter(
        func.extract('year', PeriodicInspection.created_at) == year
    ).all()
    regular_inspection_count = len(regular_inspections)
    
    # 临时维修单：临时维修单查询汇总数量（所有临时维修单）
    temporary_repairs = db.query(TemporaryRepair).all()
    temporary_repair_count = len(temporary_repairs)
    
    # 零星用工单：零星用工管理汇总数量（所有零星用工单）
    spot_works = db.query(SpotWork).all()
    spot_work_count = len(spot_works)
    
    return ApiResponse.success({
        'year': year,
        'nearExpiry': near_expiry_count,
        'overdue': overdue_count,
        'completed': completed_count,
        'regularInspectionCount': regular_inspection_count,
        'temporaryRepairCount': temporary_repair_count,
        'spotWorkCount': spot_work_count
    })


@router.get("/work-by-person", response_model=ApiResponse)
def get_work_by_person(
    year: int = Query(..., description="年度"),
    db: Session = Depends(get_db)
):
    """获取按人员统计的工单数据"""
    
    # 获取年度数据
    year_data = db.query(
        func.extract('year', PeriodicInspection.created_at) == year
    ).all()
    
    # 按人员分组统计定期巡检单
    inspection_by_person = {}
    for item in year_data:
        if hasattr(item, 'status') and item.status == '已完成':
            if item.maintenance_personnel not in inspection_by_person:
                inspection_by_person[item.maintenance_personnel] = 0
            inspection_by_person[item.maintenance_personnel] += 1
    
    # 按人员分组统计临时维修单
    repair_data = db.query(
        func.extract('year', TemporaryRepair.created_at) == year
    ).all()
    repair_by_person = {}
    for item in repair_data:
        if hasattr(item, 'status') and item.status == '已完成':
            if item.maintenance_personnel not in repair_by_person:
                repair_by_person[item.maintenance_personnel] = 0
            repair_by_person[item.maintenance_personnel] += 1
    
    # 按人员分组统计零星用工单
    spot_work_data = db.query(
        func.extract('year', SpotWork.created_at) == year
    ).all()
    labor_by_person = {}
    for item in spot_work_data:
        if hasattr(item, 'status') and item.status == '已完成':
            if item.maintenance_personnel not in labor_by_person:
                labor_by_person[item.maintenance_personnel] = 0
            labor_by_person[item.maintenance_personnel] += 1
    
    # 获取人员信息
    personnel_list = db.query(Personnel).all()
    personnel_dict = {p.id: p.name for p in personnel_list}
    
    # 构建返回数据
    work_by_person_list = []
    for person_id, total in inspection_by_person.items():
        person_name = personnel_dict.get(person_id, f'人员{person_id}')
        work_by_person_list.append({
            'name': person_name,
            'value': total
        })
    
    for person_id, total in repair_by_person.items():
        person_name = personnel_dict.get(person_id, f'人员{person_id}')
        work_by_person_list.append({
            'name': person_name,
            'value': total
        })
    
    for person_id, total in labor_by_person.items():
        person_name = personnel_dict.get(person_id, f'人员{person_id}')
        work_by_person_list.append({
            'name': person_name,
            'value': total
        })
    
    return ApiResponse.success(work_by_person_list)


@router.get("/completion-rate", response_model=ApiResponse)
def get_completion_rate(
    year: int = Query(..., description="年度"),
    db: Session = Depends(get_db)
):
    """获取准时完成率"""
    
    # 获取年度数据
    year_data = db.query(
        func.extract('year', PeriodicInspection.created_at) == year
    ).all()
    
    total_count = len(year_data)
    if total_count == 0:
        return ApiResponse.success({
            'year': year,
            'onTimeRate': 0
        })
    
    # 统计准时完成数量
    on_time_count = len([
        item for item in year_data
        if hasattr(item, 'status') and item.status == '已完成' and hasattr(item, 'plan_end_date') and hasattr(item, 'actual_end_date')
        and item.plan_end_date
        and item.actual_end_date <= item.plan_end_date
    ])
    
    # 计算准时完成率
    on_time_rate = on_time_count / total_count if total_count > 0 else 0
    
    return ApiResponse.success({
        'year': year,
        'onTimeRate': round(on_time_rate, 2)
    })


@router.get("/top-projects", response_model=ApiResponse)
def get_top_projects(
    year: int = Query(..., description="年度"),
    limit: int = Query(5, ge=1, le=10, description="返回数量"),
    db: Session = Depends(get_db)
):
    """获取年度前五项目"""
    
    # 获取年度数据
    year_data = db.query(
        func.extract('year', PeriodicInspection.created_at) == year
    ).all()
    
    # 按项目统计工单数量
    project_stats = {}
    for item in year_data:
        if hasattr(item, 'project_id') and item.project_id not in project_stats:
            project_stats[item.project_id] = 0
        if hasattr(item, 'status') and item.status == '已完成':
            project_stats[item.project_id] += 1
    
    # 排序并取前五
    sorted_projects = sorted(project_stats.items(), key=lambda x: x[1], reverse=True)[:limit]
    
    return ApiResponse.success([
        {'name': f'项目{project_id}', 'value': value}
        for project_id, value in sorted_projects
    ])
