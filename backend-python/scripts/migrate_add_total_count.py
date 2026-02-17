import os
os.environ['PYTHONIOENCODING'] = 'utf-8'
os.environ['PGCLIENTENCODING'] = 'LATIN1'

import psycopg2

try:
    conn = psycopg2.connect(
        host="localhost",
        port=5432,
        database="tq",
        user="postgres",
        password="changeme"
    )
    
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT column_name 
        FROM information_schema.columns 
        WHERE table_name = 'periodic_inspection' AND column_name = 'total_count'
    """)
    
    if cursor.fetchone() is None:
        cursor.execute("ALTER TABLE periodic_inspection ADD COLUMN total_count INTEGER DEFAULT 5")
        conn.commit()
        print("Successfully added total_count column")
    else:
        print("Column total_count already exists")
    
    cursor.close()
    conn.close()
except Exception as e:
    print(f"Error: {e}")
