import sys
sys.path.insert(0, 'D:\\共享文件\\SSTCP-paidan260120\\backend-python')

from app.main import app, settings
print(f"Main settings database_url: {settings.database_url}")

from app.database import engine
print(f"Main engine URL: {engine.url}")
