from datetime import datetime, date, timedelta
import logging

from fastapi import APIRouter, Depends, Query
from sqlalchemy import func, and_, or_, case
from sqlalchemy.orm import Session

from app.config import OverdueAlertConfig
from app.database import get_db
from app.dependencies import UserInfo, get_current_user_info
from app.models.periodic_inspection import PeriodicInspection
from app.models.project_info import ProjectInfo
from app.models.spot_work import SpotWork
from app.models.temporary_repair import TemporaryRepair
from app.schemas.common import ApiResponse

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/statistics", tags=["Statistics"])


def _apply_user_filter(query, model, user_name: str | None, is_manager: bool):
    """应用用户数据过滤"""
    if not is_manager and user_name and hasattr(model, 'maintenance_personnel'):
        query = query.filter(model.maintenance_personnel == user_name)
    return query


def _apply_soft_delete_filter(query, model):
    """应用软删除过滤"""
    if hasattr(model, 'is_deleted'):
        query = query.filter(model.is_deleted == False)
    return query


def _get_user_info(user_info: UserInfo):
    """
    获取用户信息并判断是否为管理员
    返回: (user_name, is_manager)
    """
    return user_info.name, user_info.is_manager


def _get_model_stats_with_sql(
    db: Session,
    model,
    year: int,
    user_name: str | None,
    is_manager: bool,
    valid_statuses: list,
    completed_statuses: list,
    near_due_days: int = 7
):
    """
    使用SQL聚合函数获取单个模型的统计数据
    返回: (regular_count, near_due_count, overdue_count, year_completed_count)
    """
    today = date.today()
    current_year = today.year
    year_start = datetime(year, 1, 1).date()
    year_end = datetime(year, 12, 31).date()
    near_due_end = today + timedelta(days=near_due_days)
    
    today_datetime = datetime.combine(today, datetime.min.time())
    year_start_datetime = datetime.combine(year_start, datetime.min.time())
    year_end_datetime = datetime.combine(year_end, datetime.max.time())
    near_due_end_datetime = datetime.combine(near_due_end, datetime.max.time())
    
    query = db.query(model)
    query = _apply_soft_delete_filter(query, model)
    query = _apply_user_filter(query, model, user_name, is_manager)
    
    regular_count_query = query.filter(
        model.plan_start_date >= year_start_datetime,
        model.plan_start_date <= year_end_datetime,
        model.status.in_(valid_statuses)
    )
    regular_count = regular_count_query.count()
    
    if year == current_year:
        near_due_query = db.query(model)
        near_due_query = _apply_soft_delete_filter(near_due_query, model)
        near_due_query = _apply_user_filter(near_due_query, model, user_name, is_manager)
        near_due_query = near_due_query.filter(
            model.plan_start_date >= today_datetime,
            model.plan_start_date <= near_due_end_datetime,
            model.status.in_(valid_statuses)
        )
        near_due_count = near_due_query.count()
    else:
        near_due_count = 0
    
    check_date = today if year == current_year else year_end
    check_date_datetime = datetime.combine(check_date, datetime.min.time())
    overdue_query = db.query(model)
    overdue_query = _apply_soft_delete_filter(overdue_query, model)
    overdue_query = _apply_user_filter(overdue_query, model, user_name, is_manager)
    overdue_query = overdue_query.filter(
        model.plan_end_date < check_date_datetime,
        model.status.in_(valid_statuses)
    )
    overdue_count = overdue_query.count()
    
    year_completed_query = db.query(model)
    year_completed_query = _apply_soft_delete_filter(year_completed_query, model)
    year_completed_query = _apply_user_filter(year_completed_query, model, user_name, is_manager)
    year_completed_query = year_completed_query.filter(
        model.status.in_(completed_statuses),
        model.actual_completion_date >= year_start_datetime,
        model.actual_completion_date <= year_end_datetime
    )
    year_completed_count = year_completed_query.count()
    
    return regular_count, near_due_count, overdue_count, year_completed_count


