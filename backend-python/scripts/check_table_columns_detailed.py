import sqlite3

db_path = "tq.db"
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

cursor.execute("PRAGMA table_info(project_info)")
columns = cursor.fetchall()

print(f"project_info 表共有 {len(columns)} 个字段:")
for i, col in enumerate(columns, 1):
    print(f"  {i}. {col[1]}: {col[2]} (type: {col[2]}, pk: {col[5]})")

conn.close()