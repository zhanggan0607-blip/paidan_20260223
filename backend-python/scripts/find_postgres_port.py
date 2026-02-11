import psycopg2
import sys

ports_to_try = [5432, 5433, 5434]

for port in ports_to_try:
    try:
        conn = psycopg2.connect(
            host="localhost",
            port=port,
            user="postgres",
            password="changeme",
            database="postgres"
        )
        cursor = conn.cursor()
        cursor.execute("SELECT version()")
        version = cursor.fetchone()[0]
        print(f"✅ PostgreSQL 连接成功 (端口: {port})")
        print(f"版本: {version.split(',')[0]}")
        
        cursor.execute("SELECT datname FROM pg_database WHERE datistemplate = false")
        databases = cursor.fetchall()
        print(f"\n数据库列表:")
        for db in databases:
            print(f"  - {db[0]}")
        
        conn.close()
        print(f"\n✅ 找到正确的端口: {port}")
        sys.exit(0)
    except psycopg2.OperationalError as e:
        print(f"❌ 端口 {port} 连接失败: {str(e)[:50]}")
        continue

print("\n❌ 所有端口连接失败")
print("请检查 PostgreSQL 的配置和密码")
sys.exit(1)