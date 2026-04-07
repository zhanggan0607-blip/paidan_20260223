from datetime import datetime

from pydantic import BaseModel, Field, field_validator


class MaintenancePlanBase(BaseModel):
    plan_id: str = Field(..., max_length=50, description="计划编号")
    plan_name: str = Field(..., max_length=200, description="计划名称")
    project_id: str = Field(..., max_length=50, description="关联项目编号")
    plan_type: str = Field(..., max_length=20, description="工单类型")
    equipment_id: str = Field(..., max_length=50, description="设备编号")
    equipment_name: str = Field(..., max_length=200, description="设备名称")
    equipment_model: str | None = Field(None, max_length=100, description="设备型号")
    equipment_location: str | None = Field(None, max_length=200, description="设备位置")
    plan_start_date: datetime = Field(..., description="计划开始日期")
    plan_end_date: datetime = Field(..., description="计划结束日期")
    execution_date: datetime | None = Field(None, description="执行日期")
    next_maintenance_date: datetime | None = Field(None, description="下次维保日期")
    maintenance_personnel: str | None = Field(None, max_length=100, description="运维人员")
    responsible_department: str | None = Field(None, max_length=100, description="负责部门")
    contact_info: str | None = Field(None, max_length=50, description="联系方式")
    maintenance_content: str = Field(..., description="维保内容")
    maintenance_requirements: str | None = Field(None, description="维保要求")
    maintenance_standard: str | None = Field(None, description="维保标准")
    plan_status: str = Field(..., max_length=20, description="计划状态")
    status: str = Field("执行中", max_length=20, description="执行状态")
    completion_rate: int | None = Field(0, ge=0, le=100, description="完成率")
    filled_count: int | None = Field(0, ge=0, description="已填写检查项数量")
    total_count: int | None = Field(5, ge=0, description="检查项总数量")
    remarks: str | None = Field(None, description="备注")
    inspection_items: str | None = Field(None, description="巡查项数据(JSON格式)")

    @field_validator('plan_type')
    @classmethod
    def validate_plan_type(cls, v):
        valid_types = ['定期维保', '预防性维保', '故障维修', '巡检', '其他', '定期巡检', '临时维修', '零星用工']
        if v not in valid_types:
            raise ValueError(f'工单类型必须是以下之一: {", ".join(valid_types)}')
        return v

    @field_validator('plan_status')
    @classmethod
    def validate_plan_status(cls, v):
        valid_statuses = ['执行中', '待确认', '已完成', '已退回']
        if v not in valid_statuses:
            raise ValueError(f'计划状态必须是以下之一: {", ".join(valid_statuses)}')
        return v

    @field_validator('status')
    @classmethod
    def validate_status(cls, v):
        valid_statuses = ['未开始', '执行中', '待确认', '已完成', '已退回']
        if v not in valid_statuses:
            raise ValueError(f'执行状态必须是以下之一: {", ".join(valid_statuses)}')
        return v

    @field_validator('plan_start_date', 'plan_end_date', 'execution_date', 'next_maintenance_date')
    @classmethod
    def validate_dates(cls, v):
        if isinstance(v, str):
            try:
                return datetime.fromisoformat(v)
            except ValueError as e:
                raise ValueError('日期格式无效，请使用ISO格式') from e
        return v


class MaintenancePlanCreate(BaseModel):
    plan_id: str = Field(..., max_length=50, description="计划编号")
    plan_name: str = Field(..., max_length=200, description="计划名称")
    project_id: str = Field(..., max_length=50, description="关联项目编号")
    plan_type: str = Field(..., max_length=20, description="工单类型")
    equipment_id: str = Field(..., max_length=50, description="设备编号")
    equipment_name: str = Field(..., max_length=200, description="设备名称")
    equipment_model: str | None = Field(None, max_length=100, description="设备型号")
    equipment_location: str | None = Field(None, max_length=200, description="设备位置")
    plan_start_date: str | datetime = Field(..., description="计划开始日期")
    plan_end_date: str | datetime = Field(..., description="计划结束日期")
    execution_date: str | datetime | None = Field(None, description="执行日期")
    next_maintenance_date: str | datetime | None = Field(None, description="下次维保日期")
    maintenance_personnel: str | None = Field(None, max_length=100, description="运维人员")
    responsible_department: str | None = Field(None, max_length=100, description="负责部门")
    contact_info: str | None = Field(None, max_length=50, description="联系方式")
    maintenance_content: str = Field(..., description="维保内容")
    maintenance_requirements: str | None = Field(None, description="维保要求")
    maintenance_standard: str | None = Field(None, description="维保标准")
    plan_status: str = Field(..., max_length=20, description="计划状态")
    status: str = Field("执行中", max_length=20, description="执行状态")
    completion_rate: int | None = Field(0, ge=0, le=100, description="完成率")
    filled_count: int | None = Field(0, ge=0, description="已填写检查项数量")
    total_count: int | None = Field(5, ge=0, description="检查项总数量")
    remarks: str | None = Field(None, description="备注")
    inspection_items: str | None = Field(None, description="巡查项数据(JSON格式)")


class MaintenancePlanUpdate(BaseModel):
    plan_id: str = Field(..., max_length=50, description="计划编号")
    plan_name: str = Field(..., max_length=200, description="计划名称")
    project_id: str = Field(..., max_length=50, description="关联项目编号")
    plan_type: str = Field(..., max_length=20, description="工单类型")
    equipment_id: str = Field(..., max_length=50, description="设备编号")
    equipment_name: str = Field(..., max_length=200, description="设备名称")
    equipment_model: str | None = Field(None, max_length=100, description="设备型号")
    equipment_location: str | None = Field(None, max_length=200, description="设备位置")
    plan_start_date: str | datetime = Field(..., description="计划开始日期")
    plan_end_date: str | datetime = Field(..., description="计划结束日期")
    execution_date: str | datetime | None = Field(None, description="执行日期")
    next_maintenance_date: str | datetime | None = Field(None, description="下次维保日期")
    maintenance_personnel: str | None = Field(None, max_length=100, description="运维人员")
    responsible_department: str | None = Field(None, max_length=100, description="负责部门")
    contact_info: str | None = Field(None, max_length=50, description="联系方式")
    maintenance_content: str = Field(..., description="维保内容")
    maintenance_requirements: str | None = Field(None, description="维保要求")
    maintenance_standard: str | None = Field(None, description="维保标准")
    plan_status: str = Field(..., max_length=20, description="计划状态")
    status: str = Field(..., max_length=20, description="执行状态")
    completion_rate: int | None = Field(0, ge=0, le=100, description="完成率")
    filled_count: int | None = Field(0, ge=0, description="已填写检查项数量")
    total_count: int | None = Field(5, ge=0, description="检查项总数量")
    remarks: str | None = Field(None, description="备注")
    inspection_items: str | None = Field(None, description="巡查项数据(JSON格式)")


class MaintenancePlanResponse(BaseModel):
    id: int
    plan_id: str
    plan_name: str
    project_id: str
    plan_type: str
    equipment_id: str
    equipment_name: str
    equipment_model: str | None
    equipment_location: str | None
    plan_start_date: datetime
    plan_end_date: datetime
    execution_date: datetime | None
    next_maintenance_date: datetime | None
    maintenance_personnel: str | None
    responsible_department: str | None
    contact_info: str | None
    maintenance_content: str
    maintenance_requirements: str | None
    maintenance_standard: str | None
    plan_status: str
    status: str
    completion_rate: int | None
    filled_count: int | None
    total_count: int | None
    remarks: str | None
    inspection_items: str | None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
