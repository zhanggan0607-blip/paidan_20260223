"""
测试认证功能
"""
import pytest
from fastapi.testclient import TestClient


class TestAuth:
    """
    认证测试类
    """

    def test_login_missing_credentials(self, client: TestClient):
        """
        测试缺少凭证的登录
        """
        response = client.post("/api/v1/auth/login", json={})
        assert response.status_code == 422

    def test_login_invalid_user(self, client: TestClient):
        """
        测试无效用户登录
        """
        response = client.post(
            "/api/v1/auth/login",
            json={"username": "nonexistent", "password": "wrongpassword"}
        )
        assert response.status_code in [401, 400, 404, 422]

    def test_me_without_token(self, client: TestClient):
        """
        测试无 token 访问用户信息
        """
        response = client.get("/api/v1/auth/me")
        assert response.status_code == 401
