import re
from datetime import datetime

from pydantic import BaseModel, Field, field_validator


class CustomerContactBase(BaseModel):
    contact_person: str = Field(..., max_length=50, description="联系人姓名")
    phone: str | None = Field(None, max_length=20, description="联系方式")
    contact_position: str | None = Field(None, max_length=50, description="联系人职位")
    remarks: str | None = Field(None, description="备注")


class CustomerContactCreate(CustomerContactBase):
    @field_validator('phone')
    @classmethod
    def validate_phone(cls, v: str | None) -> str | None:
        if v is None or not v.strip():
            return None

        phone = v.strip()

        phone_pattern = r'^1[3-9]\d{9}$'
        if not re.match(phone_pattern, phone):
            raise ValueError('请输入有效的手机号码')

        return phone


class CustomerContactUpdate(BaseModel):
    contact_person: str | None = Field(None, max_length=50, description="联系人姓名")
    phone: str | None = Field(None, max_length=20, description="联系方式")
    contact_position: str | None = Field(None, max_length=50, description="联系人职位")
    remarks: str | None = Field(None, description="备注")

    @field_validator('phone')
    @classmethod
    def validate_phone(cls, v: str | None) -> str | None:
        if v is None:
            return v

        if not v or not v.strip():
            return None

        phone = v.strip()

        phone_pattern = r'^1[3-9]\d{9}$'
        if not re.match(phone_pattern, phone):
            raise ValueError('请输入有效的手机号码')

        return phone


class CustomerContactResponse(CustomerContactBase):
    id: int
    customer_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
