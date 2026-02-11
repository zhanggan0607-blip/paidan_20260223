import psycopg2

conn = psycopg2.connect(
    host="localhost",
    port=5432,
    user="postgres",
    password="123456",
    database="tq"
)
cursor = conn.cursor()

cursor.execute("SELECT id, project_id, project_name, created_at FROM project_info ORDER BY id")
rows = cursor.fetchall()

print(f"数据库中的所有项目（按 ID 排序）:")
print("=" * 80)
for row in rows:
    print(f"ID: {row[0]:3d}, 项目编号: {row[1]:15s}, 项目名称: {row[2]:30s}, 创建时间: {row[3]}")

print(f"\n总记录数: {len(rows)}")

conn.close()