import sys
sys.path.insert(0, 'D:\\共享文件\\SSTCP-paidan260120\\backend-python')

import psycopg2
from datetime import datetime

conn = psycopg2.connect(
    host='localhost', 
    database='tq', 
    user='postgres', 
    password='123456', 
    port=5432,
    client_encoding='UTF8'
)
cursor = conn.cursor()

today = datetime.now().date()
year_start = datetime(today.year, 1, 1).date()
year_end = datetime(today.year, 12, 31).date()

COMPLETED_STATUSES = ['已完成', '已确认', '已审批']

cursor.execute("SELECT id, status, actual_completion_date FROM periodic_inspection")
all_inspections = cursor.fetchall()
print(f"Total inspections: {len(all_inspections)}")

yearly_completed = 0
for row in all_inspections:
    id_, status, actual_completion = row
    if status in COMPLETED_STATUSES and actual_completion:
        actual_date = actual_completion.date() if hasattr(actual_completion, 'date') else actual_completion
        if year_start <= actual_date <= year_end:
            yearly_completed += 1
            print(f"  periodic_inspection: id={id_}, status={status}, actual={actual_date}")

cursor.execute("SELECT id, status, actual_completion_date FROM temporary_repair")
all_repairs = cursor.fetchall()
print(f"Total repairs: {len(all_repairs)}")

for row in all_repairs:
    id_, status, actual_completion = row
    if status in COMPLETED_STATUSES and actual_completion:
        actual_date = actual_completion.date() if hasattr(actual_completion, 'date') else actual_completion
        if year_start <= actual_date <= year_end:
            yearly_completed += 1
            print(f"  temporary_repair: id={id_}, status={status}, actual={actual_date}")

cursor.execute("SELECT id, status, actual_completion_date FROM spot_work")
all_spotworks = cursor.fetchall()
print(f"Total spotworks: {len(all_spotworks)}")

for row in all_spotworks:
    id_, status, actual_completion = row
    if status in COMPLETED_STATUSES and actual_completion:
        actual_date = actual_completion.date() if hasattr(actual_completion, 'date') else actual_completion
        if year_start <= actual_date <= year_end:
            yearly_completed += 1
            print(f"  spot_work: id={id_}, status={status}, actual={actual_date}")

print(f"\nTotal yearly_completed: {yearly_completed}")

cursor.close()
conn.close()
