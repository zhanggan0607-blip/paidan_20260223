import sys
sys.path.insert(0, 'D:\\共享文件\\SSTCP-paidan260120\\backend-python')

from app.config import get_settings
settings = get_settings()
print(f"Database URL: {settings.database_url}")

from app.database import SessionLocal
try:
    db = SessionLocal()
    print("Database connection successful!")
    
    from app.repositories.periodic_inspection import PeriodicInspectionRepository
    inspection_repo = PeriodicInspectionRepository(db)
    all_inspections = inspection_repo.find_all_unpaginated()
    print(f"Total inspections: {len(all_inspections)}")
    
    for item in all_inspections[:3]:
        print(f"  id={item.id}, status={item.status}, actual_completion={item.actual_completion_date}")
    
    db.close()
except Exception as e:
    print(f"Error: {e}")
