from datetime import datetime

from pydantic import BaseModel, Field, field_validator


class SpotWorkBase(BaseModel):
    work_id: str = Field(..., max_length=50, description="工单编号")
    plan_id: str | None = Field(None, max_length=50, description="关联维保计划编号")
    project_id: str = Field(..., max_length=50, description="项目编号")
    project_name: str = Field(..., max_length=200, description="项目名称")
    plan_start_date: str | datetime = Field(..., description="计划开始日期")
    plan_end_date: str | datetime = Field(..., description="计划结束日期")
    client_name: str | None = Field(None, max_length=100, description="客户单位")
    client_contact: str | None = Field(None, max_length=100, description="客户联系人")
    client_contact_info: str | None = Field(None, max_length=50, description="客户联系电话")
    maintenance_personnel: str | None = Field(None, max_length=100, description="运维人员")
    work_content: str | None = Field(None, description="工作内容")
    photos: list[str] | None = Field(None, description="现场图片列表")
    signature: str | None = Field(None, description="班组签字图片")
    status: str = Field("执行中", max_length=20, description="状态")
    remarks: str | None = Field(None, max_length=500, description="备注")

    @field_validator('status')
    @classmethod
    def validate_status(cls, v):
        valid_statuses = ['执行中', '待确认', '已完成', '已退回']
        if v not in valid_statuses:
            raise ValueError(f'状态必须是以下之一: {", ".join(valid_statuses)}')
        return v


class SpotWorkCreate(BaseModel):
    work_id: str | None = Field(None, max_length=50, description="工单编号（可选，不传则自动生成）")
    plan_id: str | None = Field(None, max_length=50, description="关联维保计划编号")
    project_id: str = Field(..., max_length=50, description="项目编号")
    project_name: str = Field(..., max_length=200, description="项目名称")
    plan_start_date: str | datetime = Field(..., description="计划开始日期")
    plan_end_date: str | datetime = Field(..., description="计划结束日期")
    client_name: str | None = Field(None, max_length=100, description="客户单位")
    client_contact: str | None = Field(None, max_length=100, description="客户联系人")
    client_contact_info: str | None = Field(None, max_length=50, description="客户联系电话")
    maintenance_personnel: str | None = Field(None, max_length=100, description="运维人员")
    work_content: str | None = Field(None, description="工作内容")
    photos: list[str] | None = Field(None, description="现场图片列表")
    signature: str | None = Field(None, description="班组签字图片")
    status: str | None = Field(None, max_length=20, description="状态")
    remarks: str | None = Field(None, max_length=500, description="备注")


class SpotWorkUpdate(BaseModel):
    work_id: str = Field(..., max_length=50, description="工单编号")
    plan_id: str | None = Field(None, max_length=50, description="关联维保计划编号")
    project_id: str = Field(..., max_length=50, description="项目编号")
    project_name: str = Field(..., max_length=200, description="项目名称")
    plan_start_date: str | datetime = Field(..., description="计划开始日期")
    plan_end_date: str | datetime = Field(..., description="计划结束日期")
    client_name: str | None = Field(None, max_length=100, description="客户单位")
    client_contact: str | None = Field(None, max_length=100, description="客户联系人")
    client_contact_info: str | None = Field(None, max_length=50, description="客户联系电话")
    maintenance_personnel: str | None = Field(None, max_length=100, description="运维人员")
    work_content: str | None = Field(None, description="工作内容")
    photos: list[str] | None = Field(None, description="现场图片列表")
    signature: str | None = Field(None, description="班组签字图片")
    status: str = Field(..., max_length=20, description="状态")
    remarks: str | None = Field(None, max_length=500, description="备注")


class SpotWorkPartialUpdate(BaseModel):
    work_id: str | None = Field(None, max_length=50, description="工单编号")
    plan_id: str | None = Field(None, max_length=50, description="关联维保计划编号")
    project_id: str | None = Field(None, max_length=50, description="项目编号")
    project_name: str | None = Field(None, max_length=200, description="项目名称")
    plan_start_date: str | datetime | None = Field(None, description="计划开始日期")
    plan_end_date: str | datetime | None = Field(None, description="计划结束日期")
    client_name: str | None = Field(None, max_length=100, description="客户单位")
    client_contact: str | None = Field(None, max_length=100, description="客户联系人")
    client_contact_info: str | None = Field(None, max_length=50, description="客户联系电话")
    maintenance_personnel: str | None = Field(None, max_length=100, description="运维人员")
    work_content: str | None = Field(None, description="工作内容")
    photos: list[str] | None = Field(None, description="现场图片列表")
    signature: str | None = Field(None, description="班组签字图片")
    status: str | None = Field(None, max_length=20, description="状态")
    remarks: str | None = Field(None, max_length=500, description="备注")

    @field_validator('status')
    @classmethod
    def validate_status(cls, v):
        if v is None:
            return v
        valid_statuses = ['执行中', '待确认', '已完成', '已退回']
        if v not in valid_statuses:
            raise ValueError(f'状态必须是以下之一: {", ".join(valid_statuses)}')
        return v


class SpotWorkResponse(BaseModel):
    id: int
    work_id: str
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
    work_content: str | None
    photos: list[str] | None
    signature: str | None
    status: str
    remarks: str | None
    actual_completion_date: datetime | None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
