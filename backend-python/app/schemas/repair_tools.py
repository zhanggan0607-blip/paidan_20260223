from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class RepairToolsStockBase(BaseModel):
    tool_name: str = Field(..., description="工具名称")
    category: Optional[str] = Field(None, description="工具分类")
    specification: Optional[str] = Field(None, description="规格型号")
    unit: str = Field(default="个", description="单位")
    stock: int = Field(default=0, ge=0, description="库存数量")
    min_stock: int = Field(default=5, ge=0, description="最低库存预警")
    location: Optional[str] = Field(None, description="存放位置")
    remark: Optional[str] = Field(None, description="备注")


class RepairToolsStockCreate(RepairToolsStockBase):
    pass


class RepairToolsStockUpdate(BaseModel):
    tool_name: Optional[str] = Field(None, description="工具名称")
    category: Optional[str] = Field(None, description="工具分类")
    specification: Optional[str] = Field(None, description="规格型号")
    unit: Optional[str] = Field(None, description="单位")
    stock: Optional[int] = Field(None, ge=0, description="库存数量")
    min_stock: Optional[int] = Field(None, ge=0, description="最低库存预警")
    location: Optional[str] = Field(None, description="存放位置")
    remark: Optional[str] = Field(None, description="备注")


class RepairToolsRestock(BaseModel):
    quantity: int = Field(..., gt=0, description="入库数量")
    remark: Optional[str] = Field(None, description="备注")


class RepairToolsInboundCreate(BaseModel):
    tool_name: str = Field(..., description="工具名称")
    tool_id: Optional[str] = Field(None, description="工具编号")
    category: Optional[str] = Field(None, description="工具分类")
    specification: Optional[str] = Field(None, description="规格型号")
    quantity: int = Field(..., gt=0, description="入库数量")
    unit: str = Field(default="个", description="单位")
    supplier: Optional[str] = Field(None, description="供应商")
    location: Optional[str] = Field(None, description="存放位置")
    user_name: str = Field(..., description="入库人")
    remark: Optional[str] = Field(None, description="备注")


class RepairToolsIssueBase(BaseModel):
    tool_id: Optional[str] = Field(None, description="工具编号")
    tool_name: Optional[str] = Field(None, description="工具名称")
    specification: Optional[str] = Field(None, description="规格型号")
    quantity: int = Field(..., gt=0, description="领用数量")
    user_id: Optional[int] = Field(None, description="运维人员ID")
    user_name: Optional[str] = Field(None, description="运维人员姓名")
    project_id: Optional[str] = Field(None, description="项目编号")
    project_name: Optional[str] = Field(None, description="项目名称")
    remark: Optional[str] = Field(None, description="备注")


class RepairToolsIssueCreate(RepairToolsIssueBase):
    pass


class RepairToolsReturn(BaseModel):
    return_quantity: int = Field(..., gt=0, description="归还数量")
    remark: Optional[str] = Field(None, description="备注")


class RepairToolsStockResponse(RepairToolsStockBase):
    id: int
    tool_id: Optional[str] = None
    last_stock_time: Optional[str] = None
    
    class Config:
        from_attributes = True


class RepairToolsIssueResponse(BaseModel):
    id: int
    tool_id: Optional[str] = None
    tool_name: str
    specification: Optional[str] = None
    quantity: int
    return_quantity: int = 0
    issue_quantity: int
    user_id: Optional[int] = None
    user_name: str
    issue_time: str
    return_time: Optional[str] = None
    project_id: Optional[str] = None
    project_name: Optional[str] = None
    status: str
    remark: Optional[str] = None
    
    class Config:
        from_attributes = True
