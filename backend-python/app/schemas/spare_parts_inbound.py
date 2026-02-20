from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from app.schemas.common import ApiResponse, PaginatedResponse


class SparePartsInboundBase(BaseModel):
    inbound_no: str = Field(..., max_length=50, description="入库单号")
    product_name: str = Field(..., max_length=200, description="产品名称")
    brand: Optional[str] = Field(None, max_length=100, description="品牌")
    model: Optional[str] = Field(None, max_length=100, description="产品型号")
    quantity: int = Field(..., description="入库数量")
    supplier: Optional[str] = Field(None, max_length=200, description="供应商")
    unit: str = Field("件", max_length=20, description="单位")
    user_name: str = Field(..., max_length=100, description="入库人")
    remarks: Optional[str] = Field(None, max_length=500, description="备注")


class SparePartsInboundCreate(BaseModel):
    inbound_no: str = Field(..., max_length=50, description="入库单号")
    product_name: str = Field(..., max_length=200, description="产品名称")
    brand: Optional[str] = Field(None, max_length=100, description="品牌")
    model: Optional[str] = Field(None, max_length=100, description="产品型号")
    quantity: int = Field(..., description="入库数量")
    supplier: Optional[str] = Field(None, max_length=200, description="供应商")
    unit: str = Field("件", max_length=20, description="单位")
    user_name: str = Field(..., max_length=100, description="入库人")
    remarks: Optional[str] = Field(None, max_length=500, description="备注")


class SparePartsInboundUpdate(BaseModel):
    inbound_no: str = Field(..., max_length=50, description="入库单号")
    product_name: str = Field(..., max_length=200, description="产品名称")
    brand: Optional[str] = Field(None, max_length=100, description="品牌")
    model: Optional[str] = Field(None, max_length=100, description="产品型号")
    quantity: int = Field(..., description="入库数量")
    supplier: Optional[str] = Field(None, max_length=200, description="供应商")
    unit: str = Field("件", max_length=20, description="单位")
    user_name: str = Field(..., max_length=100, description="入库人")
    remarks: Optional[str] = Field(None, max_length=500, description="备注")


class SparePartsInboundResponse(BaseModel):
    id: int
    inbound_no: str
    product_name: str
    brand: Optional[str]
    model: Optional[str]
    quantity: int
    supplier: Optional[str]
    unit: str
    user_name: str
    remarks: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True
