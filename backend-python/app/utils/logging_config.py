import json
import logging
import os
import glob
import threading
import functools
import time
from logging.handlers import TimedRotatingFileHandler
from datetime import datetime, timezone, timedelta
from typing import Optional


DEFAULT_LOG_RETENTION_DAYS = 5
DEFAULT_LOG_MAX_FILE_SIZE_MB = 50
DEFAULT_LOG_ROTATION_WHEN = 'midnight'
DEFAULT_LOG_ROTATION_INTERVAL = 1


class RequestFormatter(logging.Formatter):
    def format(self, record):
        if not hasattr(record, 'request_id'):
            record.request_id = '-'
        if not hasattr(record, 'user_id'):
            record.user_id = '-'
        if not hasattr(record, 'trace_id'):
            record.trace_id = '-'
        if not hasattr(record, 'module_name'):
            record.module_name = record.name
        return super().format(record)


class StructuredJsonFormatter(logging.Formatter):
    def format(self, record):
        RequestFormatter().format(record)

        log_entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "level_no": record.levelno,
            "logger": record.name,
            "module": getattr(record, 'module_name', record.name),
            "funcName": record.funcName,
            "lineno": record.lineno,
            "message": record.getMessage(),
            "request_id": getattr(record, 'request_id', '-'),
            "user_id": getattr(record, 'user_id', '-'),
            "trace_id": getattr(record, 'trace_id', '-'),
        }

        if record.exc_info and record.exc_info[0] is not None:
            log_entry["exception"] = self.formatException(record.exc_info)
            log_entry["exception_type"] = record.exc_info[0].__name__ if record.exc_info[0] else None

        extra_fields = {}
        standard_attrs = set(logging.LogRecord('', 0, '', 0, '', (), None).__dict__.keys())
        standard_attrs.update({
            'request_id', 'user_id', 'trace_id', 'module_name',
            'message', 'exc_info', 'exc_text', 'args',
        })
        for k, v in record.__dict__.items():
            if k not in standard_attrs and not k.startswith('_'):
                try:
                    json.dumps(v, default=str)
                    extra_fields[k] = v
                except (TypeError, ValueError):
                    extra_fields[k] = str(v)
        if extra_fields:
            log_entry["extra"] = extra_fields

        return json.dumps(log_entry, ensure_ascii=False, default=str)


class SizeAndTimeRotatingFileHandler(TimedRotatingFileHandler):
    def __init__(
        self,
        filename,
        maxBytes: int = 50 * 1024 * 1024,
        when: str = 'midnight',
        interval: int = 1,
        backupCount: int = 5,
        retention_days: int = 5,
        encoding: str = 'utf-8',
        **kwargs,
    ):
        super().__init__(
            filename,
            when=when,
            interval=interval,
            backupCount=backupCount,
            encoding=encoding,
            **kwargs,
        )
        self.maxBytes = maxBytes
        self.retention_days = retention_days

    def shouldRollover(self, record):
        if super().shouldRollover(record):
            return 1
        if self.stream is None:
            self.stream = self._open()
        try:
            if os.path.getsize(self.baseFilename) >= self.maxBytes:
                return 1
        except OSError:
            pass
        return 0

    def doRollover(self):
        super().doRollover()
        self._cleanup_old_files()

    def _cleanup_old_files(self):
        if self.retention_days <= 0:
            return
        dir_name, base_name = os.path.split(self.baseFilename)
        cutoff = datetime.now(timezone.utc) - timedelta(days=self.retention_days)
        pattern = os.path.join(dir_name, f"{base_name}*")
        for f in glob.glob(pattern):
            if f == self.baseFilename:
                continue
            try:
                file_mtime = datetime.fromtimestamp(
                    os.path.getmtime(f), tz=timezone.utc
                )
                if file_mtime < cutoff:
                    os.remove(f)
            except OSError:
                pass


class ErrorOnlyFilter(logging.Filter):
    def filter(self, record):
        return record.levelno >= logging.ERROR


