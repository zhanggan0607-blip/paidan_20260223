from pydantic import BaseModel, Field, field_validator
from typing import Optional, Union, List, Any
from datetime import datetime
from app.schemas.common import ApiResponse, PaginatedResponse


class PeriodicInspectionBase(BaseModel):
    inspection_id: str = Field(..., max_length=50, description="工单编号")
    plan_id: Optional[str] = Field(None, max_length=50, description="关联维保计划编号")
    project_id: str = Field(..., max_length=50, description="项目编号")
    project_name: str = Field(..., max_length=200, description="项目名称")
    plan_start_date: Union[str, datetime] = Field(..., description="计划开始日期")
    plan_end_date: Union[str, datetime] = Field(..., description="计划结束日期")
    client_name: Optional[str] = Field(None, max_length=100, description="客户单位")
    maintenance_personnel: Optional[str] = Field(None, max_length=100, description="运维人员")
    status: str = Field("未进行", max_length=20, description="状态")
    filled_count: Optional[int] = Field(0, description="已填写检查项数量")
    total_count: Optional[int] = Field(5, description="检查项总数量")
    execution_result: Optional[str] = Field(None, description="发现问题")
    remarks: Optional[str] = Field(None, max_length=500, description="处理结果")
    signature: Optional[str] = Field(None, description="用户签名(base64)")

    @field_validator('status')
    @classmethod
    def validate_status(cls, v):
        valid_statuses = ['未进行', '待确认', '已确认', '已完成', '已取消', '已退回']
        if v not in valid_statuses:
            raise ValueError(f'状态必须是以下之一: {", ".join(valid_statuses)}')
        return v


class PeriodicInspectionCreate(BaseModel):
    inspection_id: str = Field(..., max_length=50, description="工单编号")
    plan_id: Optional[str] = Field(None, max_length=50, description="关联维保计划编号")
    project_id: str = Field(..., max_length=50, description="项目编号")
    project_name: str = Field(..., max_length=200, description="项目名称")
    plan_start_date: Union[str, datetime] = Field(..., description="计划开始日期")
    plan_end_date: Union[str, datetime] = Field(..., description="计划结束日期")
    client_name: Optional[str] = Field(None, max_length=100, description="客户单位")
    maintenance_personnel: Optional[str] = Field(None, max_length=100, description="运维人员")
    status: Optional[str] = Field(None, max_length=20, description="状态")
    filled_count: Optional[int] = Field(0, description="已填写检查项数量")
    total_count: Optional[int] = Field(5, description="检查项总数量")
    execution_result: Optional[str] = Field(None, description="发现问题")
    remarks: Optional[str] = Field(None, max_length=500, description="处理结果")
    signature: Optional[str] = Field(None, description="用户签名(base64)")


class PeriodicInspectionUpdate(BaseModel):
    inspection_id: str = Field(..., max_length=50, description="工单编号")
    plan_id: Optional[str] = Field(None, max_length=50, description="关联维保计划编号")
    project_id: str = Field(..., max_length=50, description="项目编号")
    project_name: str = Field(..., max_length=200, description="项目名称")
    plan_start_date: Union[str, datetime] = Field(..., description="计划开始日期")
    plan_end_date: Union[str, datetime] = Field(..., description="计划结束日期")
    client_name: Optional[str] = Field(None, max_length=100, description="客户单位")
    maintenance_personnel: Optional[str] = Field(None, max_length=100, description="运维人员")
    status: str = Field(..., max_length=20, description="状态")
    filled_count: Optional[int] = Field(0, description="已填写检查项数量")
    total_count: Optional[int] = Field(5, description="检查项总数量")
    execution_result: Optional[str] = Field(None, description="发现问题")
    remarks: Optional[str] = Field(None, max_length=500, description="处理结果")
    signature: Optional[str] = Field(None, description="用户签名(base64)")


class PeriodicInspectionPartialUpdate(BaseModel):
    signature: Optional[str] = Field(None, description="用户签名(base64)")
    execution_result: Optional[str] = Field(None, description="发现问题")
    remarks: Optional[str] = Field(None, max_length=500, description="处理结果")
    status: Optional[str] = Field(None, max_length=20, description="状态")
    filled_count: Optional[int] = Field(None, description="已填写检查项数量")
    total_count: Optional[int] = Field(None, description="检查项总数量")

    @field_validator('status')
    @classmethod
    def validate_status(cls, v):
        if v is None:
            return v
        valid_statuses = ['未进行', '待确认', '已确认', '已完成', '已取消', '已退回']
        if v not in valid_statuses:
            raise ValueError(f'状态必须是以下之一: {", ".join(valid_statuses)}')
        return v


class PeriodicInspectionResponse(BaseModel):
    id: int
    inspection_id: str
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
    filled_count: int
    total_count: int
    execution_result: Optional[str]
    remarks: Optional[str]
    signature: Optional[str]
    actual_completion_date: Optional[datetime]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
