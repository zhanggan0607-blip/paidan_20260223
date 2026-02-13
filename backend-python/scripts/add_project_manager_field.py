"""
添加 project_manager 字段到 project_info 表
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import text
from app.database import engine, SessionLocal

def migrate():
    db = SessionLocal()
    try:
        print("检查 project_manager 列是否存在...")
        result = db.execute(text("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'project_info' AND column_name = 'project_manager'
        """))
        
        if result.fetchone() is None:
            print("添加 project_manager 列...")
            db.execute(text("""
                ALTER TABLE project_info 
                ADD COLUMN project_manager VARCHAR(50)
            """))
            db.execute(text("""
                COMMENT ON COLUMN project_info.project_manager IS '项目负责人'
            """))
            db.commit()
            print("✓ project_manager 列添加成功")
        else:
            print("✓ project_manager 列已存在，跳过")
            
    except Exception as e:
        print(f"✗ 迁移失败: {e}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    migrate()
