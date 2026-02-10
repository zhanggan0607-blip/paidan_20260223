import psycopg2
from psycopg2 import sql
import os

def setup_database():
    """设置 PostgreSQL 数据库"""
    
    # 数据库配置
    db_host = "localhost"
    db_port = 5432
    db_user = "postgres"
    db_name = "tq"
    
    # 默认密码（请根据实际情况修改）
    db_password = os.getenv("DB_PASSWORD", "123456")
    
    print(f"正在连接到 PostgreSQL 服务器...")
    print(f"主机: {db_host}")
    print(f"端口: {db_port}")
    print(f"用户: {db_user}")
    print(f"数据库: {db_name}")
    print()
    
    try:
        # 连接到 PostgreSQL（默认数据库 postgres）
        conn = psycopg2.connect(
            host=db_host,
            port=db_port,
            user=db_user,
            password=db_password,
            database="postgres"
        )
        conn.autocommit = True
        cursor = conn.cursor()
        
        print("✅ 连接成功！")
        print()
        
        # 检查数据库是否存在
        cursor.execute(sql.SQL("SELECT 1 FROM pg_database WHERE datname = %s"), (db_name,))
        exists = cursor.fetchone()
        
        if exists:
            print(f"ℹ️  数据库 '{db_name}' 已存在")
        else:
            print(f"🔨 正在创建数据库 '{db_name}'...")
            cursor.execute(sql.SQL("CREATE DATABASE %s"), (sql.Identifier(db_name),))
            print(f"✅ 数据库 '{db_name}' 创建成功！")
        
        print()
        print("✅ 数据库设置完成！")
        print()
        print("现在您可以更新 .env 文件中的密码并启动后端服务。")
        
        cursor.close()
        conn.close()
        
    except psycopg2.OperationalError as e:
        print(f"❌ 连接错误: {e}")
        print()
        print("请检查：")
        print("1. PostgreSQL 服务是否正在运行")
        print("2. 密码是否正确（默认密码是 '123456'）")
        print("3. 端口是否正确（默认端口是 5432）")
        print()
        print("如果密码不是 '123456'，请设置环境变量：")
        print("  $env:DB_PASSWORD=您的密码 python setup_database.py")
    except Exception as e:
        print(f"❌ 错误: {e}")

if __name__ == "__main__":
    setup_database()
