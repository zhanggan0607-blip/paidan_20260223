import psycopg2
import json

conn = psycopg2.connect(
    host="pgm-uf6cml154nbjz51y.pg.rds.aliyuncs.com",
    database="tq",
    user="postgres",
    password="Lily421020#"
)

cur = conn.cursor()

print("=== Search for work orders with photos ===")

cur.execute("SELECT id, repair_id, status, LENGTH(photos) as photos_len FROM temporary_repair WHERE photos IS NOT NULL AND LENGTH(photos) > 10 ORDER BY id DESC LIMIT 10")
rows = cur.fetchall()
print(f"temporary_repair with photos: {len(rows)} rows")
for row in rows:
    print(f"  ID={row[0]}, repair_id={row[1]}, status={row[2]}, photos_len={row[3]}")

print("\n=== Check specific work order ===")
cur.execute("SELECT id, repair_id, photos, status FROM temporary_repair WHERE repair_id = 'WX-LJ-2025-084A-SH-20260402-0050'")
row = cur.fetchone()
if row:
    print(f"ID: {row[0]}")
    print(f"repair_id: {row[1]}")
    print(f"status: {row[3]}")
    photos = row[2]
    print(f"photos type: {type(photos)}")
    print(f"photos length: {len(photos) if photos else 0}")
    if photos and len(photos) > 2:
        print(f"photos preview: {photos[:300]}")
        try:
            photos_list = json.loads(photos)
            print(f"parsed count: {len(photos_list)}")
        except Exception as e:
            print(f"parse error: {e}")
else:
    print("Not found")

cur.close()
conn.close()
