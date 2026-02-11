import psycopg2

conn = psycopg2.connect(
    host="localhost",
    port=5432,
    user="postgres",
    password="123456",
    database="tq"
)
cursor = conn.cursor()

cursor.execute("SELECT COUNT(*) FROM project_info")
count = cursor.fetchone()[0]
print(f"PG数据库中 project_info 表的总记录数: {count}")

cursor.execute("SELECT id, project_id, project_name FROM project_info ORDER BY id")
rows = cursor.fetchall()

print(f"\nPG数据库中的所有项目:")
for row in rows:
    print(f"  ID: {row[0]}, 项目编号: {row[1]}, 项目名称: {row[2]}")

conn.close()