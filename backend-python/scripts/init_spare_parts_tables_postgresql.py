import psycopg2

print("=" * 80)
print("初始化备品备件表 (PostgreSQL)")
print("=" * 80)

try:
    conn = psycopg2.connect(
        host="localhost",
        port=5432,
        database="tq",
        user="postgres",
        password="changeme"
    )
    conn.autocommit = True
    cursor = conn.cursor()
    
    print("\n✅ 数据库连接成功\n")
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS spare_parts_inbound (
            id BIGSERIAL PRIMARY KEY,
            inbound_no VARCHAR(50) UNIQUE NOT NULL,
            product_name VARCHAR(200) NOT NULL,
            brand VARCHAR(100),
            model VARCHAR(100),
            quantity INTEGER NOT NULL,
            supplier VARCHAR(200),
            unit VARCHAR(20) NOT NULL DEFAULT '件',
            user_name VARCHAR(100) NOT NULL,
            remarks VARCHAR(500),
            created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    print("✅ spare_parts_inbound 表创建成功\n")
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS spare_parts_stock (
            id BIGSERIAL PRIMARY KEY,
            product_name VARCHAR(200) NOT NULL,
            brand VARCHAR(100),
            model VARCHAR(100),
            unit VARCHAR(20) NOT NULL DEFAULT '件',
            quantity INTEGER NOT NULL DEFAULT 0,
            updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    print("✅ spare_parts_stock 表创建成功\n")
    
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_inbound_no ON spare_parts_inbound(inbound_no);
    """)
    
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_inbound_product_name ON spare_parts_inbound(product_name);
    """)
    
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_inbound_user_name ON spare_parts_inbound(user_name);
    """)
    
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_inbound_created_at ON spare_parts_inbound(created_at);
    """)
    
    print("✅ 索引创建成功\n")
    
    cursor.execute("""
        COMMENT ON TABLE spare_parts_inbound IS '备品备件入库记录表';
    """)
    
    cursor.execute("""
        COMMENT ON COLUMN spare_parts_inbound.id IS '主键ID';
    """)
    
    cursor.execute("""
        COMMENT ON COLUMN spare_parts_inbound.inbound_no IS '入库单号';
    """)
    
    cursor.execute("""
        COMMENT ON COLUMN spare_parts_inbound.product_name IS '产品名称';
    """)
    
    cursor.execute("""
        COMMENT ON COLUMN spare_parts_inbound.brand IS '品牌';
    """)
    
    cursor.execute("""
        COMMENT ON COLUMN spare_parts_inbound.model IS '产品型号';
    """)
    
    cursor.execute("""
        COMMENT ON COLUMN spare_parts_inbound.quantity IS '入库数量';
    """)
    
    cursor.execute("""
        COMMENT ON COLUMN spare_parts_inbound.supplier IS '供应商';
    """)
    
    cursor.execute("""
        COMMENT ON COLUMN spare_parts_inbound.unit IS '单位';
    """)
    
    cursor.execute("""
        COMMENT ON COLUMN spare_parts_inbound.user_name IS '入库人';
    """)
    
    cursor.execute("""
        COMMENT ON COLUMN spare_parts_inbound.remarks IS '备注';
    """)
    
    cursor.execute("""
        COMMENT ON COLUMN spare_parts_inbound.created_at IS '入库时间';
    """)
    
    cursor.execute("""
        COMMENT ON TABLE spare_parts_stock IS '备品备件库存表';
    """)
    
    cursor.execute("""
        COMMENT ON COLUMN spare_parts_stock.id IS '主键ID';
    """)
    
    cursor.execute("""
        COMMENT ON COLUMN spare_parts_stock.product_name IS '产品名称';
    """)
    
    cursor.execute("""
        COMMENT ON COLUMN spare_parts_stock.brand IS '品牌';
    """)
    
    cursor.execute("""
        COMMENT ON COLUMN spare_parts_stock.model IS '产品型号';
    """)
    
    cursor.execute("""
        COMMENT ON COLUMN spare_parts_stock.unit IS '单位';
    """)
    
    cursor.execute("""
        COMMENT ON COLUMN spare_parts_stock.quantity IS '库存数量';
    """)
    
    cursor.execute("""
        COMMENT ON COLUMN spare_parts_stock.updated_at IS '更新时间';
    """)
    
    print("✅ 表注释添加成功\n")
    
    cursor.close()
    conn.close()
    
    print("=" * 80)
    print("✅ 备品备件表初始化完成！")
    print("=" * 80)
    
except Exception as e:
    print(f"\n❌ 错误: {e}")
    import traceback
    traceback.print_exc()
