"""
数据存储检查脚本 - 连接阿里云RDS
检查数据库中的表结构和数据存储情况
"""
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import create_engine, text

ALIYUN_RDS_URL = "postgresql://zhanggan:Lily421020%23@pgm-uf6cml154nbjz51y6o.pg.rds.aliyuncs.com:5432/tq"

print('=' * 60)
print('阿里云RDS数据库存储检查报告')
print('=' * 60)
print(f'数据库URL: {ALIYUN_RDS_URL[:50]}...')
print('✓ 使用阿里云RDS PostgreSQL数据库')

engine = create_engine(ALIYUN_RDS_URL)

with engine.connect() as conn:
    print()
    print('=' * 60)
    print('1. 数据库表列表')
    print('=' * 60)
    
    result = conn.execute(text("""
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = 'public' 
        ORDER BY table_name
    """))
    tables = [row[0] for row in result]
    
    for t in tables:
        print(f'  - {t}')
    
    print()
    print('=' * 60)
    print('2. 各表数据统计')
    print('=' * 60)
    
    total_records = 0
    for table in tables:
        try:
            count_result = conn.execute(text(f'SELECT COUNT(*) FROM "{table}"'))
            count = count_result.scalar()
            total_records += count
            print(f'  {table}: {count} 条记录')
        except Exception as e:
            print(f'  {table}: 查询失败 - {e}')
    
    print(f'\n  总记录数: {total_records}')
    
    print()
    print('=' * 60)
    print('3. 图片/文件存储检查 (uploaded_file表)')
    print('=' * 60)
    
    if 'uploaded_file' in tables:
        result = conn.execute(text('SELECT COUNT(*) FROM uploaded_file'))
        file_count = result.scalar()
        print(f'  文件记录数: {file_count}')
        
        result = conn.execute(text('SELECT SUM(file_size) FROM uploaded_file'))
        total_size = result.scalar() or 0
        print(f'  总存储大小: {total_size / 1024 / 1024:.2f} MB')
        
        if file_count > 0:
            result = conn.execute(text("""
                SELECT content_type, COUNT(*) as cnt 
                FROM uploaded_file 
                GROUP BY content_type
            """))
            print('  文件类型分布:')
            for row in result:
                print(f'    - {row[0]}: {row[1]} 个文件')
            
            result = conn.execute(text("""
                SELECT upload_date, COUNT(*) as cnt 
                FROM uploaded_file 
                GROUP BY upload_date 
                ORDER BY upload_date DESC 
                LIMIT 10
            """))
            print('  上传日期分布:')
            for row in result:
                print(f'    - {row[0]}: {row[1]} 个文件')
            
            result = conn.execute(text("""
                SELECT file_id, original_filename, file_size, content_type, upload_date
                FROM uploaded_file
                ORDER BY created_at DESC
                LIMIT 5
            """))
            print('  最近上传的文件:')
            for row in result:
                print(f'    - {row[0][:8]}... | {row[1]} | {row[2]/1024:.1f}KB | {row[3]} | {row[4]}')
    else:
        print('  uploaded_file 表不存在')
    
    print()
    print('=' * 60)
    print('4. 数据过期/清理机制检查')
    print('=' * 60)
    
    result = conn.execute(text("""
        SELECT 
            t.table_name,
            c.column_name,
            c.data_type
        FROM information_schema.tables t
        JOIN information_schema.columns c ON t.table_name = c.table_name
        WHERE t.table_schema = 'public'
        AND t.table_name NOT LIKE 'pg_%'
        AND t.table_name NOT LIKE 'sql_%'
        AND (c.column_name LIKE '%expire%' OR c.column_name LIKE '%ttl%' OR c.column_name LIKE '%auto_delete%')
        ORDER BY t.table_name, c.column_name
    """))
    expire_cols = list(result)
    if expire_cols:
        print('  发现自动过期相关字段:')
        for col in expire_cols:
            print(f'    - {col[0]}.{col[1]}: {col[2]}')
    else:
        print('  ✓ 未发现自动过期/TTL字段')
        print('  ✓ 数据不会自动过期或清理')
    
    print()
    print('=' * 60)
    print('5. 软删除字段检查')
    print('=' * 60)
    
    result = conn.execute(text("""
        SELECT DISTINCT t.table_name
        FROM information_schema.tables t
        JOIN information_schema.columns c ON t.table_name = c.table_name
        WHERE t.table_schema = 'public'
        AND c.column_name = 'is_deleted'
        ORDER BY t.table_name
    """))
    soft_delete_tables = [row[0] for row in result]
    if soft_delete_tables:
        print('  支持软删除的表 (非物理删除):')
        for t in soft_delete_tables:
            result2 = conn.execute(text(f'SELECT COUNT(*) FROM "{t}" WHERE is_deleted = true'))
            deleted_count = result2.scalar()
            result3 = conn.execute(text(f'SELECT COUNT(*) FROM "{t}"'))
            total_count = result3.scalar()
            print(f'    - {t}: {deleted_count}/{total_count} 条已软删除')
    else:
        print('  未发现支持软删除的表')
    
    print()
    print('=' * 60)
    print('6. 业务数据存储检查')
    print('=' * 60)
    
    business_tables = [
        'personnel', 'project_info', 'maintenance_plan', 'periodic_inspection',
        'temporary_repair', 'spot_work', 'work_plan', 'customer', 'weekly_report',
        'spare_parts_stock', 'inspection_item', 'work_order_operation_log'
    ]
    
    for table in business_tables:
        if table in tables:
            result = conn.execute(text(f'SELECT COUNT(*) FROM "{table}"'))
            count = result.scalar()
            print(f'  {table}: {count} 条记录')
    
    print()
    print('=' * 60)
    print('7. 数据库存储空间使用')
    print('=' * 60)
    
    result = conn.execute(text("""
        SELECT 
            schemaname,
            tablename,
            pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) as total_size,
            pg_total_relation_size(schemaname||'.'||tablename) as bytes
        FROM pg_tables
        WHERE schemaname = 'public'
        ORDER BY bytes DESC
        LIMIT 10
    """))
    print('  表存储大小 (前10):')
    total_db_size = 0
    for row in result:
        print(f'    - {row[1]}: {row[2]}')
        total_db_size += row[3]
    
    print(f'\n  数据库总大小: {total_db_size / 1024 / 1024:.2f} MB')

print()
print('=' * 60)
print('检查完成')
print('=' * 60)
