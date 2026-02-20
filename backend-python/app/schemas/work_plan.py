from pydantic import BaseModel, Field, field_validator
from typing import Optional, Union, List
from datetime import datetime
from app.schemas.common import ApiResponse, PaginatedResponse


PLAN_TYPES = ['定期巡检', '临时维修', '零星用工']


class WorkPlanBase(BaseModel):
    plan_id: str = Field(..., max_length=50, description="计划编号")
    plan_name: Optional[str] = Field(None, max_length=200, description="计划名称")
    plan_type: str = Field(..., max_length=20, description="工单类型：定期巡检/临时维修/零星用工")
    project_id: str = Field(..., max_length=50, description="项目编号")
    project_name: str = Field(..., max_length=200, description="项目名称")
    plan_start_date: Union[str, datetime] = Field(..., description="计划开始日期")
    plan_end_date: Union[str, datetime] = Field(..., description="计划结束日期")
    client_name: Optional[str] = Field(None, max_length=100, description="客户单位")
    maintenance_personnel: Optional[str] = Field(None, max_length=100, description="运维人员")
    status: str = Field("未进行", max_length=20, description="状态")
    filled_count: Optional[int] = Field(0, ge=0, description="已填写检查项数量")
    total_count: Optional[int] = Field(5, ge=0, description="检查项总数量")
    remarks: Optional[str] = Field(None, description="备注")

    @field_validator('plan_type')
    @classmethod
    def validate_plan_type(cls, v):
        if v not in PLAN_TYPES:
            raise ValueError(f'工单类型必须是以下之一: {", ".join(PLAN_TYPES)}')
        return v

    @field_validator('status')
    @classmethod
    def validate_status(cls, v):
        valid_statuses = ['未进行', '待确认', '已确认', '已完成', '已取消']
        if v not in valid_statuses:
            raise ValueError(f'状态必须是以下之一: {", ".join(valid_statuses)}')
        return v


class WorkPlanCreate(BaseModel):
    plan_id: str = Field(..., max_length=50, description="计划编号")
    plan_name: Optional[str] = Field(None, max_length=200, description="计划名称")
    plan_type: str = Field(..., max_length=20, description="工单类型：定期巡检/临时维修/零星用工")
    project_id: str = Field(..., max_length=50, description="项目编号")
    project_name: str = Field(..., max_length=200, description="项目名称")
    plan_start_date: Union[str, datetime] = Field(..., description="计划开始日期")
    plan_end_date: Union[str, datetime] = Field(..., description="计划结束日期")
    client_name: Optional[str] = Field(None, max_length=100, description="客户单位")
    maintenance_personnel: Optional[str] = Field(None, max_length=100, description="运维人员")
    status: str = Field("未进行", max_length=20, description="状态")
    filled_count: Optional[int] = Field(0, ge=0, description="已填写检查项数量")
    total_count: Optional[int] = Field(5, ge=0, description="检查项总数量")
    remarks: Optional[str] = Field(None, description="备注")


class WorkPlanUpdate(BaseModel):
    plan_id: str = Field(..., max_length=50, description="计划编号")
    plan_name: Optional[str] = Field(None, max_length=200, description="计划名称")
    plan_type: str = Field(..., max_length=20, description="工单类型：定期巡检/临时维修/零星用工")
    project_id: str = Field(..., max_length=50, description="项目编号")
    project_name: str = Field(..., max_length=200, description="项目名称")
    plan_start_date: Union[str, datetime] = Field(..., description="计划开始日期")
    plan_end_date: Union[str, datetime] = Field(..., description="计划结束日期")
    client_name: Optional[str] = Field(None, max_length=100, description="客户单位")
    maintenance_personnel: Optional[str] = Field(None, max_length=100, description="运维人员")
    status: str = Field(..., max_length=20, description="状态")
    filled_count: Optional[int] = Field(0, ge=0, description="已填写检查项数量")
    total_count: Optional[int] = Field(5, ge=0, description="检查项总数量")
    remarks: Optional[str] = Field(None, description="备注")


class WorkPlanResponse(BaseModel):
    id: int
    plan_id: str
    plan_name: Optional[str]
    plan_type: str
    project_id: str
    project_name: str
    plan_start_date: datetime
    plan_end_date: datetime
    client_name: Optional[str]
    maintenance_personnel: Optional[str]
    status: str
    filled_count: Optional[int]
    total_count: Optional[int]
    remarks: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
