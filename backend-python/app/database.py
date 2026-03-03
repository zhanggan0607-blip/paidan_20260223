from sqlalchemy import create_engine, event
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.config import get_settings
import logging

logger = logging.getLogger(__name__)

settings = get_settings()

logger.info(f"数据库URL: {settings.database_url}")

engine = create_engine(
    settings.database_url,
    echo=settings.debug,
    pool_pre_ping=True,
    pool_recycle=3600,
    pool_size=10,
    max_overflow=20,
    pool_timeout=30,
    connect_args={
        "connect_timeout": 10,
        "application_name": "sstcp_maintenance"
    }
)


@event.listens_for(engine, "connect")
def receive_connect(dbapi_connection, connection_record):
    """连接创建时触发"""
    logger.debug(f"数据库连接创建: {id(dbapi_connection)}")


@event.listens_for(engine, "checkout")
def receive_checkout(dbapi_connection, connection_record, connection_proxy):
    """连接从池中取出时触发"""
    logger.debug(f"数据库连接取出: {id(dbapi_connection)}")


@event.listens_for(engine, "checkin")
def receive_checkin(dbapi_connection, connection_record):
    """连接归还到池中时触发"""
    logger.debug(f"数据库连接归还: {id(dbapi_connection)}")


@event.listens_for(engine, "close")
def receive_close(dbapi_connection, connection_record):
    """连接关闭时触发"""
    logger.debug(f"数据库连接关闭: {id(dbapi_connection)}")

try:
    with engine.connect() as connection:
        logger.info("数据库连接成功")
except Exception as e:
    logger.error(f"数据库连接失败: {str(e)}")

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        logger.debug(f"开始事务: session={id(db)}")
        yield db
        db.commit()
    except Exception as e:
        logger.error(f"事务异常，执行回滚: {str(e)}")
        db.rollback()
        raise
    finally:
        try:
            db.close()
            logger.debug(f"关闭session: session={id(db)}")
        except Exception as e:
            logger.error(f"关闭session失败: {str(e)}")
