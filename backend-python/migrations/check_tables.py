"""
检查数据库表名
"""
from app.database import SessionLocal
from sqlalchemy import text

def check_tables():
    db = SessionLocal()
    try:
        result = db.execute(text(
            "SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'"
        )).fetchall()
        print("Tables in database:")
        for r in result:
            print(f"  - {r[0]}")
    finally:
        db.close()

if __name__ == '__main__':
    check_tables()
