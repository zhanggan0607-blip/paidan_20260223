from app.database import SessionLocal
from sqlalchemy import text

db = SessionLocal()

print('=== 检查 temporary_repair 表中 ID 173 的记录 ===')
result = db.execute(text('SELECT id, repair_id, project_name, status, is_deleted FROM temporary_repair WHERE id = 173')).fetchone()
if result:
    print(f'ID: {result[0]}')
    print(f'repair_id: {result[1]}')
    print(f'project_name: {result[2]}')
    print(f'status: {result[3]}')
    print(f'is_deleted: {result[4]}')
else:
    print('ID 173 的记录不存在')

print()
print('=== 检查工单编号 WX-TQ-2025-001A-SH-20260310-0020 的记录 ===')
result = db.execute(text("SELECT id, repair_id, project_name, status, is_deleted FROM temporary_repair WHERE repair_id = 'WX-TQ-2025-001A-SH-20260310-0020'")).fetchone()
if result:
    print(f'ID: {result[0]}')
    print(f'repair_id: {result[1]}')
    print(f'project_name: {result[2]}')
    print(f'status: {result[3]}')
    print(f'is_deleted: {result[4]}')
else:
    print('工单编号 WX-TQ-2025-001A-SH-20260310-0020 的记录不存在')

print()
print('=== 检查本年已完成的临时维修工单（前10条） ===')
result = db.execute(text("""
    SELECT id, repair_id, project_name, status, is_deleted, actual_completion_date
    FROM temporary_repair 
    WHERE status = '已完成' 
    AND EXTRACT(YEAR FROM actual_completion_date) = 2026
    AND is_deleted = false
    ORDER BY actual_completion_date DESC
    LIMIT 10
"""))
for row in result:
    print(f'ID: {row[0]}, repair_id: {row[1]}, status: {row[3]}, is_deleted: {row[4]}')

db.close()
