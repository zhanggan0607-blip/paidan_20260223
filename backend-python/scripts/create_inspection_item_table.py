import psycopg2
from psycopg2 import sql

def create_inspection_item_table():
    conn = psycopg2.connect(
        host="localhost",
        port=5432,
        database="tq",
        user="postgres",
        password="123456"
    )
    conn.autocommit = True
    cursor = conn.cursor()

    create_table_query = """
    CREATE TABLE IF NOT EXISTS inspection_item (
        id SERIAL PRIMARY KEY,
        item_code VARCHAR(50) UNIQUE NOT NULL,
        item_name VARCHAR(200) NOT NULL,
        item_type VARCHAR(50) NOT NULL,
        check_content TEXT,
        check_standard TEXT,
        created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
    );
    """

    create_indexes_query = """
    CREATE INDEX IF NOT EXISTS idx_inspection_item_item_code ON inspection_item(item_code);
    CREATE INDEX IF NOT EXISTS idx_inspection_item_item_name ON inspection_item(item_name);
    """

    insert_sample_data_query = """
    INSERT INTO inspection_item (item_code, item_name, item_type, check_content, check_standard) VALUES
    ('XC-001', '电梯运行检查', '定期巡检', '检查电梯运行是否正常，有无异常声响', '电梯运行平稳，无异常声响，门开关灵活'),
    ('XC-002', '消防设施检查', '定期巡检', '检查消防设施是否完好有效', '灭火器在有效期内，压力正常'),
    ('XC-003', '空调系统检查', '定期巡检', '检查空调制冷制热功能是否正常', '空调运行正常，温度调节有效'),
    ('XC-004', '照明系统检查', '定期巡检', '检查各区域照明是否正常', '所有照明设备正常工作，无闪烁')
    ON CONFLICT (item_code) DO NOTHING;
    """

    try:
        cursor.execute(create_table_query)
        print("✅ 创建表 inspection_item 成功")

        cursor.execute(create_indexes_query)
        print("✅ 创建索引成功")

        cursor.execute(insert_sample_data_query)
        print("✅ 插入示例数据成功")

        print("\n数据库表结构验证:")
        cursor.execute("""
            SELECT column_name, data_type 
            FROM information_schema.columns 
            WHERE table_name = 'inspection_item'
            ORDER BY ordinal_position;
        """)
        columns = cursor.fetchall()
        for col in columns:
            print(f"   - {col[0]}: {col[1]}")

    except Exception as e:
        print(f"❌ 错误: {e}")
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    create_inspection_item_table()
