from pydantic import BaseModel, Field, field_validator
from typing import Optional, Union, List, Any
from datetime import datetime
from app.config import PersonnelConfig
from app.schemas.common import ApiResponse, PaginatedResponse

class PersonnelBase(BaseModel):
    name: str = Field(..., max_length=50, description="姓名")
    gender: str = Field(..., max_length=10, description="性别")
    phone: Optional[str] = Field(None, max_length=20, description="联系电话")
    department: Optional[str] = Field(None, max_length=100, description="所属部门")
    role: str = Field("员工", max_length=20, description="角色")
    address: Optional[str] = Field(None, max_length=200, description="地址")
    remarks: Optional[str] = Field(None, max_length=500, description="备注")

    @field_validator('gender')
    @classmethod
    def validate_gender(cls, v):
        valid_genders = ['男', '女', '其他']
        if v not in valid_genders:
            raise ValueError(f'性别必须是以下之一: {", ".join(valid_genders)}')
        return v

    @field_validator('role')
    @classmethod
    def validate_role(cls, v):
        valid_roles = PersonnelConfig.get_valid_roles()
        if v not in valid_roles:
            raise ValueError(f'角色必须是以下之一: {", ".join(valid_roles)}')
        return v

class PersonnelCreate(PersonnelBase):
    name: str = Field(..., max_length=50, description="姓名")
    gender: str = Field(..., max_length=10, description="性别")
    phone: Optional[str] = Field(None, max_length=20, description="联系电话")
    department: Optional[str] = Field(None, max_length=100, description="所属部门")
    role: str = Field("员工", max_length=20, description="角色")
    address: Optional[str] = Field(None, max_length=200, description="地址")
    remarks: Optional[str] = Field(None, max_length=500, description="备注")

class PersonnelUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=50, description="姓名")
    gender: Optional[str] = Field(None, max_length=10, description="性别")
    phone: Optional[str] = Field(None, max_length=20, description="联系电话")
    department: Optional[str] = Field(None, max_length=100, description="所属部门")
    role: Optional[str] = Field(None, max_length=20, description="角色")
    address: Optional[str] = Field(None, max_length=200, description="地址")
    remarks: Optional[str] = Field(None, max_length=500, description="备注")

class PersonnelResponse(BaseModel):
    id: int
    name: str
    gender: str
    phone: Optional[str]
    department: Optional[str]
    role: str
    address: Optional[str]
    remarks: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
