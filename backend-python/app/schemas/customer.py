from pydantic import BaseModel, Field, field_validator
from typing import Optional
from datetime import datetime
import re

class CustomerBase(BaseModel):
    name: str = Field(..., max_length=100, description="客户单位")
    address: Optional[str] = Field(None, max_length=200, description="客户地址")
    contact_person: str = Field(..., max_length=50, description="客户联系人")
    phone: str = Field(..., max_length=20, description="客户联系方式")
    contact_position: Optional[str] = Field(None, max_length=50, description="客户联系人职位")
    remarks: Optional[str] = Field(None, description="备注")

class CustomerCreate(CustomerBase):
    @field_validator('phone')
    @classmethod
    def validate_phone(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError('客户联系方式不能为空')
        
        phone = v.strip()
        
        phone_pattern = r'^1[3-9]\d{9}$'
        if not re.match(phone_pattern, phone):
            raise ValueError('请输入有效的手机号码')
        
        return phone

class CustomerUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=100, description="客户单位")
    address: Optional[str] = Field(None, max_length=200, description="客户地址")
    contact_person: Optional[str] = Field(None, max_length=50, description="客户联系人")
    phone: Optional[str] = Field(None, max_length=20, description="客户联系方式")
    contact_position: Optional[str] = Field(None, max_length=50, description="客户联系人职位")
    remarks: Optional[str] = Field(None, description="备注")

    @field_validator('phone')
    @classmethod
    def validate_phone(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        
        if not v or not v.strip():
            raise ValueError('客户联系方式不能为空')
        
        phone = v.strip()
        
        phone_pattern = r'^1[3-9]\d{9}$'
        if not re.match(phone_pattern, phone):
            raise ValueError('请输入有效的手机号码')
        
        return phone

class CustomerResponse(CustomerBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class CustomerListResponse(BaseModel):
    content: list[CustomerResponse]
    totalElements: int
    totalPages: int
    size: int
    number: int
