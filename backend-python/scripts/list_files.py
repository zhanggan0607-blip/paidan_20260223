import os
os.chdir('/app')
from app.database import SessionLocal
from sqlalchemy import text

db = SessionLocal()
result = db.execute(text('SELECT file_path FROM uploaded_file LIMIT 5'))
for row in result:
    print(row[0])
db.close()
