import psycopg2
import json

conn = psycopg2.connect(
    host="pgm-uf6cml154nbjz51y.pg.rds.aliyuncs.com",
    database="tq",
    user="postgres",
    password="Lily421020#"
)

cur = conn.cursor()

print("=== Work orders with photos ===")
cur.execute("SELECT id, repair_id, LENGTH(photos) FROM temporary_repair WHERE photos IS NOT NULL AND jsonb_array_length(photos::jsonb) > 0 ORDER by id desc limit 5")
rows = cur.fetchall()
print(f"Found {len(rows)} work orders with photos")
for row in rows:
    print(f"  ID={row[0]}, repair_id={row[1]}, photos_len={row[2]}")

print("\n=== Operation logs for WX-LJ-2025-084A-SH-20260402-0050 ===")
cur.execute("SELECT * FROM work_order_operation_log WHERE work_order_no = 'WX-LJ-2025-084A-SH-20260402-0050' ORDER by created_at")
rows = cur.fetchall()
print(f"Found {len(rows)} operation logs")
for row in rows:
    print(f"  {row}")

cur.close()
conn.close()
