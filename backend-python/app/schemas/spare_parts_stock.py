from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from app.schemas.common import ApiResponse, PaginatedResponse


class SparePartsStockBase(BaseModel):
    product_name: str = Field(..., max_length=200, description="产品名称")
    brand: Optional[str] = Field(None, max_length=100, description="品牌")
    model: Optional[str] = Field(None, max_length=100, description="产品型号")
    unit: str = Field("件", max_length=20, description="单位")
    quantity: int = Field(0, description="库存数量")
    status: str = Field("在库", max_length=20, description="状态：在库/已使用/缺货")


class SparePartsStockCreate(BaseModel):
    product_name: str = Field(..., max_length=200, description="产品名称")
    brand: Optional[str] = Field(None, max_length=100, description="品牌")
    model: Optional[str] = Field(None, max_length=100, description="产品型号")
    unit: str = Field("件", max_length=20, description="单位")
    quantity: int = Field(0, description="库存数量")
    status: str = Field("在库", max_length=20, description="状态：在库/已使用/缺货")


class SparePartsStockUpdate(BaseModel):
    product_name: str = Field(..., max_length=200, description="产品名称")
    brand: Optional[str] = Field(None, max_length=100, description="品牌")
    model: Optional[str] = Field(None, max_length=100, description="产品型号")
    unit: str = Field("件", max_length=20, description="单位")
    quantity: int = Field(0, description="库存数量")
    status: str = Field("在库", max_length=20, description="状态：在库/已使用/缺货")


class SparePartsStockResponse(BaseModel):
    id: int
    product_name: str
    brand: Optional[str]
    model: Optional[str]
    unit: str
    quantity: int
    status: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
