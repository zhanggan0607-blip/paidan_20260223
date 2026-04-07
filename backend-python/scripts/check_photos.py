import sys
sys.path.insert(0, '/app')
from sqlalchemy import text
from app.database import SessionLocal
db = SessionLocal()
print('=== Spot Work ===')
result = db.execute(text("SELECT id, work_id, photos FROM spot_work WHERE photos IS NOT NULL AND photos != '[]' LIMIT 3")).fetchall()
for r in result:
    print(r)
print('=== Periodic Inspection Record ===')
result = db.execute(text("SELECT id, inspection_id, photos FROM periodic_inspection_record WHERE photos IS NOT NULL AND photos != '[]' LIMIT 3")).fetchall()
for r in result:
    print(r)
print('=== Temporary Repair ===')
result = db.execute(text("SELECT id, repair_id, photos FROM temporary_repair WHERE photos IS NOT NULL AND photos != '[]' LIMIT 3")).fetchall()
for r in result:
    print(r)
db.close()
