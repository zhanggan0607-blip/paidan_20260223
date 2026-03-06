"""
修改 is_deleted 字段类型从 integer 改为 boolean
"""
import sys
import os

backend_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, backend_path)

from sqlalchemy import create_engine, text

DATABASE_URL = "postgresql://postgres:123456@localhost:5432/tq?client_encoding=utf8"

engine = create_engine(DATABASE_URL)

def migrate():
    tables = [
        'work_plan',
        'maintenance_plan',
        'periodic_inspection',
        'temporary_repair',
        'spot_work',
        'weekly_report',
        'maintenance_log',
        'project_info',
        'personnel',
        'spare_parts_stock',
        'repair_tools_stock',
    ]
    
    with engine.connect() as conn:
        for table in tables:
            try:
                result = conn.execute(text(f"""
                    SELECT column_name, data_type, column_default FROM information_schema.columns 
                    WHERE table_name = '{table}' AND column_name = 'is_deleted'
                """))
                row = result.fetchone()
                if row:
                    col_name, data_type, default_val = row
                    print(f"表 {table}: is_deleted 字段类型={data_type}, 默认值={default_val}")
                    
                    if data_type == 'boolean':
                        print(f"⏭️ 表 {table} 的 is_deleted 已经是 boolean 类型，跳过")
                        continue
                    
                    print(f"正在修改表 {table} 的 is_deleted 字段类型...")
                    
                    conn.execute(text(f"""
                        ALTER TABLE {table} ALTER COLUMN is_deleted DROP DEFAULT
                    """))
                    
                    conn.execute(text(f"""
                        ALTER TABLE {table} ALTER COLUMN is_deleted TYPE boolean 
                        USING (CASE WHEN is_deleted::integer = 0 THEN false ELSE true END)
                    """))
                    
                    conn.execute(text(f"""
                        ALTER TABLE {table} ALTER COLUMN is_deleted SET DEFAULT false
                    """))
                    
                    conn.commit()
                    print(f"✅ 表 {table} 修改成功")
                else:
                    print(f"⏭️ 表 {table} 没有 is_deleted 字段，跳过")
            except Exception as e:
                print(f"❌ 表 {table} 修改失败: {e}")
                conn.rollback()

if __name__ == '__main__':
    migrate()
