import psycopg2
conn = psycopg2.connect(host='localhost', database='tq', user='postgres', password='123456', port=5432)
cursor = conn.cursor()
cursor.execute("""
    SELECT column_name FROM information_schema.columns 
    WHERE table_name = 'periodic_inspection' ORDER BY ordinal_position
""")
print('periodic_inspection columns:', [r[0] for r in cursor.fetchall()])
cursor.execute("""
    SELECT column_name FROM information_schema.columns 
    WHERE table_name = 'temporary_repair' ORDER BY ordinal_position
""")
print('temporary_repair columns:', [r[0] for r in cursor.fetchall()])
cursor.execute("""
    SELECT column_name FROM information_schema.columns 
    WHERE table_name = 'spot_work' ORDER BY ordinal_position
""")
print('spot_work columns:', [r[0] for r in cursor.fetchall()])
cursor.close()
conn.close()
