import psycopg2
import sys

try:
    conn = psycopg2.connect(
        host="localhost",
        port=5432,
        user="postgres",
        password="changeme",
        database="tq"
    )
    cursor = conn.cursor()
    
    cursor.execute("SELECT version()")
    version = cursor.fetchone()[0]
    print(f"✅ PostgreSQL 连接成功")
    print(f"版本: {version.split(',')[0]}")
    
    cursor.execute("SELECT COUNT(*) FROM project_info")
    count = cursor.fetchone()[0]
    print(f"project_info 表中的记录数: {count}")
    
    if count > 0:
        cursor.execute("SELECT id, project_id, project_name FROM project_info ORDER BY id")
        rows = cursor.fetchall()
        print("\nPostgreSQL 数据库中的项目:")
        for row in rows:
            print(f"  ID: {row[0]}, 项目编号: {row[1]}, 项目名称: {row[2]}")
    
    conn.close()
    
except psycopg2.OperationalError as e:
    print(f"❌ PostgreSQL 连接失败: {str(e)}")
    print("\n请检查:")
    print("1. PostgreSQL 服务是否已启动")
    print("2. 连接信息是否正确 (host: localhost, port: 5432, user: postgres, database: tq)")
    print("3. 密码是否正确 (changeme)")
    sys.exit(1)
except Exception as e:
    print(f"❌ 发生错误: {str(e)}")
    sys.exit(1)