import psycopg2
from datetime import datetime

conn = psycopg2.connect(host='localhost', database='tq', user='postgres', password='123456', port=5432)
cursor = conn.cursor()

today = datetime.now().date()
year_start = datetime(today.year, 1, 1).date()
year_end = datetime(today.year, 12, 31).date()

print(f"Today: {today}")
print(f"Year range: {year_start} to {year_end}")

COMPLETED_STATUSES = ['已完成', '已确认', '已审批']

cursor.execute("SELECT id, status, actual_completion_date FROM periodic_inspection WHERE status = ANY(%s)", (COMPLETED_STATUSES,))
rows = cursor.fetchall()
print(f"\nperiodic_inspection with completed status: {len(rows)}")
for row in rows:
    actual = row[2]
    if actual:
        actual_date = actual.date() if hasattr(actual, 'date') else actual
        in_year = year_start <= actual_date <= year_end
        print(f"  id={row[0]}, status={row[1]}, actual_completion={actual_date}, in_year={in_year}")

cursor.execute("SELECT id, status, actual_completion_date FROM temporary_repair WHERE status = ANY(%s)", (COMPLETED_STATUSES,))
rows = cursor.fetchall()
print(f"\ntemporary_repair with completed status: {len(rows)}")
for row in rows:
    actual = row[2]
    if actual:
        actual_date = actual.date() if hasattr(actual, 'date') else actual
        in_year = year_start <= actual_date <= year_end
        print(f"  id={row[0]}, status={row[1]}, actual_completion={actual_date}, in_year={in_year}")

cursor.execute("SELECT id, status, actual_completion_date FROM spot_work WHERE status = ANY(%s)", (COMPLETED_STATUSES,))
rows = cursor.fetchall()
print(f"\nspot_work with completed status: {len(rows)}")
for row in rows:
    actual = row[2]
    if actual:
        actual_date = actual.date() if hasattr(actual, 'date') else actual
        in_year = year_start <= actual_date <= year_end
        print(f"  id={row[0]}, status={row[1]}, actual_completion={actual_date}, in_year={in_year}")

cursor.close()
conn.close()
