from datetime import datetime

from pydantic import BaseModel, Field, field_validator

PLAN_TYPES = ['定期巡检', '临时维修', '零星用工']


class WorkPlanBase(BaseModel):
    plan_id: str = Field(..., max_length=50, description="计划编号")
    plan_name: str | None = Field(None, max_length=200, description="计划名称")
    plan_type: str = Field(..., max_length=20, description="工单类型：定期巡检/临时维修/零星用工")
    project_id: str = Field(..., max_length=50, description="项目编号")
    project_name: str = Field(..., max_length=200, description="项目名称")
    plan_start_date: str | datetime = Field(..., description="计划开始日期")
    plan_end_date: str | datetime = Field(..., description="计划结束日期")
    client_name: str | None = Field(None, max_length=100, description="客户单位")
    maintenance_personnel: str | None = Field(None, max_length=100, description="运维人员")
    status: str = Field("执行中", max_length=20, description="状态")
    filled_count: int | None = Field(0, ge=0, description="已填写检查项数量")
    total_count: int | None = Field(5, ge=0, description="检查项总数量")
    remarks: str | None = Field(None, description="备注")

    @field_validator('plan_type')
    @classmethod
    def validate_plan_type(cls, v):
        if v not in PLAN_TYPES:
            raise ValueError(f'工单类型必须是以下之一: {", ".join(PLAN_TYPES)}')
        return v

    @field_validator('status')
    @classmethod
    def validate_status(cls, v):
        valid_statuses = ['执行中', '待确认', '已完成', '已退回']
        if v not in valid_statuses:
            raise ValueError(f'状态必须是以下之一: {", ".join(valid_statuses)}')
        return v


class WorkPlanCreate(BaseModel):
    plan_id: str = Field(..., max_length=50, description="计划编号")
    plan_name: str | None = Field(None, max_length=200, description="计划名称")
    plan_type: str = Field(..., max_length=20, description="工单类型：定期巡检/临时维修/零星用工")
    project_id: str = Field(..., max_length=50, description="项目编号")
    project_name: str = Field(..., max_length=200, description="项目名称")
    plan_start_date: str | datetime = Field(..., description="计划开始日期")
    plan_end_date: str | datetime = Field(..., description="计划结束日期")
    client_name: str | None = Field(None, max_length=100, description="客户单位")
    maintenance_personnel: str | None = Field(None, max_length=100, description="运维人员")
    status: str = Field("执行中", max_length=20, description="状态")
    filled_count: int | None = Field(0, ge=0, description="已填写检查项数量")
    total_count: int | None = Field(5, ge=0, description="检查项总数量")
    remarks: str | None = Field(None, description="备注")


class WorkPlanUpdate(BaseModel):
    plan_id: str = Field(..., max_length=50, description="计划编号")
    plan_name: str | None = Field(None, max_length=200, description="计划名称")
    plan_type: str = Field(..., max_length=20, description="工单类型：定期巡检/临时维修/零星用工")
    project_id: str = Field(..., max_length=50, description="项目编号")
    project_name: str = Field(..., max_length=200, description="项目名称")
    plan_start_date: str | datetime = Field(..., description="计划开始日期")
    plan_end_date: str | datetime = Field(..., description="计划结束日期")
    client_name: str | None = Field(None, max_length=100, description="客户单位")
    maintenance_personnel: str | None = Field(None, max_length=100, description="运维人员")
    status: str = Field(..., max_length=20, description="状态")
    filled_count: int | None = Field(0, ge=0, description="已填写检查项数量")
    total_count: int | None = Field(5, ge=0, description="检查项总数量")
    remarks: str | None = Field(None, description="备注")


class WorkPlanResponse(BaseModel):
    id: int
    plan_id: str
    plan_name: str | None
    plan_type: str
    project_id: str
    project_name: str
    plan_start_date: datetime
    plan_end_date: datetime
    client_name: str | None
    maintenance_personnel: str | None
    status: str
    filled_count: int | None
    total_count: int | None
    remarks: str | None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
