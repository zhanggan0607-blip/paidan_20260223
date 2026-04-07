import os
os.chdir('/app')
from app.database import SessionLocal
from sqlalchemy import text

db = SessionLocal()
try:
    # 检查表是否存在
    result = db.execute(text("SELECT table_name FROM information_schema.tables WHERE table_name = 'uploaded_file'"))
    tables = [row[0] for row in result]
    print('uploaded_file 表存在:', 'uploaded_file' in tables)
    
    # 检查记录数
    count_result = db.execute(text('SELECT COUNT(*) FROM uploaded_file'))
    count = count_result.scalar()
    print(f'uploaded_file 表记录数: {count}')
    
    # 检查总大小
    size_result = db.execute(text('SELECT SUM(file_size) FROM uploaded_file'))
    total_size = size_result.scalar() or 0
    print(f'总大小: {total_size / 1024 / 1024:.2f} MB')
finally:
    db.close()
