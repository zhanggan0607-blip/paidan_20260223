import os
import json
import glob
from datetime import datetime, timezone, timedelta
from typing import Optional

from fastapi import APIRouter, Depends, Query, HTTPException
from pydantic import BaseModel, Field

from app.dependencies import get_admin_user
from app.utils.logging_config import get_logger, get_log_dir, DEFAULT_LOG_RETENTION_DAYS
from app.config import get_settings

logger = get_logger(__name__)
router = APIRouter(prefix="/logs", tags=["日志管理"])


class LogQueryParams(BaseModel):
    start_time: Optional[str] = Field(None, description="开始时间 (ISO格式, 如 2025-01-01T00:00:00)")
    end_time: Optional[str] = Field(None, description="结束时间 (ISO格式)")
    level: Optional[str] = Field(None, description="日志级别: DEBUG, INFO, WARNING, ERROR, CRITICAL")
    module: Optional[str] = Field(None, description="模块名称 (模糊匹配)")
    keyword: Optional[str] = Field(None, description="关键词搜索 (消息内容)")
    request_id: Optional[str] = Field(None, description="请求ID")
    user_id: Optional[str] = Field(None, description="用户ID")
    log_type: Optional[str] = Field("app", description="日志类型: app, error, access")
    page: int = Field(1, ge=1, description="页码")
    page_size: int = Field(50, ge=1, le=200, description="每页条数")


class LogStats(BaseModel):
    total_files: int = 0
    total_size_mb: float = 0.0
    retention_days: int = DEFAULT_LOG_RETENTION_DAYS
    log_files: list[dict] = []
    level_distribution: dict[str, int] = {}
    oldest_log: Optional[str] = None
    newest_log: Optional[str] = None


LEVEL_MAP = {
    "DEBUG": 10,
    "INFO": 20,
    "WARNING": 30,
    "ERROR": 40,
    "CRITICAL": 50,
}


def _parse_log_line(line: str) -> Optional[dict]:
    line = line.strip()
    if not line:
        return None
    try:
        entry = json.loads(line)
        return entry
    except (json.JSONDecodeError, ValueError):
        return None


def _get_log_files(log_dir: str, log_type: str = "app") -> list[str]:
    base_names = {
        "app": "app.log",
        "error": "error.log",
        "access": "access.log",
    }
    base_name = base_names.get(log_type, "app.log")
    pattern = os.path.join(log_dir, f"{base_name}*")
    files = glob.glob(pattern)
    files.sort(key=lambda f: os.path.getmtime(f), reverse=True)
    return files


@router.get("/query", summary="查询日志")
async def query_logs(
    start_time: Optional[str] = Query(None, description="开始时间 (ISO格式)"),
    end_time: Optional[str] = Query(None, description="结束时间 (ISO格式)"),
    level: Optional[str] = Query(None, description="日志级别"),
    module: Optional[str] = Query(None, description="模块名称"),
    keyword: Optional[str] = Query(None, description="关键词"),
    request_id: Optional[str] = Query(None, description="请求ID"),
    user_id: Optional[str] = Query(None, description="用户ID"),
    log_type: str = Query("app", description="日志类型: app, error, access"),
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
    current_user=Depends(get_admin_user),
):
    settings = get_settings()
    log_dir = get_log_dir()
    if not os.path.exists(log_dir):
        return {"code": 200, "data": {"items": [], "total": 0, "page": page, "page_size": page_size}}

    files = _get_log_files(log_dir, log_type)
    if not files:
        return {"code": 200, "data": {"items": [], "total": 0, "page": page, "page_size": page_size}}

    min_level = LEVEL_MAP.get(level.upper(), 0) if level else 0

    parsed_start = None
    parsed_end = None
    if start_time:
        try:
            parsed_start = datetime.fromisoformat(start_time.replace('Z', '+00:00'))
        except ValueError:
            raise HTTPException(status_code=400, detail=f"无效的开始时间格式: {start_time}")
    if end_time:
        try:
            parsed_end = datetime.fromisoformat(end_time.replace('Z', '+00:00'))
        except ValueError:
            raise HTTPException(status_code=400, detail=f"无效的结束时间格式: {end_time}")

    all_entries = []
    max_scan_lines = settings.log_query_max_scan_lines

    for filepath in files:
        if len(all_entries) >= max_scan_lines:
            break
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                for line in f:
                    if len(all_entries) >= max_scan_lines:
                        break
                    entry = _parse_log_line(line)
                    if entry is None:
                        continue

                    if min_level > 0:
                        entry_level_no = entry.get('level_no', 0)
                        if entry_level_no < min_level:
                            continue

                    if parsed_start or parsed_end:
                        ts = entry.get('timestamp', '')
                        try:
                            entry_time = datetime.fromisoformat(ts.replace('Z', '+00:00'))
                            if parsed_start and entry_time < parsed_start:
                                continue
                            if parsed_end and entry_time > parsed_end:
                                continue
                        except (ValueError, AttributeError):
                            pass

                    if module:
                        entry_module = entry.get('module', entry.get('logger', ''))
                        if module.lower() not in entry_module.lower():
                            continue

                    if keyword:
                        msg = entry.get('message', '')
                        if keyword.lower() not in msg.lower():
                            continue

                    if request_id:
                        if entry.get('request_id', '-') != request_id:
                            continue

                    if user_id:
                        if entry.get('user_id', '-') != user_id:
                            continue

                    all_entries.append(entry)
        except OSError:
            continue

    all_entries.sort(key=lambda x: x.get('timestamp', ''), reverse=True)

    total = len(all_entries)
    start_idx = (page - 1) * page_size
    end_idx = start_idx + page_size
    page_entries = all_entries[start_idx:end_idx]

    return {
        "code": 200,
        "data": {
            "items": page_entries,
            "total": total,
            "page": page,
            "page_size": page_size,
        },
    }


