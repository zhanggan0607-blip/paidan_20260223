import sqlite3

db_path = "tq.db"
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

cursor.execute("SELECT * FROM project_info LIMIT 1")
rows = cursor.fetchall()

if rows:
    print(f"表中有 {len(rows)} 条数据")
    for row in rows:
        print(f"  - {row}")
else:
    print("表为空")

conn.close()