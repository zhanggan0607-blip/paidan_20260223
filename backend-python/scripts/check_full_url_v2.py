import sys
sys.path.insert(0, '/app')
from sqlalchemy import text
from app.database import SessionLocal
db = SessionLocal()

print('=== Checking for ANY photos with https:// ===')
result = db.execute(text("SELECT id, work_id, photos FROM spot_work WHERE photos LIKE '%https://%'")).fetchall()
for r in result:
    print(f"Spot Work ID: {r[0]}, work_id: {r[1]}")
    print(f"  photos: {r[2]}")
    print()

result = db.execute(text("SELECT id, inspection_id, photos FROM periodic_inspection_record WHERE photos LIKE '%https://%'")).fetchall()
for r in result:
    print(f"Inspection Record ID: {r[0]}, inspection_id: {r[1]}")
    print(f"  photos: {r[2]}")
    print()

result = db.execute(text("SELECT id, repair_id, photos FROM temporary_repair WHERE photos LIKE '%https://%'")).fetchall()
for r in result:
    print(f"Temporary Repair ID: {r[0]}, repair_id: {r[1]}")
    print(f"  photos: {r[2]}")
    print()

print('=== Checking for ANY photos with http:// ===')
result = db.execute(text("SELECT id, work_id, photos FROM spot_work WHERE photos LIKE '%http://%'")).fetchall()
for r in result:
    print(f"Spot Work ID: {r[0]}, work_id: {r[1]}")
    print(f"  photos: {r[2]}")
    print()

result = db.execute(text("SELECT id, inspection_id, photos FROM periodic_inspection_record WHERE photos LIKE '%http://%'")).fetchall()
for r in result:
    print(f"Inspection Record ID: {r[0]}, inspection_id: {r[1]}")
    print(f"  photos: {r[2]}")
    print()

result = db.execute(text("SELECT id, repair_id, photos FROM temporary_repair WHERE photos LIKE '%http://%'")).fetchall()
for r in result:
    print(f"Temporary Repair ID: {r[0]}, repair_id: {r[1]}")
    print(f"  photos: {r[2]}")
    print()

print('=== Checking for ANY photos with www.sstcp.top ===')
result = db.execute(text("SELECT id, work_id, photos FROM spot_work WHERE photos LIKE '%sstcp.top%'")).fetchall()
for r in result:
    print(f"Spot Work ID: {r[0]}, work_id: {r[1]}")
    print(f"  photos: {r[2]}")
    print()

result = db.execute(text("SELECT id, inspection_id, photos FROM periodic_inspection_record WHERE photos LIKE '%sstcp.top%'")).fetchall()
for r in result:
    print(f"Inspection Record ID: {r[0]}, inspection_id: {r[1]}")
    print(f"  photos: {r[2]}")
    print()

result = db.execute(text("SELECT id, repair_id, photos FROM temporary_repair WHERE photos LIKE '%sstcp.top%'")).fetchall()
for r in result:
    print(f"Temporary Repair ID: {r[0]}, repair_id: {r[1]}")
    print(f"  photos: {r[2]}")
    print()

db.close()
