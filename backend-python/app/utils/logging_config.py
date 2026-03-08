"""
日志配置模块
提供统一的日志配置和格式化
"""
import logging
import sys
from datetime import datetime
from pathlib import Path

LOG_DIR = Path(__file__).parent.parent.parent / "logs"
LOG_DIR.mkdir(exist_ok=True)


class RequestFormatter(logging.Formatter):
    """
    自定义日志格式化器，支持请求ID和用户信息
    """
    def format(self, record: logging.LogRecord) -> str:
        if hasattr(record, 'request_id'):
            record.request_id = getattr(record, 'request_id', '-')
        else:
            record.request_id = '-'

        if hasattr(record, 'user_id'):
            record.user_id = getattr(record, 'user_id', '-')
        else:
            record.user_id = '-'

        return super().format(record)


def get_log_format(include_request: bool = False) -> str:
    """
    获取日志格式字符串
    """
    if include_request:
        return (
            '%(asctime)s | %(levelname)-8s | %(name)s | '
            'request_id=%(request_id)s user=%(user_id)s | '
            '%(message)s'
        )
    return '%(asctime)s | %(levelname)-8s | %(name)s | %(message)s'


def setup_logging(
    level: str = "INFO",
    log_file: str | None = None,
    include_request_info: bool = True
) -> None:
    """
    配置应用日志

    Args:
        level: 日志级别 (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: 日志文件路径，默认自动生成
        include_request_info: 是否包含请求信息
    """
    log_level = getattr(logging, level.upper(), logging.INFO)

    if log_file is None:
        log_file = LOG_DIR / f"app_{datetime.now().strftime('%Y%m%d')}.log"

    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)

    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(log_level)
    console_format = logging.Formatter(
        '%(asctime)s | %(levelname)-8s | %(name)s | %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    console_handler.setFormatter(console_format)
    root_logger.addHandler(console_handler)

    file_handler = logging.FileHandler(log_file, encoding='utf-8')
    file_handler.setLevel(log_level)
    file_format = RequestFormatter(
        get_log_format(include_request_info),
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    file_handler.setFormatter(file_format)
    root_logger.addHandler(file_handler)

    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("uvicorn.error").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)

    root_logger.info(f"日志系统初始化完成，日志级别: {level}")


def get_logger(name: str) -> logging.Logger:
    """
    获取指定名称的日志记录器
    """
    return logging.getLogger(name)


logger = get_logger(__name__)
