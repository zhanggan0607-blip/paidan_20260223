import psycopg2
import sys

try:
    conn = psycopg2.connect(
        host="localhost",
        port=5432,
        user="postgres",
        password="123456",
        database="postgres"
    )
    conn.autocommit = True
    cursor = conn.cursor()
    
    cursor.execute("SELECT 1 FROM pg_database WHERE datname = 'tq'")
    exists = cursor.fetchone()
    
    if exists:
        print("✅ 数据库 'tq' 已存在")
    else:
        cursor.execute("CREATE DATABASE tq")
        print("✅ 数据库 'tq' 创建成功")
    
    conn.close()
    
    conn = psycopg2.connect(
        host="localhost",
        port=5432,
        user="postgres",
        password="123456",
        database="tq"
    )
    conn.autocommit = True
    cursor = conn.cursor()
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS project_info (
            id SERIAL PRIMARY KEY,
            project_id VARCHAR(50) NOT NULL UNIQUE,
            project_name VARCHAR(200) NOT NULL,
            completion_date TIMESTAMP NOT NULL,
            maintenance_end_date TIMESTAMP NOT NULL,
            maintenance_period VARCHAR(20) NOT NULL,
            client_name VARCHAR(100) NOT NULL,
            address VARCHAR(200) NOT NULL,
            project_abbr VARCHAR(10),
            client_contact VARCHAR(50),
            client_contact_position VARCHAR(20),
            client_contact_info VARCHAR(50),
            created_at TIMESTAMP,
            updated_at TIMESTAMP
        )
    """)
    print("✅ 表 'project_info' 创建成功")
    
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_project_info_id ON project_info(project_id);
        CREATE INDEX IF NOT EXISTS idx_project_info_client_name ON project_info(client_name);
        CREATE INDEX IF NOT EXISTS idx_project_info_project_name ON project_info(project_name);
    """)
    print("✅ 索引创建成功")
    
    conn.close()
    print("\n✅ PostgreSQL 数据库和表结构创建完成")
    
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