@router.get("/overview", response_model=ApiResponse)
async def get_statistics_overview(
    year: int = Query(..., description="年度"),
    db: Session = Depends(get_db),
    user_info: UserInfo = Depends(get_current_user_info)
):
    """
    获取统计数据概览 - 从三种工单表获取数据
    年份过滤统一使用 plan_start_date
    本年完成使用 actual_completion_date 判断
    使用SQL聚合函数优化性能
    """

    user_name, is_manager = _get_user_info(user_info)

    valid_statuses = OverdueAlertConfig.VALID_STATUSES
    completed_statuses = OverdueAlertConfig.COMPLETED_STATUSES
    near_due_days = 7

    regular_inspection_count, near_due_inspection, overdue_inspection, completed_inspection = \
        _get_model_stats_with_sql(db, PeriodicInspection, year, user_name, is_manager, 
                                   valid_statuses, completed_statuses, near_due_days)
    
    temporary_repair_count, near_due_repair, overdue_repair, completed_repair = \
        _get_model_stats_with_sql(db, TemporaryRepair, year, user_name, is_manager,
                                   valid_statuses, completed_statuses, near_due_days)
    
    spot_work_count, near_due_work, overdue_work, completed_work = \
        _get_model_stats_with_sql(db, SpotWork, year, user_name, is_manager,
                                   valid_statuses, completed_statuses, near_due_days)

    near_due_count = near_due_inspection + near_due_repair + near_due_work
    overdue_count = overdue_inspection + overdue_repair + overdue_work
    year_completed_count = completed_inspection + completed_repair + completed_work
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


def _get_completion_stats_with_sql(
    db: Session,
    model,
    year: int,
    user_name: str | None,
    is_manager: bool,
    completed_statuses: list
):
    """
    使用SQL聚合函数获取单个模型的完成率统计
    返回: (on_time_count, total_count)
    """
    year_start = datetime(year, 1, 1).date()
    year_end = datetime(year, 12, 31).date()
    year_start_datetime = datetime.combine(year_start, datetime.min.time())
    year_end_datetime = datetime.combine(year_end, datetime.max.time())
    
    query = db.query(model).filter(model.status.in_(completed_statuses))
    query = _apply_soft_delete_filter(query, model)
    query = _apply_user_filter(query, model, user_name, is_manager)
    query = query.filter(
        model.plan_start_date >= year_start_datetime,
        model.plan_start_date <= year_end_datetime,
        model.actual_completion_date.isnot(None)
    )
    
    total_count = query.count()
    
    on_time_query = query.filter(model.actual_completion_date <= model.plan_end_date)
    on_time_count = on_time_query.count()
    
    return on_time_count, total_count


@router.get("/completion-rate", response_model=ApiResponse)
async def get_completion_rate(
    year: int = Query(..., description="年度"),
    db: Session = Depends(get_db),
    user_info: UserInfo = Depends(get_current_user_info)
):
    """
    获取准时完成率 - 从三种工单表获取数据
    使用 actual_completion_date 判断实际完成时间
    使用 plan_start_date 过滤年份
    使用SQL聚合函数优化性能
    """

    user_name, is_manager = _get_user_info(user_info)

    completed_statuses = OverdueAlertConfig.COMPLETED_STATUSES

    on_time_inspection, total_inspection = _get_completion_stats_with_sql(
        db, PeriodicInspection, year, user_name, is_manager, completed_statuses
    )
    
    on_time_repair, total_repair = _get_completion_stats_with_sql(
        db, TemporaryRepair, year, user_name, is_manager, completed_statuses
    )
    
    on_time_work, total_work = _get_completion_stats_with_sql(
        db, SpotWork, year, user_name, is_manager, completed_statuses
    )

    on_time_count = on_time_inspection + on_time_repair + on_time_work
    total_count = total_inspection + total_repair + total_work

    delayed_count = total_count - on_time_count
    on_time_rate = on_time_count / total_count if total_count > 0 else 0

    return ApiResponse.success({
        'year': year,
        'onTimeRate': round(on_time_rate, 4),
        'onTimeCount': on_time_count,
        'delayedCount': delayed_count,
        'totalCount': total_count
    })


def _get_project_stats_with_sql(
    db: Session,
    model,
    year: int,
    user_name: str | None,
    is_manager: bool,
    completed_statuses: list
):
    """
    使用SQL聚合函数获取单个模型的项目统计
    返回: dict {project_id: count}
    """
    year_start = datetime(year, 1, 1).date()
    year_end = datetime(year, 12, 31).date()
    year_start_datetime = datetime.combine(year_start, datetime.min.time())
    year_end_datetime = datetime.combine(year_end, datetime.max.time())
    
    query = db.query(
        model.project_id,
        func.count(model.id).label('count')
    ).filter(
        model.status.in_(completed_statuses),
        model.plan_start_date >= year_start_datetime,
        model.plan_start_date <= year_end_datetime,
        model.project_id.isnot(None)
    )
    
    query = _apply_soft_delete_filter(query, model)
    query = _apply_user_filter(query, model, user_name, is_manager)
    
    query = query.group_by(model.project_id)
    
    results = query.all()
    
    return {result.project_id: result.count for result in results}


