import os
import sys
sys.path.insert(0, '/app')
os.chdir('/app')

from sqlalchemy import create_engine, text
from dotenv import load_dotenv

load_dotenv('/app/.env')
db_url = os.getenv('DATABASE_URL', '')
print('DB URL pattern:', db_url[:30] + '...' if db_url else 'Not set')

engine = create_engine(db_url)
with engine.connect() as conn:
    # 检查uploaded_file表是否存在
    result = conn.execute(text("SELECT table_name FROM information_schema.tables WHERE table_name = 'uploaded_file'"))
    tables = [row[0] for row in result]
    print('uploaded_file table exists:', 'uploaded_file' in tables)
    
    # 列出所有表
    result = conn.execute(text("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public' ORDER BY table_name"))
    print('All tables:', [row[0] for row in result])
    
    # 如果uploaded_file表存在，统计记录
    if 'uploaded_file' in tables:
        result = conn.execute(text("SELECT COUNT(*) FROM uploaded_file"))
        count = result.scalar()
        print(f'\nuploaded_file records: {count}')
        
        result = conn.execute(text("SELECT SUM(file_size) FROM uploaded_file"))
        total_size = result.scalar() or 0
        print(f'Total size: {total_size / 1024 / 1024:.2f} MB')
