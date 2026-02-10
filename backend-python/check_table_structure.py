import psycopg2

def check_table_structure():
    """检查表结构"""
    
    conn = psycopg2.connect(
        host="localhost",
        port=5432,
        user="postgres",
        password="123456",
        database="tq"
    )
    conn.autocommit = True
    cursor = conn.cursor()
    
    # 检查 inspection_item 表结构
    cursor.execute("""
        SELECT column_name, data_type 
        FROM information_schema.columns 
        WHERE table_name = 'inspection_item' 
        ORDER BY ordinal_position;
    """)
    
    print("inspection_item 表结构：")
    for row in cursor.fetchall():
        print(f"  {row[0]}: {row[1]}")
    
    cursor.close()
    conn.close()

if __name__ == "__main__":
    check_table_structure()
