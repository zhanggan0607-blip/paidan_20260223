from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from app.schemas.common import ApiResponse, PaginatedResponse


class SpotWorkWorkerBase(BaseModel):
    spot_work_id: Optional[int] = Field(None, description="关联用工单ID")
    project_id: str = Field(..., max_length=50, description="项目编号")
    project_name: Optional[str] = Field(None, max_length=200, description="项目名称")
    start_date: Optional[datetime] = Field(None, description="开始日期")
    end_date: Optional[datetime] = Field(None, description="结束日期")
    name: str = Field(..., max_length=50, description="姓名")
    gender: Optional[str] = Field(None, max_length=10, description="性别")
    birth_date: Optional[str] = Field(None, max_length=20, description="出生日期")
    address: Optional[str] = Field(None, max_length=200, description="住址")
    id_card_number: Optional[str] = Field(None, max_length=18, description="身份证号码")
    issuing_authority: Optional[str] = Field(None, max_length=100, description="签发机关")
    valid_period: Optional[str] = Field(None, max_length=50, description="有效期限")
    id_card_front: Optional[str] = Field(None, max_length=500, description="身份证正面照片URL")
    id_card_back: Optional[str] = Field(None, max_length=500, description="身份证反面照片URL")


class SpotWorkWorkerCreate(BaseModel):
    spot_work_id: Optional[int] = Field(None, description="关联用工单ID")
    project_id: str = Field(..., max_length=50, description="项目编号")
    project_name: Optional[str] = Field(None, max_length=200, description="项目名称")
    start_date: Optional[datetime] = Field(None, description="开始日期")
    end_date: Optional[datetime] = Field(None, description="结束日期")
    name: str = Field(..., max_length=50, description="姓名")
    gender: Optional[str] = Field(None, max_length=10, description="性别")
    birth_date: Optional[str] = Field(None, max_length=20, description="出生日期")
    address: Optional[str] = Field(None, max_length=200, description="住址")
    id_card_number: Optional[str] = Field(None, max_length=18, description="身份证号码")
    issuing_authority: Optional[str] = Field(None, max_length=100, description="签发机关")
    valid_period: Optional[str] = Field(None, max_length=50, description="有效期限")
    id_card_front: Optional[str] = Field(None, max_length=500, description="身份证正面照片URL")
    id_card_back: Optional[str] = Field(None, max_length=500, description="身份证反面照片URL")


class SpotWorkWorkerUpdate(BaseModel):
    spot_work_id: Optional[int] = Field(None, description="关联用工单ID")
    project_id: str = Field(..., max_length=50, description="项目编号")
    project_name: Optional[str] = Field(None, max_length=200, description="项目名称")
    start_date: Optional[datetime] = Field(None, description="开始日期")
    end_date: Optional[datetime] = Field(None, description="结束日期")
    name: str = Field(..., max_length=50, description="姓名")
    gender: Optional[str] = Field(None, max_length=10, description="性别")
    birth_date: Optional[str] = Field(None, max_length=20, description="出生日期")
    address: Optional[str] = Field(None, max_length=200, description="住址")
    id_card_number: Optional[str] = Field(None, max_length=18, description="身份证号码")
    issuing_authority: Optional[str] = Field(None, max_length=100, description="签发机关")
    valid_period: Optional[str] = Field(None, max_length=50, description="有效期限")
    id_card_front: Optional[str] = Field(None, max_length=500, description="身份证正面照片URL")
    id_card_back: Optional[str] = Field(None, max_length=500, description="身份证反面照片URL")


class SpotWorkWorkerResponse(BaseModel):
    id: int
    spot_work_id: Optional[int]
    project_id: str
    project_name: Optional[str]
    start_date: Optional[datetime]
    end_date: Optional[datetime]
    name: str
    gender: Optional[str]
    birth_date: Optional[str]
    address: Optional[str]
    id_card_number: Optional[str]
    issuing_authority: Optional[str]
    valid_period: Optional[str]
    id_card_front: Optional[str]
    id_card_back: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
