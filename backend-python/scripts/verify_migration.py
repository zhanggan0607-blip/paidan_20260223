import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app.database import engine
from sqlalchemy import text

print("=" * 100)
print("验证数据库字段")
print("=" * 100)

try:
    with engine.connect() as conn:
        print("\n1. 检查 spare_parts_stock 表...")
        result = conn.execute(text("PRAGMA table_info(spare_parts_stock)"))
        columns = [row[1] for row in result.fetchall()]
        print(f"   字段列表: {columns}")
        
        if 'created_at' in columns:
            print("   ✅ created_at 字段存在")
        else:
            print("   ❌ created_at 字段不存在")
        
        if 'updated_at' in columns:
            print("   ✅ updated_at 字段存在")
        else:
            print("   ❌ updated_at 字段不存在")
        
        print("\n2. 检查 inspection_item 表...")
        result = conn.execute(text("PRAGMA table_info(inspection_item)"))
        columns = [row[1] for row in result.fetchall()]
        print(f"   字段列表: {columns}")
        
        if 'created_at' in columns:
            print("   ✅ created_at 字段存在")
        else:
            print("   ❌ created_at 字段不存在")
        
        if 'updated_at' in columns:
            print("   ✅ updated_at 字段存在")
        else:
            print("   ❌ updated_at 字段不存在")
        
        print("\n" + "=" * 100)
        print("验证完成！")
        print("=" * 100)

except Exception as e:
    print(f"\n❌ 验证失败: {str(e)}")
    import traceback
    traceback.print_exc()
