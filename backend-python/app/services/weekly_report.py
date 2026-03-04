"""
维保周报服务
提供维保周报业务逻辑处理
"""
import json
import logging
from typing import List, Optional, Union
from datetime import datetime
from sqlalchemy.orm import Session

from app.models.weekly_report import WeeklyReport
from app.repositories.weekly_report import WeeklyReportRepository
from app.schemas.weekly_report import WeeklyReportCreate, WeeklyReportUpdate
from app.utils.date_utils import parse_datetime
from app.exceptions import NotFoundException, ValidationException

logger = logging.getLogger(__name__)


class WeeklyReportService:
    """
    维保周报服务
    提供维保周报的增删改查等业务逻辑
    """
    
    def __init__(self, db: Session):
        self.repository = WeeklyReportRepository(db)
        self._db = db

    def _parse_date(self, date_value: Union[str, datetime, None]) -> Optional[datetime]:
        """解析日期"""
        return parse_datetime(date_value)

    def _generate_report_id(self, project_id: str) -> str:
        """生成周报编号"""
        today = datetime.now().strftime("%Y%m%d")
        base_id = f"ZB-{project_id}-{today}"
        count = self._db.query(WeeklyReport).filter(
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
        """
        分页获取维保周报列表
        
        Args:
            page: 页码
            size: 每页数量
            report_id: 周报编号
            report_date: 填报日期
            work_summary: 周报内容
            created_by: 创建人
            
        Returns:
            (周报列表, 总数)
        """
        return self.repository.find_all(
            page, size, report_id, report_date, work_summary, created_by
        )

    def get_by_id(self, id: int) -> WeeklyReport:
        """
        根据ID获取维保周报
        
        Args:
            id: 周报ID
            
        Returns:
            周报对象
            
        Raises:
            NotFoundException: 周报不存在
        """
        report = self.repository.find_by_id(id)
        if not report:
            raise NotFoundException("维保周报不存在")
        return report

    def get_by_report_id(self, report_id: str) -> WeeklyReport:
        """
        根据周报编号获取维保周报
        
        Args:
            report_id: 周报编号
            
        Returns:
            周报对象
            
        Raises:
            NotFoundException: 周报不存在
        """
        report = self.repository.find_by_report_id(report_id)
        if not report:
            raise NotFoundException("维保周报不存在")
        return report

    def create(self, dto: WeeklyReportCreate, created_by: Optional[str] = None) -> WeeklyReport:
        """
        创建维保周报
        
        Args:
            dto: 创建数据传输对象
            created_by: 创建人
            
        Returns:
            创建的周报对象
        """
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

    def update(
        self, 
        id: int, 
        dto: WeeklyReportUpdate, 
        operator_id: Optional[int] = None, 
        operator_name: Optional[str] = None
    ) -> WeeklyReport:
        """
        更新维保周报
        
        Args:
            id: 周报ID
            dto: 更新数据传输对象
            operator_id: 操作者ID
            operator_name: 操作者名称
            
        Returns:
            更新后的周报对象
        """
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

    def submit(self, id: int, operator_id: Optional[int] = None, operator_name: Optional[str] = None) -> WeeklyReport:
        """
        提交维保周报
        
        Args:
            id: 周报ID
            operator_id: 操作者ID
            operator_name: 操作者名称
            
        Returns:
            更新后的周报对象
            
        Raises:
            ValidationException: 状态不允许提交
        """
        report = self.get_by_id(id)
        if report.status != "draft":
            raise ValidationException("只有草稿状态的周报才能提交")
        report.status = "submitted"
        return self.repository.update(report)

    def approve(
        self, 
        id: int, 
        approved_by: str, 
        operator_id: Optional[int] = None, 
        operator_name: Optional[str] = None
    ) -> WeeklyReport:
        """
        审批通过维保周报
        
        Args:
            id: 周报ID
            approved_by: 审批人
            operator_id: 操作者ID
            operator_name: 操作者名称
            
        Returns:
            更新后的周报对象
            
        Raises:
            ValidationException: 状态不允许审批
        """
        report = self.get_by_id(id)
        if report.status != "submitted":
            raise ValidationException("只有已提交状态的周报才能审核")
        report.status = "approved"
        report.approved_by = approved_by
        report.approved_at = datetime.now()
        return self.repository.update(report)

    def reject(
        self, 
        id: int, 
        reject_reason: str, 
        operator_id: Optional[int] = None, 
        operator_name: Optional[str] = None
    ) -> WeeklyReport:
        """
        退回维保周报
        
        Args:
            id: 周报ID
            reject_reason: 退回原因
            operator_id: 操作者ID
            operator_name: 操作者名称
            
        Returns:
            更新后的周报对象
            
        Raises:
            ValidationException: 状态不允许退回
        """
        report = self.get_by_id(id)
        if report.status != "submitted":
            raise ValidationException("只有已提交状态的周报才能退回")
        report.status = "rejected"
        report.reject_reason = reject_reason
        return self.repository.update(report)

    def sign(
        self, 
        id: int, 
        signature: str, 
        operator_id: Optional[int] = None, 
        operator_name: Optional[str] = None
    ) -> WeeklyReport:
        """
        部门经理签字
        
        Args:
            id: 周报ID
            signature: 签名图片
            operator_id: 操作者ID
            operator_name: 操作者名称
            
        Returns:
            更新后的周报对象
        """
        report = self.get_by_id(id)
        report.manager_signature = signature
        report.manager_sign_time = datetime.now()
        return self.repository.update(report)

    def delete(self, id: int, operator_id: Optional[int] = None, operator_name: Optional[str] = None) -> None:
        """
        软删除维保周报
        
        Args:
            id: 周报ID
            operator_id: 操作者ID
            operator_name: 操作者名称
        """
        report = self.get_by_id(id)
        self.repository.soft_delete(report, operator_id)

    def get_all_unpaginated(self) -> List[WeeklyReport]:
        """
        获取所有维保周报（不分页）
        
        Returns:
            周报列表
        """
        return self.repository.find_all_unpaginated()
