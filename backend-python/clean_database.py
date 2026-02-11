"""
数据库清理脚本
删除所有表并重新创建
"""
from app.database import engine, Base
import logging

logger = logging.getLogger(__name__)

def clean_database():
    """清理数据库：删除所有表"""
    logger.info("开始清理数据库...")
    try:
        Base.metadata.drop_all(bind=engine)
        logger.info("数据库清理成功")
    except Exception as e:
        logger.error(f"清理数据库失败: {str(e)}", exc_info=True)
        raise

def recreate_tables():
    """重新创建所有表"""
    logger.info("开始重新创建数据库表...")
    try:
        Base.metadata.create_all(bind=engine, checkfirst=False)
        logger.info("数据库表创建成功")
    except Exception as e:
        logger.error(f"创建数据库表失败: {str(e)}", exc_info=True)
        raise

if __name__ == "__main__":
    clean_database()
    recreate_tables()
    logger.info("数据库初始化完成")
