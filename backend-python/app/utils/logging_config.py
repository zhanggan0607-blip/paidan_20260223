"""
日志配置模块
配置日志格式、轮转和输出
"""
import logging
import logging.handlers
import os
from pathlib import Path
from datetime import datetime


LOG_DIR = Path(__file__).parent.parent / "logs"
LOG_DIR.mkdir(exist_ok=True)


def setup_logging(log_level: str = "INFO"):
    """
    配置应用日志
    
    Args:
        log_level: 日志级别 (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    """
    log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    date_format = "%Y-%m-%d %H:%M:%S"
    
    level = getattr(logging, log_level.upper(), logging.INFO)
    
    root_logger = logging.getLogger()
    root_logger.setLevel(level)
    
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    console_handler = logging.StreamHandler()
    console_handler.setLevel(level)
    console_formatter = logging.Formatter(log_format, datefmt=date_format)
    console_handler.setFormatter(console_formatter)
    root_logger.addHandler(console_handler)
    
    today = datetime.now().strftime("%Y-%m-%d")
    app_log_file = LOG_DIR / f"app-{today}.log"
    file_handler = logging.handlers.RotatingFileHandler(
        app_log_file,
        maxBytes=10 * 1024 * 1024,
        backupCount=5,
        encoding="utf-8"
    )
    file_handler.setLevel(level)
    file_formatter = logging.Formatter(log_format, datefmt=date_format)
    file_handler.setFormatter(file_formatter)
    root_logger.addHandler(file_handler)
    
    error_log_file = LOG_DIR / f"error-{today}.log"
    error_handler = logging.handlers.RotatingFileHandler(
        error_log_file,
        maxBytes=10 * 1024 * 1024,
        backupCount=5,
        encoding="utf-8"
    )
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(file_formatter)
    root_logger.addHandler(error_handler)
    
    logging.getLogger("uvicorn").setLevel(logging.WARNING)
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)
    
    return root_logger


def get_log_stats() -> dict:
    """
    获取日志统计信息
    """
    log_files = list(LOG_DIR.glob("*.log"))
    total_size = sum(f.stat().st_size for f in log_files if f.exists())
    
    return {
        "log_dir": str(LOG_DIR),
        "file_count": len(log_files),
        "total_size_mb": round(total_size / (1024 * 1024), 2),
        "files": [
            {
                "name": f.name,
                "size_kb": round(f.stat().st_size / 1024, 2)
            }
            for f in sorted(log_files, key=lambda x: x.stat().st_mtime, reverse=True)[:10]
        ]
    }


def cleanup_old_logs(days: int = 30):
    """
    清理旧日志文件
    
    Args:
        days: 保留天数
    """
    from datetime import datetime, timedelta
    
    cutoff = datetime.now() - timedelta(days=days)
    cleaned = 0
    
    for log_file in LOG_DIR.glob("*.log"):
        try:
            mtime = datetime.fromtimestamp(log_file.stat().st_mtime)
            if mtime < cutoff:
                log_file.unlink()
                cleaned += 1
        except Exception:
            pass
    
    return cleaned
