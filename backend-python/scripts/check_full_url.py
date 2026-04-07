import sys
sys.path.insert(0, '/app')
from sqlalchemy import text
from app.database import SessionLocal
db = SessionLocal()
print('=== Spot Work - check for full URL ===')
result = db.execute(text("SELECT id, work_id, photos FROM spot_work WHERE photos LIKE '%http%'")).fetchall()
for r in result:
    print(r)
print('=== Periodic Inspection Record - check for full URL ===')
result = db.execute(text("SELECT id, inspection_id, photos FROM periodic_inspection_record WHERE photos LIKE '%http%'")).fetchall()
for r in result:
    print(r)
print('=== Temporary Repair - check for full URL ===')
result = db.execute(text("SELECT id, repair_id, photos FROM temporary_repair WHERE photos LIKE '%http%'")).fetchall()
for r in result:
    print(r)
db.close()
