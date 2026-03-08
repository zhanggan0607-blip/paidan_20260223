import os
from functools import lru_cache
from pathlib import Path

from pydantic import field_validator
from pydantic_settings import BaseSettings

ENV_FILE_PATH = Path(__file__).parent.parent / ".env"


class Settings(BaseSettings):
    app_name: str = "SSTCP Maintenance System"
    app_version: str = "1.0.0"
    debug: bool = os.getenv("DEBUG", "False").lower() in ("true", "1")
    secret_key: str | None = None
    port: int = 8000

    database_url: str | None = None

    aliyun_access_key_id: str = os.getenv("ALIYUN_ACCESS_KEY_ID", "")
    aliyun_access_key_secret: str = os.getenv("ALIYUN_ACCESS_KEY_SECRET", "")
    aliyun_ocr_region_id: str = os.getenv("ALIYUN_OCR_REGION_ID", "cn-shanghai")

    dingtalk_agent_id: str = os.getenv("DINGTALK_AGENT_ID", "")
    dingtalk_app_key: str = os.getenv("DINGTALK_APP_KEY", "")
    dingtalk_app_secret: str = os.getenv("DINGTALK_APP_SECRET", "")

    api_prefix: str = "/api/v1"
    docs_url: str = "/api/docs"
    redoc_url: str = "/api/redoc"
    openapi_url: str = "/api/openapi.json"

    cors_origins: str = "*"

    page_size: int = 10
    max_page_size: int = 1000

    @field_validator('cors_origins', mode='after')
    @classmethod
    def parse_cors_origins(cls, v):
        if v == "*":
            return ["*"]
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(',')]
        return v

    @field_validator('secret_key', mode='after')
    @classmethod
    def validate_secret_key(cls, v):
        if not v:
            raise ValueError("SECRET_KEY 环境变量未设置，请在 .env 文件中配置 SECRET_KEY")
        if v == "your-secret-key-here-change-in-production":
            raise ValueError("SECRET_KEY 使用了不安全的默认值，请生成新的密钥 (可使用: openssl rand -hex 32)")
        return v

    @field_validator('database_url', mode='after')
    @classmethod
    def validate_database_url(cls, v):
        if not v:
            raise ValueError("DATABASE_URL 环境变量未设置，请在 .env 文件中配置数据库连接")
        return v

    class Config:
        env_file = str(ENV_FILE_PATH)
        case_sensitive = False


class OverdueAlertConfig:
    VALID_STATUSES: list[str] = ['执行中', '待确认', '已退回']
    COMPLETED_STATUSES: list[str] = ['已完成']
    WORK_ORDER_TYPES: list[str] = ['定期巡检', '临时维修', '零星用工', '维保计划']
    OVERDUE_THRESHOLD_DAYS: int = 0

    @classmethod
    def get_valid_statuses(cls) -> list[str]:
        return cls.VALID_STATUSES

    @classmethod
    def get_completed_statuses(cls) -> list[str]:
        return cls.COMPLETED_STATUSES

    @classmethod
    def is_completed(cls, status: str) -> bool:
        return status in cls.COMPLETED_STATUSES

    @classmethod
    def get_work_order_types(cls) -> list[str]:
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
    VALID_ROLES: list[str] = ['管理员', '部门经理', '材料员', '运维人员']

    @classmethod
    def get_valid_roles(cls) -> list[str]:
        return cls.VALID_ROLES

    @classmethod
    def add_valid_role(cls, role: str):
        if role not in cls.VALID_ROLES:
            cls.VALID_ROLES.append(role)

    @classmethod
    def remove_valid_role(cls, role: str):
        if role in cls.VALID_ROLES:
            cls.VALID_ROLES.remove(role)


@lru_cache
def get_settings() -> Settings:
    return Settings()
