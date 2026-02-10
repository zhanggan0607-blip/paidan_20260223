import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from app.models.project_info import ProjectInfo
from app.database import Base
import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MySQLToPostgreSQLMigrator:
    def __init__(self, mysql_url: str, postgres_url: str):
        self.mysql_url = mysql_url
        self.postgres_url = postgres_url
        self.mysql_engine = None
        self.postgres_engine = None
        self.mysql_session = None
        self.postgres_session = None

    def connect(self):
        logger.info("连接到MySQL数据库...")
        self.mysql_engine = create_engine(
            self.mysql_url,
            pool_pre_ping=True,
            pool_recycle=3600,
        )
        MySQLSession = sessionmaker(bind=self.mysql_engine)
        self.mysql_session = MySQLSession()

        logger.info("连接到PostgreSQL数据库...")
        self.postgres_engine = create_engine(
            self.postgres_url,
            pool_pre_ping=True,
            pool_recycle=3600,
        )
        PostgreSQLSession = sessionmaker(bind=self.postgres_engine)
        self.postgres_session = PostgreSQLSession()

        logger.info("数据库连接成功!")

    def create_postgresql_tables(self):
        logger.info("在PostgreSQL中创建表结构...")
        Base.metadata.create_all(self.postgres_engine)
        logger.info("表结构创建成功!")

    def migrate_project_info(self):
        logger.info("开始迁移project_info表数据...")

        try:
            query = text("SELECT * FROM project_info")
            result = self.mysql_session.execute(query)
            rows = result.fetchall()
            columns = result.keys()

            logger.info(f"从MySQL读取到 {len(rows)} 条记录")

            migrated_count = 0
            for row in rows:
                row_dict = dict(zip(columns, row))

                project_info = ProjectInfo(
                    id=row_dict['id'],
                    project_id=row_dict['project_id'],
                    project_name=row_dict['project_name'],
                    completion_date=row_dict['completion_date'],
                    maintenance_end_date=row_dict['maintenance_end_date'],
                    maintenance_period=row_dict['maintenance_period'],
                    client_name=row_dict['client_name'],
                    address=row_dict['address'],
                    project_abbr=row_dict['project_abbr'],
                    client_contact=row_dict['client_contact'],
                    client_contact_position=row_dict['client_contact_position'],
                    client_contact_info=row_dict['client_contact_info'],
                    created_at=row_dict['created_at'],
                    updated_at=row_dict['updated_at'],
                )

                self.postgres_session.add(project_info)
                migrated_count += 1

                if migrated_count % 100 == 0:
                    self.postgres_session.commit()
                    logger.info(f"已迁移 {migrated_count}/{len(rows)} 条记录")

            self.postgres_session.commit()
            logger.info(f"project_info表迁移完成! 共迁移 {migrated_count} 条记录")

        except Exception as e:
            logger.error(f"迁移project_info表时出错: {str(e)}")
            self.postgres_session.rollback()
            raise

    def verify_migration(self):
        logger.info("验证数据迁移...")

        mysql_count = self.mysql_session.execute(text("SELECT COUNT(*) FROM project_info")).scalar()
        postgres_count = self.postgres_session.execute(text("SELECT COUNT(*) FROM project_info")).scalar()

        logger.info(f"MySQL记录数: {mysql_count}")
        logger.info(f"PostgreSQL记录数: {postgres_count}")

        if mysql_count == postgres_count:
            logger.info("数据验证通过! 记录数一致")
            return True
        else:
            logger.error(f"数据验证失败! 记录数不一致: MySQL={mysql_count}, PostgreSQL={postgres_count}")
            return False

    def close(self):
        if self.mysql_session:
            self.mysql_session.close()
        if self.postgres_session:
            self.postgres_session.close()
        if self.mysql_engine:
            self.mysql_engine.dispose()
        if self.postgres_engine:
            self.postgres_engine.dispose()
        logger.info("数据库连接已关闭")

    def migrate(self):
        try:
            self.connect()
            self.create_postgresql_tables()
            self.migrate_project_info()
            success = self.verify_migration()
            return success
        except Exception as e:
            logger.error(f"迁移过程中发生错误: {str(e)}")
            return False
        finally:
            self.close()


def main():
    mysql_url = "mysql+pymysql://root:root@localhost:3306/sstcp_maintenance"
    postgres_url = "postgresql://postgres:123456@localhost:5432/tq"

    logger.info("=" * 60)
    logger.info("MySQL 到 PostgreSQL 数据迁移工具")
    logger.info("=" * 60)
    logger.info(f"MySQL连接: {mysql_url}")
    logger.info(f"PostgreSQL连接: {postgres_url}")
    logger.info("=" * 60)

    migrator = MySQLToPostgreSQLMigrator(mysql_url, postgres_url)
    success = migrator.migrate()

    if success:
        logger.info("=" * 60)
        logger.info("数据迁移成功完成!")
        logger.info("=" * 60)
        sys.exit(0)
    else:
        logger.error("=" * 60)
        logger.error("数据迁移失败!")
        logger.error("=" * 60)
        sys.exit(1)


if __name__ == "__main__":
    main()