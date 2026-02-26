from app.config import get_settings
settings = get_settings()
print('Database URL:', settings.database_url)

from app.database import SessionLocal
from app.services.work_plan import WorkPlanService

db = SessionLocal()
service = WorkPlanService(db)
stats = service.get_statistics(user_name=None, is_manager=True)
print('Statistics:', stats)
db.close()
