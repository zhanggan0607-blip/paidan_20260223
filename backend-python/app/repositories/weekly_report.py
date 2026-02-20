from typing import List, Optional
from sqlalchemy.orm import Session, joinedload
from app.models.weekly_report import WeeklyReport
import logging

logger = logging.getLogger(__name__)


class WeeklyReportRepository:
    def __init__(self, db: Session):
        self._db = db

    @property
    def db(self):
        return self._db

    def find_all(
        self,
        page: int = 0,
        size: int = 10,
        report_id: Optional[str] = None,
        report_date: Optional[str] = None,
        work_summary: Optional[str] = None,
        created_by: Optional[str] = None
    ) -> tuple[List[WeeklyReport], int]:
        try:
            query = self.db.query(WeeklyReport).options(joinedload(WeeklyReport.project)).filter(WeeklyReport.is_deleted == 0)

            if report_id:
                query = query.filter(WeeklyReport.report_id.ilike(f'%{report_id}%'))

            if report_date:
                query = query.filter(WeeklyReport.report_date == report_date)

            if work_summary:
                query = query.filter(WeeklyReport.work_summary.ilike(f'%{work_summary}%'))

            if created_by:
                query = query.filter(WeeklyReport.created_by == created_by)

            total = query.count()
            items = query.order_by(WeeklyReport.created_at.desc()).offset(page * size).limit(size).all()

            return items, total
        except Exception as e:
            logger.error(f"查询维保周报列表失败: {str(e)}")
            raise

    def find_by_id(self, id: int) -> Optional[WeeklyReport]:
        try:
            return self.db.query(WeeklyReport).options(joinedload(WeeklyReport.project)).filter(WeeklyReport.id == id, WeeklyReport.is_deleted == 0).first()
        except Exception as e:
            logger.error(f"查询维保周报失败 (id={id}): {str(e)}")
            raise

    def find_by_report_id(self, report_id: str) -> Optional[WeeklyReport]:
        try:
            return self.db.query(WeeklyReport).options(joinedload(WeeklyReport.project)).filter(WeeklyReport.report_id == report_id, WeeklyReport.is_deleted == 0).first()
        except Exception as e:
            logger.error(f"查询维保周报失败 (report_id={report_id}): {str(e)}")
            raise

    def exists_by_report_id(self, report_id: str) -> bool:
        try:
            return self.db.query(WeeklyReport).filter(WeeklyReport.report_id == report_id, WeeklyReport.is_deleted == 0).first() is not None
        except Exception as e:
            logger.error(f"检查维保周报是否存在失败 (report_id={report_id}): {str(e)}")
            raise

    def find_by_project_and_week(self, project_id: str, week_start_date, week_end_date) -> Optional[WeeklyReport]:
        try:
            return self.db.query(WeeklyReport).options(joinedload(WeeklyReport.project)).filter(
                WeeklyReport.project_id == project_id,
                WeeklyReport.week_start_date == week_start_date,
                WeeklyReport.week_end_date == week_end_date,
                WeeklyReport.is_deleted == 0
            ).first()
        except Exception as e:
            logger.error(f"查询维保周报失败 (project_id={project_id}): {str(e)}")
            raise

    def create(self, report: WeeklyReport) -> WeeklyReport:
        try:
            self.db.add(report)
            self.db.commit()
            self.db.refresh(report)
            return report
        except Exception as e:
            self.db.rollback()
            logger.error(f"创建维保周报失败: {str(e)}")
            raise

    def update(self, report: WeeklyReport) -> WeeklyReport:
        try:
            self.db.commit()
            self.db.refresh(report)
            return report
        except Exception as e:
            self.db.rollback()
            logger.error(f"更新维保周报失败: {str(e)}")
            raise

    def delete(self, report: WeeklyReport) -> None:
        try:
            report.is_deleted = 1
            self.db.commit()
        except Exception as e:
            self.db.rollback()
            logger.error(f"删除维保周报失败: {str(e)}")
            raise

    def find_all_unpaginated(self) -> List[WeeklyReport]:
        try:
            return self.db.query(WeeklyReport).options(joinedload(WeeklyReport.project)).filter(WeeklyReport.is_deleted == 0).all()
        except Exception as e:
            logger.error(f"查询所有维保周报失败: {str(e)}")
            raise
