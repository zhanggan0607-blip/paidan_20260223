from functools import lru_cache
from pathlib import Path

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

ENV_FILE_PATH = Path(__file__).parent.parent / ".env"


class Settings(BaseSettings):
    app_name: str = "SSTCP Maintenance System"
    app_version: str = "2.0.8"
    debug: bool = False
    secret_key: str | None = None

    database_url: str | None = None

    redis_url: str = "redis://localhost:6379/0"
    redis_enabled: bool = True
    redis_cache_ttl: int = 3600

    rate_limit_per_minute: int = 600
    rate_limit_per_hour: int = 10000

    aliyun_access_key_id: str = ""
    aliyun_access_key_secret: str = ""
    aliyun_ocr_region_id: str = "cn-shanghai"

    aliyun_oss_access_key_id: str = ""
    aliyun_oss_access_key_secret: str = ""
    aliyun_oss_endpoint: str = "oss-cn-shanghai.aliyuncs.com"
    aliyun_oss_bucket_name: str = "sstcp-uploads"
    aliyun_oss_cdn_domain: str = ""
    aliyun_oss_enabled: bool = True

    dingtalk_agent_id: str = ""
    dingtalk_app_key: str = ""
    dingtalk_app_secret: str = ""

    api_prefix: str = "/api/v1"
    docs_url: str = "/api/docs"
    redoc_url: str = "/api/redoc"
    openapi_url: str = "/api/openapi.json"
    server_base_url: str = "http://localhost:8000"

    cors_origins: str = "https://www.paidan.sstcp.top,https://paidan.sstcp.top,http://localhost:5173,http://localhost:5180"

    @field_validator('cors_origins', mode='after')
    @classmethod
    def parse_cors_origins(cls, v):
        if v == "*":
            import logging
            logging.getLogger(__name__).warning("CORS_ORIGINS 设置为 '*'，允许所有来源访问，仅建议在开发环境使用！")
            return ["*"]
        if isinstance(v, str):
            origins = [origin.strip() for origin in v.split(',')]
            for origin in origins:
                if origin.startswith('http://') and origin not in ('http://localhost:5173', 'http://localhost:5180', 'http://localhost:8000', 'http://localhost:3000'):
                    import logging
                    logging.getLogger(__name__).warning(f"CORS 包含不安全的 HTTP 源: {origin}，生产环境建议仅使用 HTTPS")
            return origins
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
        extra = 'ignore'


class OverdueAlertConfig:
    VALID_STATUSES: list[str] = ['执行中', '待确认', '已退回']
    COMPLETED_STATUSES: list[str] = ['已完成']

    @classmethod
    def get_valid_statuses(cls) -> list[str]:
        return cls.VALID_STATUSES

    @classmethod
    def get_completed_statuses(cls) -> list[str]:
        return cls.COMPLETED_STATUSES

    @classmethod
    def is_completed(cls, status: str) -> bool:
        return status in cls.COMPLETED_STATUSES


class PersonnelConfig:
    VALID_ROLES: list[str] = ['管理员', '部门经理', '材料员', '运维人员']

    @classmethod
    def get_valid_roles(cls) -> list[str]:
        return cls.VALID_ROLES


@lru_cache
def get_settings() -> Settings:
    return Settings()

