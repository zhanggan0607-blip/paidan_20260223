from app.database import engine
from sqlalchemy import text

conn = engine.connect()
result = conn.execute(text("SELECT tablename FROM pg_tables WHERE schemaname = 'public'"))
print("Tables in database:")
for r in result:
    print(f"  - {r[0]}")
conn.close()
