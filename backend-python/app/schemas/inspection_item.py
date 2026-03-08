from datetime import datetime

from pydantic import BaseModel, Field


class InspectionItemBase(BaseModel):
    item_code: str = Field(..., max_length=50, description='事项编码')
    item_name: str = Field(..., max_length=200, description='事项名称')
    item_type: str = Field(..., max_length=50, description='事项类型')
    level: int = Field(1, ge=1, le=3, description='层级: 1-项目类型, 2-系统类型, 3-检查项')
    parent_id: int | None = Field(None, description='父节点ID')
    check_content: str | None = Field(None, description='检查内容')
    check_standard: str | None = Field(None, description='检查标准')
    sort_order: int = Field(0, description='排序')

class InspectionItemCreate(InspectionItemBase):
    pass

class InspectionItemUpdate(BaseModel):
    item_code: str | None = Field(None, max_length=50, description='事项编码')
    item_name: str | None = Field(None, max_length=200, description='事项名称')
    item_type: str | None = Field(None, max_length=50, description='事项类型')
    level: int | None = Field(None, ge=1, le=3, description='层级')
    parent_id: int | None = Field(None, description='父节点ID')
    check_content: str | None = Field(None, description='检查内容')
    check_standard: str | None = Field(None, description='检查标准')
    sort_order: int | None = Field(None, description='排序')

class InspectionItem(InspectionItemBase):
    id: int
    created_at: datetime
    updated_at: datetime
    children: list['InspectionItem'] = []

    class Config:
        from_attributes = True

InspectionItem.model_rebuild()
