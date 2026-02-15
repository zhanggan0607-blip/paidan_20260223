"""
Migration script to add filled_count column to periodic_inspection table
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
                WHERE table_name = 'periodic_inspection' AND column_name = 'filled_count'
            """))
            if result.fetchone() is None:
                conn.execute(text("""
                    ALTER TABLE periodic_inspection 
                    ADD COLUMN filled_count INTEGER DEFAULT 0
                """))
                conn.commit()
                print("Successfully added filled_count column to periodic_inspection table")
            else:
                print("Column filled_count already exists in periodic_inspection table")
        except Exception as e:
            print(f"Migration failed: {str(e)}")
            conn.rollback()
            raise


if __name__ == "__main__":
    migrate()
