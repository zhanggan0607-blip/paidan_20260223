import sqlite3

db_path = "tq.db"
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

cursor.execute("SELECT id, project_id, project_name FROM project_info ORDER BY id")
rows = cursor.fetchall()

print(f"数据库中的项目信息（共 {len(rows)} 条）:")
print("-" * 80)
for row in rows:
    print(f"ID: {row[0]}, 项目编号: {row[1]}, 项目名称: {row[2]}")

conn.close()