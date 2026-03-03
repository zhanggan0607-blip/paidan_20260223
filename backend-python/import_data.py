"""
数据库数据导入脚本
在服务器上运行，导入从本地导出的数据
"""
import json
import sys
from datetime import datetime
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

SERVER_DB_URL = "postgresql://postgres:123456@tq_postgres:5432/tq"


def import_data(filename="db_export.json"):
    """导入数据到服务器数据库"""
    print("正在读取导出文件...")
    with open(filename, 'r', encoding='utf-8') as f:
        all_data = json.load(f)
    
    print("正在连接服务器数据库...")
    engine = create_engine(SERVER_DB_URL)
    Session = sessionmaker(bind=engine)
    session = Session()
    
    total_imported = 0
    total_skipped = 0
    
    for table, content in all_data.items():
        columns = content["columns"]
        data = content["data"]
        
        if not data:
            print(f"  {table}: 无数据，跳过")
            continue
        
        try:
            session.execute(text(f'TRUNCATE TABLE "{table}" CASCADE'))
            
            if table == "inspection_item":
                sorted_data = sorted(data, key=lambda x: (x.get('level', 1) or 1, x.get('parent_id') is not None, x.get('parent_id') or 0))
            else:
                sorted_data = data
            
            col_names = ', '.join(f'"{col}"' for col in columns)
            placeholders = ', '.join(f':{col}' for col in columns)
            insert_sql = f'INSERT INTO "{table}" ({col_names}) VALUES ({placeholders})'
            
            imported_count = 0
            for row in sorted_data:
                processed_row = {}
                for col in columns:
                    val = row.get(col)
                    if val == '' or val is None:
                        processed_row[col] = None
                    else:
                        processed_row[col] = val
                
                try:
                    session.execute(text(insert_sql), processed_row)
                    imported_count += 1
                except Exception as e:
                    if table == "inspection_item":
                        pass
                    else:
                        raise e
            
            session.commit()
            print(f"  {table}: 导入 {imported_count} 条记录")
            total_imported += imported_count
        except Exception as e:
            session.rollback()
            print(f"  {table}: 导入失败 - {e}")
            total_skipped += len(data)
    
    session.close()
    engine.dispose()
    return total_imported, total_skipped


if __name__ == "__main__":
    print("=" * 50)
    print("服务器数据库数据导入")
    print("=" * 50)
    
    filename = sys.argv[1] if len(sys.argv) > 1 else "db_export.json"
    
    imported, skipped = import_data(filename)
    
    print("\n" + "=" * 50)
    print(f"导入完成: 成功 {imported} 条，跳过 {skipped} 条")
    print("=" * 50)
