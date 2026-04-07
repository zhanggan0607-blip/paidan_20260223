import sys
sys.path.insert(0, '/app')
from sqlalchemy import text
from app.database import SessionLocal
db = SessionLocal()
print('=== Spot Work - RAW photos data ===')
result = db.execute(text("SELECT id, work_id, photos FROM spot_work WHERE photos IS NOT NULL AND photos != '[]' LIMIT 3")).fetchall()
for r in result:
    print(f"ID: {r[0]}, work_id: {r[1]}")
    print(f"  RAW: {repr(r[2])}")
    print()
print('=== Periodic Inspection Record - RAW photos data ===')
result = db.execute(text("SELECT id, inspection_id, photos FROM periodic_inspection_record WHERE photos IS NOT NULL AND photos != '[]' LIMIT 3")).fetchall()
for r in result:
    print(f"ID: {r[0]}, inspection_id: {r[1]}")
    print(f"  RAW: {repr(r[2])}")
    print()
db.close()
