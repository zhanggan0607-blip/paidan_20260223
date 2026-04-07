import sys
sys.path.insert(0, '/app')
from sqlalchemy import text
from app.database import SessionLocal
db = SessionLocal()
print('=== Spot Work - ALL photos ===')
result = db.execute(text("SELECT id, work_id, photos FROM spot_work WHERE photos IS NOT NULL AND photos != '[]' LIMIT 5")).fetchall()
for r in result:
    print(f"ID: {r[0]}, work_id: {r[1]}")
    print(f"  photos: {r[2][:200] if r[2] else 'None'}...")
    print()
print('=== Periodic Inspection Record - ALL photos ===')
result = db.execute(text("SELECT id, inspection_id, photos FROM periodic_inspection_record WHERE photos IS NOT NULL AND photos != '[]' LIMIT 5")).fetchall()
for r in result:
    print(f"ID: {r[0]}, inspection_id: {r[1]}")
    print(f"  photos: {r[2][:200] if r[2] else 'None'}...")
    print()
print('=== Temporary Repair - ALL photos ===')
result = db.execute(text("SELECT id, repair_id, photos FROM temporary_repair WHERE photos IS NOT NULL AND photos != '[]' LIMIT 5")).fetchall()
for r in result:
    print(f"ID: {r[0]}, repair_id: {r[1]}")
    print(f"  photos: {r[2][:200] if r[2] else 'None'}...")
    print()
db.close()
