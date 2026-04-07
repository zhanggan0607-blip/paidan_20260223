import psycopg2

conn = psycopg2.connect('postgresql://zhanggan:Lily421020%23@pgm-uf6cml154nbjz51y6o.pg.rds.aliyuncs.com:5432/tq')
cur = conn.cursor()

print('=== 列出所有表 ===')
cur.execute("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'")
for row in cur.fetchall():
    print(row[0])

cur.close()
conn.close()
