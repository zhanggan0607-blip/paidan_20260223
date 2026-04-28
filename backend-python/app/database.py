"""
数据库配置模块
同时支持同步和异步数据库操作

同步模式：用于现有代码兼容
异步模式：用于新的异步路由，避免阻塞事件循环
"""
import logging

from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import AsyncSession, AsyncEngine, create_async_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase

from app.config import get_settings

logger = logging.getLogger(__name__)

settings = get_settings()

_sync_db_url = settings.database_url
_async_db_url = _sync_db_url.replace("postgresql://", "postgresql+asyncpg://", 1) if _sync_db_url else None

engine = create_engine(
    _sync_db_url,
    echo=settings.debug,
    pool_pre_ping=True,
    pool_recycle=1800,
    pool_size=10,
    max_overflow=20,
    pool_timeout=60,
    pool_use_lifo=True,
    connect_args={
        "connect_timeout": 10
    }
)

async_engine: AsyncEngine | None = None
if _async_db_url:
    try:
        async_engine = create_async_engine(
            _async_db_url,
            echo=settings.debug,
            pool_pre_ping=True,
            pool_recycle=1800,
            pool_size=5,
            max_overflow=10,
            pool_timeout=60,
            pool_use_lifo=True,
            connect_args={
                "statement_cache_size": 0,
                "timeout": 10,
            }
        )
        logger.info("异步数据库引擎创建成功")
    except Exception as e:
        logger.warning(f"异步数据库引擎创建失败: {str(e)}，将仅使用同步模式")
        async_engine = None

try:
    with engine.connect() as connection:
        logger.info("数据库连接成功")
except Exception as e:
    logger.error(f"数据库连接失败: {str(e)}")

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

AsyncSessionLocal: sessionmaker | None = None
if async_engine:
    AsyncSessionLocal = sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=async_engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )


class Base(DeclarativeBase):
    pass


def get_db():
    """
    获取同步数据库会话

    事务管理说明：
    - 此函数不再自动 commit，事务由 Service 层统一管理
    - Service 层应在业务操作完成后调用 db.commit()
    - 发生异常时自动 rollback
    - Repository 层只执行 flush，不执行 commit
    """
    db = SessionLocal()
    try:
        yield db
    except Exception as e:
        logger.error(f"事务异常，执行回滚: {str(e)}")
        db.rollback()
        raise
    finally:
        try:
            db.close()
        except Exception as e:
            logger.error(f"关闭session失败: {str(e)}")


async def get_async_db():
    """
    获取异步数据库会话

    用于异步路由，避免阻塞事件循环
    事务管理同同步模式
    """
    if not AsyncSessionLocal:
        raise RuntimeError("异步数据库会话不可用，请检查asyncpg是否安装")

    async with AsyncSessionLocal() as session:
        try:
            yield session
        except Exception as e:
            logger.error(f"异步事务异常，执行回滚: {str(e)}")
            await session.rollback()
            raise
        finally:
            await session.close()
