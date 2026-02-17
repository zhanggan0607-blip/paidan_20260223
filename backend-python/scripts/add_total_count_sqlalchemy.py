import sys
import os

sys.path.insert(0, r'D:\共享文件\SSTCP-paidan260120\backend-python')

from sqlalchemy import create_engine, text

DATABASE_URL = "postgresql://postgres:changeme@localhost:5432/tq"

engine = create_engine(DATABASE_URL)

with engine.connect() as conn:
    try:
        result = conn.execute(text("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'periodic_inspection' AND column_name = 'total_count'
        """))
        
        if result.fetchone() is None:
            conn.execute(text("ALTER TABLE periodic_inspection ADD COLUMN total_count INTEGER DEFAULT 5"))
            conn.commit()
            print("Successfully added total_count column")
        else:
            print("Column total_count already exists")
    except Exception as e:
        print(f"Error: {e}")
