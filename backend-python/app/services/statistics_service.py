from app.utils.logging_config import get_logger
from datetime import datetime, date, timedelta
from typing import Any

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.config import OverdueAlertConfig
from app.models.periodic_inspection import PeriodicInspection
from app.models.project_info import ProjectInfo
from app.models.spot_work import SpotWork
from app.models.temporary_repair import TemporaryRepair

logger = get_logger(__name__)

WORK_ORDER_MODELS = [
    (PeriodicInspection, '定期巡检单'),
    (TemporaryRepair, '临时维修单'),
    (SpotWork, '零星用工单'),
]


def _apply_user_filter(query, model, user_name: str | None, is_manager: bool):
    if not is_manager and user_name and hasattr(model, 'maintenance_personnel'):
        query = query.filter(model.maintenance_personnel == user_name)
    return query


def _apply_soft_delete_filter(query, model):
    if hasattr(model, 'is_deleted'):
        query = query.filter(model.is_deleted == False)
    return query


def _format_work_order(item, order_type_str: str, project_dict: dict) -> dict:
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

    return {
        'id': item.id,
        'orderType': order_type_str,
        'orderNumber': order_number,
        'projectName': project_dict.get(item.project_id, item.project_id or ''),
        'maintenancePersonnel': item.maintenance_personnel or '',
        'planStartDate': plan_start.strftime('%Y-%m-%d') if plan_start else '',
        'planEndDate': plan_end.strftime('%Y-%m-%d') if plan_end else '',
        'status': item.status or '',
        'content': item.remarks or ''
    }


def _load_project_dict(db: Session, project_ids: set) -> dict:
    if not project_ids:
        return {}
    return dict(
        (p.project_id, p.project_name)
        for p in db.query(ProjectInfo).filter(
            ProjectInfo.project_id.in_(project_ids)
        ).all()
    )


def _sql_filter_and_paginate(
    db: Session,
    base_query,
    model,
    order_type_str: str,
    sql_filters: list,
    user_name: str | None,
    is_manager: bool,
    project_dict: dict
) -> tuple[list[dict], int, dict]:
    query = _apply_soft_delete_filter(base_query, model)
    query = _apply_user_filter(query, model, user_name, is_manager)
    for f in sql_filters:
        query = query.filter(f)
    total = query.count()
    needed_ids = {pid for pid, in query.with_entities(model.project_id).distinct().all() if pid}
    missing_ids = needed_ids - set(project_dict.keys())
    if missing_ids:
        project_dict.update(_load_project_dict(db, missing_ids))
    items = [_format_work_order(item, order_type_str, project_dict) for item in query.all()]
    return items, total, project_dict


