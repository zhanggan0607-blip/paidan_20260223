"""
数据库迁移脚本：添加密码相关字段
为 personnel 表添加 password_hash 和 must_change_password 字段
"""
from sqlalchemy import create_engine, text
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.config import get_settings

settings = get_settings()


def run_migration():
    """执行数据库迁移"""
    engine = create_engine(settings.database_url)
    
    print("=" * 60)
    print("数据库迁移：添加密码相关字段")
    print("=" * 60)
    
    with engine.connect() as conn:
        print("\n1. 检查 password_hash 字段...")
        result = conn.execute(text("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'personnel' AND column_name = 'password_hash'
        """))
        
        if result.fetchone() is None:
            print("   添加 password_hash 字段...")
            conn.execute(text("""
                ALTER TABLE personnel 
                ADD COLUMN password_hash VARCHAR(255) NULL
            """))
            conn.commit()
            print("   ✅ password_hash 字段添加成功")
        else:
            print("   ⏭️ password_hash 字段已存在，跳过")
        
        print("\n2. 检查 must_change_password 字段...")
        result = conn.execute(text("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'personnel' AND column_name = 'must_change_password'
        """))
        
        if result.fetchone() is None:
            print("   添加 must_change_password 字段...")
            conn.execute(text("""
                ALTER TABLE personnel 
                ADD COLUMN must_change_password BOOLEAN DEFAULT TRUE
            """))
            conn.commit()
            print("   ✅ must_change_password 字段添加成功")
        else:
            print("   ⏭️ must_change_password 字段已存在，跳过")
        
        print("\n3. 验证字段...")
        result = conn.execute(text("""
            SELECT column_name, data_type, is_nullable, column_default
            FROM information_schema.columns 
            WHERE table_name = 'personnel' 
            AND column_name IN ('password_hash', 'must_change_password')
            ORDER BY column_name
        """))
        
        print("\n   字段信息：")
        for row in result:
            print(f"   - {row[0]}: {row[1]}, nullable={row[2]}, default={row[3]}")
    
    print("\n" + "=" * 60)
    print("迁移完成！")
    print("=" * 60)


if __name__ == "__main__":
    run_migration()
