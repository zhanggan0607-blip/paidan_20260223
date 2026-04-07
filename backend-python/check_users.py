from app.database import SessionLocal
from app.models.personnel import Personnel

db = SessionLocal()
users = db.query(Personnel).all()
print(f"Total users: {len(users)}")
for u in users:
    print(f"ID: {u.id}, Name: {u.name}, Phone: {u.phone}, HasPasswordHash: {bool(u.password_hash)}")
db.close()
