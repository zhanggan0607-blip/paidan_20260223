import json
from typing import List, Optional, Union
from fastapi import HTTPException, status
from datetime import datetime
from sqlalchemy.orm import Session
from app.models.weekly_report import WeeklyReport
from app.repositories.weekly_report import WeeklyReportRepository
from app.schemas.weekly_report import WeeklyReportCreate, WeeklyReportUpdate
from app.utils.date_utils import parse_datetime


class WeeklyReportService:
    def __init__(self, db: Session):
        self.repository = WeeklyReportRepository(db)

    def _parse_date(self, date_value: Union[str, datetime, None]) -> Optional[datetime]:
        return parse_datetime(date_value)

    def _generate_report_id(self, project_id: str) -> str:
        today = datetime.now().strftime("%Y%m%d")
        base_id = f"ZB-{project_id}-{today}"
        count = self.repository.db.query(WeeklyReport).filter(
            WeeklyReport.report_id.like(f"{base_id}%")
        ).count()
        sequence = str(count + 1).zfill(2)
        return f"{base_id}-{sequence}"

    def get_all(
        self,
        page: int = 0,
        size: int = 10,
        report_id: Optional[str] = None,
        report_date: Optional[str] = None,
        work_summary: Optional[str] = None,
        created_by: Optional[str] = None
    ) -> tuple[List[WeeklyReport], int]:
        return self.repository.find_all(
            page, size, report_id, report_date, work_summary, created_by
        )

    def get_by_id(self, id: int) -> WeeklyReport:
        report = self.repository.find_by_id(id)
        if not report:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="维保周报不存在"
            )
        return report

    def get_by_report_id(self, report_id: str) -> WeeklyReport:
        report = self.repository.find_by_report_id(report_id)
        if not report:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="维保周报不存在"
            )
        return report

    def create(self, dto: WeeklyReportCreateDTO, created_by: Optional[str] = None) -> WeeklyReport:
        if dto.report_id:
            report_id = dto.report_id
        else:
            report_id = self._generate_report_id(dto.project_id or "")

        images_json = json.dumps(dto.images, ensure_ascii=False) if dto.images else None

        report = WeeklyReport(
            report_id=report_id,
            project_id=dto.project_id,
            project_name=dto.project_name,
            week_start_date=self._parse_date(dto.week_start_date),
            week_end_date=self._parse_date(dto.week_end_date),
            report_date=self._parse_date(dto.report_date),
            work_summary=dto.work_summary,
            work_content=dto.work_content,
            next_week_plan=dto.next_week_plan,
            issues=dto.issues,
            suggestions=dto.suggestions,
            images=images_json,
            manager_signature=dto.manager_signature,
            status="submitted",
            created_by=created_by
        )

        return self.repository.create(report)

    def update(self, id: int, dto: WeeklyReportUpdateDTO) -> WeeklyReport:
        existing_report = self.get_by_id(id)

        if dto.project_id is not None:
            existing_report.project_id = dto.project_id
        if dto.project_name is not None:
            existing_report.project_name = dto.project_name
        if dto.week_start_date is not None:
            existing_report.week_start_date = self._parse_date(dto.week_start_date)
        if dto.week_end_date is not None:
            existing_report.week_end_date = self._parse_date(dto.week_end_date)
        if dto.report_date is not None:
            existing_report.report_date = self._parse_date(dto.report_date)
        if dto.work_summary is not None:
            existing_report.work_summary = dto.work_summary
        if dto.work_content is not None:
            existing_report.work_content = dto.work_content
        if dto.next_week_plan is not None:
            existing_report.next_week_plan = dto.next_week_plan
        if dto.issues is not None:
            existing_report.issues = dto.issues
        if dto.suggestions is not None:
            existing_report.suggestions = dto.suggestions
        if dto.images is not None:
            existing_report.images = json.dumps(dto.images, ensure_ascii=False)
        if dto.manager_signature is not None:
            existing_report.manager_signature = dto.manager_signature
            existing_report.manager_sign_time = datetime.now()
        if dto.status is not None:
            existing_report.status = dto.status

        return self.repository.update(existing_report)

    def submit(self, id: int) -> WeeklyReport:
        report = self.get_by_id(id)
        if report.status != "draft":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="只有草稿状态的周报才能提交"
            )
        report.status = "submitted"
        return self.repository.update(report)

    def approve(self, id: int, approved_by: str) -> WeeklyReport:
        report = self.get_by_id(id)
        if report.status != "submitted":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="只有已提交状态的周报才能审核"
            )
        report.status = "approved"
        report.approved_by = approved_by
        report.approved_at = datetime.now()
        return self.repository.update(report)

    def reject(self, id: int, reject_reason: str) -> WeeklyReport:
        report = self.get_by_id(id)
        if report.status != "submitted":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="只有已提交状态的周报才能退回"
            )
        report.status = "rejected"
        report.reject_reason = reject_reason
        return self.repository.update(report)

    def sign(self, id: int, signature: str) -> WeeklyReport:
        report = self.get_by_id(id)
        report.manager_signature = signature
        report.manager_sign_time = datetime.now()
        return self.repository.update(report)

    def delete(self, id: int) -> None:
        report = self.get_by_id(id)
        self.repository.delete(report)

    def get_all_unpaginated(self) -> List[WeeklyReport]:
        return self.repository.find_all_unpaginated()
