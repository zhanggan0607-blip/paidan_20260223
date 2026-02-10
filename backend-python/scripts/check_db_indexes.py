import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from sqlalchemy import text
from app.database import engine

print("=" * 100)
print("检查数据库中现有的索引")
print("=" * 100)

try:
    with engine.connect() as conn:
        result = conn.execute(text("SELECT name FROM sqlite_master WHERE type='index' ORDER BY name"))
        indexes = [row[0] for row in result.fetchall()]
        
        print(f"\n所有索引名称: {indexes}")
        
        duplicates = [idx for idx in indexes if indexes.count(idx) > 1]
        if duplicates:
            print(f"\n⚠️  重复的索引名称: {set(duplicates)}")
        else:
            print("\n✅ 没有重复的索引名称")
        
        print("\n" + "=" * 100)

except Exception as e:
    print(f"\n❌ 检查失败: {str(e)}")
    import traceback
    traceback.print_exc()
