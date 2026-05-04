"""
测试配置模块
提供测试用的数据库会话、客户端和工具函数
"""
import asyncio
from typing import AsyncGenerator, Generator

import pytest
import pytest_asyncio
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, Integer, JSON
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base, get_db
from app.main import app

SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)


for table in Base.metadata.sorted_tables:
    for column in table.columns:
        if column.type.__class__.__name__ == "BigInteger" and column.autoincrement:
            column.type = Integer()
            column._is_autoincrement = True
        col_type_name = column.type.__class__.__name__
        if col_type_name == "JSONB":
            column.type = JSON()

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    """覆盖数据库依赖"""
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(scope="function")
def db_session() -> Generator:
    """创建测试数据库会话"""
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db_session) -> TestClient:
    """创建测试客户端"""
    return TestClient(app)


@pytest_asyncio.fixture
async def async_client() -> AsyncGenerator:
    """创建异步测试客户端"""
    from httpx import AsyncClient
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac


@pytest.fixture(scope="session")
def event_loop():
    """创建事件循环"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def auth_headers() -> dict:
    """获取认证头"""
    from app.auth import create_access_token
    
    token = create_access_token({"sub": "test_user", "role": "管理员"})
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def normal_user_headers() -> dict:
    """获取普通用户认证头"""
    from app.auth import create_access_token
    
    token = create_access_token({"sub": "normal_user", "role": "运维人员"})
    return {"Authorization": f"Bearer {token}"}
