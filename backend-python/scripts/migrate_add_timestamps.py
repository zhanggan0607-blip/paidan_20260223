import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app.database import engine
from sqlalchemy import text

print("=" * 100)
print("数据库迁移脚本 - 添加时间戳字段")
print("=" * 100)

try:
    with engine.connect() as conn:
        print("\n正在检查 spare_parts_stock 表...")
        
        result = conn.execute(text("PRAGMA table_info(spare_parts_stock)"))
        columns = [row[1] for row in result.fetchall()]
        
        print(f"当前字段: {columns}")
        
        if 'created_at' not in columns:
            print("\n添加 created_at 字段到 spare_parts_stock 表...")
            conn.execute(text("""
                ALTER TABLE spare_parts_stock 
                ADD COLUMN created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
            """))
            conn.commit()
            print("✅ created_at 字段添加成功")
        else:
            print("✅ created_at 字段已存在")
        
        print("\n正在检查 inspection_item 表...")
        
        result = conn.execute(text("PRAGMA table_info(inspection_item)"))
        columns = [row[1] for row in result.fetchall()]
        
        print(f"当前字段: {columns}")
        
        if 'created_at' not in columns:
            print("\n添加 created_at 字段到 inspection_item 表...")
            conn.execute(text("""
                ALTER TABLE inspection_item 
                ADD COLUMN created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
            """))
            conn.commit()
            print("✅ created_at 字段添加成功")
        else:
            print("✅ created_at 字段已存在")
        
        if 'updated_at' not in columns:
            print("\n添加 updated_at 字段到 inspection_item 表...")
            conn.execute(text("""
                ALTER TABLE inspection_item 
                ADD COLUMN updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
            """))
            conn.commit()
            print("✅ updated_at 字段添加成功")
        else:
            print("✅ updated_at 字段已存在")
        
        print("\n" + "=" * 100)
        print("数据库迁移完成！")
        print("=" * 100)

except Exception as e:
    print(f"\n❌ 数据库迁移失败: {str(e)}")
    import traceback
    traceback.print_exc()
