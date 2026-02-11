import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from app.database import engine, Base
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def recreate_tables():
    """重新创建数据库表"""
    try:
        Base.metadata.drop_all(bind=engine)
        logger.info("✅ 删除所有表")
        
        Base.metadata.create_all(bind=engine)
        logger.info("✅ 创建所有表")
        
    except Exception as e:
        logger.error(f"❌ 重新创建表失败: {str(e)}")

if __name__ == "__main__":
    recreate_tables()