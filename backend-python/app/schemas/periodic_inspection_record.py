from datetime import datetime

from pydantic import BaseModel, Field


class PeriodicInspectionRecordBase(BaseModel):
    inspection_id: str = Field(..., max_length=50, description="巡检单编号")
    item_id: str = Field(..., max_length=50, description="巡检项ID")
    item_name: str | None = Field(None, max_length=200, description="巡检项名称")
    inspection_item: str | None = Field(None, max_length=200, description="巡查项")
    inspection_content: str | None = Field(None, description="巡查内容")
    check_content: str | None = Field(None, description="检查要求")
    brief_description: str | None = Field(None, description="简要说明")
    equipment_name: str | None = Field(None, max_length=200, description="设备名称")
    equipment_location: str | None = Field(None, max_length=200, description="设备位置")
    inspected: bool = Field(False, description="是否已处理")
    photos: list[str] | None = Field(default=[], description="照片URL列表")
    inspection_result: str | None = Field(None, description="巡检结果")


class PeriodicInspectionRecordCreate(PeriodicInspectionRecordBase):
    pass


class PeriodicInspectionRecordUpdate(BaseModel):
    inspected: bool | None = Field(None, description="是否已处理")
    photos: list[str] | None = Field(None, description="照片URL列表")
    inspection_result: str | None = Field(None, description="巡检结果")


class PeriodicInspectionRecordResponse(PeriodicInspectionRecordBase):
    id: int
    photos_uploaded: bool = False
    created_at: datetime | None = None
    updated_at: datetime | None = None

    class Config:
        from_attributes = True


class BatchRecordSave(BaseModel):
    inspection_id: str = Field(..., description="巡检单编号")
    records: list[PeriodicInspectionRecordCreate] = Field(..., description="巡检记录列表")
