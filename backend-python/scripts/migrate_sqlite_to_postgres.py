import sqlite3
import psycopg2
from datetime import datetime

sqlite_db_path = "tq.db"
pg_conn = psycopg2.connect(
    host="localhost",
    port=5432,
    user="postgres",
    password="123456",
    database="tq"
)
pg_cursor = pg_conn.cursor()

sqlite_conn = sqlite3.connect(sqlite_db_path)
sqlite_cursor = sqlite_conn.cursor()

print("开始从 SQLite 迁移数据到 PostgreSQL...")

sqlite_cursor.execute("SELECT * FROM project_info")
rows = sqlite_cursor.fetchall()

print(f"找到 {len(rows)} 条记录需要迁移")

columns = [
    'project_id', 'project_name', 'completion_date', 'maintenance_end_date',
    'maintenance_period', 'client_name', 'address', 'project_abbr',
    'client_contact', 'client_contact_position', 'client_contact_info',
    'created_at', 'updated_at'
]

migrated_count = 0
for row in rows:
    id = row[0]
    data = row[1:]
    
    pg_cursor.execute("SELECT id FROM project_info WHERE project_id = %s", (data[0],))
    if pg_cursor.fetchone():
        print(f"  跳过已存在的项目: {data[0]}")
        continue
    
    try:
        pg_cursor.execute("""
            INSERT INTO project_info (
                project_id, project_name, completion_date, maintenance_end_date,
                maintenance_period, client_name, address, project_abbr,
                client_contact, client_contact_position, client_contact_info,
                created_at, updated_at
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, data)
        migrated_count += 1
        print(f"  ✅ 迁移: {data[0]} - {data[1]}")
    except Exception as e:
        print(f"  ❌ 迁移失败 {data[0]}: {str(e)}")

pg_conn.commit()

pg_cursor.execute("SELECT COUNT(*) FROM project_info")
pg_count = pg_cursor.fetchone()[0]

print(f"\n✅ 迁移完成！")
print(f"  - SQLite 原始记录数: {len(rows)}")
print(f"  - PostgreSQL 迁移记录数: {migrated_count}")
print(f"  - PostgreSQL 总记录数: {pg_count}")

pg_cursor.execute("SELECT id, project_id, project_name FROM project_info ORDER BY id")
pg_rows = pg_cursor.fetchall()

print(f"\nPostgreSQL 数据库中的项目:")
for row in pg_rows:
    print(f"  ID: {row[0]}, 项目编号: {row[1]}, 项目名称: {row[2]}")

sqlite_conn.close()
pg_conn.close()

print("\n✅ 数据迁移完成！")