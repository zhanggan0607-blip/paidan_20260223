from app.database import SessionLocal
from app.models.personnel import Personnel

db = SessionLocal()

print('=== personnel 表用户列表 ===')
users = db.query(Personnel).all()
for u in users:
    print(f'  name="{u.name}", role="{u.role}"')
