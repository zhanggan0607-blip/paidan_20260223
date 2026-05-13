from app.utils.logging_config import get_logger
from datetime import date, datetime, timedelta

from sqlalchemy import and_, func, text
from sqlalchemy.orm import Session

from app.config import OverdueAlertConfig
from app.models.periodic_inspection import PeriodicInspection
from app.models.spot_work import SpotWork
from app.models.temporary_repair import TemporaryRepair

logger = get_logger(__name__)


class ExpiringSoonService:

    def __init__(self, db: Session):
        self.db = db

    def get_expiring_items(
        self,
        project_name: str | None = None,
        client_name: str | None = None,
        work_order_type: str | None = None,
        page: int = 0,
        size: int = 10,
        maintenance_personnel: str | None = None
    ) -> tuple[list[dict], int]:
        today = date.today()
        today_start = datetime.combine(today, datetime.min.time())
        week_end = datetime.combine(today + timedelta(days=7), datetime.max.time())
        valid_statuses = OverdueAlertConfig.VALID_STATUSES
        status_list = "','".join(valid_statuses)

        base_conditions = [
            "is_deleted = false",
            "plan_start_date >= :today_start",
            "plan_start_date <= :week_end",
            f"status IN ('{status_list}')"
        ]
        params: dict = {'today_start': today_start, 'week_end': week_end}

        if project_name:
            base_conditions.append("project_name ILIKE :project_name")
            params['project_name'] = f'%{project_name}%'
        if client_name:
            base_conditions.append("client_name ILIKE :client_name")
            params['client_name'] = f'%{client_name}%'
        if maintenance_personnel:
            base_conditions.append("maintenance_personnel = :maintenance_personnel")
            params['maintenance_personnel'] = maintenance_personnel

        filter_sql = " AND ".join(base_conditions)

        subqueries = []
        if work_order_type is None or work_order_type == '定期巡检':
            subqueries.append(f"""
                SELECT id, inspection_id AS order_no, project_id, project_name, client_name,
                       '定期巡检' AS work_order_type, plan_start_date, plan_end_date, status,
                       maintenance_personnel,
                       (CAST(plan_start_date AS date) - CURRENT_DATE) AS days_remaining,
                       created_at
                FROM periodic_inspection WHERE {filter_sql}
            """)
        if work_order_type is None or work_order_type == '临时维修':
            subqueries.append(f"""
                SELECT id, repair_id AS order_no, project_id, project_name, client_name,
                       '临时维修' AS work_order_type, plan_start_date, plan_end_date, status,
                       maintenance_personnel,
                       (CAST(plan_start_date AS date) - CURRENT_DATE) AS days_remaining,
                       created_at
                FROM temporary_repair WHERE {filter_sql}
            """)
        if work_order_type is None or work_order_type == '零星用工':
            subqueries.append(f"""
                SELECT id, work_id AS order_no, project_id, project_name, client_name,
                       '零星用工' AS work_order_type, plan_start_date, plan_end_date, status,
                       maintenance_personnel,
                       (CAST(plan_start_date AS date) - CURRENT_DATE) AS days_remaining,
                       created_at
                FROM spot_work WHERE {filter_sql}
            """)

        if not subqueries:
            return [], 0

        union_sql = " UNION ALL ".join(subqueries)

        count_sql = text(f"SELECT COUNT(*) FROM ({union_sql}) AS combined")
        total = self.db.execute(count_sql, params).scalar() or 0

        offset = page * size
        data_sql = text(f"""
            SELECT * FROM ({union_sql}) AS combined
            ORDER BY days_remaining ASC
            LIMIT :limit OFFSET :offset
        """)
        data_params = {**params, 'limit': size, 'offset': offset}
        rows = self.db.execute(data_sql, data_params).fetchall()

        items = []
        for row in rows:
            plan_start = row.plan_start_date
            if plan_start and isinstance(plan_start, datetime):
                plan_start = plan_start.date()
            plan_end = row.plan_end_date
            if plan_end and isinstance(plan_end, datetime):
                plan_end = plan_end.date()
            created_at = row.created_at
            if created_at and isinstance(created_at, datetime):
                created_at = created_at.isoformat()
            items.append({
                'id': str(row.id),
                'workOrderNo': row.order_no,
                'project_id': row.project_id,
                'projectName': row.project_name,
                'customerName': row.client_name,
                'workOrderType': row.work_order_type,
                'planStartDate': plan_start.isoformat() if plan_start else None,
                'planEndDate': plan_end.isoformat() if plan_end else None,
                'workOrderStatus': row.status,
                'daysRemaining': int(row.days_remaining) if row.days_remaining else 0,
                'executor': row.maintenance_personnel,
                'created_at': created_at
            })

        return items, total

    def get_expiring_count(self, maintenance_personnel: str | None = None) -> int:
        today = date.today()
        end_date = today + timedelta(days=7)
        today_datetime = datetime.combine(today, datetime.min.time())
        end_datetime = datetime.combine(end_date, datetime.max.time())
        valid_statuses = OverdueAlertConfig.VALID_STATUSES
        
        total_count = 0
        
        inspection_query = self.db.query(func.count(PeriodicInspection.id)).filter(
            and_(
                PeriodicInspection.plan_start_date >= today_datetime,
                PeriodicInspection.plan_start_date <= end_datetime,
                PeriodicInspection.status.in_(valid_statuses),
                PeriodicInspection.is_deleted == False
            )
        )
        if maintenance_personnel:
            inspection_query = inspection_query.filter(
                PeriodicInspection.maintenance_personnel == maintenance_personnel
            )
        total_count += inspection_query.scalar() or 0
        
        repair_query = self.db.query(func.count(TemporaryRepair.id)).filter(
            and_(
                TemporaryRepair.plan_start_date >= today_datetime,
                TemporaryRepair.plan_start_date <= end_datetime,
                TemporaryRepair.status.in_(valid_statuses),
                TemporaryRepair.is_deleted == False
            )
        )
        if maintenance_personnel:
            repair_query = repair_query.filter(
                TemporaryRepair.maintenance_personnel == maintenance_personnel
            )
        total_count += repair_query.scalar() or 0
        
        work_query = self.db.query(func.count(SpotWork.id)).filter(
            and_(
                SpotWork.plan_start_date >= today_datetime,
                SpotWork.plan_start_date <= end_datetime,
                SpotWork.status.in_(valid_statuses),
                SpotWork.is_deleted == False
            )
        )
        if maintenance_personnel:
            work_query = work_query.filter(
                SpotWork.maintenance_personnel == maintenance_personnel
            )
        total_count += work_query.scalar() or 0
        
        return total_count
