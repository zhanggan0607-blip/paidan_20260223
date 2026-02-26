import sys
sys.path.insert(0, 'D:\\共享文件\\SSTCP-paidan260120\\backend-python')

import logging
logging.basicConfig(level=logging.DEBUG)

from app.config import get_settings
settings = get_settings()
print(f"Database URL: {settings.database_url}")

from app.database import engine
print(f"Engine: {engine}")
print(f"Engine URL: {engine.url}")

with engine.connect() as conn:
    result = conn.execute("SELECT 1")
    print(f"Connection test: {result.fetchone()}")