def setup_logging(
    debug: bool = False,
    log_dir: Optional[str] = None,
    retention_days: int = DEFAULT_LOG_RETENTION_DAYS,
    max_file_size_mb: int = DEFAULT_LOG_MAX_FILE_SIZE_MB,
    rotation_when: str = DEFAULT_LOG_ROTATION_WHEN,
    rotation_interval: int = DEFAULT_LOG_ROTATION_INTERVAL,
):
    log_level = logging.DEBUG if debug else logging.INFO
    max_bytes = max_file_size_mb * 1024 * 1024

    if log_dir is None:
        log_dir = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'logs'
        )
    os.makedirs(log_dir, exist_ok=True)

    console_handler = logging.StreamHandler()
    console_handler.setLevel(log_level)
    console_format = logging.Formatter(
        '%(asctime)s | %(levelname)-8s | %(name)s | %(funcName)s:%(lineno)d | %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S',
    )
    console_handler.setFormatter(console_format)

    app_handler = SizeAndTimeRotatingFileHandler(
        os.path.join(log_dir, 'app.log'),
        maxBytes=max_bytes,
        when=rotation_when,
        interval=rotation_interval,
        backupCount=retention_days,
        retention_days=retention_days,
        encoding='utf-8',
    )
    app_handler.setLevel(log_level)
    app_handler.setFormatter(StructuredJsonFormatter())

    error_handler = SizeAndTimeRotatingFileHandler(
        os.path.join(log_dir, 'error.log'),
        maxBytes=max_bytes,
        when=rotation_when,
        interval=rotation_interval,
        backupCount=retention_days,
        retention_days=retention_days,
        encoding='utf-8',
    )
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(StructuredJsonFormatter())
    error_handler.addFilter(ErrorOnlyFilter())

    access_handler = SizeAndTimeRotatingFileHandler(
        os.path.join(log_dir, 'access.log'),
        maxBytes=max_bytes,
        when=rotation_when,
        interval=rotation_interval,
        backupCount=retention_days,
        retention_days=retention_days,
        encoding='utf-8',
    )
    access_handler.setLevel(logging.INFO)
    access_handler.setFormatter(StructuredJsonFormatter())

    access_logger = logging.getLogger('access')
    access_logger.setLevel(logging.INFO)
    access_logger.propagate = False
    if access_logger.handlers:
        access_logger.handlers.clear()
    access_logger.addHandler(access_handler)

    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)

    if root_logger.handlers:
        root_logger.handlers.clear()

    root_logger.addHandler(console_handler)
    root_logger.addHandler(app_handler)
    root_logger.addHandler(error_handler)

    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)

    _schedule_cleanup(log_dir, retention_days)


def _schedule_cleanup(log_dir: str, retention_days: int):
    def _cleanup_task():
        cutoff = datetime.now(timezone.utc) - timedelta(days=retention_days)
        for filename in os.listdir(log_dir):
            filepath = os.path.join(log_dir, filename)
            if not os.path.isfile(filepath):
                continue
            try:
                file_mtime = datetime.fromtimestamp(
                    os.path.getmtime(filepath), tz=timezone.utc
                )
                if file_mtime < cutoff:
                    os.remove(filepath)
                    logging.getLogger(__name__).info(f"清理过期日志文件: {filename}")
            except OSError:
                pass

    def _periodic_cleanup():
        while True:
            _cleanup_task()
            threading.Event().wait(86400)

    cleanup_thread = threading.Thread(target=_periodic_cleanup, daemon=True)
    cleanup_thread.start()


def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(name)


def get_access_logger() -> logging.Logger:
    return logging.getLogger('access')


def get_log_dir() -> str:
    return os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'logs'
    )


logger = get_logger(__name__)


