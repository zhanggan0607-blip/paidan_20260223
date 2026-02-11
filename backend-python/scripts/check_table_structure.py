import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from sqlalchemy import inspect
from app.database import engine
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def check_table_structure():
    """检查表结构"""
    inspector = inspect(engine)
    
    tables = inspector.get_table_names()
    logger.info(f"数据库中的表: {tables}")
    
    if 'project_info' in tables:
        columns = inspector.get_columns('project_info')
        logger.info(f"\nproject_info 表结构:")
        for col in columns:
            logger.info(f"  - {col['name']}: {col['type']} (nullable: {col['nullable']}, primary_key: {col.get('primary_key', False)})")
        
        indexes = inspector.get_indexes('project_info')
        logger.info(f"\nproject_info 表索引:")
        for idx in indexes:
            logger.info(f"  - {idx['name']}: {idx['column_names']}")
    else:
        logger.warning("project_info 表不存在")

if __name__ == "__main__":
    check_table_structure()