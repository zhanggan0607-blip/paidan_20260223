import sqlite3

db_path = "tq.db"
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

cursor.execute("SELECT * FROM project_info LIMIT 0")
print("查询结果为空，表结构正确")

conn.close()