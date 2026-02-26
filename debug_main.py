import sys
sys.path.insert(0, 'D:\\共享文件\\SSTCP-paidan260120\\backend-python')

import logging
logging.basicConfig(level=logging.INFO, format='%(name)s - %(levelname)s - %(message)s')

from app.config import get_settings
settings = get_settings()
print(f"Settings database_url: {settings.database_url}")

from app.database import engine, SessionLocal
print(f"Engine URL: {engine.url}")

db = SessionLocal()
from app.services.work_plan import WorkPlanService
service = WorkPlanService(db)
stats = service.get_statistics(user_name=None, is_manager=True)
print(f"Statistics from service: {stats}")
db.close()
