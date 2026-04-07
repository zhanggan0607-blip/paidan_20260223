import psycopg2
import json

conn = psycopg2.connect(
    host="pgm-uf6cml154nbjz51y.pg.rds.aliyuncs.com",
    database="tq",
    user="postgres",
    password="Lily421020#"
)

cur = conn.cursor()

print("=== Query work order LJ-2025-084A-SH ===")
cur.execute("SELECT id, repair_id, photos FROM temporary_repair WHERE repair_id = 'LJ-2025-084A-SH'")
row = cur.fetchone()
if row:
    print(f"ID: {row[0]}")
    print(f"repair_id: {row[1]}")
    photos = row[2]
    print(f"photos type: {type(photos)}")
    print(f"photos length: {len(photos) if photos else 0}")
    if photos:
        print(f"photos preview (first 300 chars): {photos[:300]}")
        try:
            photos_list = json.loads(photos)
            print(f"parsed count: {len(photos_list)}")
            if photos_list:
                for i, p in enumerate(photos_list[:3]):
                    print(f"photo {i+1} preview (first 100 chars): {p[:100]}")
        except Exception as e:
            print(f"parse error: {e}")
else:
    print("Not found")

cur.close()
conn.close()
