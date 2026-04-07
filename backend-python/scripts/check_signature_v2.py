import psycopg2

conn = psycopg2.connect('postgresql://zhanggan:Lily421020%23@pgm-uf6cml154nbjz51y6o.pg.rds.aliyuncs.com:5432/tq')
cur = conn.cursor()

print('=== 检查签字字段 ===')
print()

print('--- spot_work.signature (前5条) ---')
cur.execute("SELECT id, work_id, signature FROM spot_work WHERE signature IS NOT NULL AND signature != '' LIMIT 5")
for row in cur.fetchall():
    sig = row[2][:300] if row[2] else None
    print(f'ID: {row[0]}, work_id: {row[1]}')
    print(f'signature: {sig}')
    print()

print()
print('--- maintenance_logs.signature (前5条) ---')
cur.execute("SELECT id, signature FROM maintenance_logs WHERE signature IS NOT NULL AND signature != '' LIMIT 5")
for row in cur.fetchall():
    sig = row[1][:300] if row[1] else None
    print(f'ID: {row[0]}')
    print(f'signature: {sig}')
    print()

print()
print('--- 检查签字中是否包含 sstcp.top ---')
cur.execute("SELECT id, work_id, signature FROM spot_work WHERE signature LIKE '%sstcp.top%'")
for row in cur.fetchall():
    print(f'Found in spot_work: ID={row[0]}, work_id={row[1]}, signature={row[2][:200]}')

cur.execute("SELECT id, signature FROM maintenance_logs WHERE signature LIKE '%sstcp.top%'")
for row in cur.fetchall():
    print(f'Found in maintenance_logs: ID={row[0]}, signature={row[1][:200]}')

cur.close()
conn.close()
