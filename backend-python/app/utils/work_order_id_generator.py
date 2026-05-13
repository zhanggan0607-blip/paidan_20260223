"""
工单编号生成工具 - 基于数据库查询保证唯一性
兼容无CREATE SEQUENCE权限的RDS环境
"""
import threading
from app.utils.logging_config import get_logger
from datetime import datetime

from sqlalchemy import text
from sqlalchemy.orm import Session

logger = get_logger(__name__)

_seq_lock = threading.Lock()


def _try_nextval(db: Session) -> int | None:
    try:
        seq = db.execute(text("SELECT nextval('work_order_seq')")).scalar()
        return int(seq)
    except Exception as e:
        logger.debug(f"数据库序列不可用: {e}")
        return None


def _get_next_seq_from_table(db: Session, prefix: str, today: str) -> int:
    pattern = f"{prefix}-%-{today}-%"
    try:
        result = db.execute(text(
            "SELECT MAX(CAST(SUBSTRING(id_col FROM '[0-9]+$') AS INTEGER)) "
            "FROM (SELECT repair_id AS id_col FROM temporary_repair WHERE repair_id LIKE :pat "
            "UNION ALL "
            "SELECT inspection_id AS id_col FROM periodic_inspection WHERE inspection_id LIKE :pat "
            "UNION ALL "
            "SELECT work_id AS id_col FROM spot_work WHERE work_id LIKE :pat) sub"
        ), {"pat": pattern}).scalar()
        return (result or 0) + 1
    except Exception as e:
        logger.warning(f"从表查询序号失败: {e}")
        return 1


def generate_work_order_id(db: Session, prefix: str, project_id: str) -> str:
    """
    生成唯一的工单编号
    格式: 前缀-项目编号-年月日-序号
    例如: XJ-PRJ001-20260222-0001

    优先使用数据库序列，序列不可用时降级为表查询方式
    """
    today = datetime.now().strftime("%Y%m%d")

    seq = _try_nextval(db)

    if seq is None:
        with _seq_lock:
            seq = _get_next_seq_from_table(db, prefix, today)

    sequence = str(seq).zfill(4)
    work_id = f"{prefix}-{project_id}-{today}-{sequence}"

    logger.debug(f"生成工单编号: {work_id}")
    return work_id


def generate_inspection_id(db: Session, project_id: str) -> str:
    """生成定期巡检单编号"""
    return generate_work_order_id(db, "XJ", project_id)


def generate_repair_id(db: Session, project_id: str) -> str:
    """生成临时维修单编号"""
    return generate_work_order_id(db, "WX", project_id)


def generate_spot_work_id(db: Session, project_id: str) -> str:
    """生成零星用工单编号"""
    return generate_work_order_id(db, "YG", project_id)
