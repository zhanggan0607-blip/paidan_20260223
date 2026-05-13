from datetime import datetime

from pydantic import BaseModel, Field, field_validator, model_validator

from app.models.enums import VALID_WORK_ORDER_STATUSES


class TemporaryRepairBase(BaseModel):
    repair_id: str = Field(..., max_length=50, description="维修单编号")
    plan_id: str | None = Field(None, max_length=50, description="关联维保计划编号")
    project_id: str = Field(..., max_length=50, description="项目编号")
    project_name: str = Field(..., max_length=200, description="项目名称")
    plan_start_date: str | datetime = Field(..., description="计划开始日期")
    plan_end_date: str | datetime = Field(..., description="计划结束日期")
    client_name: str | None = Field(None, max_length=100, description="客户单位")
    client_contact: str | None = Field(None, max_length=100, description="客户联系人")
    client_contact_info: str | None = Field(None, max_length=50, description="客户联系电话")
    maintenance_personnel: str = Field(..., max_length=100, description="运维人员")
    status: str = Field("执行中", max_length=20, description="状态")
    remarks: str | None = Field(None, max_length=500, description="备注")
    fault_description: str | None = Field(None, description="故障描述")
    solution: str | None = Field(None, description="解决方案")
    photos: list[str] | None = Field(None, description="现场图片列表")
    signature: str | None = Field(None, description="用户签字Base64")
    customer_signature: str | None = Field(None, description="客户签字Base64")
    execution_date: str | datetime | None = Field(None, description="执行日期")

    @model_validator(mode='after')
    def validate_dates(self):
        if self.plan_start_date and self.plan_end_date:
            start = self.plan_start_date if isinstance(self.plan_start_date, datetime) else datetime.fromisoformat(str(self.plan_start_date))
            end = self.plan_end_date if isinstance(self.plan_end_date, datetime) else datetime.fromisoformat(str(self.plan_end_date))
            if end < start:
                raise ValueError('计划结束日期不能早于开始日期')
        return self

    @field_validator('status')
    @classmethod
    def validate_status(cls, v):
        valid_statuses = VALID_WORK_ORDER_STATUSES
        if v not in valid_statuses:
            raise ValueError(f'状态必须是以下之一: {", ".join(valid_statuses)}')
        return v


class TemporaryRepairCreate(BaseModel):
    repair_id: str | None = Field(None, max_length=50, description="维修单编号（可选，不传则自动生成）")
    plan_id: str | None = Field(None, max_length=50, description="关联维保计划编号")
    project_id: str = Field(..., max_length=50, description="项目编号")
    project_name: str = Field(..., max_length=200, description="项目名称")
    plan_start_date: str | datetime = Field(..., description="计划开始日期")
    plan_end_date: str | datetime = Field(..., description="计划结束日期")
    client_name: str | None = Field(None, max_length=100, description="客户单位")
    client_contact: str | None = Field(None, max_length=100, description="客户联系人")
    client_contact_info: str | None = Field(None, max_length=50, description="客户联系电话")
    maintenance_personnel: str = Field(..., max_length=100, description="运维人员")
    status: str | None = Field(None, max_length=20, description="状态")
    remarks: str | None = Field(None, max_length=500, description="备注")
    fault_description: str | None = Field(None, description="故障描述")
    solution: str | None = Field(None, description="解决方案")
    photos: list[str] | None = Field(None, description="现场图片列表")
    signature: str | None = Field(None, description="用户签字Base64")
    customer_signature: str | None = Field(None, description="客户签字Base64")
    execution_date: str | datetime | None = Field(None, description="执行日期")


class TemporaryRepairUpdate(BaseModel):
    repair_id: str = Field(..., max_length=50, description="维修单编号")
    plan_id: str | None = Field(None, max_length=50, description="关联维保计划编号")
    project_id: str = Field(..., max_length=50, description="项目编号")
    project_name: str = Field(..., max_length=200, description="项目名称")
    plan_start_date: str | datetime = Field(..., description="计划开始日期")
    plan_end_date: str | datetime = Field(..., description="计划结束日期")
    client_name: str | None = Field(None, max_length=100, description="客户单位")
    client_contact: str | None = Field(None, max_length=100, description="客户联系人")
    client_contact_info: str | None = Field(None, max_length=50, description="客户联系电话")
    maintenance_personnel: str = Field(..., max_length=100, description="运维人员")
    status: str = Field(..., max_length=20, description="状态")
    remarks: str | None = Field(None, max_length=500, description="备注")
    fault_description: str | None = Field(None, description="故障描述")
    solution: str | None = Field(None, description="解决方案")
    photos: list[str] | None = Field(None, description="现场图片列表")
    signature: str | None = Field(None, description="用户签字Base64")
    customer_signature: str | None = Field(None, description="客户签字Base64")
    execution_date: str | datetime | None = Field(None, description="执行日期")


class TemporaryRepairPartialUpdate(BaseModel):
    repair_id: str | None = Field(None, max_length=50, description="维修单编号")
    plan_id: str | None = Field(None, max_length=50, description="关联维保计划编号")
    project_id: str | None = Field(None, max_length=50, description="项目编号")
    project_name: str | None = Field(None, max_length=200, description="项目名称")
    plan_start_date: str | datetime | None = Field(None, description="计划开始日期")
    plan_end_date: str | datetime | None = Field(None, description="计划结束日期")
    client_name: str | None = Field(None, max_length=100, description="客户单位")
    client_contact: str | None = Field(None, max_length=100, description="客户联系人")
    client_contact_info: str | None = Field(None, max_length=50, description="客户联系电话")
    maintenance_personnel: str | None = Field(None, max_length=100, description="运维人员")
    status: str | None = Field(None, max_length=20, description="状态")
    remarks: str | None = Field(None, max_length=500, description="备注")
    fault_description: str | None = Field(None, description="故障描述")
    solution: str | None = Field(None, description="解决方案")
    photos: list[str] | None = Field(None, description="现场图片列表")
    signature: str | None = Field(None, description="用户签字Base64")
    customer_signature: str | None = Field(None, description="客户签字Base64")
    execution_date: str | datetime | None = Field(None, description="执行日期")
    reject_reason: str | None = Field(None, max_length=500, description="退回原因")

    @field_validator('status')
    @classmethod
    def validate_status(cls, v):
        if v is None:
            return v
        valid_statuses = VALID_WORK_ORDER_STATUSES
        if v not in valid_statuses:
            raise ValueError(f'状态必须是以下之一: {", ".join(valid_statuses)}')
        return v


class TemporaryRepairApprove(BaseModel):
    approved: bool
    reject_reason: str | None = Field(None, max_length=500, description="退回原因")


class TemporaryRepairResponse(BaseModel):
    id: int
    repair_id: str
    plan_id: str | None
    project_id: str
    project_name: str
    plan_start_date: datetime
    plan_end_date: datetime
    client_name: str | None
    client_contact: str | None
    client_contact_info: str | None
    address: str | None
    client_contact_position: str | None
    maintenance_personnel: str | None
    status: str
    remarks: str | None
    fault_description: str | None
    solution: str | None
    photos: list[str] | None
    signature: str | None
    customer_signature: str | None
    reject_reason: str | None
    execution_date: datetime | None
    actual_completion_date: datetime | None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
