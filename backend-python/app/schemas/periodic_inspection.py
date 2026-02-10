from pydantic import BaseModel, Field, field_validator
from typing import Optional, Union, List, Any
from datetime import datetime


class PeriodicInspectionBase(BaseModel):
    inspection_id: str = Field(..., max_length=50, description="巡检单编号")
    project_id: str = Field(..., max_length=50, description="项目编号")
    project_name: str = Field(..., max_length=200, description="项目名称")
    plan_start_date: Union[str, datetime] = Field(..., description="计划开始日期")
    plan_end_date: Union[str, datetime] = Field(..., description="计划结束日期")
    client_name: Optional[str] = Field(None, max_length=100, description="客户单位")
    maintenance_personnel: Optional[str] = Field(None, max_length=100, description="运维人员")
    status: str = Field("未进行", max_length=20, description="状态")
    remarks: Optional[str] = Field(None, max_length=500, description="备注")
    
    @field_validator('status')
    @classmethod
    def validate_status(cls, v):
        valid_statuses = ['未进行', '待确认', '已确认', '进行中', '已完成', '已取消']
        if v not in valid_statuses:
            raise ValueError(f'状态必须是以下之一: {", ".join(valid_statuses)}')
        return v


class PeriodicInspectionCreate(BaseModel):
    inspection_id: str = Field(..., max_length=50, description="巡检单编号")
    project_id: str = Field(..., max_length=50, description="项目编号")
    project_name: str = Field(..., max_length=200, description="项目名称")
    plan_start_date: Union[str, datetime] = Field(..., description="计划开始日期")
    plan_end_date: Union[str, datetime] = Field(..., description="计划结束日期")
    client_name: Optional[str] = Field(None, max_length=100, description="客户单位")
    maintenance_personnel: Optional[str] = Field(None, max_length=100, description="运维人员")
    status: str = Field("未进行", max_length=20, description="状态")
    remarks: Optional[str] = Field(None, max_length=500, description="备注")


class PeriodicInspectionUpdate(BaseModel):
    inspection_id: str = Field(..., max_length=50, description="巡检单编号")
    project_id: str = Field(..., max_length=50, description="项目编号")
    project_name: str = Field(..., max_length=200, description="项目名称")
    plan_start_date: Union[str, datetime] = Field(..., description="计划开始日期")
    plan_end_date: Union[str, datetime] = Field(..., description="计划结束日期")
    client_name: Optional[str] = Field(None, max_length=100, description="客户单位")
    maintenance_personnel: Optional[str] = Field(None, max_length=100, description="运维人员")
    status: str = Field(..., max_length=20, description="状态")
    remarks: Optional[str] = Field(None, max_length=500, description="备注")


class PeriodicInspectionResponse(BaseModel):
    id: int
    inspection_id: str
    project_id: str
    project_name: str
    plan_start_date: datetime
    plan_end_date: datetime
    client_name: Optional[str]
    maintenance_personnel: Optional[str]
    status: str
    remarks: Optional[str]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class ApiResponse(BaseModel):
    code: int = 200
    message: str = "success"
    data: Optional[Union[dict, List[Any]]] = None
    
    @classmethod
    def success(cls, data=None, message="success"):
        return cls(code=200, message=message, data=data)
    
    @classmethod
    def error(cls, message="error", code=500):
        return cls(code=code, message=message, data=None)


class PaginatedResponse(BaseModel):
    code: int = 200
    message: str = "success"
    data: dict
    
    @classmethod
    def success(cls, items, total, page, size, message="success"):
        return cls(
            code=200,
            message=message,
            data={
                'content': items,
                'totalElements': total,
                'totalPages': (total + size - 1) // size,
                'size': size,
                'number': page,
                'first': page == 0,
                'last': page >= (total + size - 1) // size - 1,
            }
        )
