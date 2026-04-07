"""
数据库迁移脚本：添加 client_contact_id 字段到 project_info 表
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import text
from app.database import engine, SessionLocal


def migrate():
    """执行迁移"""
    print("=" * 50)
    print("迁移脚本：添加 client_contact_id 字段到 project_info 表")
    print("=" * 50)
    
    session = SessionLocal()
    try:
        result = session.execute(text("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'project_info' AND column_name = 'client_contact_id'
        """))
        
        if result.fetchone():
            print("✅ client_contact_id 字段已存在，无需迁移")
            return
        
        print("正在添加 client_contact_id 字段...")
        
        session.execute(text("""
            ALTER TABLE project_info 
            ADD COLUMN client_contact_id INTEGER NULL
        """))
        
        session.execute(text("""
            COMMENT ON COLUMN project_info.client_contact_id IS '客户联系人ID'
        """))
        
        session.execute(text("""
            ALTER TABLE project_info 
            ADD CONSTRAINT fk_project_info_client_contact_id 
            FOREIGN KEY (client_contact_id) 
            REFERENCES customer_contact(id) 
            ON DELETE SET NULL
        """))
        
        session.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_project_info_client_contact_id 
            ON project_info(client_contact_id)
        """))
        
        session.commit()
        print("✅ 迁移完成！")
        
    except Exception as e:
        print(f"❌ 迁移失败: {str(e)}")
        session.rollback()
        raise
    finally:
        session.close()


if __name__ == "__main__":
    migrate()
