"""
测试配置文件
"""
import pytest
import os
from typing import Generator
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base, get_db


SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    """
    覆盖数据库依赖
    """
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


def create_test_app():
    """
    创建测试应用
    """
    from fastapi import FastAPI
    from fastapi.middleware.cors import CORSMiddleware
    from app.config import get_settings
    from app.api.v1 import auth
    from app.exceptions import BusinessException
    from fastapi.responses import JSONResponse
    from fastapi.exceptions import RequestValidationError
    from starlette.exceptions import HTTPException as StarletteHTTPException
    
    settings = get_settings()
    
    test_app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        docs_url=settings.docs_url,
        redoc_url=settings.redoc_url,
        openapi_url=settings.openapi_url,
    )
    
    test_app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],
        allow_headers=["Content-Type", "Authorization", "X-User-Name", "X-User-Role"],
    )
    
    test_app.include_router(auth.router, prefix=settings.api_prefix)
    
    @test_app.get("/")
    def read_root():
        return {
            "message": "SSTCP Maintenance System API",
            "version": settings.app_version,
        }
    
    @test_app.get("/health")
    def health_check():
        return {"status": "healthy"}
    
    @test_app.exception_handler(BusinessException)
    async def business_exception_handler(request, exc):
        return JSONResponse(
            status_code=exc.code,
            content={"code": exc.code, "message": exc.message, "data": None},
        )
    
    @test_app.exception_handler(StarletteHTTPException)
    async def http_exception_handler(request, exc):
        return JSONResponse(
            status_code=exc.status_code,
            content={"code": exc.status_code, "message": exc.detail, "data": None},
        )
    
    @test_app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request, exc):
        errors = []
        for error in exc.errors():
            errors.append({
                "field": ".".join(str(x) for x in error["loc"]),
                "message": error["msg"],
                "type": error["type"],
            })
        return JSONResponse(
            status_code=422,
            content={"code": 422, "message": "参数验证失败", "data": {"errors": errors}},
        )
    
    return test_app


@pytest.fixture(scope="session", autouse=True)
def setup_test_env():
    """
    设置测试环境变量
    """
    os.environ["SECRET_KEY"] = "test-secret-key-for-testing-12345678"
    os.environ["DATABASE_URL"] = "sqlite:///./test.db"


@pytest.fixture(scope="function")
def db_session() -> Generator:
    """
    创建数据库会话
    """
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client() -> Generator:
    """
    创建测试客户端
    """
    test_app = create_test_app()
    test_app.dependency_overrides[get_db] = override_get_db
    with TestClient(test_app) as c:
        yield c


@pytest.fixture(scope="function")
def test_user_data():
    """
    测试用户数据
    """
    return {
        "username": "testuser",
        "password": "testpassword123",
        "name": "测试用户",
        "role": "运维人员"
    }


@pytest.fixture(scope="function")
def test_admin_data():
    """
    测试管理员数据
    """
    return {
        "username": "admin",
        "password": "adminpassword123",
        "name": "管理员",
        "role": "管理员"
    }
