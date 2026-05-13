"""
数据库配置模块

同步模式：用于所有数据库操作
异步模式：仅用于健康检查，连接池最小化
"""
import time
from app.utils.logging_config import get_logger

import psycopg2
from sqlalchemy import create_engine, text
from sqlalchemy.engine import make_url
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase

from app.config import get_settings

logger = get_logger(__name__)

settings = get_settings()

_sync_db_url = settings.database_url
_async_db_url = None
if _sync_db_url:
    if _sync_db_url.startswith("postgresql+psycopg://"):
        _async_db_url = _sync_db_url.replace("postgresql+psycopg://", "postgresql+asyncpg://", 1)
    elif _sync_db_url.startswith("postgresql://"):
        _async_db_url = _sync_db_url.replace("postgresql://", "postgresql+asyncpg://", 1)

_DB_CONNECT_RETRIES = 3
_DB_CONNECT_RETRY_BASE_DELAY = 0.5
_TRANSIENT_DB_ERROR_PATTERNS = (
    "remaining connection slots",
    "too many connections",
    "connection to server",
    "could not connect to server",
    "the database system is starting up",
    "could not establish connection",
)


def _is_transient_db_error(error_msg: str) -> bool:
    lower_msg = error_msg.lower()
    return any(p in lower_msg for p in _TRANSIENT_DB_ERROR_PATTERNS)


def _create_sync_connection_with_retry():
    url = make_url(_sync_db_url)
    connect_kwargs = {
        "host": url.host,
        "port": url.port or 5432,
        "dbname": url.database,
        "user": url.username,
        "password": url.password,
        "connect_timeout": 10,
        "options": "-c statement_timeout=30000",
    }
    for key, value in url.query.items():
        connect_kwargs[key] = value

    last_error = None
    for attempt in range(_DB_CONNECT_RETRIES):
        try:
            return psycopg2.connect(**connect_kwargs)
        except psycopg2.OperationalError as e:
            last_error = e
            if _is_transient_db_error(str(e)) and attempt < _DB_CONNECT_RETRIES - 1:
                delay = _DB_CONNECT_RETRY_BASE_DELAY * (attempt + 1)
                logger.warning(
                    f"数据库连接失败（第{attempt + 1}/{_DB_CONNECT_RETRIES}次重试，"
                    f"等待{delay}秒）: {str(e)[:120]}"
                )
                time.sleep(delay)
                continue
            raise
    raise last_error


engine = create_engine(
    _sync_db_url,
    echo=settings.debug,
    pool_pre_ping=True,
    pool_recycle=settings.db_pool_recycle,
    pool_size=settings.db_pool_size,
    max_overflow=settings.db_max_overflow,
    pool_timeout=15,
    pool_use_lifo=True,
    creator=_create_sync_connection_with_retry,
)

async_engine: AsyncEngine | None = None
if _async_db_url:
    try:
        async_engine = create_async_engine(
            _async_db_url,
            echo=settings.debug,
            pool_pre_ping=True,
            pool_recycle=settings.db_pool_recycle,
            pool_size=1,
            max_overflow=1,
            pool_timeout=10,
            pool_use_lifo=True,
            connect_args={
                "statement_cache_size": 0,
                "timeout": 10,
            }
        )
        logger.info("异步数据库引擎创建成功（仅用于健康检查）")
    except Exception as e:
        logger.warning(f"异步数据库引擎创建失败: {str(e)}，将仅使用同步模式")
        async_engine = None

try:
    with engine.connect() as connection:
        connection.execute(text("SELECT 1"))
        connection.commit()
        logger.info("数据库连接成功")
except Exception as e:
    logger.error(f"数据库连接失败: {str(e)}")

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine, expire_on_commit=False)


class Base(DeclarativeBase):
    pass


def get_db():
    db = SessionLocal()
    try:
        yield db
    except Exception as e:
        from starlette.exceptions import HTTPException as StarletteHTTPException
        if isinstance(e, StarletteHTTPException):
            logger.debug(f"HTTP异常({e.status_code}), 执行回滚: {e.detail}")
        else:
            logger.error(f"事务异常，执行回滚: {str(e)}")
        db.rollback()
        raise
    finally:
        try:
            db.close()
        except Exception as e:
            logger.error(f"关闭session失败: {str(e)}")

