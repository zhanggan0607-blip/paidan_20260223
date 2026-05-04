import json
import logging
import os
from logging.handlers import RotatingFileHandler
from datetime import datetime, timezone


class RequestFormatter(logging.Formatter):
    def format(self, record):
        if not hasattr(record, 'request_id'):
            record.request_id = '-'
        if not hasattr(record, 'user_id'):
            record.user_id = '-'
        return super().format(record)


class JsonFormatter(logging.Formatter):
    def format(self, record):
        log_entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "request_id": getattr(record, 'request_id', '-'),
            "user_id": getattr(record, 'user_id', '-'),
        }

        if record.exc_info and record.exc_info[0] is not None:
            log_entry["exception"] = self.formatException(record.exc_info)

        extra_fields = {
            k: v for k, v in record.__dict__.items()
            if k not in logging.LogRecord(
                '', 0, '', 0, '', (), None
            ).__dict__ and k not in ('request_id', 'user_id', 'message', 'exc_info', 'exc_text')
        }
        if extra_fields:
            log_entry["extra"] = str(extra_fields)

        return json.dumps(log_entry, ensure_ascii=False, default=str)


def setup_logging(debug: bool = False):
    log_level = logging.DEBUG if debug else logging.INFO

    log_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'logs')
    os.makedirs(log_dir, exist_ok=True)

    console_handler = logging.StreamHandler()
    console_handler.setLevel(log_level)
    console_format = logging.Formatter(
        '%(asctime)s | %(levelname)-8s | %(name)s | %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    console_handler.setFormatter(console_format)

    file_handler = RotatingFileHandler(
        os.path.join(log_dir, 'app.log'),
        maxBytes=10 * 1024 * 1024,
        backupCount=10,
        encoding='utf-8',
    )
    file_handler.setLevel(log_level)
    file_handler.setFormatter(JsonFormatter())

    json_file_handler = RotatingFileHandler(
        os.path.join(log_dir, 'app.json.log'),
        maxBytes=10 * 1024 * 1024,
        backupCount=10,
        encoding='utf-8',
    )
    json_file_handler.setLevel(log_level)
    json_file_handler.setFormatter(JsonFormatter())

    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)

    if root_logger.handlers:
        root_logger.handlers.clear()

    root_logger.addHandler(console_handler)
    root_logger.addHandler(file_handler)
    root_logger.addHandler(json_file_handler)

    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)


def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(name)


logger = get_logger(__name__)
