from pydantic import BaseModel, Field, field_validator
from typing import Optional, Union, List
from datetime import datetime
from app.schemas.common import ApiResponse, PaginatedResponse


class SparePartsStockBase(BaseModel):
    spare_part_id: str = Field(..., max_length=50, description="备品备件编号")
    spare_part_name: str = Field(..., max_length=200, description="备品备件名称")
    specifications: Optional[str] = Field(None, max_length=100, description="规格型号")
    unit: Optional[str] = Field(None, max_length=20, description="单位")
    quantity: int = Field(0, description="数量")
    min_stock: int = Field(0, description="最小库存")
    max_stock: int = Field(0, description="最大库存")
    remarks: Optional[str] = Field(None, max_length=500, description="备注")


class SparePartsStockCreate(BaseModel):
    spare_part_id: str = Field(..., max_length=50, description="备品备件编号")
    spare_part_name: str = Field(..., max_length=200, description="备品备件名称")
    specifications: Optional[str] = Field(None, max_length=100, description="规格型号")
    unit: Optional[str] = Field(None, max_length=20, description="单位")
    quantity: int = Field(0, description="数量")
    min_stock: int = Field(0, description="最小库存")
    max_stock: int = Field(0, description="最大库存")
    remarks: Optional[str] = Field(None, max_length=500, description="备注")


class SparePartsStockUpdate(BaseModel):
    spare_part_id: str = Field(..., max_length=50, description="备品备件编号")
    spare_part_name: str = Field(..., max_length=200, description="备品备件名称")
    specifications: Optional[str] = Field(None, max_length=100, description="规格型号")
    unit: Optional[str] = Field(None, max_length=20, description="单位")
    quantity: int = Field(0, description="数量")
    min_stock: int = Field(0, description="最小库存")
    max_stock: int = Field(0, description="最大库存")
    remarks: Optional[str] = Field(None, max_length=500, description="备注")


class SparePartsStockResponse(BaseModel):
    id: int
    spare_part_id: str
    spare_part_name: str
    specifications: Optional[str]
    unit: Optional[str]
    quantity: int
    min_stock: int
    max_stock: int
    remarks: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True