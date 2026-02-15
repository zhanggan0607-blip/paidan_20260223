from pydantic import BaseModel, Field, field_validator
from datetime import datetime
from typing import Optional, Union, List, Any
from app.schemas.common import ApiResponse, PaginatedResponse


class MaintenancePlanBase(BaseModel):
    plan_id: str = Field(..., max_length=50, description="计划编号")
    plan_name: str = Field(..., max_length=200, description="计划名称")
    project_id: str = Field(..., max_length=50, description="关联项目编号")
    plan_type: str = Field(..., max_length=20, description="计划类型")
    equipment_id: str = Field(..., max_length=50, description="设备编号")
    equipment_name: str = Field(..., max_length=200, description="设备名称")
    equipment_model: Optional[str] = Field(None, max_length=100, description="设备型号")
    equipment_location: Optional[str] = Field(None, max_length=200, description="设备位置")
    plan_start_date: datetime = Field(..., description="计划开始日期")
    plan_end_date: datetime = Field(..., description="计划结束日期")
    execution_date: Optional[datetime] = Field(None, description="执行日期")
    next_maintenance_date: Optional[datetime] = Field(None, description="下次维保日期")
    responsible_person: str = Field(..., max_length=50, description="负责人")
    responsible_department: Optional[str] = Field(None, max_length=100, description="负责部门")
    contact_info: Optional[str] = Field(None, max_length=50, description="联系方式")
    maintenance_content: str = Field(..., description="维保内容")
    maintenance_requirements: Optional[str] = Field(None, description="维保要求")
    maintenance_standard: Optional[str] = Field(None, description="维保标准")
    plan_status: str = Field(..., max_length=20, description="计划状态")
    execution_status: str = Field(..., max_length=20, description="执行状态")
    completion_rate: Optional[int] = Field(0, ge=0, le=100, description="完成率")
    remarks: Optional[str] = Field(None, description="备注")

    @field_validator('plan_type')
    @classmethod
    def validate_plan_type(cls, v):
        valid_types = ['定期维保', '预防性维保', '故障维修', '巡检', '其他']
        if v not in valid_types:
            raise ValueError(f'计划类型必须是以下之一: {", ".join(valid_types)}')
        return v

    @field_validator('plan_status')
    @classmethod
    def validate_plan_status(cls, v):
        valid_statuses = ['待执行', '执行中', '已完成', '已取消', '已延期']
        if v not in valid_statuses:
            raise ValueError(f'计划状态必须是以下之一: {", ".join(valid_statuses)}')
        return v

    @field_validator('execution_status')
    @classmethod
    def validate_execution_status(cls, v):
        valid_statuses = ['未开始', '待确认', '已完成', '已取消', '异常']
        if v not in valid_statuses:
            raise ValueError(f'执行状态必须是以下之一: {", ".join(valid_statuses)}')
        return v

    @field_validator('plan_start_date', 'plan_end_date', 'execution_date', 'next_maintenance_date')
    @classmethod
    def validate_dates(cls, v):
        if isinstance(v, str):
            try:
                return datetime.fromisoformat(v)
            except ValueError:
                raise ValueError('日期格式无效，请使用ISO格式')
        return v


class MaintenancePlanCreate(BaseModel):
    plan_id: str = Field(..., max_length=50, description="计划编号")
    plan_name: str = Field(..., max_length=200, description="计划名称")
    project_id: str = Field(..., max_length=50, description="关联项目编号")
    plan_type: str = Field(..., max_length=20, description="计划类型")
    equipment_id: str = Field(..., max_length=50, description="设备编号")
    equipment_name: str = Field(..., max_length=200, description="设备名称")
    equipment_model: Optional[str] = Field(None, max_length=100, description="设备型号")
    equipment_location: Optional[str] = Field(None, max_length=200, description="设备位置")
    plan_start_date: Union[str, datetime] = Field(..., description="计划开始日期")
    plan_end_date: Union[str, datetime] = Field(..., description="计划结束日期")
    execution_date: Optional[Union[str, datetime]] = Field(None, description="执行日期")
    next_maintenance_date: Optional[Union[str, datetime]] = Field(None, description="下次维保日期")
    responsible_person: str = Field(..., max_length=50, description="负责人")
    responsible_department: Optional[str] = Field(None, max_length=100, description="负责部门")
    contact_info: Optional[str] = Field(None, max_length=50, description="联系方式")
    maintenance_content: str = Field(..., description="维保内容")
    maintenance_requirements: Optional[str] = Field(None, description="维保要求")
    maintenance_standard: Optional[str] = Field(None, description="维保标准")
    plan_status: str = Field(..., max_length=20, description="计划状态")
    execution_status: str = Field(..., max_length=20, description="执行状态")
    completion_rate: Optional[int] = Field(0, ge=0, le=100, description="完成率")
    remarks: Optional[str] = Field(None, description="备注")


class MaintenancePlanUpdate(BaseModel):
    plan_id: str = Field(..., max_length=50, description="计划编号")
    plan_name: str = Field(..., max_length=200, description="计划名称")
    project_id: str = Field(..., max_length=50, description="关联项目编号")
    plan_type: str = Field(..., max_length=20, description="计划类型")
    equipment_id: str = Field(..., max_length=50, description="设备编号")
    equipment_name: str = Field(..., max_length=200, description="设备名称")
    equipment_model: Optional[str] = Field(None, max_length=100, description="设备型号")
    equipment_location: Optional[str] = Field(None, max_length=200, description="设备位置")
    plan_start_date: Union[str, datetime] = Field(..., description="计划开始日期")
    plan_end_date: Union[str, datetime] = Field(..., description="计划结束日期")
    execution_date: Optional[Union[str, datetime]] = Field(None, description="执行日期")
    next_maintenance_date: Optional[Union[str, datetime]] = Field(None, description="下次维保日期")
    responsible_person: str = Field(..., max_length=50, description="负责人")
    responsible_department: Optional[str] = Field(None, max_length=100, description="负责部门")
    contact_info: Optional[str] = Field(None, max_length=50, description="联系方式")
    maintenance_content: str = Field(..., description="维保内容")
    maintenance_requirements: Optional[str] = Field(None, description="维保要求")
    maintenance_standard: Optional[str] = Field(None, description="维保标准")
    plan_status: str = Field(..., max_length=20, description="计划状态")
    execution_status: str = Field(..., max_length=20, description="执行状态")
    completion_rate: Optional[int] = Field(0, ge=0, le=100, description="完成率")
    remarks: Optional[str] = Field(None, description="备注")


class MaintenancePlanResponse(BaseModel):
    id: int
    plan_id: str
    plan_name: str
    project_id: str
    plan_type: str
    equipment_id: str
    equipment_name: str
    equipment_model: Optional[str]
    equipment_location: Optional[str]
    plan_start_date: datetime
    plan_end_date: datetime
    execution_date: Optional[datetime]
    next_maintenance_date: Optional[datetime]
    responsible_person: str
    responsible_department: Optional[str]
    contact_info: Optional[str]
    maintenance_content: str
    maintenance_requirements: Optional[str]
    maintenance_standard: Optional[str]
    plan_status: str
    execution_status: str
    completion_rate: Optional[int]
    remarks: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
