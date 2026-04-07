import psycopg2

conn = psycopg2.connect(host='localhost', dbname='sstcp', user='postgres', password='sstcp2024')
cur = conn.cursor()

print('=== 检查是否包含 https:// 或 http:// ===')
print()

print('--- spot_work.photos ---')
cur.execute("SELECT id, work_id, photos FROM spot_work WHERE photos LIKE '%https://%' OR photos LIKE '%http://%'")
for row in cur.fetchall():
    print(f'ID: {row[0]}, work_id: {row[1]}, photos: {row[2]}')

print()
print('--- inspection_records.photos ---')
cur.execute("SELECT id, photos FROM inspection_records WHERE photos LIKE '%https://%' OR photos LIKE '%http://%'")
for row in cur.fetchall():
    print(f'ID: {row[0]}, photos: {row[1]}')

print()
print('--- maintenance_logs.photos ---')
cur.execute("SELECT id, photos FROM maintenance_logs WHERE photos LIKE '%https://%' OR photos LIKE '%http://%'")
for row in cur.fetchall():
    print(f'ID: {row[0]}, photos: {row[1]}')

print()
print('--- spot_work.signature ---')
cur.execute("SELECT id, work_id, signature FROM spot_work WHERE signature LIKE '%https://%' OR signature LIKE '%http://%'")
for row in cur.fetchall():
    print(f'ID: {row[0]}, work_id: {row[1]}, signature: {row[2][:200] if row[2] else None}')

print()
print('--- maintenance_logs.signature ---')
cur.execute("SELECT id, signature FROM maintenance_logs WHERE signature LIKE '%https://%' OR signature LIKE '%http://%'")
for row in cur.fetchall():
    print(f'ID: {row[0]}, signature: {row[1][:200] if row[1] else None}')

cur.close()
conn.close()
