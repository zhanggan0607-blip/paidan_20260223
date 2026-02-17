"""
Migration script to add total_count column to periodic_inspection table
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import text
from app.database import engine


def migrate():
    with engine.connect() as conn:
        try:
            result = conn.execute(text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'periodic_inspection' AND column_name = 'total_count'
            """))
            if result.fetchone() is None:
                conn.execute(text("""
                    ALTER TABLE periodic_inspection 
                    ADD COLUMN total_count INTEGER DEFAULT 5
                """))
                conn.commit()
                print("Successfully added total_count column to periodic_inspection table")
            else:
                print("Column total_count already exists in periodic_inspection table")
        except Exception as e:
            print(f"Migration failed: {str(e)}")
            conn.rollback()
            raise


if __name__ == "__main__":
    migrate()
