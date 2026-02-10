import psycopg2
from psycopg2 import sql
import os

def check_database():
    """检查数据库状态"""
    
    # 数据库配置
    db_host = "localhost"
    db_port = 5432
    db_user = "postgres"
    db_name = "tq"
    db_password = "123456"
    
    print(f"正在检查数据库 '{db_name}'...")
    print()
    
    try:
        # 连接到数据库
        conn = psycopg2.connect(
            host=db_host,
            port=db_port,
            user=db_user,
            password=db_password,
            database=db_name
        )
        conn.autocommit = True
        cursor = conn.cursor()
        
        print("✅ 连接成功！")
        print()
        
        # 检查表
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
            ORDER BY table_name;
        """)
        tables = cursor.fetchall()
        
        if tables:
            print(f"ℹ️  数据库中的表 ({len(tables)} 个）：")
            for table in tables:
                print(f"  - {table[0]}")
        else:
            print("⚠️  数据库中没有表")
            print()
            print("正在创建必要的表...")
            
            # 创建 maintenance_plan 表
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS maintenance_plan (
                    id BIGSERIAL PRIMARY KEY,
                    plan_id VARCHAR(50) UNIQUE NOT NULL,
                    plan_name VARCHAR(200) NOT NULL,
                    project_id VARCHAR(50) NOT NULL,
                    plan_type VARCHAR(20) NOT NULL,
                    equipment_id VARCHAR(50) NOT NULL,
                    equipment_name VARCHAR(200) NOT NULL,
                    equipment_model VARCHAR(100),
                    equipment_location VARCHAR(200),
                    plan_start_date TIMESTAMP NOT NULL,
                    plan_end_date TIMESTAMP NOT NULL,
                    execution_date TIMESTAMP,
                    next_maintenance_date TIMESTAMP,
                    responsible_person VARCHAR(50) NOT NULL,
                    responsible_department VARCHAR(100),
                    contact_info VARCHAR(50),
                    maintenance_content TEXT NOT NULL,
                    maintenance_requirements TEXT,
                    maintenance_standard TEXT,
                    plan_status VARCHAR(20) NOT NULL,
                    execution_status VARCHAR(20) NOT NULL,
                    completion_rate INTEGER DEFAULT 0,
                    remarks TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)
            print("✅ maintenance_plan 表创建成功！")
            
            # 创建 project_info 表
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS project_info (
                    id BIGSERIAL PRIMARY KEY,
                    project_id VARCHAR(50) UNIQUE NOT NULL,
                    project_name VARCHAR(200) NOT NULL,
                    completion_date DATE,
                    maintenance_end_date DATE,
                    maintenance_period VARCHAR(50),
                    client_name VARCHAR(200),
                    address VARCHAR(500),
                    project_abbr VARCHAR(50),
                    client_contact VARCHAR(100),
                    client_contact_position VARCHAR(100),
                    client_contact_info VARCHAR(200),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)
            print("✅ project_info 表创建成功！")
            
            # 创建 personnel 表
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS personnel (
                    id BIGSERIAL PRIMARY KEY,
                    name VARCHAR(100) NOT NULL,
                    gender VARCHAR(10),
                    phone VARCHAR(20),
                    department VARCHAR(100),
                    role VARCHAR(50),
                    address VARCHAR(500),
                    remarks TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)
            print("✅ personnel 表创建成功！")
            
            # 创建 periodic_inspection 表
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS periodic_inspection (
                    id BIGSERIAL PRIMARY KEY,
                    inspection_id VARCHAR(50) UNIQUE NOT NULL,
                    project_id VARCHAR(50),
                    project_name VARCHAR(200),
                    plan_start_date DATE,
                    plan_end_date DATE,
                    client_name VARCHAR(200),
                    maintenance_personnel VARCHAR(100),
                    status VARCHAR(20),
                    remarks TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)
            print("✅ periodic_inspection 表创建成功！")
            
            # 创建 inspection_item 表
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS inspection_item (
                    id BIGSERIAL PRIMARY KEY,
                    item_id VARCHAR(50) UNIQUE NOT NULL,
                    item_name VARCHAR(200) NOT NULL,
                    item_category VARCHAR(100),
                    inspection_content TEXT,
                    inspection_requirements TEXT,
                    inspection_standard TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)
            print("✅ inspection_item 表创建成功！")
        
        print()
        print("✅ 数据库检查完成！")
        
        cursor.close()
        conn.close()
        
    except psycopg2.OperationalError as e:
        print(f"❌ 数据库错误: {e}")
        print()
        print("请检查：")
        print("1. 数据库是否存在")
        print("2. 用户权限是否足够")
        print("3. 密码是否正确")
    except Exception as e:
        print(f"❌ 错误: {e}")

if __name__ == "__main__":
    check_database()
