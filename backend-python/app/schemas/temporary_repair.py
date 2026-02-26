from pydantic import BaseModel, Field, field_validator
from typing import Optional, Union, List
from datetime import datetime
from app.schemas.common import ApiResponse, PaginatedResponse


class TemporaryRepairBase(BaseModel):
    repair_id: str = Field(..., max_length=50, description="维修单编号")
    plan_id: Optional[str] = Field(None, max_length=50, description="关联维保计划编号")
    project_id: str = Field(..., max_length=50, description="项目编号")
    project_name: str = Field(..., max_length=200, description="项目名称")
    plan_start_date: Union[str, datetime] = Field(..., description="计划开始日期")
    plan_end_date: Union[str, datetime] = Field(..., description="计划结束日期")
    client_name: Optional[str] = Field(None, max_length=100, description="客户单位")
    client_contact: Optional[str] = Field(None, max_length=100, description="客户联系人")
    client_contact_info: Optional[str] = Field(None, max_length=50, description="客户联系电话")
    maintenance_personnel: Optional[str] = Field(None, max_length=100, description="运维人员")
    status: str = Field("未进行", max_length=20, description="状态")
    remarks: Optional[str] = Field(None, max_length=500, description="备注")
    fault_description: Optional[str] = Field(None, description="故障描述")
    solution: Optional[str] = Field(None, description="解决方案")
    photos: Optional[List[str]] = Field(None, description="现场图片列表")
    signature: Optional[str] = Field(None, description="用户签字Base64")
    customer_signature: Optional[str] = Field(None, description="客户签字Base64")
    execution_date: Optional[Union[str, datetime]] = Field(None, description="执行日期")

    @field_validator('status')
    @classmethod
    def validate_status(cls, v):
        valid_statuses = ['未进行', '待确认', '已确认', '已完成', '已取消', '已退回']
        if v not in valid_statuses:
            raise ValueError(f'状态必须是以下之一: {", ".join(valid_statuses)}')
        return v


class TemporaryRepairCreate(BaseModel):
    repair_id: str = Field(..., max_length=50, description="维修单编号")
    plan_id: Optional[str] = Field(None, max_length=50, description="关联维保计划编号")
    project_id: str = Field(..., max_length=50, description="项目编号")
    project_name: str = Field(..., max_length=200, description="项目名称")
    plan_start_date: Union[str, datetime] = Field(..., description="计划开始日期")
    plan_end_date: Union[str, datetime] = Field(..., description="计划结束日期")
    client_name: Optional[str] = Field(None, max_length=100, description="客户单位")
    client_contact: Optional[str] = Field(None, max_length=100, description="客户联系人")
    client_contact_info: Optional[str] = Field(None, max_length=50, description="客户联系电话")
    maintenance_personnel: Optional[str] = Field(None, max_length=100, description="运维人员")
    status: str = Field("未进行", max_length=20, description="状态")
    remarks: Optional[str] = Field(None, max_length=500, description="备注")
    fault_description: Optional[str] = Field(None, description="故障描述")
    solution: Optional[str] = Field(None, description="解决方案")
    photos: Optional[List[str]] = Field(None, description="现场图片列表")
    signature: Optional[str] = Field(None, description="用户签字Base64")
    customer_signature: Optional[str] = Field(None, description="客户签字Base64")
    execution_date: Optional[Union[str, datetime]] = Field(None, description="执行日期")


class TemporaryRepairUpdate(BaseModel):
    repair_id: str = Field(..., max_length=50, description="维修单编号")
    plan_id: Optional[str] = Field(None, max_length=50, description="关联维保计划编号")
    project_id: str = Field(..., max_length=50, description="项目编号")
    project_name: str = Field(..., max_length=200, description="项目名称")
    plan_start_date: Union[str, datetime] = Field(..., description="计划开始日期")
    plan_end_date: Union[str, datetime] = Field(..., description="计划结束日期")
    client_name: Optional[str] = Field(None, max_length=100, description="客户单位")
    client_contact: Optional[str] = Field(None, max_length=100, description="客户联系人")
    client_contact_info: Optional[str] = Field(None, max_length=50, description="客户联系电话")
    maintenance_personnel: Optional[str] = Field(None, max_length=100, description="运维人员")
    status: str = Field(..., max_length=20, description="状态")
    remarks: Optional[str] = Field(None, max_length=500, description="备注")
    fault_description: Optional[str] = Field(None, description="故障描述")
    solution: Optional[str] = Field(None, description="解决方案")
    photos: Optional[List[str]] = Field(None, description="现场图片列表")
    signature: Optional[str] = Field(None, description="用户签字Base64")
    customer_signature: Optional[str] = Field(None, description="客户签字Base64")
    execution_date: Optional[Union[str, datetime]] = Field(None, description="执行日期")


class TemporaryRepairPartialUpdate(BaseModel):
    repair_id: Optional[str] = Field(None, max_length=50, description="维修单编号")
    plan_id: Optional[str] = Field(None, max_length=50, description="关联维保计划编号")
    project_id: Optional[str] = Field(None, max_length=50, description="项目编号")
    project_name: Optional[str] = Field(None, max_length=200, description="项目名称")
    plan_start_date: Optional[Union[str, datetime]] = Field(None, description="计划开始日期")
    plan_end_date: Optional[Union[str, datetime]] = Field(None, description="计划结束日期")
    client_name: Optional[str] = Field(None, max_length=100, description="客户单位")
    client_contact: Optional[str] = Field(None, max_length=100, description="客户联系人")
    client_contact_info: Optional[str] = Field(None, max_length=50, description="客户联系电话")
    maintenance_personnel: Optional[str] = Field(None, max_length=100, description="运维人员")
    status: Optional[str] = Field(None, max_length=20, description="状态")
    remarks: Optional[str] = Field(None, max_length=500, description="备注")
    fault_description: Optional[str] = Field(None, description="故障描述")
    solution: Optional[str] = Field(None, description="解决方案")
    photos: Optional[List[str]] = Field(None, description="现场图片列表")
    signature: Optional[str] = Field(None, description="用户签字Base64")
    customer_signature: Optional[str] = Field(None, description="客户签字Base64")
    execution_date: Optional[Union[str, datetime]] = Field(None, description="执行日期")

    @field_validator('status')
    @classmethod
    def validate_status(cls, v):
        if v is None:
            return v
        valid_statuses = ['未进行', '待确认', '已确认', '已完成', '已取消', '已退回']
        if v not in valid_statuses:
            raise ValueError(f'状态必须是以下之一: {", ".join(valid_statuses)}')
        return v


class TemporaryRepairResponse(BaseModel):
    id: int
    repair_id: str
    plan_id: Optional[str]
    project_id: str
    project_name: str
    plan_start_date: datetime
    plan_end_date: datetime
    client_name: Optional[str]
    client_contact: Optional[str]
    client_contact_info: Optional[str]
    address: Optional[str]
    client_contact_position: Optional[str]
    maintenance_personnel: Optional[str]
    status: str
    remarks: Optional[str]
    fault_description: Optional[str]
    solution: Optional[str]
    photos: Optional[List[str]]
    signature: Optional[str]
    execution_date: Optional[datetime]
    actual_completion_date: Optional[datetime]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
