"""
工单编号生成工具 - 使用数据库序列保证唯一性
"""
from sqlalchemy import text
from sqlalchemy.orm import Session
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


def generate_work_order_id(db: Session, prefix: str, project_id: str) -> str:
    """
    生成唯一的工单编号
    格式: 前缀-项目编号-年月日-序号
    例如: XJ-PRJ001-20260222-0001
    
    使用数据库序列保证并发安全
    序列应该在应用启动时创建
    """
    today = datetime.now().strftime("%Y%m%d")
    
    seq = db.execute(text("SELECT nextval('work_order_seq')")).scalar()
    
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
