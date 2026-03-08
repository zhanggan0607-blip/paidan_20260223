
from pydantic import BaseModel, Field


class RepairToolsStockBase(BaseModel):
    tool_name: str = Field(..., description="工具名称")
    category: str | None = Field(None, description="工具分类")
    specification: str | None = Field(None, description="规格型号")
    unit: str = Field(default="个", description="单位")
    stock: int = Field(default=0, ge=0, description="库存数量")
    min_stock: int = Field(default=5, ge=0, description="最低库存预警")
    location: str | None = Field(None, description="存放位置")
    remark: str | None = Field(None, description="备注")


class RepairToolsStockCreate(RepairToolsStockBase):
    pass


class RepairToolsStockUpdate(BaseModel):
    tool_name: str | None = Field(None, description="工具名称")
    category: str | None = Field(None, description="工具分类")
    specification: str | None = Field(None, description="规格型号")
    unit: str | None = Field(None, description="单位")
    stock: int | None = Field(None, ge=0, description="库存数量")
    min_stock: int | None = Field(None, ge=0, description="最低库存预警")
    location: str | None = Field(None, description="存放位置")
    remark: str | None = Field(None, description="备注")


class RepairToolsRestock(BaseModel):
    quantity: int = Field(..., gt=0, description="入库数量")
    remark: str | None = Field(None, description="备注")


class RepairToolsInboundCreate(BaseModel):
    tool_name: str = Field(..., description="工具名称")
    tool_id: str | None = Field(None, description="工具编号")
    category: str | None = Field(None, description="工具分类")
    specification: str | None = Field(None, description="规格型号")
    quantity: int = Field(..., gt=0, description="入库数量")
    unit: str = Field(default="个", description="单位")
    supplier: str | None = Field(None, description="供应商")
    location: str | None = Field(None, description="存放位置")
    user_name: str = Field(..., description="入库人")
    remark: str | None = Field(None, description="备注")


class RepairToolsIssueBase(BaseModel):
    tool_id: str | None = Field(None, description="工具编号")
    tool_name: str | None = Field(None, description="工具名称")
    specification: str | None = Field(None, description="规格型号")
    quantity: int = Field(..., gt=0, description="领用数量")
    user_id: int | None = Field(None, description="运维人员ID")
    user_name: str | None = Field(None, description="运维人员姓名")
    project_id: str | None = Field(None, description="项目编号")
    project_name: str | None = Field(None, description="项目名称")
    remark: str | None = Field(None, description="备注")


class RepairToolsIssueCreate(RepairToolsIssueBase):
    pass


class RepairToolsReturn(BaseModel):
    return_quantity: int = Field(..., gt=0, description="归还数量")
    remark: str | None = Field(None, description="备注")


class RepairToolsStockResponse(RepairToolsStockBase):
    id: int
    tool_id: str | None = None
    last_stock_time: str | None = None

    class Config:
        from_attributes = True


class RepairToolsIssueResponse(BaseModel):
    id: int
    tool_id: str | None = None
    tool_name: str
    specification: str | None = None
    quantity: int
    return_quantity: int = 0
    issue_quantity: int
    user_id: int | None = None
    user_name: str
    issue_time: str
    return_time: str | None = None
    project_id: str | None = None
    project_name: str | None = None
    status: str
    remark: str | None = None

    class Config:
        from_attributes = True
