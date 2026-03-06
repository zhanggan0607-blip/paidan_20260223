"""
数据库迁移脚本：为所有使用SoftDeleteMixin的表添加完整的软删除字段
检查并添加 is_deleted, deleted_at, deleted_by 三个字段
"""
from sqlalchemy import create_engine, text
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.config import get_settings

TABLES_TO_MIGRATE = [
    'maintenance_plan',
    'work_plan',
    'temporary_repair',
    'spot_work',
    'periodic_inspection',
    'weekly_report',
    'maintenance_log'
]

def migrate():
    settings = get_settings()
    engine = create_engine(settings.database_url)
    
    with engine.connect() as conn:
        for table_name in TABLES_TO_MIGRATE:
            print(f'Checking {table_name}...')
            
            # 检查 is_deleted
            result = conn.execute(text(f"""
                SELECT column_name FROM information_schema.columns 
                WHERE table_name = '{table_name}' AND column_name = 'is_deleted'
            """))
            if not result.fetchone():
                print(f'  Adding is_deleted column...')
                conn.execute(text(f'ALTER TABLE {table_name} ADD COLUMN is_deleted INTEGER DEFAULT 0'))
                conn.commit()
            
            # 检查 deleted_at
            result = conn.execute(text(f"""
                SELECT column_name FROM information_schema.columns 
                WHERE table_name = '{table_name}' AND column_name = 'deleted_at'
            """))
            if not result.fetchone():
                print(f'  Adding deleted_at column...')
                conn.execute(text(f'ALTER TABLE {table_name} ADD COLUMN deleted_at TIMESTAMP'))
                conn.commit()
            
            # 检查 deleted_by
            result = conn.execute(text(f"""
                SELECT column_name FROM information_schema.columns 
                WHERE table_name = '{table_name}' AND column_name = 'deleted_by'
            """))
            if not result.fetchone():
                print(f'  Adding deleted_by column...')
                conn.execute(text(f'ALTER TABLE {table_name} ADD COLUMN deleted_by BIGINT'))
                conn.commit()
            
            print(f'  {table_name}: OK')

if __name__ == '__main__':
    migrate()
