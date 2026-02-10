from pydantic_settings import BaseSettings
from pydantic import field_validator
from functools import lru_cache
from typing import List
import os


class Settings(BaseSettings):
    app_name: str = "SSTCP Maintenance System"
    app_version: str = "1.0.0"
    debug: bool = os.getenv("DEBUG", "False").lower() in ("true", "1")
    secret_key: str = os.getenv("SECRET_KEY", "your-secret-key-here-change-in-production")
    
    database_url: str = os.getenv(
        "DATABASE_URL",
        "postgresql://postgres:changeme@localhost:5432/tq"
    )
    
    api_prefix: str = "/api/v1"
    docs_url: str = "/docs"
    redoc_url: str = "/redoc"
    openapi_url: str = "/openapi.json"
    
    cors_origins: str = "http://localhost:3000,http://localhost:4173"
    
    page_size: int = 10
    max_page_size: int = 100
    
    @field_validator('cors_origins', mode='after')
    @classmethod
    def parse_cors_origins(cls, v):
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(',')]
        return v
    
    class Config:
        env_file = ".env"
        case_sensitive = False


class OverdueAlertConfig:
    VALID_STATUSES: List[str] = ['未确认', '未下发', '未进行', '进行中', '待确认', '已退回']
    WORK_ORDER_TYPES: List[str] = ['定期巡检', '临时维修', '零星用工']
    OVERDUE_THRESHOLD_DAYS: int = 1
    
    @classmethod
    def get_valid_statuses(cls) -> List[str]:
        return cls.VALID_STATUSES
    
    @classmethod
    def get_work_order_types(cls) -> List[str]:
        return cls.WORK_ORDER_TYPES
    
    @classmethod
    def get_overdue_threshold_days(cls) -> int:
        return cls.OVERDUE_THRESHOLD_DAYS
    
    @classmethod
    def set_overdue_threshold_days(cls, days: int):
        if days < 0:
            raise ValueError("超期天数阈值必须大于等于 0")
        cls.OVERDUE_THRESHOLD_DAYS = days
    
    @classmethod
    def add_valid_status(cls, status: str):
        if status not in cls.VALID_STATUSES:
            cls.VALID_STATUSES.append(status)
    
    @classmethod
    def remove_valid_status(cls, status: str):
        if status in cls.VALID_STATUSES:
            cls.VALID_STATUSES.remove(status)
    
    @classmethod
    def add_work_order_type(cls, work_order_type: str):
        if work_order_type not in cls.WORK_ORDER_TYPES:
            cls.WORK_ORDER_TYPES.append(work_order_type)
    
    @classmethod
    def remove_work_order_type(cls, work_order_type: str):
        if work_order_type in cls.WORK_ORDER_TYPES:
            cls.WORK_ORDER_TYPES.remove(work_order_type)


class PersonnelConfig:
    VALID_ROLES: List[str] = ['管理员', '部门经理', '材料员', '员工']
    
    @classmethod
    def get_valid_roles(cls) -> List[str]:
        return cls.VALID_ROLES
    
    @classmethod
    def add_valid_role(cls, role: str):
        if role not in cls.VALID_ROLES:
            cls.VALID_ROLES.append(role)
    
    @classmethod
    def remove_valid_role(cls, role: str):
        if role in cls.VALID_ROLES:
            cls.VALID_ROLES.remove(role)


@lru_cache()
def get_settings() -> Settings:
    return Settings()
