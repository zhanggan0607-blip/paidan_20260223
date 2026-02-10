import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from app.models.project_info import ProjectInfo
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def verify_data():
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
        logger.info("=" * 60)
        logger.info("数据验证报告")
        logger.info("=" * 60)

        count = session.query(ProjectInfo).count()
        logger.info(f"总记录数: {count}")

        if count == 0:
            logger.warning("数据库中没有数据!")
            return False

        logger.info("\n数据样本（前3条）:")
        projects = session.query(ProjectInfo).limit(3).all()
        for project in projects:
            logger.info(f"  - ID: {project.id}, 项目编号: {project.project_id}, 项目名称: {project.project_name}")

        logger.info("\n数据字段检查:")
        sample = session.query(ProjectInfo).first()
        if sample:
            logger.info(f"  - project_id: {sample.project_id}")
            logger.info(f"  - project_name: {sample.project_name}")
            logger.info(f"  - completion_date: {sample.completion_date}")
            logger.info(f"  - maintenance_end_date: {sample.maintenance_end_date}")
            logger.info(f"  - maintenance_period: {sample.maintenance_period}")
            logger.info(f"  - client_name: {sample.client_name}")
            logger.info(f"  - address: {sample.address}")
            logger.info(f"  - created_at: {sample.created_at}")
            logger.info(f"  - updated_at: {sample.updated_at}")

        logger.info("\n索引检查:")
        result = session.execute(text("""
            SELECT indexname, indexdef
            FROM pg_indexes
            WHERE tablename = 'project_info'
        """))
        indexes = result.fetchall()
        logger.info(f"  索引数量: {len(indexes)}")
        for idx in indexes:
            logger.info(f"  - {idx[0]}")

        logger.info("\n表结构检查:")
        result = session.execute(text("""
            SELECT column_name, data_type, is_nullable
            FROM information_schema.columns
            WHERE table_name = 'project_info'
            ORDER BY ordinal_position
        """))
        columns = result.fetchall()
        logger.info(f"  字段数量: {len(columns)}")
        for col in columns:
            logger.info(f"  - {col[0]}: {col[1]} (nullable: {col[2]})")

        logger.info("\n" + "=" * 60)
        logger.info("数据验证完成!")
        logger.info("=" * 60)

        return True

    except Exception as e:
        logger.error(f"验证数据时出错: {str(e)}")
        return False
    finally:
        session.close()
        engine.dispose()
        logger.info("数据库连接已关闭")


if __name__ == "__main__":
    success = verify_data()
    sys.exit(0 if success else 1)