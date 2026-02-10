from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional

class InspectionItemBase(BaseModel):
    item_code: str = Field(..., max_length=50, description='事项编码')
    item_name: str = Field(..., max_length=200, description='事项名称')
    item_type: str = Field(..., max_length=50, description='事项类型')
    check_content: Optional[str] = Field(None, description='检查内容')
    check_standard: Optional[str] = Field(None, description='检查标准')

class InspectionItemCreate(InspectionItemBase):
    pass

class InspectionItemUpdate(BaseModel):
    item_code: Optional[str] = Field(None, max_length=50, description='事项编码')
    item_name: Optional[str] = Field(None, max_length=200, description='事项名称')
    item_type: Optional[str] = Field(None, max_length=50, description='事项类型')
    check_content: Optional[str] = Field(None, description='检查内容')
    check_standard: Optional[str] = Field(None, description='检查标准')

class InspectionItem(InspectionItemBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
