import os
import sys
import json
sys.path.insert(0, '/app')
os.chdir('/app')

from sqlalchemy import create_engine, text
from dotenv import load_dotenv

load_dotenv('/app/.env')
db_url = os.getenv('DATABASE_URL', '')

engine = create_engine(db_url)
with engine.connect() as conn:
    print("=" * 60)
    print("检查数据库中的图片引用")
    print("=" * 60)
    
    all_paths = []
    
    # 检查 temporary_repair 表
    print("\n1. temporary_repair 表:")
    result = conn.execute(text("""
        SELECT COUNT(*) FROM temporary_repair 
        WHERE photos IS NOT NULL AND photos != '' AND photos != '[]'
    """))
    count = result.scalar()
    print(f"   有图片的记录: {count}")
    
    result = conn.execute(text("""
        SELECT photos FROM temporary_repair 
        WHERE photos IS NOT NULL AND photos != '' AND photos != '[]'
    """))
    for row in result:
        try:
            photos = json.loads(row[0]) if row[0] else []
            all_paths.extend(photos)
        except:
            pass
    
    # 检查 periodic_inspection_record 表
    print("\n2. periodic_inspection_record 表:")
    result = conn.execute(text("""
        SELECT COUNT(*) FROM periodic_inspection_record 
        WHERE photos IS NOT NULL AND photos != '' AND photos != '[]'
    """))
    count = result.scalar()
    print(f"   有图片的记录: {count}")
    
    result = conn.execute(text("""
        SELECT photos FROM periodic_inspection_record 
        WHERE photos IS NOT NULL AND photos != '' AND photos != '[]'
    """))
    for row in result:
        try:
            photos = json.loads(row[0]) if row[0] else []
            all_paths.extend(photos)
        except:
            pass
    
    # 检查 spot_work 表
    print("\n3. spot_work 表:")
    result = conn.execute(text("""
        SELECT COUNT(*) FROM spot_work 
        WHERE photos IS NOT NULL AND photos != '' AND photos != '[]'
    """))
    count = result.scalar()
    print(f"   有图片的记录: {count}")
    
    result = conn.execute(text("""
        SELECT photos FROM spot_work 
        WHERE photos IS NOT NULL AND photos != '' AND photos != '[]'
    """))
    for row in result:
        try:
            photos = json.loads(row[0]) if row[0] else []
            all_paths.extend(photos)
        except:
            pass
    
    # 检查 spot_work_worker 表
    print("\n4. spot_work_worker 表:")
    result = conn.execute(text("""
        SELECT column_name FROM information_schema.columns 
        WHERE table_name = 'spot_work_worker'
    """))
    columns = [row[0] for row in result]
    print(f"   表列: {columns}")
    
    if 'id_card_front' in columns:
        result = conn.execute(text("""
            SELECT id_card_front FROM spot_work_worker 
            WHERE id_card_front IS NOT NULL AND id_card_front != ''
        """))
        for row in result:
            all_paths.append(row[0])
    
    if 'id_card_back' in columns:
        result = conn.execute(text("""
            SELECT id_card_back FROM spot_work_worker 
            WHERE id_card_back IS NOT NULL AND id_card_back != ''
        """))
        for row in result:
            all_paths.append(row[0])
    
    # 检查 maintenance_log 表
    print("\n5. maintenance_log 表:")
    result = conn.execute(text("""
        SELECT column_name FROM information_schema.columns 
        WHERE table_name = 'maintenance_log'
    """))
    ml_columns = [row[0] for row in result]
    print(f"   表列: {ml_columns}")
    
    if 'photos' in ml_columns:
        result = conn.execute(text("""
            SELECT COUNT(*) FROM maintenance_log 
            WHERE photos IS NOT NULL AND photos != '' AND photos != '[]'
        """))
        count = result.scalar()
        print(f"   有图片的记录: {count}")
        
        result = conn.execute(text("""
            SELECT photos FROM maintenance_log 
            WHERE photos IS NOT NULL AND photos != '' AND photos != '[]'
        """))
        for row in result:
            try:
                photos = json.loads(row[0]) if row[0] else []
                all_paths.extend(photos)
            except:
                pass
    else:
        print("   表中没有 photos 列")
    
    # 统计所有图片路径
    print("\n" + "=" * 60)
    print("统计所有图片路径")
    print("=" * 60)
    
    print(f"\n总共找到 {len(all_paths)} 个图片路径引用")
    
    # 统计路径前缀
    prefixes = {}
    for path in all_paths:
        if path:
            prefix = path.split('/')[1] if '/' in path else 'unknown'
            prefixes[prefix] = prefixes.get(prefix, 0) + 1
    
    print("\n路径前缀统计:")
    for prefix, count in sorted(prefixes.items(), key=lambda x: -x[1]):
        print(f"  /{prefix}: {count}")
    
    # 按日期统计
    dates = {}
    for path in all_paths:
        if path and '/uploads/' in path:
            parts = path.split('/')
            if len(parts) >= 3:
                date = parts[2]
                dates[date] = dates.get(date, 0) + 1
    
    print("\n按日期统计:")
    for date, count in sorted(dates.items()):
        print(f"  {date}: {count} 个图片")
    
    # 显示部分路径示例
    print("\n路径示例 (前20个):")
    for path in all_paths[:20]:
        print(f"  {path}")
    
    # 检查签名图片
    print("\n" + "=" * 60)
    print("检查签名图片")
    print("=" * 60)
    
    # temporary_repair 签名
    result = conn.execute(text("""
        SELECT COUNT(*) FROM temporary_repair 
        WHERE signature IS NOT NULL AND signature != ''
    """))
    count = result.scalar()
    print(f"\ntemporary_repair 签名: {count}")
    
    result = conn.execute(text("""
        SELECT signature FROM temporary_repair 
        WHERE signature IS NOT NULL AND signature != ''
    """))
    for row in result:
        if row[0]:
            all_paths.append(row[0])
    
    # periodic_inspection_record 签名
    result = conn.execute(text("""
        SELECT COUNT(*) FROM periodic_inspection_record 
        WHERE signature IS NOT NULL AND signature != ''
    """))
    count = result.scalar()
    print(f"periodic_inspection_record 签名: {count}")
    
    result = conn.execute(text("""
        SELECT signature FROM periodic_inspection_record 
        WHERE signature IS NOT NULL AND signature != ''
    """))
    for row in result:
        if row[0]:
            all_paths.append(row[0])
    
    # spot_work 签名
    result = conn.execute(text("""
        SELECT COUNT(*) FROM spot_work 
        WHERE signature IS NOT NULL AND signature != ''
    """))
    count = result.scalar()
    print(f"spot_work 签名: {count}")
    
    result = conn.execute(text("""
        SELECT signature FROM spot_work 
        WHERE signature IS NOT NULL AND signature != ''
    """))
    for row in result:
        if row[0]:
            all_paths.append(row[0])
    
    print(f"\n最终总计: {len(all_paths)} 个图片路径引用")
