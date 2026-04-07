"""
数据库迁移脚本：添加reject_reason字段到工单表
"""
from app.database import SessionLocal
from sqlalchemy import text

def migrate():
    db = SessionLocal()
    try:
        # 检查并添加 temporary_repair 表的 reject_reason 字段
        result = db.execute(text(
            "SELECT column_name FROM information_schema.columns "
            "WHERE table_name = 'temporary_repair' AND column_name = 'reject_reason'"
        )).fetchone()
        if not result:
            db.execute(text('ALTER TABLE temporary_repair ADD COLUMN reject_reason VARCHAR(500)'))
            print('Added reject_reason to temporary_repair')
        else:
            print('reject_reason already exists in temporary_repair')

        # 检查并添加 spot_work 表的 reject_reason 字段
        result = db.execute(text(
            "SELECT column_name FROM information_schema.columns "
            "WHERE table_name = 'spot_work' AND column_name = 'reject_reason'"
        )).fetchone()
        if not result:
            db.execute(text('ALTER TABLE spot_work ADD COLUMN reject_reason VARCHAR(500)'))
            print('Added reject_reason to spot_work')
        else:
            print('reject_reason already exists in spot_work')

        # 检查并添加 periodic_inspection 表的 reject_reason 字段
        result = db.execute(text(
            "SELECT column_name FROM information_schema.columns "
            "WHERE table_name = 'periodic_inspection' AND column_name = 'reject_reason'"
        )).fetchone()
        if not result:
            db.execute(text('ALTER TABLE periodic_inspection ADD COLUMN reject_reason VARCHAR(500)'))
            print('Added reject_reason to periodic_inspection')
        else:
            print('reject_reason already exists in periodic_inspection')

        db.commit()
        print('Database migration completed successfully')
    except Exception as e:
        db.rollback()
        print(f'Error: {e}')
    finally:
        db.close()

if __name__ == '__main__':
    migrate()
