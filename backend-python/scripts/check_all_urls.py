import psycopg2

conn = psycopg2.connect('postgresql://zhanggan:Lily421020%23@pgm-uf6cml154nbjz51y6o.pg.rds.aliyuncs.com:5432/tq')
cur = conn.cursor()

print('=== 检查所有可能存储URL的字段 ===')
print()

print('--- spot_work 所有photos ---')
cur.execute("SELECT id, work_id, photos FROM spot_work WHERE photos IS NOT NULL AND photos != '[]'")
for row in cur.fetchall():
    print(f'ID: {row[0]}, work_id: {row[1]}, photos: {row[2]}')

print()
print('--- periodic_inspection_record 所有photos ---')
cur.execute("SELECT id, photos FROM periodic_inspection_record WHERE photos IS NOT NULL AND photos != '[]'")
for row in cur.fetchall():
    print(f'ID: {row[0]}, photos: {row[1]}')

print()
print('--- temporary_repair 所有photos ---')
cur.execute("SELECT id, photos FROM temporary_repair WHERE photos IS NOT NULL AND photos != '[]'")
for row in cur.fetchall():
    print(f'ID: {row[0]}, photos: {row[1]}')

print()
print('--- spot_work_worker 身份证照片 ---')
cur.execute("SELECT id, name, id_card_front, id_card_back FROM spot_work_worker WHERE id_card_front IS NOT NULL OR id_card_back IS NOT NULL LIMIT 5")
for row in cur.fetchall():
    print(f'ID: {row[0]}, name: {row[1]}, front: {row[2][:100] if row[2] else None}, back: {row[3][:100] if row[3] else None}')

cur.close()
conn.close()
