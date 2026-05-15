
import json
from pydantic import BaseModel, field_validator


def _parse_images(v):
    if isinstance(v, str):
        try:
            parsed = json.loads(v)
            if isinstance(parsed, list):
                return parsed
        except (json.JSONDecodeError, TypeError):
            pass
        return []
    return v


class WeeklyReportCreate(BaseModel):
    report_id: str | None = None
    project_id: str | None = None
    project_name: str | None = None
    week_start_date: str | None = None
    week_end_date: str | None = None
    report_date: str
    work_summary: str | None = None
    work_content: str | None = None
    next_week_plan: str | None = None
    issues: str | None = None
    suggestions: str | None = None
    images: list[str] | None = None
    manager_signature: str | None = None

    @field_validator('images', mode='before')
    @classmethod
    def validate_images(cls, v):
        return _parse_images(v)


class WeeklyReportUpdate(BaseModel):
    project_id: str | None = None
    project_name: str | None = None
    week_start_date: str | None = None
    week_end_date: str | None = None
    report_date: str | None = None
    work_summary: str | None = None
    work_content: str | None = None
    next_week_plan: str | None = None
    issues: str | None = None
    suggestions: str | None = None
    images: list[str] | None = None
    manager_signature: str | None = None
    status: str | None = None

    @field_validator('images', mode='before')
    @classmethod
    def validate_images(cls, v):
        return _parse_images(v)


class WeeklyReportApprove(BaseModel):
    approved: bool
    reject_reason: str | None = None


class WeeklyReportSign(BaseModel):
    manager_signature: str
