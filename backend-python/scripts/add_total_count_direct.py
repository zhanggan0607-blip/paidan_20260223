import psycopg2
import os

os.environ['PGCLIENTENCODING'] = 'UTF8'

conn = psycopg2.connect(
    host="localhost",
    port=5432,
    database="tq",
    user="postgres",
    password="changeme",
    client_encoding='UTF8'
)

cursor = conn.cursor()

try:
    cursor.execute("""
        SELECT column_name 
        FROM information_schema.columns 
        WHERE table_name = 'periodic_inspection' AND column_name = 'total_count'
    """)
    
    if cursor.fetchone() is None:
        cursor.execute("ALTER TABLE periodic_inspection ADD COLUMN total_count INTEGER DEFAULT 5")
        conn.commit()
        print("Successfully added total_count column to periodic_inspection table")
    else:
        print("Column total_count already exists in periodic_inspection table")
except Exception as e:
    print(f"Error: {e}")
    conn.rollback()
finally:
    cursor.close()
    conn.close()
