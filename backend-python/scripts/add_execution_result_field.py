"""
添加 execution_result 字段到 periodic_inspection 表
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import text
from app.database import engine

def migrate():
    with engine.connect() as conn:
        try:
            conn.execute(text("ALTER TABLE periodic_inspection ADD COLUMN execution_result TEXT"))
            conn.commit()
            print("成功添加 execution_result 字段")
        except Exception as e:
            if "already exists" in str(e) or "已存在" in str(e):
                print("execution_result 字段已存在，跳过")
            else:
                print(f"添加字段失败: {e}")
                raise

if __name__ == "__main__":
    migrate()
