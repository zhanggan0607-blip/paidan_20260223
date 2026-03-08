import logging

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from app.config import get_settings

logger = logging.getLogger(__name__)

settings = get_settings()

logger.info(f"数据库URL: {settings.database_url}")

engine = create_engine(
    settings.database_url,
    echo=settings.debug,
    pool_pre_ping=True,
    pool_recycle=1800,
    pool_size=15,
    max_overflow=30,
    pool_timeout=60,
    connect_args={
        "connect_timeout": 10
    }
)

try:
    with engine.connect() as connection:
        logger.info("数据库连接成功")
except Exception as e:
    logger.error(f"数据库连接失败: {str(e)}")

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    """
    获取数据库会话

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
