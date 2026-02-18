from typing import Optional, List
from pydantic import BaseModel, Field, field_validator
from datetime import datetime


class PeriodicInspectionRecordBase(BaseModel):
    inspection_id: str = Field(..., max_length=50, description="巡检单编号")
    item_id: str = Field(..., max_length=50, description="巡检项ID")
    item_name: Optional[str] = Field(None, max_length=200, description="巡检项名称")
    inspection_item: Optional[str] = Field(None, max_length=200, description="巡查项")
    inspection_content: Optional[str] = Field(None, description="巡查内容")
    check_content: Optional[str] = Field(None, description="检查要求")
    brief_description: Optional[str] = Field(None, description="简要说明")
    equipment_name: Optional[str] = Field(None, max_length=200, description="设备名称")
    equipment_location: Optional[str] = Field(None, max_length=200, description="设备位置")
    inspected: bool = Field(False, description="是否已处理")
    photos: Optional[List[str]] = Field(default=[], description="照片URL列表")
    inspection_result: Optional[str] = Field(None, description="巡检结果")


class PeriodicInspectionRecordCreate(PeriodicInspectionRecordBase):
    pass


class PeriodicInspectionRecordUpdate(BaseModel):
    inspected: Optional[bool] = Field(None, description="是否已处理")
    photos: Optional[List[str]] = Field(None, description="照片URL列表")
    inspection_result: Optional[str] = Field(None, description="巡检结果")


class PeriodicInspectionRecordResponse(PeriodicInspectionRecordBase):
    id: int
    photos_uploaded: bool = False
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class BatchRecordSave(BaseModel):
    inspection_id: str = Field(..., description="巡检单编号")
    records: List[PeriodicInspectionRecordCreate] = Field(..., description="巡检记录列表")
