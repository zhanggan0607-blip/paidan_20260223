from pydantic import BaseModel, Field
from datetime import datetime


class SparePartsInboundCreate(BaseModel):
    product_name: str = Field(..., min_length=1, max_length=200, description="产品名称")
    quantity: int = Field(..., gt=0, description="入库数量")
    brand: str | None = Field(None, max_length=100, description="品牌")
    model: str | None = Field(None, max_length=100, description="产品型号")
    supplier: str | None = Field(None, max_length=200, description="供应商")
    unit: str = Field("件", max_length=20, description="单位")
    user_name: str | None = Field(None, max_length=100, description="入库人")
    remarks: str | None = Field(None, max_length=500, description="备注")


class SparePartsInboundUpdate(BaseModel):
    product_name: str | None = Field(None, min_length=1, max_length=200, description="产品名称")
    quantity: int | None = Field(None, gt=0, description="入库数量")
    brand: str | None = Field(None, max_length=100, description="品牌")
    model: str | None = Field(None, max_length=100, description="产品型号")
    supplier: str | None = Field(None, max_length=200, description="供应商")
    unit: str | None = Field(None, max_length=20, description="单位")
    user_name: str | None = Field(None, max_length=100, description="入库人")
    remarks: str | None = Field(None, max_length=500, description="备注")


class SparePartsReturn(BaseModel):
    return_quantity: int = Field(..., gt=0, description="归还数量")
    remark: str | None = Field(None, max_length=500, description="备注")


class SparePartsStockCreate(BaseModel):
    product_name: str = Field(..., min_length=1, max_length=200, description="产品名称")
    brand: str | None = Field(None, max_length=100, description="品牌")
    model: str | None = Field(None, max_length=100, description="产品型号")
    quantity: int = Field(..., ge=0, description="库存数量")
    unit: str = Field("件", max_length=20, description="单位")
    remark: str | None = Field(None, max_length=500, description="备注")
