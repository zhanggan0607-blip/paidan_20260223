import sys
sys.path.insert(0, '/app')
from sqlalchemy import text
from app.database import SessionLocal
db = SessionLocal()

print('=== Checking for ANY URL patterns in photos ===')

# Check spot_work
result = db.execute(text("SELECT id, work_id, photos FROM spot_work WHERE photos IS NOT NULL")).fetchall()
for r in result:
    photos_str = r[2]
    if photos_str and len(photos_str) > 10:
        print(f"Spot Work ID: {r[0]}, work_id: {r[1]}")
        print(f"  RAW photos string: {repr(photos_str)}")
        # Check if contains http
        if 'http' in photos_str.lower():
            print("  WARNING: Contains 'http'!")
        print()

# Check periodic_inspection_record  
result = db.execute(text("SELECT id, inspection_id, photos FROM periodic_inspection_record WHERE photos IS NOT NULL")).fetchall()
for r in result:
    photos_str = r[2]
    if photos_str and len(photos_str) > 10:
        print(f"Inspection Record ID: {r[0]}, inspection_id: {r[1]}")
        print(f"  RAW photos string: {repr(photos_str)}")
        if 'http' in photos_str.lower():
            print("  WARNING: Contains 'http'!")
        print()

db.close()
