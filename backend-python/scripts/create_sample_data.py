import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models.project_info import ProjectInfo
from app.database import Base
from datetime import datetime, timedelta
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def create_sample_data():
    postgres_url = "postgresql://postgres:123456@localhost:5432/tq"

    logger.info("连接到PostgreSQL数据库...")
    engine = create_engine(
        postgres_url,
        pool_pre_ping=True,
        pool_recycle=3600,
    )
    SessionLocal = sessionmaker(bind=engine)
    session = SessionLocal()

    try:
        logger.info("创建表结构...")
        Base.metadata.create_all(engine)

        logger.info("创建示例数据...")

        sample_projects = [
            {
                "project_id": "PRJ001",
                "project_name": "智慧城市综合管理平台",
                "completion_date": datetime.now() - timedelta(days=365),
                "maintenance_end_date": datetime.now() + timedelta(days=365),
                "maintenance_period": "1年",
                "client_name": "北京市人民政府",
                "address": "北京市东城区长安街1号",
                "project_abbr": "智慧城市",
                "client_contact": "张三",
                "client_contact_position": "信息中心主任",
                "client_contact_info": "13800138000",
            },
            {
                "project_id": "PRJ002",
                "project_name": "交通信号智能控制系统",
                "completion_date": datetime.now() - timedelta(days=180),
                "maintenance_end_date": datetime.now() + timedelta(days=180),
                "maintenance_period": "6个月",
                "client_name": "上海市交通委员会",
                "address": "上海市黄浦区人民大道200号",
                "project_abbr": "交通控制",
                "client_contact": "李四",
                "client_contact_position": "技术总监",
                "client_contact_info": "13900139000",
            },
            {
                "project_id": "PRJ003",
                "project_name": "环境监测数据平台",
                "completion_date": datetime.now() - timedelta(days=90),
                "maintenance_end_date": datetime.now() + timedelta(days=270),
                "maintenance_period": "1年",
                "client_name": "广州市生态环境局",
                "address": "广州市天河区天河北路183号",
                "project_abbr": "环境监测",
                "client_contact": "王五",
                "client_contact_position": "项目经理",
                "client_contact_info": "13700137000",
            },
            {
                "project_id": "PRJ004",
                "project_name": "智慧医疗信息系统",
                "completion_date": datetime.now() - timedelta(days=270),
                "maintenance_end_date": datetime.now() + timedelta(days=90),
                "maintenance_period": "1年",
                "client_name": "深圳市卫生健康委员会",
                "address": "深圳市福田区深南中路1025号",
                "project_abbr": "智慧医疗",
                "client_contact": "赵六",
                "client_contact_position": "信息科科长",
                "client_contact_info": "13600136000",
            },
            {
                "project_id": "PRJ005",
                "project_name": "教育云服务平台",
                "completion_date": datetime.now() - timedelta(days=120),
                "maintenance_end_date": datetime.now() + timedelta(days=240),
                "maintenance_period": "1年",
                "client_name": "杭州市教育局",
                "address": "杭州市拱墅区屏风街8号",
                "project_abbr": "教育云",
                "client_contact": "孙七",
                "client_contact_position": "技术负责人",
                "client_contact_info": "13500135000",
            },
        ]

        for project_data in sample_projects:
            project_info = ProjectInfo(**project_data)
            session.add(project_info)

        session.commit()
        logger.info(f"成功创建 {len(sample_projects)} 条示例数据!")

        count = session.query(ProjectInfo).count()
        logger.info(f"数据库中当前共有 {count} 条记录")

        return True

    except Exception as e:
        logger.error(f"创建示例数据时出错: {str(e)}")
        session.rollback()
        return False
    finally:
        session.close()
        engine.dispose()
        logger.info("数据库连接已关闭")


if __name__ == "__main__":
    logger.info("=" * 60)
    logger.info("PostgreSQL 示例数据创建工具")
    logger.info("=" * 60)

    success = create_sample_data()

    if success:
        logger.info("=" * 60)
        logger.info("示例数据创建成功!")
        logger.info("=" * 60)
        sys.exit(0)
    else:
        logger.error("=" * 60)
        logger.error("示例数据创建失败!")
        logger.error("=" * 60)
        sys.exit(1)