import sys
sys.path.insert(0, 'D:\\共享文件\\SSTCP-paidan260120\\backend-python')

from app.database import SessionLocal
from app.repositories.periodic_inspection import PeriodicInspectionRepository
from app.repositories.temporary_repair import TemporaryRepairRepository
from app.repositories.spot_work import SpotWorkRepository
from app.config import OverdueAlertConfig
from datetime import datetime
from app.utils.date_utils import parse_date

db = SessionLocal()

inspection_repo = PeriodicInspectionRepository(db)
repair_repo = TemporaryRepairRepository(db)
spotwork_repo = SpotWorkRepository(db)

all_inspections = inspection_repo.find_all_unpaginated()
all_repairs = repair_repo.find_all_unpaginated()
all_spotworks = spotwork_repo.find_all_unpaginated()

print(f"Total inspections: {len(all_inspections)}")
print(f"Total repairs: {len(all_repairs)}")
print(f"Total spotworks: {len(all_spotworks)}")

today = datetime.now().date()
year_start = datetime(today.year, 1, 1).date()
year_end = datetime(today.year, 12, 31).date()

print(f"\nYear range: {year_start} to {year_end}")
print(f"COMPLETED_STATUSES: {OverdueAlertConfig.COMPLETED_STATUSES}")

yearly_completed = 0

for item in all_inspections:
    actual_completion = parse_date(item.actual_completion_date)
    if item.status in OverdueAlertConfig.COMPLETED_STATUSES and actual_completion:
        if year_start <= actual_completion <= year_end:
            yearly_completed += 1
            print(f"  periodic_inspection: id={item.id}, status={item.status}, actual={actual_completion}")

for item in all_repairs:
    actual_completion = parse_date(item.actual_completion_date)
    if item.status in OverdueAlertConfig.COMPLETED_STATUSES and actual_completion:
        if year_start <= actual_completion <= year_end:
            yearly_completed += 1
            print(f"  temporary_repair: id={item.id}, status={item.status}, actual={actual_completion}")

for item in all_spotworks:
    actual_completion = parse_date(item.actual_completion_date)
    if item.status in OverdueAlertConfig.COMPLETED_STATUSES and actual_completion:
        if year_start <= actual_completion <= year_end:
            yearly_completed += 1
            print(f"  spot_work: id={item.id}, status={item.status}, actual={actual_completion}")

print(f"\nTotal yearly_completed: {yearly_completed}")

db.close()
