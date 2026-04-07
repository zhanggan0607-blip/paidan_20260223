#!/usr/bin/env python3
"""
数据库迁移：将 customer 表的 contact_person 和 phone 字段改为可空
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import create_engine, text
from app.config import get_settings


def migrate():
    """
    执行数据库迁移
    """
    settings = get_settings()
    engine = create_engine(settings.database_url)

    with engine.connect() as conn:
        print("开始迁移 customer 表...")

        conn.execute(text("""
            ALTER TABLE customer 
            ALTER COLUMN contact_person DROP NOT NULL,
            ALTER COLUMN phone DROP NOT NULL
        """))
        conn.commit()

        print("迁移完成！contact_person 和 phone 字段已改为可空")


if __name__ == "__main__":
    migrate()
