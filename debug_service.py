import sys
sys.path.insert(0, 'D:\\共享文件\\SSTCP-paidan260120\\backend-python')

from app.config import get_settings, ENV_FILE_PATH

print(f"ENV_FILE_PATH: {ENV_FILE_PATH}")
print(f"ENV file exists: {ENV_FILE_PATH.exists()}")

settings = get_settings()
print(f"Database URL: {settings.database_url}")

from app.services.work_plan import WorkPlanService
from app.database import SessionLocal

db = SessionLocal()
service = WorkPlanService(db)
stats = service.get_statistics(user_name=None, is_manager=True)
print(f"Statistics: {stats}")
db.close()
