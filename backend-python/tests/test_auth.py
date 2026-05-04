"""
认证模块测试
测试JWT Token生成/验证、Token黑名单、暴力破解防护
"""
import time
import pytest
from app.auth import (
    create_access_token,
    create_refresh_token,
    verify_refresh_token,
    verify_password,
    get_password_hash,
    add_token_to_blacklist,
    is_token_blacklisted,
    clear_memory_blacklist,
    ACCESS_TOKEN_EXPIRE_MINUTES,
)
from app.services.auth import (
    check_login_lockout,
    record_login_failure,
    clear_login_failures,
    MAX_LOGIN_ATTEMPTS,
    LOGIN_LOCKOUT_SECONDS,
)


class TestPasswordHashing:
    def test_hash_and_verify(self):
        password = "TestPassword123"
        hashed = get_password_hash(password)
        assert verify_password(password, hashed)

    def test_wrong_password_fails(self):
        hashed = get_password_hash("correct")
        assert not verify_password("wrong", hashed)

    def test_long_password_truncation(self):
        long_password = "a" * 100
        hashed = get_password_hash(long_password)
        assert verify_password(long_password, hashed)

    def test_different_hashes_for_same_password(self):
        password = "same_password"
        hash1 = get_password_hash(password)
        hash2 = get_password_hash(password)
        assert hash1 != hash2


class TestAccessToken:
    def test_create_access_token(self):
        data = {"sub": "test_user", "role": "管理员", "user_id": 1}
        token = create_access_token(data)
        assert isinstance(token, str)
        assert len(token) > 0

    def test_access_token_contains_jti(self):
        from jose import jwt
        from app.config import get_settings
        data = {"sub": "test_user", "role": "管理员", "user_id": 1}
        token = create_access_token(data)
        payload = jwt.decode(token, get_settings().secret_key, algorithms=["HS256"])
        assert "jti" in payload
        assert payload["type"] == "access"

    def test_access_token_expiry(self):
        from jose import jwt
        from app.config import get_settings
        data = {"sub": "test_user", "role": "管理员", "user_id": 1}
        token = create_access_token(data)
        payload = jwt.decode(token, get_settings().secret_key, algorithms=["HS256"])
        assert "exp" in payload


class TestRefreshToken:
    def test_create_refresh_token(self):
        data = {"sub": "test_user", "role": "管理员", "user_id": 1}
        token = create_refresh_token(data)
        assert isinstance(token, str)

    def test_verify_valid_refresh_token(self):
        data = {"sub": "test_user", "role": "管理员", "user_id": 1}
        token = create_refresh_token(data)
        payload = verify_refresh_token(token)
        assert payload is not None
        assert payload["sub"] == "test_user"
        assert payload["type"] == "refresh"

    def test_verify_access_token_as_refresh_fails(self):
        data = {"sub": "test_user", "role": "管理员", "user_id": 1}
        token = create_access_token(data)
        payload = verify_refresh_token(token)
        assert payload is None

    def test_verify_invalid_token_fails(self):
        payload = verify_refresh_token("invalid.token.here")
        assert payload is None


class TestTokenBlacklist:
    def setup_method(self):
        clear_memory_blacklist()

    def test_add_and_check_blacklist(self):
        import uuid
        jti = f"test-jti-{uuid.uuid4().hex[:12]}"
        add_token_to_blacklist(jti, exp_seconds=3600)
        assert is_token_blacklisted(jti)

    def test_non_blacklisted_token_passes(self):
        jti = "non-blacklisted-jti"
        assert not is_token_blacklisted(jti)

    def test_empty_jti_not_blacklisted(self):
        assert not is_token_blacklisted("")
        assert not is_token_blacklisted(None)

    def test_blacklisted_refresh_token_fails_verification(self):
        data = {"sub": "test_user", "role": "管理员", "user_id": 1}
        token = create_refresh_token(data)
        from jose import jwt
        from app.config import get_settings
        payload = jwt.decode(token, get_settings().secret_key, algorithms=["HS256"])
        jti = payload.get("jti")
        add_token_to_blacklist(jti, 3600)
        result = verify_refresh_token(token)
        assert result is None


class TestLoginLockout:
    def setup_method(self):
        clear_login_failures("test_user_lockout")

    def teardown_method(self):
        clear_login_failures("test_user_lockout")

    def test_no_lockout_initially(self):
        result = check_login_lockout("test_user_lockout")
        assert result is None

    def test_lockout_after_max_attempts(self):
        for _ in range(MAX_LOGIN_ATTEMPTS):
            record_login_failure("test_user_lockout")
        result = check_login_lockout("test_user_lockout")
        assert result is not None
        assert result > 0

    def test_clear_failures_resets_lockout(self):
        for _ in range(MAX_LOGIN_ATTEMPTS):
            record_login_failure("test_user_lockout")
        clear_login_failures("test_user_lockout")
        result = check_login_lockout("test_user_lockout")
        assert result is None
