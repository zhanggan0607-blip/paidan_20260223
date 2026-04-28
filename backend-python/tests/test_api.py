"""
API 端点测试
测试主要的 API 端点功能
"""
import pytest
from fastapi.testclient import TestClient


class TestHealthEndpoint:
    """健康检查端点测试"""

    def test_health_check_returns_healthy(self, client: TestClient):
        """测试健康检查返回正常状态"""
        response = client.get("/api/v1/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] in ["healthy", "degraded"]
        assert "timestamp" in data
        assert "version" in data

    def test_root_endpoint(self, client: TestClient):
        """测试根路径"""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "version" in data


class TestAuthEndpoint:
    """认证端点测试"""

    def test_login_with_invalid_credentials(self, client: TestClient):
        """测试无效凭据登录"""
        response = client.post(
            "/api/v1/auth/login",
            data={"username": "invalid", "password": "invalid"},
        )
        assert response.status_code == 401

    def test_protected_endpoint_without_token(self, client: TestClient):
        """测试无 token 访问受保护端点（personnel详情需要认证）"""
        response = client.get("/api/v1/personnel/99999")
        assert response.status_code in [401, 404]

    def test_protected_endpoint_with_valid_token(self, client: TestClient, auth_headers: dict):
        """测试有效 token 访问受保护端点"""
        response = client.get("/api/v1/personnel", headers=auth_headers)
        assert response.status_code == 200


class TestPersonnelEndpoint:
    """人员管理端点测试"""

    def test_get_personnel_list(self, client: TestClient, auth_headers: dict):
        """测试获取人员列表"""
        response = client.get("/api/v1/personnel", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert "code" in data
        assert data["code"] == 200

    def test_create_personnel_requires_admin(self, client: TestClient, normal_user_headers: dict):
        """测试创建人员需要管理员权限"""
        response = client.post(
            "/api/v1/personnel",
            json={"name": "测试人员", "role": "运维人员"},
            headers=normal_user_headers,
        )
        assert response.status_code == 403


class TestProjectInfoEndpoint:
    """项目信息端点测试"""

    def test_get_project_list(self, client: TestClient, auth_headers: dict):
        """测试获取项目列表"""
        response = client.get("/api/v1/project-info", headers=auth_headers)
        assert response.status_code == 200

    def test_get_project_by_id_not_found(self, client: TestClient, auth_headers: dict):
        """测试获取不存在的项目"""
        response = client.get("/api/v1/project-info/99999", headers=auth_headers)
        assert response.status_code == 404


class TestMaintenancePlanEndpoint:
    """维保计划端点测试"""

    def test_get_maintenance_plan_list(self, client: TestClient, auth_headers: dict):
        """测试获取维保计划列表"""
        response = client.get("/api/v1/maintenance-plan", headers=auth_headers)
        assert response.status_code == 200

    def test_create_maintenance_plan_validation(self, client: TestClient, auth_headers: dict):
        """测试创建维保计划数据验证"""
        response = client.post(
            "/api/v1/maintenance-plan",
            json={},
            headers=auth_headers,
        )
        assert response.status_code == 422
