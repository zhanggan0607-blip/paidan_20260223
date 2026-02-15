"""
数据库迁移脚本：创建临时维修和零星用工表
"""
from datetime import datetime, timedelta
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from app.config import get_settings
from app.database import Base
from app.models.temporary_repair import TemporaryRepair
from app.models.spot_work import SpotWork


def create_tables():
    engine = create_engine(get_settings().database_url)
    
    try:
        Base.metadata.create_all(bind=engine, checkfirst=True)
        print("✅ 数据库表创建成功")
    except Exception as e:
        print(f"⚠️ 表创建警告: {str(e)}")


def insert_test_data():
    engine = create_engine(get_settings().database_url)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = SessionLocal()
    
    try:
        today = datetime.now()
        
        temporary_repairs = [
            TemporaryRepair(
                repair_id='WX-2025-001',
                project_id='PRJ-2025-001',
                project_name='上海中心大厦临时维修项目',
                plan_start_date=today - timedelta(days=30),
                plan_end_date=today - timedelta(days=5),
                client_name='上海城投（集团）有限公司',
                maintenance_personnel='刘园智',
                status='待确认',
                remarks='电梯故障维修'
            ),
            TemporaryRepair(
                repair_id='WX-2025-002',
                project_id='PRJ-2025-002',
                project_name='环球金融中心临时维修项目',
                plan_start_date=today - timedelta(days=25),
                plan_end_date=today - timedelta(days=3),
                client_name='上海建工集团股份有限公司',
                maintenance_personnel='晋海龙',
                status='未确认',
                remarks='空调系统维修'
            ),
            TemporaryRepair(
                repair_id='WX-2025-003',
                project_id='PRJ-2025-003',
                project_name='金茂大厦临时维修项目',
                plan_start_date=today - timedelta(days=20),
                plan_end_date=today - timedelta(days=2),
                client_name='中国金茂控股集团有限公司',
                maintenance_personnel='张伟',
                status='未进行',
                remarks='消防系统维修'
            ),
        ]
        
        for repair in temporary_repairs:
            session.add(repair)
        
        spot_works = [
            SpotWork(
                work_id='LX-2025-001',
                project_id='PRJ-2025-001',
                project_name='上海中心大厦零星用工项目',
                plan_start_date=today - timedelta(days=35),
                plan_end_date=today - timedelta(days=7),
                client_name='上海城投（集团）有限公司',
                maintenance_personnel='李明',
                status='待确认',
                remarks='临时搬运工'
            ),
            SpotWork(
                work_id='LX-2025-002',
                project_id='PRJ-2025-002',
                project_name='环球金融中心零星用工项目',
                plan_start_date=today - timedelta(days=28),
                plan_end_date=today - timedelta(days=4),
                client_name='上海建工集团股份有限公司',
                maintenance_personnel='王芳',
                status='未确认',
                remarks='临时清洁工'
            ),
            SpotWork(
                work_id='LX-2025-003',
                project_id='PRJ-2025-003',
                project_name='金茂大厦零星用工项目',
                plan_start_date=today - timedelta(days=22),
                plan_end_date=today - timedelta(days=1),
                client_name='中国金茂控股集团有限公司',
                maintenance_personnel='赵强',
                status='未进行',
                remarks='临时安保工'
            ),
        ]
        
        for work in spot_works:
            session.add(work)
        
        session.commit()
        print("✅ 测试数据插入成功")
        print(f"   - 临时维修数据：{len(temporary_repairs)} 条")
        print(f"   - 零星用工数据：{len(spot_works)} 条")
        
    except Exception as e:
        session.rollback()
        print(f"❌ 测试数据插入失败: {e}")
        raise
    finally:
        session.close()


if __name__ == "__main__":
    print("🔄 开始数据库迁移...")
    create_tables()
    insert_test_data()
    print("🎉 数据库迁移完成！")
