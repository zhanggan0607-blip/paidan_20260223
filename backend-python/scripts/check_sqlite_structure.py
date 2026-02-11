import sqlite3

db_path = "tq.db"
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

cursor.execute("PRAGMA table_info(project_info)")
columns = cursor.fetchall()

print("project_info 表结构:")
for col in columns:
    print(f"  - {col[1]}: {col[2]} (nullable: {not col[3]}, primary_key: {col[5]})")

conn.close()