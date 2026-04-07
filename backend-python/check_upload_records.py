import psycopg2

conn = psycopg2.connect(
    host="pgm-uf6cml154nbjz51y.pg.rds.aliyuncs.com",
    database="tq",
    user="postgres",
    password="Lily421020#"
)

cur = conn.cursor()

print("=== Work order info ===")
cur.execute("SELECT id, repair_id, photos, created_at, updated_at FROM temporary_repair WHERE repair_id = 'WX-LJ-2025-084A-SH-20260402-0050'")
row = cur.fetchone()
if row:
    work_order_id = row[0]
    print(f"ID: {work_order_id}")
    print(f"repair_id: {row[1]}")
    print(f"photos: {row[2]}")
    print(f"created_at: {row[3]}")
    print(f"updated_at: {row[4]}")

print("\n=== Uploaded files on 20260402 ===")
cur.execute("SELECT id, file_id, file_path, file_size, original_filename, created_at FROM uploaded_file WHERE upload_date = '20260402' ORDER BY id DESC LIMIT 20")
rows = cur.fetchall()
print(f"Found {len(rows)} files uploaded on 20260402")
for row in rows:
    print(f"  ID={row[0]}, file_id={row[1]}, path={row[2]}, size={row[3]}, filename={row[4]}, created_at={row[5]}")

print("\n=== All uploaded files count ===")
cur.execute("SELECT COUNT(*) FROM uploaded_file")
print(f"Total files in database: {cur.fetchone()[0]}")

print("\n=== Recent uploaded files (last 10) ===")
cur.execute("SELECT id, file_id, file_path, upload_date, created_at FROM uploaded_file ORDER BY id DESC LIMIT 10")
rows = cur.fetchall()
for row in rows:
    print(f"  ID={row[0]}, upload_date={row[3]}, path={row[2]}, created_at={row[4]}")

cur.close()
conn.close()
