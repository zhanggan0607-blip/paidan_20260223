"""
数据存储检查脚本
检查数据库中的表结构和数据存储情况
"""
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import create_engine, text
from dotenv import load_dotenv

load_dotenv()

db_url = os.getenv('DATABASE_URL', '')
if not db_url:
    print('错误: DATABASE_URL 未设置')
    sys.exit(1)

print('=' * 60)
print('数据库连接信息')
print('=' * 60)
print(f'数据库URL: {db_url[:50]}...')

if 'aliyuncs.com' in db_url:
    print('✓ 使用阿里云RDS数据库')
else:
    print('✗ 未使用阿里云RDS数据库')

engine = create_engine(db_url)

with engine.connect() as conn:
    print()
    print('=' * 60)
    print('数据库表列表')
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
    print('各表数据统计')
    print('=' * 60)
    
    table_stats = []
    for table in tables:
        try:
            count_result = conn.execute(text(f'SELECT COUNT(*) FROM "{table}"'))
            count = count_result.scalar()
            table_stats.append((table, count))
            print(f'  {table}: {count} 条记录')
        except Exception as e:
            print(f'  {table}: 查询失败 - {e}')
    
    print()
    print('=' * 60)
    print('图片/文件存储检查 (uploaded_file表)')
    print('=' * 60)
    
    if 'uploaded_file' in tables:
        result = conn.execute(text('SELECT COUNT(*) FROM uploaded_file'))
        file_count = result.scalar()
        print(f'  文件记录数: {file_count}')
        
        result = conn.execute(text('SELECT SUM(file_size) FROM uploaded_file'))
        total_size = result.scalar() or 0
        print(f'  总存储大小: {total_size / 1024 / 1024:.2f} MB')
        
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
            LIMIT 5
        """))
        print('  最近上传日期:')
        for row in result:
            print(f'    - {row[0]}: {row[1]} 个文件')
    else:
        print('  uploaded_file 表不存在')
    
    print()
    print('=' * 60)
    print('数据过期/清理机制检查')
    print('=' * 60)
    
    result = conn.execute(text("""
        SELECT column_name, data_type 
        FROM information_schema.columns 
        WHERE table_name = 'uploaded_file' AND column_name LIKE '%expire%' OR column_name LIKE '%delete%' OR column_name LIKE '%ttl%'
    """))
    expire_cols = list(result)
    if expire_cols:
        print('  发现过期相关字段:')
        for col in expire_cols:
            print(f'    - {col[0]}: {col[1]}')
    else:
        print('  ✓ 未发现自动过期字段')
    
    result = conn.execute(text("""
        SELECT 
            t.table_name,
            c.column_name
        FROM information_schema.tables t
        JOIN information_schema.columns c ON t.table_name = c.table_name
        WHERE t.table_schema = 'public'
        AND (c.column_name LIKE '%expire%' OR c.column_name LIKE '%ttl%' OR c.column_name LIKE '%delete%')
        ORDER BY t.table_name, c.column_name
    """))
    all_expire_cols = list(result)
    if all_expire_cols:
        print('  所有表中的过期/删除相关字段:')
        for col in all_expire_cols:
            print(f'    - {col[0]}.{col[1]}')
    
    print()
    print('=' * 60)
    print('软删除字段检查')
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
        print('  支持软删除的表:')
        for t in soft_delete_tables:
            result2 = conn.execute(text(f'SELECT COUNT(*) FROM "{t}" WHERE is_deleted = true'))
            deleted_count = result2.scalar()
            print(f'    - {t}: {deleted_count} 条已删除记录')
    else:
        print('  未发现支持软删除的表')

print()
print('=' * 60)
print('检查完成')
print('=' * 60)
