"""
迁移脚本：更新外键约束为 CASCADE 删除
当项目被删除时，自动删除所有关联记录
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import text
from app.database import engine
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def migrate():
    tables_to_update = [
        ('work_plan', 'work_plan_project_id_fkey'),
        ('periodic_inspection', 'periodic_inspection_project_id_fkey'),
        ('temporary_repair', 'temporary_repair_project_id_fkey'),
        ('spot_work', 'spot_work_project_id_fkey'),
        ('maintenance_plan', 'maintenance_plan_project_id_fkey'),
    ]
    
    with engine.connect() as conn:
        for table_name, old_constraint_name in tables_to_update:
            try:
                logger.info(f"处理表: {table_name}")
                
                result = conn.execute(text(f"""
                    SELECT constraint_name 
                    FROM information_schema.table_constraints 
                    WHERE table_name = '{table_name}' 
                    AND constraint_type = 'FOREIGN KEY'
                    AND constraint_name LIKE '%project_id%'
                """))
                
                constraints = result.fetchall()
                logger.info(f"  找到的外键约束: {constraints}")
                
                for constraint in constraints:
                    constraint_name = constraint[0]
                    logger.info(f"  删除旧约束: {constraint_name}")
                    conn.execute(text(f"""
                        ALTER TABLE {table_name} 
                        DROP CONSTRAINT IF EXISTS {constraint_name}
                    """))
                
                logger.info(f"  添加新的 CASCADE 约束 (NOT VALID)")
                conn.execute(text(f"""
                    ALTER TABLE {table_name} 
                    ADD CONSTRAINT {table_name}_project_id_fkey 
                    FOREIGN KEY (project_id) 
                    REFERENCES project_info(project_id) 
                    ON DELETE CASCADE
                    NOT VALID
                """))
                
                conn.commit()
                logger.info(f"  ✅ 表 {table_name} 更新成功")
                
            except Exception as e:
                logger.error(f"  ❌ 表 {table_name} 更新失败: {str(e)}")
                conn.rollback()
                raise
        
        logger.info("\n🎉 所有外键约束已更新为 CASCADE 删除")


if __name__ == "__main__":
    migrate()
