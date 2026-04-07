import psycopg2

conn = psycopg2.connect(
    host="pgm-uf6cml154nbjz51y.pg.rds.aliyuncs.com",
    database="tq",
    user="postgres",
    password="Lily421020#"
)

cur = conn.cursor()

print("=== Check uploaded files on 20260402 ===")
cur.execute("SELECT id, file_id, original_filename, file_path, file_size FROM uploaded_file WHERE upload_date = '20260402' ORDER BY id DESC LIMIT 20")
rows = cur.fetchall()
print(f"Found {len(rows)} files")
for row in rows:
    print(f"  ID={row[0]}, path={row[3]}, size={row[4]}")

print("\n=== Check work order photos ===")
cur.execute("SELECT id, repair_id, photos FROM temporary_repair WHERE repair_id = 'WX-LJ-2025-084A-SH-20260402-0050'")
row = cur.fetchone()
if row:
    print(f"ID: {row[0]}")
    print(f"repair_id: {row[1]}")
    print(f"photos: {row[2]}")

cur.close()
conn.close()
