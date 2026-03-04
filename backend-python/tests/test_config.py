"""
测试配置验证
"""
import pytest
import os
from pydantic import ValidationError

from app.config import Settings


class TestConfig:
    """
    配置测试类
    """

    def test_settings_valid_with_env_vars(self):
        """
        测试有效的配置（环境变量已设置）
        """
        os.environ["SECRET_KEY"] = "test-secret-key-for-testing-12345678"
        os.environ["DATABASE_URL"] = "postgresql://test:test@localhost/test"
        
        settings = Settings()
        assert settings.secret_key == "test-secret-key-for-testing-12345678"
        assert settings.database_url == "postgresql://test:test@localhost/test"

    def test_settings_rejects_insecure_secret_key(self):
        """
        测试拒绝不安全的默认 SECRET_KEY
        """
        original_key = os.environ.get("SECRET_KEY")
        original_db = os.environ.get("DATABASE_URL")
        
        try:
            os.environ["SECRET_KEY"] = "your-secret-key-here-change-in-production"
            os.environ["DATABASE_URL"] = "postgresql://test:test@localhost/test"
            
            with pytest.raises(ValidationError) as exc_info:
                Settings()
            
            errors = exc_info.value.errors()
            insecure_error = any(
                "不安全" in str(error) for error in errors
            )
            assert insecure_error, "应该拒绝不安全的默认密钥"
        finally:
            if original_key:
                os.environ["SECRET_KEY"] = original_key
            if original_db:
                os.environ["DATABASE_URL"] = original_db

    def test_cors_origins_parsing(self):
        """
        测试 CORS 源解析
        """
        os.environ["SECRET_KEY"] = "test-secret-key-for-testing-12345678"
        os.environ["DATABASE_URL"] = "postgresql://test:test@localhost/test"
        os.environ["CORS_ORIGINS"] = "http://localhost:3000,http://localhost:8080"
        
        settings = Settings()
        assert "http://localhost:3000" in settings.cors_origins
        assert "http://localhost:8080" in settings.cors_origins

    def test_cors_origins_wildcard(self):
        """
        测试 CORS 通配符
        """
        os.environ["SECRET_KEY"] = "test-secret-key-for-testing-12345678"
        os.environ["DATABASE_URL"] = "postgresql://test:test@localhost/test"
        os.environ["CORS_ORIGINS"] = "*"
        
        settings = Settings()
        assert settings.cors_origins == ["*"]
