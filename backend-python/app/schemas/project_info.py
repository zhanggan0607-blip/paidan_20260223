from pydantic import BaseModel, Field, field_validator
from datetime import datetime
from typing import Optional, List, Union


class ProjectInfoBase(BaseModel):
    project_id: str = Field(..., max_length=50, description="项目编号")
    project_name: str = Field(..., max_length=200, description="项目名称")
    completion_date: datetime = Field(..., description="开始日期")
    maintenance_end_date: datetime = Field(..., description="结束日期")
    maintenance_period: str = Field(..., max_length=20, description="维保周期")
    client_name: str = Field(..., max_length=100, description="客户单位名称")
    address: str = Field(..., max_length=200, description="客户地址")
    project_abbr: Optional[str] = Field(None, max_length=10, description="项目简称")
    client_contact: Optional[str] = Field(None, max_length=50, description="客户联系人")
    client_contact_position: Optional[str] = Field(None, max_length=20, description="客户联系人职位")
    client_contact_info: Optional[str] = Field(None, max_length=50, description="客户联系方式")
    
    @field_validator('maintenance_period')
    @classmethod
    def validate_maintenance_period(cls, v):
        valid_periods = ['每天', '每周', '每月', '每季度', '每半年']
        if v not in valid_periods:
            raise ValueError(f'维保周期必须是以下之一: {", ".join(valid_periods)}')
        return v
    
    @field_validator('completion_date', 'maintenance_end_date')
    @classmethod
    def validate_dates(cls, v):
        if isinstance(v, str):
            try:
                return datetime.fromisoformat(v)
            except ValueError:
                raise ValueError('日期格式无效，请使用ISO格式')
        return v


class ProjectInfoCreate(BaseModel):
    project_id: str = Field(..., max_length=50, description="项目编号")
    project_name: str = Field(..., max_length=200, description="项目名称")
    completion_date: datetime = Field(..., description="开始日期")
    maintenance_end_date: datetime = Field(..., description="结束日期")
    maintenance_period: str = Field(..., max_length=20, description="维保周期")
    client_name: str = Field(..., max_length=100, description="客户单位名称")
    address: str = Field(..., max_length=200, description="客户地址")
    project_abbr: Optional[str] = Field(None, max_length=10, description="项目简称")
    client_contact: Optional[str] = Field(None, max_length=50, description="客户联系人")
    client_contact_position: Optional[str] = Field(None, max_length=20, description="客户联系人职位")
    client_contact_info: Optional[str] = Field(None, max_length=50, description="客户联系方式")


class ProjectInfoUpdate(BaseModel):
    project_id: str = Field(..., max_length=50, description="项目编号")
    project_name: str = Field(..., max_length=200, description="项目名称")
    completion_date: datetime = Field(..., description="开始日期")
    maintenance_end_date: datetime = Field(..., description="结束日期")
    maintenance_period: str = Field(..., max_length=20, description="维保周期")
    client_name: str = Field(..., max_length=100, description="客户单位名称")
    address: str = Field(..., max_length=200, description="客户地址")
    project_abbr: Optional[str] = Field(None, max_length=10, description="项目简称")
    client_contact: Optional[str] = Field(None, max_length=50, description="客户联系人")
    client_contact_position: Optional[str] = Field(None, max_length=20, description="客户联系人职位")
    client_contact_info: Optional[str] = Field(None, max_length=50, description="客户联系方式")


class ProjectInfoResponse(BaseModel):
    id: int
    project_id: str
    project_name: str
    completion_date: datetime
    maintenance_end_date: datetime
    maintenance_period: str
    client_name: str
    address: str
    project_abbr: Optional[str]
    client_contact: Optional[str]
    client_contact_position: Optional[str]
    client_contact_info: Optional[str]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class ApiResponse(BaseModel):
    code: int = 200
    message: str = "success"
    data: Optional[Union[dict, List]] = None
    
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
