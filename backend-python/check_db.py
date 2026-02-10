import sqlite3

conn = sqlite3.connect('tq.db')
cursor = conn.cursor()

cursor.execute('SELECT name FROM sqlite_master WHERE type="table"')
tables = cursor.fetchall()

print("数据库中的表:")
for table in tables:
    print(f"  - {table[0]}")

if not tables:
    print("  (空)")

conn.close()
