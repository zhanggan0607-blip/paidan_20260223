"""
数据库迁移脚本：创建customer_contact表并迁移现有数据
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import create_engine, text

from app.config import get_settings


def migrate():
    """
    执行数据库迁移
    1. 创建customer_contact表
    2. 将现有customer表中的联系人数据迁移到新表
    """
    settings = get_settings()
    engine = create_engine(settings.database_url)

    with engine.connect() as conn:
        print("开始迁移...")

        print("1. 创建customer_contact表...")
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS customer_contact (
                id SERIAL PRIMARY KEY,
                customer_id INTEGER NOT NULL REFERENCES customer(id) ON DELETE CASCADE,
                contact_person VARCHAR(50) NOT NULL,
                phone VARCHAR(20),
                contact_position VARCHAR(50),
                remarks TEXT,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
                updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL
            )
        """))
        conn.commit()
        print("   customer_contact表创建成功")

        print("2. 创建索引...")
        conn.execute(text("""
            CREATE INDEX IF NOT EXISTS ix_customer_contact_id ON customer_contact(id)
        """))
        conn.execute(text("""
            CREATE INDEX IF NOT EXISTS ix_customer_contact_customer_id ON customer_contact(customer_id)
        """))
        conn.commit()
        print("   索引创建成功")

        print("3. 迁移现有联系人数据...")
        result = conn.execute(text("""
            SELECT id, contact_person, phone, contact_position
            FROM customer
            WHERE contact_person IS NOT NULL AND contact_person != ''
        """))
        customers = result.fetchall()

        migrated_count = 0
        for customer in customers:
            customer_id = customer[0]
            contact_person = customer[1]
            phone = customer[2]
            contact_position = customer[3]

            if contact_person and contact_person.strip():
                conn.execute(text("""
                    INSERT INTO customer_contact (customer_id, contact_person, phone, contact_position)
                    VALUES (:customer_id, :contact_person, :phone, :contact_position)
                """), {
                    'customer_id': customer_id,
                    'contact_person': contact_person.strip(),
                    'phone': phone.strip() if phone else None,
                    'contact_position': contact_position.strip() if contact_position else None
                })
                migrated_count += 1

        conn.commit()
        print(f"   已迁移 {migrated_count} 条联系人数据")

        print("迁移完成！")


if __name__ == "__main__":
    migrate()