@router.get("/top-projects", response_model=ApiResponse)
async def get_top_projects(
    year: int = Query(..., description="年度"),
    limit: int = Query(5, ge=1, le=10, description="返回数量"),
    db: Session = Depends(get_db),
    user_info: UserInfo = Depends(get_current_user_info)
):
    """
    获取年度前五项目（工单数量）- 从三种工单表获取数据
    使用 plan_start_date 过滤年份
    使用SQL聚合函数优化性能
    """

    user_name, is_manager = _get_user_info(user_info)

    completed_statuses = OverdueAlertConfig.COMPLETED_STATUSES

    project_stats = {}
    
    inspection_stats = _get_project_stats_with_sql(
        db, PeriodicInspection, year, user_name, is_manager, completed_statuses
    )
    for project_id, count in inspection_stats.items():
        project_stats[project_id] = project_stats.get(project_id, 0) + count
    
    repair_stats = _get_project_stats_with_sql(
        db, TemporaryRepair, year, user_name, is_manager, completed_statuses
    )
    for project_id, count in repair_stats.items():
        project_stats[project_id] = project_stats.get(project_id, 0) + count
    
    work_stats = _get_project_stats_with_sql(
        db, SpotWork, year, user_name, is_manager, completed_statuses
    )
    for project_id, count in work_stats.items():
        project_stats[project_id] = project_stats.get(project_id, 0) + count

    sorted_projects = sorted(project_stats.items(), key=lambda x: x[1], reverse=True)[:limit]

    needed_project_ids = [pid for pid, _ in sorted_projects]
    project_dict = {p.project_id: p.project_name for p in db.query(ProjectInfo).filter(
        ProjectInfo.project_id.in_(needed_project_ids)
    ).all()} if needed_project_ids else {}

    result = []
    for project_id, value in sorted_projects:
        project_name = project_dict.get(project_id, project_id)
        result.append({
            'name': project_name,
            'value': value
        })

    return ApiResponse.success(result)


@router.get("/top-repairs", response_model=ApiResponse)
async def get_top_repairs(
    year: int = Query(..., description="年度"),
    limit: int = Query(5, ge=1, le=10, description="返回数量"),
    db: Session = Depends(get_db),
    user_info: UserInfo = Depends(get_current_user_info)
):
    """
    获取临时维修单年度前五 - 按项目统计临时维修单数量
    使用 plan_start_date 过滤年份
    使用SQL聚合函数优化性能
    """

    user_name, is_manager = _get_user_info(user_info)

    completed_statuses = OverdueAlertConfig.COMPLETED_STATUSES

    project_stats = _get_project_stats_with_sql(
        db, TemporaryRepair, year, user_name, is_manager, completed_statuses
    )

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


def _get_employee_stats_with_sql(
    db: Session,
    model,
    year: int,
    user_name: str | None,
    is_manager: bool,
    status_filter: list | None = None
):
    """
    使用SQL聚合函数获取单个模型的员工统计
    返回: dict {personnel_name: count}
    """
    year_start = datetime(year, 1, 1).date()
    year_end = datetime(year, 12, 31).date()
    year_start_datetime = datetime.combine(year_start, datetime.min.time())
    year_end_datetime = datetime.combine(year_end, datetime.max.time())
    
    query = db.query(
        model.maintenance_personnel,
        func.count(model.id).label('count')
    ).filter(
        model.plan_start_date >= year_start_datetime,
        model.plan_start_date <= year_end_datetime
    )
    
    if status_filter:
        query = query.filter(model.status.in_(status_filter))
    
    query = _apply_soft_delete_filter(query, model)
    query = _apply_user_filter(query, model, user_name, is_manager)
    
    query = query.group_by(model.maintenance_personnel)
    
    results = query.all()
    
    return {result.maintenance_personnel or '未知': result.count for result in results}


