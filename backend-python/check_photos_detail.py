import psycopg2
import json

conn = psycopg2.connect(
    host="pgm-uf6cml154nbjz51y.pg.rds.aliyuncs.com",
    database="tq",
    user="postgres",
    password="Lily421020#"
)

cur = conn.cursor()

print("=== Check uploaded files on 20260402 ===")
cur.execute("SELECT id, file_id, file_path, file_size FROM uploaded_file WHERE upload_date = '20260402' ORDER BY id DESC LIMIT 10")
rows = cur.fetchall()
print(f"Found {len(rows)} files")
for row in rows:
    print(f"  ID={row[0]}, path={row[2]}, size={row[3]}")

print("\n=== Check work order WX-LJ-2025-084A-SH-20260402-0050 ===")
cur.execute("SELECT id, repair_id, photos, status FROM temporary_repair WHERE repair_id = 'WX-LJ-2025-084A-SH-20260402-0050'")
row = cur.fetchone()
if row:
    print(f"ID: {row[0]}")
    print(f"repair_id: {row[1]}")
    print(f"status: {row[3]}")
    photos = row[2]
    print(f"photos raw: {photos}")
    print(f"photos length: {len(photos) if photos else 0}")
    if photos and len(photos) > 2:
        try:
            photos_list = json.loads(photos)
            print(f"parsed photos count: {len(photos_list)}")
            for i, p in enumerate(photos_list[:3]):
                print(f"  photo {i+1}: {p[:100]}...")
        except Exception as e:
            print(f"parse error: {e}")

cur.close()
conn.close()