class StatisticsService:
    def __init__(self, db: Session):
        self._db = db

    def get_detail(
        self,
        year: int,
        data_type: str,
        user_name: str | None,
        is_manager: bool,
        employee_name: str | None = None,
        project_name: str | None = None,
        order_type: str | None = None,
        page: int = 1,
        page_size: int = 20
    ) -> dict:
        today = datetime.now().date()
        current_year = today.year
        year_start = datetime(year, 1, 1).date()
        year_end = datetime(year, 12, 31).date()
        near_due_days = 7
        valid_statuses = OverdueAlertConfig.VALID_STATUSES
        completed_statuses = OverdueAlertConfig.COMPLETED_STATUSES

        year_start_dt = datetime.combine(year_start, datetime.min.time())
        year_end_dt = datetime.combine(year_end, datetime.max.time())

        project_dict: dict[str, str] = {}
        results: list[dict] = []

        handlers = {
            'nearDue': lambda: self._handle_near_due(today, near_due_days, valid_statuses, user_name, is_manager, project_dict),
            'overdue': lambda: self._handle_overdue(today, current_year, year_end, valid_statuses, user_name, is_manager, project_dict),
            'yearCompleted': lambda: self._handle_year_completed(year_start_dt, year_end_dt, completed_statuses, user_name, is_manager, project_dict),
            'regularInspection': lambda: self._handle_single_type(PeriodicInspection, '定期巡检单', year_start_dt, year_end_dt, valid_statuses, user_name, is_manager, project_dict),
            'temporaryRepair': lambda: self._handle_single_type(TemporaryRepair, '临时维修单', year_start_dt, year_end_dt, valid_statuses, user_name, is_manager, project_dict),
            'spotWork': lambda: self._handle_single_type(SpotWork, '零星用工单', year_start_dt, year_end_dt, valid_statuses, user_name, is_manager, project_dict),
            'onTime': lambda: self._handle_on_time(year_start_dt, year_end_dt, completed_statuses, user_name, is_manager, project_dict),
            'delayed': lambda: self._handle_delayed(year_start_dt, year_end_dt, completed_statuses, user_name, is_manager, project_dict),
            'employee': lambda: self._handle_employee(year_start_dt, year_end_dt, completed_statuses, employee_name, order_type, user_name, is_manager, project_dict),
            'project': lambda: self._handle_project(year_start_dt, year_end_dt, completed_statuses, project_name, order_type, user_name, is_manager, project_dict),
        }

        handler = handlers.get(data_type)
        if handler:
            results = handler()

        total = len(results)
        start_idx = (page - 1) * page_size
        end_idx = start_idx + page_size
        paginated_results = results[start_idx:end_idx]

        return {
            'total': total,
            'page': page,
            'pageSize': page_size,
            'data': paginated_results
        }

    def _query_models(
        self,
        model_class,
        label: str,
        sql_filters: list,
        user_name: str | None,
        is_manager: bool,
        project_dict: dict
    ) -> tuple[list[dict], dict]:
        items, _, updated_dict = _sql_filter_and_paginate(
            self._db, self._db.query(model_class), model_class, label,
            sql_filters, user_name, is_manager, project_dict
        )
        return items, updated_dict

    def _handle_near_due(self, today, near_due_days, valid_statuses, user_name, is_manager, project_dict):
        results = []
        today_dt = datetime.combine(today, datetime.min.time())
        near_due_end_dt = datetime.combine(today + timedelta(days=near_due_days), datetime.max.time())
        for model_class, label in WORK_ORDER_MODELS:
            filters = [
                model_class.plan_start_date >= today_dt,
                model_class.plan_start_date <= near_due_end_dt,
                model_class.status.in_(valid_statuses)
            ]
            items, project_dict = self._query_models(model_class, label, filters, user_name, is_manager, project_dict)
            results.extend(items)
        return results

    def _handle_overdue(self, today, current_year, year_end, valid_statuses, user_name, is_manager, project_dict):
        results = []
        check_date = datetime.combine(today if current_year == today.year else year_end, datetime.min.time())
        for model_class, label in WORK_ORDER_MODELS:
            filters = [
                model_class.plan_end_date < check_date,
                model_class.status.in_(valid_statuses)
            ]
            items, project_dict = self._query_models(model_class, label, filters, user_name, is_manager, project_dict)
            results.extend(items)
        return results

    def _handle_year_completed(self, year_start_dt, year_end_dt, completed_statuses, user_name, is_manager, project_dict):
        results = []
        for model_class, label in WORK_ORDER_MODELS:
            filters = [
                model_class.status.in_(completed_statuses),
                model_class.actual_completion_date >= year_start_dt,
                model_class.actual_completion_date <= year_end_dt
            ]
            items, project_dict = self._query_models(model_class, label, filters, user_name, is_manager, project_dict)
            results.extend(items)
        return results

    def _handle_single_type(self, model_class, label, year_start_dt, year_end_dt, valid_statuses, user_name, is_manager, project_dict):
        filters = [
            model_class.plan_start_date >= year_start_dt,
            model_class.plan_start_date <= year_end_dt,
            model_class.status.in_(valid_statuses)
        ]
        items, _ = self._query_models(model_class, label, filters, user_name, is_manager, project_dict)
        return items

    def _handle_on_time(self, year_start_dt, year_end_dt, completed_statuses, user_name, is_manager, project_dict):
        results = []
        for model_class, label in WORK_ORDER_MODELS:
            filters = [
                model_class.status.in_(completed_statuses),
                model_class.plan_start_date >= year_start_dt,
                model_class.plan_start_date <= year_end_dt,
                model_class.actual_completion_date.isnot(None),
                model_class.actual_completion_date <= model_class.plan_end_date
            ]
            items, project_dict = self._query_models(model_class, label, filters, user_name, is_manager, project_dict)
            results.extend(items)
        return results

    def _handle_delayed(self, year_start_dt, year_end_dt, completed_statuses, user_name, is_manager, project_dict):
        results = []
        for model_class, label in WORK_ORDER_MODELS:
            filters = [
                model_class.status.in_(completed_statuses),
                model_class.plan_start_date >= year_start_dt,
                model_class.plan_start_date <= year_end_dt,
                model_class.actual_completion_date.isnot(None),
                model_class.actual_completion_date > model_class.plan_end_date
            ]
            items, project_dict = self._query_models(model_class, label, filters, user_name, is_manager, project_dict)
            results.extend(items)
        return results

    def _handle_employee(self, year_start_dt, year_end_dt, completed_statuses, employee_name, order_type, user_name, is_manager, project_dict):
        if not employee_name:
            return []

        order_type_map = {
            'inspection': (PeriodicInspection, '定期巡检单'),
            'repair': (TemporaryRepair, '临时维修单'),
            'spotwork': (SpotWork, '零星用工单'),
        }

        results = []
        if order_type and order_type in order_type_map:
            model_class, label = order_type_map[order_type]
            filters = [
                model_class.plan_start_date >= year_start_dt,
                model_class.plan_start_date <= year_end_dt,
                model_class.maintenance_personnel == employee_name,
                model_class.status.in_(completed_statuses)
            ]
            items, project_dict = self._query_models(model_class, label, filters, user_name, is_manager, project_dict)
            results.extend(items)
        else:
            for model_class, label in WORK_ORDER_MODELS:
                filters = [
                    model_class.plan_start_date >= year_start_dt,
                    model_class.plan_start_date <= year_end_dt,
                    model_class.maintenance_personnel == employee_name
                ]
                items, project_dict = self._query_models(model_class, label, filters, user_name, is_manager, project_dict)
                results.extend(items)
        return results

    def _handle_project(self, year_start_dt, year_end_dt, completed_statuses, project_name, order_type, user_name, is_manager, project_dict):
        if not project_name:
            return []

        project_dict.update(
            dict(self._db.query(ProjectInfo.project_id, ProjectInfo.project_name).all())
        )

        project_id = None
        for pid, pname in project_dict.items():
            if pname == project_name:
                project_id = pid
                break

        if not project_id:
            return []

        order_type_map = {
            'inspection': (PeriodicInspection, '定期巡检单'),
            'repair': (TemporaryRepair, '临时维修单'),
            'spotwork': (SpotWork, '零星用工单'),
        }

        results = []
        if order_type and order_type in order_type_map:
            model_class, label = order_type_map[order_type]
            filters = [
                model_class.plan_start_date >= year_start_dt,
                model_class.plan_start_date <= year_end_dt,
                model_class.project_id == project_id,
                model_class.status.in_(completed_statuses)
            ]
            items, project_dict = self._query_models(model_class, label, filters, user_name, is_manager, project_dict)
            results.extend(items)
        else:
            for model_class, label in WORK_ORDER_MODELS:
                filters = [
                    model_class.plan_start_date >= year_start_dt,
                    model_class.plan_start_date <= year_end_dt,
                    model_class.project_id == project_id
                ]
                items, project_dict = self._query_models(model_class, label, filters, user_name, is_manager, project_dict)
                results.extend(items)
        return results

    def get_model_stats_with_sql(
        self,
        model,
        year: int,
        user_name: str | None,
        is_manager: bool,
        valid_statuses: list,
        completed_statuses: list,
    ) -> dict:
        year_start = datetime(year, 1, 1)
        year_end = datetime(year, 12, 31, 23, 59, 59)

        query = self._db.query(model)
        query = _apply_soft_delete_filter(query, model)
        query = _apply_user_filter(query, model, user_name, is_manager)

        total = query.count()

        valid_query = query.filter(model.status.in_(valid_statuses))
        valid_count = valid_query.count()

        completed_query = query.filter(
            model.status.in_(completed_statuses),
            model.actual_completion_date >= year_start,
            model.actual_completion_date <= year_end
        )
        completed_count = completed_query.count()

        return {
            'total': total,
            'valid': valid_count,
            'completed': completed_count
        }

    def get_employee_stats_with_sql(
        self,
        model,
        year: int,
        valid_statuses: list,
        completed_statuses: list,
    ) -> list[dict]:
        year_start = datetime(year, 1, 1)
        year_end = datetime(year, 12, 31, 23, 59, 59)

        query = self._db.query(
            model.maintenance_personnel,
            func.count(model.id).label('total'),
            func.count(case((model.status.in_(valid_statuses), 1))).label('valid'),
            func.count(case((model.status.in_(completed_statuses), 1), (model.actual_completion_date >= year_start, 1), (model.actual_completion_date <= year_end, 1))).label('completed')
        ).filter(
            model.is_deleted == False if hasattr(model, 'is_deleted') else True,
            model.maintenance_personnel.isnot(None),
            model.maintenance_personnel != ''
        ).group_by(
            model.maintenance_personnel
        ).all()

        return [
            {
                'name': row[0],
                'total': row[1],
                'valid': row[2],
                'completed': row[3]
            }
            for row in query
        ]
