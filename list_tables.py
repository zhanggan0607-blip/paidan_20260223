"""
查询本机PostgreSQL数据库中的表名
"""
import psycopg2

conn = psycopg2.connect(
    host="localhost",
    database="tq",
    user="postgres",
    password="123456",
    port=5432
)
cursor = conn.cursor()

cursor.execute("""
    SELECT table_name FROM information_schema.tables 
    WHERE table_schema = 'public'
    ORDER BY table_name
""")
tables = cursor.fetchall()
print("数据库中的表:")
for t in tables:
    print(f"  - {t[0]}")

cursor.close()
conn.close()