@router.get("/stats", summary="日志统计信息")
async def get_log_stats(
    current_user=Depends(get_admin_user),
):
    settings = get_settings()
    log_dir = get_log_dir()
    stats = LogStats(retention_days=settings.log_retention_days)

    if not os.path.exists(log_dir):
        return {"code": 200, "data": stats.model_dump()}

    level_dist = {}
    oldest_mtime = None
    newest_mtime = None

    for filename in os.listdir(log_dir):
        filepath = os.path.join(log_dir, filename)
        if not os.path.isfile(filepath):
            continue
        try:
            file_size = os.path.getsize(filepath)
            file_mtime = os.path.getmtime(filepath)

            stats.total_files += 1
            stats.total_size_mb += file_size / (1024 * 1024)

            stats.log_files.append({
                "name": filename,
                "size_mb": round(file_size / (1024 * 1024), 2),
                "modified": datetime.fromtimestamp(file_mtime, tz=timezone.utc).isoformat(),
            })

            if oldest_mtime is None or file_mtime < oldest_mtime:
                oldest_mtime = file_mtime
            if newest_mtime is None or file_mtime > newest_mtime:
                newest_mtime = file_mtime
        except OSError:
            continue

    stats.total_size_mb = round(stats.total_size_mb, 2)
    stats.log_files.sort(key=lambda x: x['modified'], reverse=True)

    if oldest_mtime:
        stats.oldest_log = datetime.fromtimestamp(oldest_mtime, tz=timezone.utc).isoformat()
    if newest_mtime:
        stats.newest_log = datetime.fromtimestamp(newest_mtime, tz=timezone.utc).isoformat()

    app_log_path = os.path.join(log_dir, 'app.log')
    if os.path.exists(app_log_path):
        try:
            with open(app_log_path, 'r', encoding='utf-8') as f:
                for line in f:
                    entry = _parse_log_line(line)
                    if entry:
                        lvl = entry.get('level', 'UNKNOWN')
                        level_dist[lvl] = level_dist.get(lvl, 0) + 1
        except OSError:
            pass

    stats.level_distribution = level_dist

    return {"code": 200, "data": stats.model_dump()}


@router.delete("/cleanup", summary="手动触发日志清理")
async def manual_cleanup(
    current_user=Depends(get_admin_user),
):
    settings = get_settings()
    log_dir = get_log_dir()
    cutoff = datetime.now(timezone.utc) - timedelta(days=settings.log_retention_days)
    cleaned = []

    if not os.path.exists(log_dir):
        return {"code": 200, "data": {"cleaned_files": [], "count": 0}}

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
                cleaned.append(filename)
        except OSError:
            pass

    if cleaned:
        logger.info(f"手动清理过期日志文件: {cleaned}")

    return {"code": 200, "data": {"cleaned_files": cleaned, "count": len(cleaned)}}
