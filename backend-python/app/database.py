from sqlalchemy import create_engine
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
)

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
    finally:
        try:
            db.close()
            logger.debug(f"关闭session: session={id(db)}")
        except Exception as e:
            logger.error(f"关闭session失败: {str(e)}")
