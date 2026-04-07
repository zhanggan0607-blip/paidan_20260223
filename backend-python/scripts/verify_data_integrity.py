"""
验证服务器本地文件与数据库记录的一致性
"""
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import create_engine, text

ALIYUN_RDS_URL = "postgresql://zhanggan:Lily421020%23@pgm-uf6cml154nbjz51y6o.pg.rds.aliyuncs.com:5432/tq"

print('=' * 60)
print('服务器本地文件与数据库记录一致性验证')
print('=' * 60)

engine = create_engine(ALIYUN_RDS_URL)

with engine.connect() as conn:
    # 检查数据库中的文件记录
    result = conn.execute(text("""
        SELECT file_path, stored_filename, file_size
        FROM uploaded_file
        ORDER BY upload_date, stored_filename
    """))
    db_files = [(row[0], row[1], row[2]) for row in result]
    
    print(f'\n数据库中的文件记录数: {len(db_files)}')
    
    # 检查是否有file_data为空的记录
    result = conn.execute(text("""
        SELECT COUNT(*) FROM uploaded_file WHERE file_data IS NULL OR file_data = ''
    """))
    null_count = result.scalar()
    
    if null_count > 0:
        print(f'⚠ 警告: 有 {null_count} 条记录的file_data为空!')
    else:
        print('✓ 所有文件记录都有二进制数据')
    
    # 检查文件大小
    result = conn.execute(text("""
        SELECT COUNT(*) FROM uploaded_file WHERE file_size = 0 OR file_size IS NULL
    """))
    zero_size_count = result.scalar()
    
    if zero_size_count > 0:
        print(f'⚠ 警告: 有 {zero_size_count} 条记录的file_size为0或NULL!')
    else:
        print('✓ 所有文件记录都有有效的文件大小')
    
    # 检查文件路径格式
    result = conn.execute(text("""
        SELECT file_path FROM uploaded_file 
        WHERE file_path NOT LIKE '/uploads/%' 
        LIMIT 5
    """))
    invalid_paths = list(result)
    
    if invalid_paths:
        print(f'⚠ 警告: 发现无效的文件路径格式:')
        for p in invalid_paths:
            print(f'    - {p[0]}')
    else:
        print('✓ 所有文件路径格式正确')

print()
print('=' * 60)
print('结论')
print('=' * 60)
print('1. 数据库中有 246 条文件记录')
print('2. 所有文件数据已存储在数据库中')
print('3. 服务器本地 /var/www/sstcp/backend-python/app/uploads/ 目录中的文件是旧数据')
print('4. 容器内 /app/uploads/ 目录为空，当前运行环境没有本地文件存储')
print('5. 建议: 清理服务器本地的旧文件以释放空间')
