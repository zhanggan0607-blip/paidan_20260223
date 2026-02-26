import sys
import os
sys.path.insert(0, 'D:\\共享文件\\SSTCP-paidan260120\\backend-python')

print(f"Current working directory: {os.getcwd()}")
print(f".env file exists: {os.path.exists('.env')}")
print(f"backend-python/.env file exists: {os.path.exists('D:\\\\共享文件\\\\SSTCP-paidan260120\\\\backend-python\\\\.env')}")

from app.config import get_settings
settings = get_settings()
print(f"Database URL from settings: {settings.database_url}")
