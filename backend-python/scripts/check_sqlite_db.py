import sqlite3

db_path = "tq.db"
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

cursor.execute("SELECT COUNT(*) FROM project_info")
count = cursor.fetchone()[0]

print(f"SQLite 数据库 (tq.db) 中的项目数量: {count}")

if count > 0:
    cursor.execute("SELECT id, project_id, project_name FROM project_info ORDER BY id")
    rows = cursor.fetchall()
    print("\nSQLite 数据库中的项目:")
    for row in rows:
        print(f"  ID: {row[0]}, 项目编号: {row[1]}, 项目名称: {row[2]}")
else:
    print("SQLite 数据库为空")

conn.close()