"""
Migration script to add total_count column to work_plan table
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import create_engine, text
from app.config import get_settings

def migrate():
    settings = get_settings()
    engine = create_engine(settings.database_url)
    with engine.connect() as conn:
        result = conn.execute(text("""
            SELECT column_name FROM information_schema.columns 
            WHERE table_name = 'work_plan' AND column_name = 'total_count'
        """))
        if result.fetchone() is None:
            conn.execute(text('ALTER TABLE work_plan ADD COLUMN total_count INTEGER DEFAULT 5'))
            conn.commit()
            print('Successfully added total_count column to work_plan table')
        else:
            print('Column total_count already exists in work_plan table')

if __name__ == '__main__':
    migrate()
