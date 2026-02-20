from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel


class WeeklyReportCreate(BaseModel):
    report_id: Optional[str] = None
    project_id: Optional[str] = None
    project_name: Optional[str] = None
    week_start_date: Optional[str] = None
    week_end_date: Optional[str] = None
    report_date: str
    work_summary: Optional[str] = None
    work_content: Optional[str] = None
    next_week_plan: Optional[str] = None
    issues: Optional[str] = None
    suggestions: Optional[str] = None
    images: Optional[List[str]] = None
    manager_signature: Optional[str] = None


class WeeklyReportUpdate(BaseModel):
    project_id: Optional[str] = None
    project_name: Optional[str] = None
    week_start_date: Optional[str] = None
    week_end_date: Optional[str] = None
    report_date: Optional[str] = None
    work_summary: Optional[str] = None
    work_content: Optional[str] = None
    next_week_plan: Optional[str] = None
    issues: Optional[str] = None
    suggestions: Optional[str] = None
    images: Optional[List[str]] = None
    manager_signature: Optional[str] = None
    status: Optional[str] = None


class WeeklyReportApprove(BaseModel):
    approved: bool
    reject_reason: Optional[str] = None


class WeeklyReportSign(BaseModel):
    manager_signature: str
