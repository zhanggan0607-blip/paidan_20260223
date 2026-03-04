"""
测试健康检查端点
"""
import pytest
from fastapi.testclient import TestClient


class TestHealth:
    """
    健康检查测试类
    """

    def test_health_check(self, client: TestClient):
        """
        测试健康检查端点
        """
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data.get("status") == "healthy"

    def test_api_docs(self, client: TestClient):
        """
        测试 API 文档端点
        """
        response = client.get("/api/docs")
        assert response.status_code == 200

    def test_root_endpoint(self, client: TestClient):
        """
        测试根端点
        """
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "version" in data
