from typing import List
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_, case
from app.database import get_db
from app.schemas.common import ApiResponse
from app.models.periodic_inspection import PeriodicInspection
from app.models.temporary_repair import TemporaryRepair
from app.models.spot_work import SpotWork
from app.models.maintenance_plan import MaintenancePlan
from app.models.personnel import Personnel

router = APIRouter(prefix="/statistics", tags=["Statistics"])


@router.get("/overview", response_model=ApiResponse)
def get_statistics_overview(
    year: int = Query(..., description="年度"),
    db: Session = Depends(get_db)
):
    """获取统计数据概览"""
    
    # 获取年度数据
    year_data = db.query(
        func.extract('year', PeriodicInspection.created_at) == year
    ).all()
    
    # 统计定期巡检单
    regular_inspection_count = len([
        item for item in year_data
        if hasattr(item, 'status') and item.status == '已完成'
    ])
    
    # 统计临时维修单
    temporary_repair_count = len([
        item for item in year_data
        if hasattr(item, 'status') and item.status == '已完成'
    ])
    
    # 统计零星用工单
    spot_work_data = db.query(
        func.extract('year', SpotWork.created_at) == year
    ).all()
    spot_work_count = len([
        item for item in spot_work_data
        if hasattr(item, 'status') and item.status == '已完成'
    ])
    
    # 统计维保计划
    maintenance_plan_data = db.query(
        func.extract('year', MaintenancePlan.created_at) == year
    ).all()
    maintenance_plan_count = len([
        item for item in maintenance_plan_data
        if hasattr(item, 'plan_status') and item.plan_status == '已完成'
    ])
    
    return ApiResponse.success({
        'year': year,
        'regularInspectionCount': regular_inspection_count,
        'temporaryRepairCount': temporary_repair_count,
        'spotWorkCount': spot_work_count,
        'maintenancePlanCount': maintenance_plan_count
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