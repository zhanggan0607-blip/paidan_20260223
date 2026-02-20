from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from app.schemas.common import ApiResponse, PaginatedResponse


class SparePartsUsageBase(BaseModel):
    product_name: str = Field(..., max_length=200, description="产品名称")
    brand: Optional[str] = Field(None, max_length=100, description="品牌")
    model: Optional[str] = Field(None, max_length=100, description="产品型号")
    quantity: int = Field(..., description="领用数量")
    user_name: str = Field(..., max_length=100, description="运维人员")
    issue_time: datetime = Field(..., description="领用时间")
    unit: str = Field("件", max_length=20, description="单位")
    project_id: Optional[str] = Field(None, max_length=50, description="项目编号")
    project_name: Optional[str] = Field(None, max_length=200, description="项目名称")
    stock_id: Optional[int] = Field(None, description="库存记录ID")
    status: str = Field("已使用", max_length=20, description="状态")


class SparePartsUsageCreate(BaseModel):
    product_name: str = Field(..., max_length=200, description="产品名称")
    brand: Optional[str] = Field(None, max_length=100, description="品牌")
    model: Optional[str] = Field(None, max_length=100, description="产品型号")
    quantity: int = Field(..., description="领用数量")
    user_name: str = Field(..., max_length=100, description="运维人员")
    issue_time: datetime = Field(..., description="领用时间")
    unit: str = Field("件", max_length=20, description="单位")
    project_id: Optional[str] = Field(None, max_length=50, description="项目编号")
    project_name: Optional[str] = Field(None, max_length=200, description="项目名称")
    stock_id: Optional[int] = Field(None, description="库存记录ID")
    status: str = Field("已使用", max_length=20, description="状态")


class SparePartsUsageUpdate(BaseModel):
    product_name: str = Field(..., max_length=200, description="产品名称")
    brand: Optional[str] = Field(None, max_length=100, description="品牌")
    model: Optional[str] = Field(None, max_length=100, description="产品型号")
    quantity: int = Field(..., description="领用数量")
    user_name: str = Field(..., max_length=100, description="运维人员")
    issue_time: datetime = Field(..., description="领用时间")
    unit: str = Field("件", max_length=20, description="单位")
    project_id: Optional[str] = Field(None, max_length=50, description="项目编号")
    project_name: Optional[str] = Field(None, max_length=200, description="项目名称")
    stock_id: Optional[int] = Field(None, description="库存记录ID")
    status: str = Field("已使用", max_length=20, description="状态")


class SparePartsUsageResponse(BaseModel):
    id: int
    product_name: str
    brand: Optional[str]
    model: Optional[str]
    quantity: int
    user_name: str
    issue_time: datetime
    unit: str
    project_id: Optional[str]
    project_name: Optional[str]
    stock_id: Optional[int]
    status: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
