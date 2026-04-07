import psycopg2
import json

conn = psycopg2.connect(
    host="pgm-uf6cml154nbjz51y.pg.rds.aliyuncs.com",
    database="tq",
    user="postgres",
    password="Lily421020#"
)

cur = conn.cursor()

print("=== Operation logs ===")
cur.execute("SELECT id, operation_type_name, operator_name, remark, created_at FROM work_order_operation_log WHERE work_order_no = 'WX-LJ-2025-084A-SH-20260402-0050' ORDER BY created_at")
rows = cur.fetchall()
print(f"Found {len(rows)} logs")
for row in rows:
    print(f"  [{row[4]}] {row[1]} by {row[2]}: {row[3]}")

print("\n=== Uploaded files on 20260402 ===")
cur.execute("SELECT id, file_path, file_size, original_filename, created_at FROM uploaded_file WHERE upload_date = '20260402' ORDER BY id DESC LIMIT 20")
rows = cur.fetchall()
print(f"Found {len(rows)} files")
for row in rows:
    print(f"  [{row[4]}] ID={row[0]}, path={row[1]}, size={row[2]}, filename={row[3]}")

print("\n=== Total uploaded files ===")
cur.execute("SELECT COUNT(*) FROM uploaded_file")
print(f"Total: {cur.fetchone()[0]}")

cur.close()
conn.close()
