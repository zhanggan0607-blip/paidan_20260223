from app.database import SessionLocal
from app.models.personnel import Personnel
from app.auth import verify_password

db = SessionLocal()
user = db.query(Personnel).filter(Personnel.name == '张干').first()
if user:
    print(f'User found: {user.name}')
    print(f'Phone: {user.phone}')
    print(f'Password hash exists: {bool(user.password_hash)}')
    
    default_pwd = user.phone[-6:] if user.phone and len(user.phone) >= 6 else '123456'
    print(f'Default password should be: {default_pwd}')
    
    if user.password_hash:
        result = verify_password(default_pwd, user.password_hash)
        print(f'Verify default password result: {result}')
else:
    print('User not found')
db.close()
