from datetime import datetime

from pydantic import BaseModel, Field


class SparePartsUsageCreate(BaseModel):
    product_name: str = Field(..., min_length=1, max_length=200, description="产品名称")
    brand: str | None = Field(None, max_length=100, description="品牌")
    model: str | None = Field(None, max_length=100, description="产品型号")
    quantity: int = Field(..., gt=0, description="领用数量")
    user_name: str = Field(..., min_length=1, max_length=100, description="运维人员")
    issue_time: str | datetime = Field(..., description="领用时间")
    unit: str = Field("件", max_length=20, description="单位")
    project_id: str | None = Field(None, max_length=50, description="项目编号")
    project_name: str | None = Field(None, max_length=200, description="项目名称")
    remark: str | None = Field(None, max_length=500, description="备注")
    stock_id: int | None = Field(None, description="库存记录ID")
    status: str = Field("待归还", max_length=20, description="状态")


class SparePartsUsageUpdate(BaseModel):
    product_name: str = Field(..., max_length=200, description="产品名称")
    brand: str | None = Field(None, max_length=100, description="品牌")
    model: str | None = Field(None, max_length=100, description="产品型号")
    quantity: int = Field(..., description="领用数量")
    user_name: str = Field(..., max_length=100, description="运维人员")
    issue_time: datetime = Field(..., description="领用时间")
    unit: str = Field("件", max_length=20, description="单位")
    project_id: str | None = Field(None, max_length=50, description="项目编号")
    project_name: str | None = Field(None, max_length=200, description="项目名称")
    stock_id: int | None = Field(None, description="库存记录ID")
    status: str = Field("待归还", max_length=20, description="状态")