def log_business_operation(operation_name: str):
    def decorator(func):
        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            op_logger = get_logger(func.__module__)
            op_logger.info(f"[BUSINESS] {operation_name} 开始")
            start_time = time.monotonic()
            try:
                result = await func(*args, **kwargs)
                elapsed_ms = (time.monotonic() - start_time) * 1000
                op_logger.info(f"[BUSINESS] {operation_name} 完成, 耗时={elapsed_ms:.1f}ms")
                return result
            except Exception as e:
                elapsed_ms = (time.monotonic() - start_time) * 1000
                op_logger.error(f"[BUSINESS] {operation_name} 失败, 耗时={elapsed_ms:.1f}ms, 错误={str(e)}")
                raise

        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs):
            op_logger = get_logger(func.__module__)
            op_logger.info(f"[BUSINESS] {operation_name} 开始")
            start_time = time.monotonic()
            try:
                result = func(*args, **kwargs)
                elapsed_ms = (time.monotonic() - start_time) * 1000
                op_logger.info(f"[BUSINESS] {operation_name} 完成, 耗时={elapsed_ms:.1f}ms")
                return result
            except Exception as e:
                elapsed_ms = (time.monotonic() - start_time) * 1000
                op_logger.error(f"[BUSINESS] {operation_name} 失败, 耗时={elapsed_ms:.1f}ms, 错误={str(e)}")
                raise

        import asyncio
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        return sync_wrapper
    return decorator


def log_external_call(service_name: str):
    def decorator(func):
        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            ext_logger = get_logger(func.__module__)
            ext_logger.info(f"[EXTERNAL] 调用 {service_name} 开始")
            start_time = time.monotonic()
            try:
                result = await func(*args, **kwargs)
                elapsed_ms = (time.monotonic() - start_time) * 1000
                ext_logger.info(f"[EXTERNAL] 调用 {service_name} 完成, 耗时={elapsed_ms:.1f}ms")
                return result
            except Exception as e:
                elapsed_ms = (time.monotonic() - start_time) * 1000
                ext_logger.error(f"[EXTERNAL] 调用 {service_name} 失败, 耗时={elapsed_ms:.1f}ms, 错误={str(e)}")
                raise

        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs):
            ext_logger = get_logger(func.__module__)
            ext_logger.info(f"[EXTERNAL] 调用 {service_name} 开始")
            start_time = time.monotonic()
            try:
                result = func(*args, **kwargs)
                elapsed_ms = (time.monotonic() - start_time) * 1000
                ext_logger.info(f"[EXTERNAL] 调用 {service_name} 完成, 耗时={elapsed_ms:.1f}ms")
                return result
            except Exception as e:
                elapsed_ms = (time.monotonic() - start_time) * 1000
                ext_logger.error(f"[EXTERNAL] 调用 {service_name} 失败, 耗时={elapsed_ms:.1f}ms, 错误={str(e)}")
                raise

        import asyncio
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        return sync_wrapper
    return decorator


def log_performance(threshold_ms: float = 1000):
    def decorator(func):
        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            start_time = time.monotonic()
            try:
                result = await func(*args, **kwargs)
                elapsed_ms = (time.monotonic() - start_time) * 1000
                if elapsed_ms > threshold_ms:
                    perf_logger = get_logger(func.__module__)
                    perf_logger.warning(f"[PERFORMANCE] {func.__qualname__} 慢操作, 耗时={elapsed_ms:.1f}ms, 阈值={threshold_ms}ms")
                return result
            except Exception:
                raise

        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs):
            start_time = time.monotonic()
            try:
                result = func(*args, **kwargs)
                elapsed_ms = (time.monotonic() - start_time) * 1000
                if elapsed_ms > threshold_ms:
                    perf_logger = get_logger(func.__module__)
                    perf_logger.warning(f"[PERFORMANCE] {func.__qualname__} 慢操作, 耗时={elapsed_ms:.1f}ms, 阈值={threshold_ms}ms")
                return result
            except Exception:
                raise

        import asyncio
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        return sync_wrapper
    return decorator