@router.get("/employee-stats", response_model=ApiResponse)
async def get_employee_stats(
    year: int = Query(..., description="年度"),
    db: Session = Depends(get_db),
    user_info: UserInfo = Depends(get_current_user_info)
):
    """
    获取运维人员工单数量统计 - 按运维人员分组统计
    使用 plan_start_date 过滤年份
    使用SQL聚合函数优化性能
    """

    user_name, is_manager = _get_user_info(user_info)

    employee_stats = {}

    inspection_stats = _get_employee_stats_with_sql(
        db, PeriodicInspection, year, user_name, is_manager
    )
    for personnel, count in inspection_stats.items():
        employee_stats[personnel] = employee_stats.get(personnel, 0) + count

    repair_stats = _get_employee_stats_with_sql(
        db, TemporaryRepair, year, user_name, is_manager
    )
    for personnel, count in repair_stats.items():
        employee_stats[personnel] = employee_stats.get(personnel, 0) + count

    work_stats = _get_employee_stats_with_sql(
        db, SpotWork, year, user_name, is_manager
    )
    for personnel, count in work_stats.items():
        employee_stats[personnel] = employee_stats.get(personnel, 0) + count

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
async def get_repair_stats(
    year: int = Query(..., description="年度"),
    db: Session = Depends(get_db),
    user_info: UserInfo = Depends(get_current_user_info)
):
    """
    获取临时维修单完成数量统计 - 按运维人员分组统计已完成的临时维修单
    使用 plan_start_date 过滤年份
    使用SQL聚合函数优化性能
    """

    user_name, is_manager = _get_user_info(user_info)

    completed_statuses = OverdueAlertConfig.COMPLETED_STATUSES

    repair_stats = _get_employee_stats_with_sql(
        db, TemporaryRepair, year, user_name, is_manager, completed_statuses
    )

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
async def get_spotwork_stats(
    year: int = Query(..., description="年度"),
    db: Session = Depends(get_db),
    user_info: UserInfo = Depends(get_current_user_info)
):
    """
    获取零星用工单完成数量统计 - 按运维人员分组统计已完成的零星用工单
    使用 plan_start_date 过滤年份
    使用SQL聚合函数优化性能
    """

    user_name, is_manager = _get_user_info(user_info)

    completed_statuses = OverdueAlertConfig.COMPLETED_STATUSES

    spotwork_stats = _get_employee_stats_with_sql(
        db, SpotWork, year, user_name, is_manager, completed_statuses
    )

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
async def get_inspection_stats(
    year: int = Query(..., description="年度"),
    db: Session = Depends(get_db),
    user_info: UserInfo = Depends(get_current_user_info)
):
    """
    获取定期巡检单完成数量统计 - 按运维人员分组统计已完成的定期巡检单
    使用 plan_start_date 过滤年份
    使用SQL聚合函数优化性能
    """

    user_name, is_manager = _get_user_info(user_info)

    completed_statuses = OverdueAlertConfig.COMPLETED_STATUSES

    inspection_stats = _get_employee_stats_with_sql(
        db, PeriodicInspection, year, user_name, is_manager, completed_statuses
    )

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
async def get_statistics_detail(
    year: int = Query(..., description="年度"),
    data_type: str = Query(..., description="数据类型: nearDue/overdue/yearCompleted/regularInspection/temporaryRepair/spotWork/onTime/delayed/employee/project"),
    employee_name: str | None = Query(None, description="运维人员姓名(运维人员详情时使用)"),
    project_name: str | None = Query(None, description="项目名称(项目详情时使用)"),
    order_type: str | None = Query(None, description="工单类型(运维人员/项目详情时使用): inspection/repair/spotwork"),
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=1000, description="每页数量"),
    db: Session = Depends(get_db),
    user_info: UserInfo = Depends(get_current_user_info)
):
    """
    获取统计数据详细列表
    data_type: nearDue-临期工单, overdue-超期工单, yearCompleted-本年完成,
               regularInspection-定期巡检单, temporaryRepair-临时维修单, spotWork-零星用工单,
               onTime-准时完成, delayed-延期完成, employee-运维人员工单详情, project-项目工单详情
    年份过滤统一使用 plan_start_date
    本年完成使用 actual_completion_date 判断
    """

    user_name, is_manager = _get_user_info(user_info)

    today = datetime.now().date()
    current_year = today.year
    year_start = datetime(year, 1, 1).date()
    year_end = datetime(year, 12, 31).date()
    near_due_days = 7
    valid_statuses = OverdueAlertConfig.VALID_STATUSES
    completed_statuses = OverdueAlertConfig.COMPLETED_STATUSES

    results = []
    total = 0

    project_dict = {}

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
        """过滤并分页 - 使用SQL过滤而非内存过滤"""
        nonlocal project_dict
        query = _apply_soft_delete_filter(query, model)
        query = _apply_user_filter(query, model, user_name, is_manager)
        all_items = query.all()
        if not project_dict and all_items:
            needed_ids = {item.project_id for item in all_items if item.project_id}
            if needed_ids:
                project_dict.update(
                    (p.project_id, p.project_name)
                    for p in db.query(ProjectInfo).filter(
                        ProjectInfo.project_id.in_(needed_ids)
                    ).all()
                )
        items = [format_work_order(item, order_type_str) for item in all_items if filter_func(item)]
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
            return bool(plan_end and plan_end < check_date and item.status in valid_statuses)

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
                if year_start <= plan_start <= year_end:
                    return item.status in valid_statuses
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
                if year_start <= plan_start <= year_end:
                    return item.status in valid_statuses
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
                if year_start <= plan_start <= year_end:
                    return item.status in valid_statuses
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
