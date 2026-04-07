import re
from datetime import datetime

from pydantic import BaseModel, Field, field_validator

from app.schemas.customer_contact import (
    CustomerContactCreate,
    CustomerContactResponse,
    CustomerContactUpdate,
)


class CustomerBase(BaseModel):
    name: str = Field(..., max_length=100, description="客户单位")
    address: str | None = Field(None, max_length=200, description="客户地址")
    remarks: str | None = Field(None, description="备注")


class CustomerCreate(CustomerBase):
    contacts: list[CustomerContactCreate] | None = Field(None, description="联系人列表")

    @field_validator('contacts', mode='before')
    @classmethod
    def validate_contacts(cls, v):
        if v is None:
            return []
        return v


class CustomerUpdate(BaseModel):
    name: str | None = Field(None, max_length=100, description="客户单位")
    address: str | None = Field(None, max_length=200, description="客户地址")
    remarks: str | None = Field(None, description="备注")
    contacts: list[CustomerContactCreate] | None = Field(None, description="联系人列表（完整替换）")


class CustomerResponse(CustomerBase):
    id: int
    contact_person: str | None = None
    phone: str | None = None
    contact_position: str | None = None
    contacts: list[CustomerContactResponse] = []
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
