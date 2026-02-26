"""
执行软删除字段迁移脚本
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy import text
from app.database import engine

def run_migration():
    migration_sql = """
    -- 1. 为定期巡检单表添加软删除字段
    ALTER TABLE periodic_inspection 
    ADD COLUMN IF NOT EXISTS is_deleted BOOLEAN DEFAULT FALSE;

    ALTER TABLE periodic_inspection 
    ADD COLUMN IF NOT EXISTS deleted_at TIMESTAMP;

    ALTER TABLE periodic_inspection 
    ADD COLUMN IF NOT EXISTS deleted_by BIGINT;

    -- 添加索引以提高查询性能
    CREATE INDEX IF NOT EXISTS idx_periodic_is_deleted ON periodic_inspection(is_deleted);

    -- 2. 为临时维修单表添加软删除字段
    ALTER TABLE temporary_repair 
    ADD COLUMN IF NOT EXISTS is_deleted BOOLEAN DEFAULT FALSE;

    ALTER TABLE temporary_repair 
    ADD COLUMN IF NOT EXISTS deleted_at TIMESTAMP;

    ALTER TABLE temporary_repair 
    ADD COLUMN IF NOT EXISTS deleted_by BIGINT;

    -- 添加索引以提高查询性能
    CREATE INDEX IF NOT EXISTS idx_temp_repair_is_deleted ON temporary_repair(is_deleted);

    -- 3. 为零星用工单表添加软删除字段
    ALTER TABLE spot_work 
    ADD COLUMN IF NOT EXISTS is_deleted BOOLEAN DEFAULT FALSE;

    ALTER TABLE spot_work 
    ADD COLUMN IF NOT EXISTS deleted_at TIMESTAMP;

    ALTER TABLE spot_work 
    ADD COLUMN IF NOT EXISTS deleted_by BIGINT;

    -- 添加索引以提高查询性能
    CREATE INDEX IF NOT EXISTS idx_spot_work_is_deleted ON spot_work(is_deleted);

    -- 4. 更新现有数据，确保所有记录的is_deleted字段都有值
    UPDATE periodic_inspection SET is_deleted = FALSE WHERE is_deleted IS NULL;
    UPDATE temporary_repair SET is_deleted = FALSE WHERE is_deleted IS NULL;
    UPDATE spot_work SET is_deleted = FALSE WHERE is_deleted IS NULL;
    """
    
    with engine.connect() as conn:
        statements = [s.strip() for s in migration_sql.split(';') if s.strip()]
        for statement in statements:
            if statement:
                try:
                    conn.execute(text(statement))
                    print(f"执行成功: {statement[:50]}...")
                except Exception as e:
                    print(f"执行失败: {statement[:50]}...")
                    print(f"错误: {e}")
        conn.commit()
    
    print("迁移完成!")

if __name__ == "__main__":
    run_migration()
