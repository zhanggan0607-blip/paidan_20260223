import logging
from datetime import datetime

from sqlalchemy import text
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)


class WorkOrderService:
    def __init__(self, db: Session):
        self._db = db

    @property
    def db(self) -> Session:
        return self._db

    @staticmethod
    def build_filter_conditions(
        project_name: str | None,
        order_id: str | None,
        status: str | None,
        maintenance_personnel: str | None,
        user_name: str | None,
        is_manager: bool,
    ) -> tuple[str, dict]:
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

    @staticmethod
    def _build_order_subquery(table: str, id_col: str, order_type: str, order_type_code: str, filter_sql: str) -> str:
        return f"""
            SELECT 
                id,
                {id_col} as order_id,
                '{order_type}' as order_type,
                '{order_type_code}' as order_type_code,
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
            FROM {table} 
            WHERE {filter_sql}
        """

    @staticmethod
    def _build_completed_subquery(table: str, id_col: str, order_type: str, order_type_code: str, plan_type: str, filter_sql: str) -> str:
        has_actual = table != "spot_work"
        actual_col = "actual_completion_date" if has_actual else "NULL as actual_completion_date"
        return f"""
            SELECT 
                id,
                {id_col} as order_id,
                '{order_type}' as order_type,
                '{order_type_code}' as order_type_code,
                '{plan_type}' as plan_type,
                project_id,
                project_name,
                client_name,
                plan_start_date,
                plan_end_date,
                {actual_col},
                maintenance_personnel,
                status,
                remarks,
                created_at,
                updated_at
            FROM {table} 
            WHERE {filter_sql} AND is_deleted = false
        """

    @staticmethod
    def _format_row(row, include_actual: bool = False) -> dict:
        result = {
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
        }
        if include_actual:
            result['plan_type'] = getattr(row, 'plan_type', None)
            result['actual_completion_date'] = (
                row.actual_completion_date.isoformat() if row.actual_completion_date else None
            )
        else:
            result['execution_result'] = row.execution_result
            result['signature'] = row.signature
        result['created_at'] = row.created_at.isoformat() if row.created_at else None
        result['updated_at'] = row.updated_at.isoformat() if row.updated_at else None
        return result

    def get_work_order_list(
        self,
        project_name: str | None,
        order_id: str | None,
        order_type: str | None,
        status: str | None,
        maintenance_personnel: str | None,
        user_name: str,
        is_manager: bool,
        page: int,
        size: int,
    ) -> tuple[list[dict], int]:
        base_filter, base_params = self.build_filter_conditions(
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
            data_subqueries.append(
                self._build_order_subquery("periodic_inspection", "inspection_id", "定期巡检单", "inspection", inspection_filter)
            )

        if not order_type or order_type == 'repair':
            count_subqueries.append(f"SELECT id FROM temporary_repair WHERE {repair_filter}")
            data_subqueries.append(
                self._build_order_subquery("temporary_repair", "repair_id", "临时维修单", "repair", repair_filter)
            )

        if not order_type or order_type == 'spotwork':
            count_subqueries.append(f"SELECT id FROM spot_work WHERE {spotwork_filter}")
            data_subqueries.append(
                self._build_order_subquery("spot_work", "work_id", "零星用工单", "spotwork", spotwork_filter)
            )

        count_sql = text(f"SELECT COUNT(*) as total FROM ({' UNION ALL '.join(count_subqueries)}) AS combined")
        total = self.db.execute(count_sql, base_params).scalar() or 0

        offset = page * size
        data_sql = text(f"""
            SELECT * FROM (
                {' UNION ALL '.join(data_subqueries)}
            ) AS combined
            ORDER BY created_at DESC NULLS LAST, updated_at DESC
            LIMIT :limit OFFSET :offset
        """)

        data_params = {**base_params, 'limit': size, 'offset': offset}
        results = self.db.execute(data_sql, data_params).fetchall()

        return [self._format_row(row) for row in results], total

    def get_all_work_orders(
        self,
        user_name: str,
        is_manager: bool,
    ) -> list[dict]:
        base_filter, base_params = self.build_filter_conditions(
            None, None, None, None, user_name, is_manager
        )

        data_sql = text(f"""
            SELECT * FROM (
                {self._build_order_subquery("periodic_inspection", "inspection_id", "定期巡检单", "inspection", base_filter)}
                UNION ALL
                {self._build_order_subquery("temporary_repair", "repair_id", "临时维修单", "repair", base_filter)}
                UNION ALL
                {self._build_order_subquery("spot_work", "work_id", "零星用工单", "spotwork", base_filter)}
            ) AS combined
            ORDER BY created_at DESC NULLS LAST, updated_at DESC
        """)

        results = self.db.execute(data_sql, base_params).fetchall()
        return [self._format_row(row) for row in results]

    def get_completed_this_year(
        self,
        user_name: str,
        is_manager: bool,
        page: int,
        size: int,
    ) -> tuple[list[dict], int]:
        current_year = datetime.now().year

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

        total = self.db.execute(count_sql, params).scalar() or 0

        offset = page * size
        data_sql = text(f"""
            SELECT * FROM (
                {self._build_completed_subquery("periodic_inspection", "inspection_id", "定期巡检单", "inspection", "定期巡检", base_filter)}
                UNION ALL
                {self._build_completed_subquery("temporary_repair", "repair_id", "临时维修单", "repair", "临时维修", base_filter)}
                UNION ALL
                {self._build_completed_subquery("spot_work", "work_id", "零星用工单", "spotwork", "零星用工", base_filter)}
            ) AS combined
            ORDER BY actual_completion_date DESC NULLS LAST, updated_at DESC
            LIMIT :limit OFFSET :offset
        """)

        data_params = {**params, 'limit': size, 'offset': offset}
        results = self.db.execute(data_sql, data_params).fetchall()

        return [self._format_row(row, include_actual=True) for row in results], total
