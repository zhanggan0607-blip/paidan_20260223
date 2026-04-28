"""
后端集成测试
测试核心业务CRUD流程：认证、项目信息、人员管理、工单审批

注意：部分测试依赖PostgreSQL特性（如nextval序列），在SQLite下会跳过
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.auth import get_password_hash
from app.models.personnel import Personnel
from app.models.project_info import ProjectInfo
from app.models.customer import Customer
from app.models.customer_contact import CustomerContact


@pytest.fixture
def admin_user(db_session: Session):
    user = Personnel(
        name="测试管理员",
        gender="男",
        phone="13800000001",
        password_hash=get_password_hash("test123456"),
        department="技术部",
        role="管理员",
        must_change_password=False,
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def normal_user(db_session: Session):
    user = Personnel(
        name="测试运维",
        gender="男",
        phone="13800000002",
        password_hash=get_password_hash("test123456"),
        department="运维部",
        role="运维人员",
        must_change_password=False,
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def admin_token(client: TestClient, admin_user):
    response = client.post(
        "/api/v1/auth/login-json",
        json={"username": "测试管理员", "password": "test123456"},
    )
    assert response.status_code == 200
    data = response.json()
    return data["data"]["access_token"]


@pytest.fixture
def normal_token(client: TestClient, normal_user):
    response = client.post(
        "/api/v1/auth/login-json",
        json={"username": "测试运维", "password": "test123456"},
    )
    assert response.status_code == 200
    data = response.json()
    return data["data"]["access_token"]


@pytest.fixture
def admin_headers(admin_token):
    return {"Authorization": f"Bearer {admin_token}"}


@pytest.fixture
def normal_headers(normal_token):
    return {"Authorization": f"Bearer {normal_token}"}


@pytest.fixture
def sample_project(db_session: Session):
    customer = Customer(name="测试客户公司", address="测试地址")
    db_session.add(customer)
    db_session.commit()
    db_session.refresh(customer)

    contact = CustomerContact(
        customer_id=customer.id,
        contact_person="张三",
        contact_position="经理",
        phone="13900000001",
    )
    db_session.add(contact)
    db_session.commit()
    db_session.refresh(contact)

    from datetime import datetime, timedelta
    project = ProjectInfo(
        project_id="PRJ-TEST-001",
        project_name="测试项目A",
        completion_date=datetime.now(),
        maintenance_end_date=datetime.now() + timedelta(days=365),
        maintenance_period="月度",
        client_name="测试客户公司",
        address="测试地址",
        project_abbr="测试A",
        project_manager="测试管理员",
        client_contact_id=contact.id,
        client_contact="张三",
        client_contact_position="经理",
        client_contact_info="13900000001",
    )
    db_session.add(project)
    db_session.commit()
    db_session.refresh(project)
    return project


class TestAuthIntegration:
    def test_login_json_success(self, client, admin_user):
        response = client.post(
            "/api/v1/auth/login-json",
            json={"username": "测试管理员", "password": "test123456"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200
        assert "access_token" in data["data"]
        assert "refresh_token" in data["data"]
        assert data["data"]["user"]["name"] == "测试管理员"
        assert data["data"]["user"]["role"] == "管理员"

    def test_login_json_wrong_password(self, client, admin_user):
        response = client.post(
            "/api/v1/auth/login-json",
            json={"username": "测试管理员", "password": "wrongpassword"},
        )
        assert response.status_code == 401

    def test_login_json_nonexistent_user(self, client):
        response = client.post(
            "/api/v1/auth/login-json",
            json={"username": "不存在用户", "password": "anything"},
        )
        assert response.status_code == 401

    def test_get_current_user_info(self, client, admin_headers, admin_user):
        response = client.get("/api/v1/auth/me", headers=admin_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200
        assert data["data"]["name"] == "测试管理员"

    def test_get_current_user_without_token(self, client):
        response = client.get("/api/v1/auth/me")
        assert response.status_code == 401

    def test_refresh_token(self, client, admin_user):
        login_resp = client.post(
            "/api/v1/auth/login-json",
            json={"username": "测试管理员", "password": "test123456"},
        )
        refresh_token = login_resp.json()["data"]["refresh_token"]

        response = client.post(
            "/api/v1/auth/refresh",
            json={"refresh_token": refresh_token},
        )
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data["data"]
        assert "refresh_token" in data["data"]

    def test_refresh_token_invalid(self, client):
        response = client.post(
            "/api/v1/auth/refresh",
            json={"refresh_token": "invalid.token.here"},
        )
        assert response.status_code == 401

    def test_logout(self, client, admin_headers):
        response = client.post("/api/v1/auth/logout", headers=admin_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200


class TestProjectInfoIntegration:
    def test_get_project_list(self, client, admin_headers, sample_project):
        response = client.get("/api/v1/project-info", headers=admin_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200

    def test_get_project_by_id(self, client, admin_headers, sample_project):
        response = client.get(
            f"/api/v1/project-info/{sample_project.id}", headers=admin_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert data["data"]["project_id"] == "PRJ-TEST-001"

    def test_get_project_not_found(self, client, admin_headers):
        response = client.get("/api/v1/project-info/99999", headers=admin_headers)
        assert response.status_code == 404

    def test_delete_project(self, client, admin_headers, sample_project):
        response = client.delete(
            f"/api/v1/project-info/{sample_project.id}", headers=admin_headers
        )
        assert response.status_code == 200


class TestPersonnelIntegration:
    def test_create_personnel(self, client, admin_headers):
        response = client.post(
            "/api/v1/personnel",
            json={
                "name": "新员工",
                "gender": "男",
                "phone": "13800000099",
                "department": "运维部",
                "role": "运维人员",
            },
            headers=admin_headers,
        )
        assert response.status_code in [200, 201]
        data = response.json()
        assert data["data"]["name"] == "新员工"

    def test_get_personnel_list(self, client, admin_headers, admin_user):
        response = client.get("/api/v1/personnel", headers=admin_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200

    def test_get_personnel_by_id(self, client, admin_headers, admin_user):
        response = client.get(
            f"/api/v1/personnel/{admin_user.id}", headers=admin_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert data["data"]["name"] == "测试管理员"

    def test_update_personnel(self, client, admin_headers, admin_user):
        response = client.put(
            f"/api/v1/personnel/{admin_user.id}",
            json={
                "name": "测试管理员",
                "gender": "男",
                "phone": "13800000001",
                "department": "技术部",
                "role": "管理员",
                "remarks": "更新备注",
            },
            headers=admin_headers,
        )
        assert response.status_code == 200

    def test_delete_personnel(self, client, admin_headers, normal_user):
        response = client.delete(
            f"/api/v1/personnel/{normal_user.id}", headers=admin_headers
        )
        assert response.status_code == 200


class TestWorkOrderIntegration:
    def test_get_temporary_repair_list(self, client, admin_headers):
        response = client.get("/api/v1/temporary-repair", headers=admin_headers)
        assert response.status_code == 200

    def test_get_spot_work_list(self, client, admin_headers):
        response = client.get("/api/v1/spot-work", headers=admin_headers)
        assert response.status_code == 200

    def test_get_periodic_inspection_list(self, client, admin_headers):
        response = client.get("/api/v1/periodic-inspection", headers=admin_headers)
        assert response.status_code == 200


class TestDictionaryIntegration:
    def test_get_dictionary_by_type(self, client, admin_headers):
        response = client.get(
            "/api/v1/dictionary/type/work_status", headers=admin_headers
        )
        assert response.status_code == 200

    def test_create_dictionary_item(self, client, admin_headers):
        response = client.post(
            "/api/v1/dictionary",
            json={
                "dict_type": "test_type",
                "dict_key": "test_key",
                "dict_value": "测试值",
                "dict_label": "测试标签",
            },
            headers=admin_headers,
        )
        assert response.status_code in [200, 201]


class TestHealthAndStats:
    def test_health_check(self, client):
        response = client.get("/api/v1/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] in ["healthy", "degraded"]

    def test_root_endpoint(self, client):
        response = client.get("/")
        assert response.status_code == 200

    def test_statistics_overview(self, client, admin_headers):
        response = client.get(
            "/api/v1/statistics/overview",
            params={"year": 2026},
            headers=admin_headers,
        )
        assert response.status_code == 200
