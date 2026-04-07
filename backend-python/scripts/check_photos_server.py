import psycopg2

conn = psycopg2.connect(host='localhost', dbname='sstcp', user='postgres', password='sstcp2024')
cur = conn.cursor()

print('=== inspection_records ===')
cur.execute("SELECT id, photos FROM inspection_records WHERE photos IS NOT NULL AND photos != '[]' LIMIT 5")
for row in cur.fetchall():
    print(f'ID: {row[0]}, photos: {row[1][:200]}')

print()
print('=== spot_work ===')
cur.execute("SELECT id, photos FROM spot_work WHERE photos IS NOT NULL AND photos != '[]' LIMIT 5")
for row in cur.fetchall():
    print(f'ID: {row[0]}, photos: {row[1][:200]}')

print()
print('=== maintenance_logs ===')
cur.execute("SELECT id, photos FROM maintenance_logs WHERE photos IS NOT NULL AND photos != '[]' LIMIT 5")
for row in cur.fetchall():
    print(f'ID: {row[0]}, photos: {row[1][:200]}')

cur.close()
conn.close()
