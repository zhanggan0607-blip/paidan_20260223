"""
检查数据库中的图片存储情况
"""
from app.database import SessionLocal
from sqlalchemy import text

db = SessionLocal()

print('=== uploaded_file表统计 ===')
result = db.execute(text('SELECT COUNT(*) FROM uploaded_file')).scalar()
print(f'总图片数量: {result}')

print('\n前10条file_path示例:')
result = db.execute(text('SELECT id, file_path, upload_date FROM uploaded_file LIMIT 10')).fetchall()
for row in result:
    print(f'  ID={row[0]}, file_path={row[1]}, upload_date={row[2]}')

print('\n按日期分布:')
result = db.execute(text('SELECT upload_date, COUNT(*) FROM uploaded_file GROUP BY upload_date')).fetchall()
for row in result:
    print(f'  {row[0]}: {row[1]}张')

print('\n=== temporary_repair表统计 ===')
result = db.execute(text('SELECT COUNT(*) FROM temporary_repair')).scalar()
print(f'总工单数: {result}')

print('\n工单photos字段示例:')
result = db.execute(text("SELECT id, repair_id, photos FROM temporary_repair WHERE photos IS NOT NULL AND photos != '' AND photos != '[]' LIMIT 5")).fetchall()
for row in result:
    print(f'  ID={row[0]}, repair_id={row[1]}, photos={row[2][:200] if row[2] else None}...')

print('\n=== periodic_inspection_record表统计 ===')
result = db.execute(text('SELECT COUNT(*) FROM periodic_inspection_record')).scalar()
print(f'总记录数: {result}')

print('\n巡检记录photos字段示例:')
result = db.execute(text("SELECT id, inspection_id, photos FROM periodic_inspection_record WHERE photos IS NOT NULL AND photos != '' AND photos != '[]' LIMIT 5")).fetchall()
for row in result:
    print(f'  ID={row[0]}, inspection_id={row[1]}, photos={row[2][:200] if row[2] else None}...')

db.close()
