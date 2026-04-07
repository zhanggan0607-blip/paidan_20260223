import psycopg2

conn = psycopg2.connect('postgresql://zhanggan:Lily421020%23@pgm-uf6cml154nbjz51y6o.pg.rds.aliyuncs.com:5432/tq')
cur = conn.cursor()

print('=== 检查所有表的图片字段 ===')
print()

print('--- spot_work.photos ---')
cur.execute("SELECT id, work_id, photos FROM spot_work WHERE photos IS NOT NULL AND photos != '[]' LIMIT 3")
for row in cur.fetchall():
    print(f'ID: {row[0]}, work_id: {row[1]}, photos: {row[2]}')

print()
print('--- periodic_inspection_record.photos ---')
cur.execute("SELECT id, photos FROM periodic_inspection_record WHERE photos IS NOT NULL AND photos != '[]' LIMIT 3")
for row in cur.fetchall():
    print(f'ID: {row[0]}, photos: {row[1]}')

print()
print('--- temporary_repair.photos ---')
cur.execute("SELECT id, photos FROM temporary_repair WHERE photos IS NOT NULL AND photos != '[]' LIMIT 3")
for row in cur.fetchall():
    print(f'ID: {row[0]}, photos: {row[1]}')

print()
print('--- maintenance_log.photos ---')
cur.execute("SELECT id, photos FROM maintenance_log WHERE photos IS NOT NULL AND photos != '[]' LIMIT 3")
for row in cur.fetchall():
    print(f'ID: {row[0]}, photos: {row[1]}')

print()
print('--- 检查是否包含 https:// 或 http:// ---')
cur.execute("SELECT id, work_id, photos FROM spot_work WHERE photos LIKE '%https://%' OR photos LIKE '%http://%'")
rows = cur.fetchall()
print(f'spot_work: {len(rows)} records with full URL')
for row in rows:
    print(f'  ID: {row[0]}, work_id: {row[1]}, photos: {row[2]}')

cur.execute("SELECT id, photos FROM periodic_inspection_record WHERE photos LIKE '%https://%' OR photos LIKE '%http://%'")
rows = cur.fetchall()
print(f'periodic_inspection_record: {len(rows)} records with full URL')
for row in rows:
    print(f'  ID: {row[0]}, photos: {row[1]}')

cur.execute("SELECT id, photos FROM temporary_repair WHERE photos LIKE '%https://%' OR photos LIKE '%http://%'")
rows = cur.fetchall()
print(f'temporary_repair: {len(rows)} records with full URL')
for row in rows:
    print(f'  ID: {row[0]}, photos: {row[1]}')

cur.execute("SELECT id, photos FROM maintenance_log WHERE photos LIKE '%https://%' OR photos LIKE '%http://%'")
rows = cur.fetchall()
print(f'maintenance_log: {len(rows)} records with full URL')
for row in rows:
    print(f'  ID: {row[0]}, photos: {row[1]}')

cur.close()
conn.close()
