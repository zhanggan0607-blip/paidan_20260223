import sqlite3

db_path = "tq.db"
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

cursor.execute("SELECT * FROM project_info")
rows = cursor.fetchall()

print(f"数据库中的项目信息（共 {len(rows)} 条）:")
print("-" * 100)
for row in rows:
    print(f"ID: {row[0]}")
    print(f"  项目编号: {row[1]}")
    print(f"  项目名称: {row[2]}")
    print(f"  完工日期: {row[3]}")
    print(f"  维保结束日期: {row[4]}")
    print(f"  维保周期: {row[5]}")
    print(f"  客户名称: {row[6]}")
    print(f"  地址: {row[7]}")
    print(f"  项目简称: {row[8]}")
    print(f"  客户联系人: {row[9]}")
    print(f"  客户联系人职位: {row[10]}")
    print(f"  客户联系方式: {row[11]}")
    print(f"  创建时间: {row[12]}")
    print(f"  更新时间: {row[13]}")
    print("-" * 100)

conn.close()