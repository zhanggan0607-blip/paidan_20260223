import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.database import get_db, Base

SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)


@pytest.fixture
def db():
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


def test_read_root():
    response = client.get("/")
    assert response.status_code == 200
    assert "message" in response.json()


def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_create_project_info(db):
    response = client.post(
        "/api/project-info",
        json={
            "project_id": "TEST-001",
            "project_name": "测试项目",
            "completion_date": "2024-01-01T00:00:00",
            "maintenance_end_date": "2025-12-31T00:00:00",
            "maintenance_period": "每月",
            "client_unit": "测试客户",
            "client_address": "测试地址",
        }
    )
    assert response.status_code == 201
    data = response.json()
    assert data["code"] == 200
    assert data["data"]["project_id"] == "TEST-001"


def test_get_project_info_list(db):
    response = client.get("/api/project-info")
    assert response.status_code == 200
    data = response.json()
    assert data["code"] == 200
    assert "data" in data


def test_get_project_info_by_id(db):
    response = client.post(
        "/api/project-info",
        json={
            "project_id": "TEST-002",
            "project_name": "测试项目2",
            "completion_date": "2024-01-01T00:00:00",
            "maintenance_end_date": "2025-12-31T00:00:00",
            "maintenance_period": "每月",
            "client_unit": "测试客户",
            "client_address": "测试地址",
        }
    )
    created_data = response.json()
    project_id = created_data["data"]["id"]
    
    response = client.get(f"/api/project-info/{project_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["code"] == 200
    assert data["data"]["project_id"] == "TEST-002"


def test_update_project_info(db):
    response = client.post(
        "/api/project-info",
        json={
            "project_id": "TEST-003",
            "project_name": "测试项目3",
            "completion_date": "2024-01-01T00:00:00",
            "maintenance_end_date": "2025-12-31T00:00:00",
            "maintenance_period": "每月",
            "client_unit": "测试客户",
            "client_address": "测试地址",
        }
    )
    created_data = response.json()
    project_id = created_data["data"]["id"]
    
    response = client.put(
        f"/api/project-info/{project_id}",
        json={
            "project_id": "TEST-003",
            "project_name": "更新后的测试项目3",
            "completion_date": "2024-01-01T00:00:00",
            "maintenance_end_date": "2025-12-31T00:00:00",
            "maintenance_period": "每月",
            "client_name": "更新后的测试客户",
            "address": "更新后的测试地址",
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["code"] == 200
    assert data["data"]["project_name"] == "更新后的测试项目3"


def test_delete_project_info(db):
    response = client.post(
        "/api/project-info",
        json={
            "project_id": "TEST-004",
            "project_name": "测试项目4",
            "completion_date": "2024-01-01T00:00:00",
            "maintenance_end_date": "2025-12-31T00:00:00",
            "maintenance_period": "每月",
            "client_unit": "测试客户",
            "client_address": "测试地址",
        }
    )
    created_data = response.json()
    project_id = created_data["data"]["id"]
    
    response = client.delete(f"/api/project-info/{project_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["code"] == 200
    
    response = client.get(f"/api/project-info/{project_id}")
    assert response.status_code == 404
