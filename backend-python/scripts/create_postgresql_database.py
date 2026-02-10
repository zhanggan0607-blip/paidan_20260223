import psycopg2
from psycopg2 import sql
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def create_database():
    try:
        logger.info("连接到PostgreSQL服务器...")
        conn = psycopg2.connect(
            host="localhost",
            port="5432",
            user="postgres",
            password="123456",
            database="postgres"
        )
        conn.autocommit = True
        cursor = conn.cursor()

        logger.info("检查数据库tq是否存在...")
        cursor.execute("SELECT 1 FROM pg_database WHERE datname = %s", ('tq',))
        exists = cursor.fetchone()

        if exists:
            logger.info("数据库tq已存在，将断开所有连接并删除...")
            cursor.execute("""
                SELECT pg_terminate_backend(pg_stat_activity.pid)
                FROM pg_stat_activity
                WHERE pg_stat_activity.datname = %s
                AND pid <> pg_backend_pid();
            """, ('tq',))
            cursor.execute(sql.SQL("DROP DATABASE {}").format(sql.Identifier("tq")))
            logger.info("已删除旧数据库tq")

        logger.info("创建数据库tq...")
        cursor.execute(sql.SQL("CREATE DATABASE {}").format(sql.Identifier("tq")))
        logger.info("数据库tq创建成功!")

        cursor.close()
        conn.close()
        logger.info("PostgreSQL连接已关闭")
        return True

    except Exception as e:
        logger.error(f"创建数据库时出错: {str(e)}")
        return False


if __name__ == "__main__":
    logger.info("=" * 60)
    logger.info("PostgreSQL 数据库创建工具")
    logger.info("=" * 60)

    success = create_database()

    if success:
        logger.info("=" * 60)
        logger.info("数据库创建成功!")
        logger.info("=" * 60)
    else:
        logger.error("=" * 60)
        logger.error("数据库创建失败!")
        logger.error("=" * 60)