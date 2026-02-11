import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.database import get_db
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models.personnel import Personnel
from app.models.project_info import ProjectInfo

SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)


@pytest.fixture(scope="module")
def test_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}


def test_create_personnel(test_db):
    response = client.post(
        "/api/v1/personnel",
        json={
            "name": "张三",
            "gender": "男",
            "phone": "13800138000",
            "department": "技术部",
            "role": "管理员",
            "address": "北京市",
            "remarks": "测试人员"
        }
    )
    assert response.status_code == 201
    data = response.json()
    assert data["code"] == 200
    assert data["data"]["name"] == "张三"


def test_get_personnel_list(test_db):
    response = client.get("/api/v1/personnel?page=0&size=10")
    assert response.status_code == 200
    data = response.json()
    assert data["code"] == 200
    assert "data" in data


def test_create_project_info(test_db):
    response = client.post(
        "/api/v1/project-info",
        json={
            "project_id": "P001",
            "project_name": "测试项目",
            "completion_date": "2024-01-01T00:00:00",
            "maintenance_end_date": "2024-12-31T00:00:00",
            "maintenance_period": "每月",
            "client_name": "测试客户",
            "address": "北京市朝阳区",
            "project_abbr": "TP",
            "client_contact": "张三",
            "client_contact_position": "经理",
            "client_contact_info": "13800138000"
        }
    )
    assert response.status_code == 201
    data = response.json()
    assert data["code"] == 200
    assert data["data"]["project_name"] == "测试项目"


def test_get_project_info_list(test_db):
    response = client.get("/api/v1/project-info?page=0&size=10")
    assert response.status_code == 200
    data = response.json()
    assert data["code"] == 200
    assert "data" in data