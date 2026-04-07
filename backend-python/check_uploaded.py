import psycopg2

conn = psycopg2.connect(
    host="pgm-uf6cml154nbjz51y.pg.rds.aliyuncs.com",
    database="tq",
    user="postgres",
    password="Lily421020#"
)

cur = conn.cursor()

print("=== Work order WX-LJ-2025-084A-SH-20260402-0050 ===")
cur.execute("SELECT id, repair_id, photos, status FROM temporary_repair WHERE repair_id = 'WX-LJ-2025-084A-SH-20260402-0050'")
row = cur.fetchone()
if row:
    print(f"ID: {row[0]}")
    print(f"repair_id: {row[1]}")
    print(f"photos: {row[2]}")
    print(f"status: {row[3]}")

print("\n=== Uploaded files on 20260402 ===")
cur.execute("SELECT id, file_id, file_path, file_size, upload_date, created_at FROM uploaded_file WHERE upload_date = '20260402' ORDER BY id DESC LIMIT 20")
rows = cur.fetchall()
print(f"Found {len(rows)} files uploaded on 20260402")
for row in rows:
    print(f"  ID={row[0]}, path={row[2]}, size={row[3]}, created_at={row[5]}")

print("\n=== Recent uploaded files (last 20) ===")
cur.execute("SELECT id, file_id, file_path, file_size, upload_date, created_at FROM uploaded_file ORDER BY id DESC LIMIT 20")
rows = cur.fetchall()
for row in rows:
    print(f"  ID={row[0]}, upload_date={row[4]}, path={row[2]}, created_at={row[5]}")

print("\n=== Total uploaded files count ===")
cur.execute("SELECT COUNT(*) FROM uploaded_file")
print(f"Total files in database: {cur.fetchone()[0]}")

cur.close()
conn.close()
