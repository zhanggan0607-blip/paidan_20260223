from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from app.schemas.common import ApiResponse, PaginatedResponse


class SparePartsUsageResponse(BaseModel):
    id: int
    usage_id: str
    spare_part_id: str
    spare_part_name: str
    project_id: str
    project_name: str
    usage_date: datetime
    usage_quantity: int
    usage_person: Optional[str]
    remarks: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True