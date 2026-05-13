"""
文件恢复脚本
扫描数据库中所有引用 /uploads/ 路径的记录，检查 uploaded_file 表中是否有对应记录，
并从阿里云OSS恢复缺失的记录。

使用方法:
    docker exec sstcp-backend python -m scripts.recover_files
    docker exec sstcp-backend python -m scripts.recover_files --dry-run
    docker exec sstcp-backend python -m scripts.recover_files --check-only
"""
import argparse
import json
import os
import sys
import uuid

os.environ.setdefault("DATABASE_URL", "")

from sqlalchemy import text
from sqlalchemy.orm import sessionmaker

from app.models.uploaded_file import UploadedFile
from app.utils.oss_service import get_oss_service, OSSService
from app.utils.logging_config import get_logger

logger = get_logger(__name__)

_session_local = None


def get_db_session():
    global _session_local
    if _session_local is None:
        from app.database import engine
        _session_local = sessionmaker(bind=engine)
    return _session_local()


def extract_upload_paths(value) -> list[str]:
    if not value:
        return []
    paths = []
    if isinstance(value, str):
        if value.startswith("/uploads/"):
            paths.append(value)
        else:
            try:
                parsed = json.loads(value)
                if isinstance(parsed, list):
                    for item in parsed:
                        if isinstance(item, str) and item.startswith("/uploads/"):
                            paths.append(item)
            except (json.JSONDecodeError, TypeError):
                pass
    elif isinstance(value, list):
        for item in value:
            if isinstance(item, str) and item.startswith("/uploads/"):
                paths.append(item)
    return paths


def scan_all_file_references(db) -> dict[str, list[dict]]:
    logger.info("扫描数据库中所有文件引用...")
    references = {}

    scan_configs = [
        {
            "table": "spot_work_worker",
            "columns": ["id_card_front", "id_card_back"],
            "label": "身份证照片",
            "extra_cols": ["name", "spot_work_id"],
        },
        {
            "table": "temporary_repair",
            "columns": ["photos"],
            "label": "临时维修照片",
            "extra_cols": ["work_order_id"],
        },
        {
            "table": "spot_work",
            "columns": ["photos"],
            "label": "零星用工照片",
            "extra_cols": ["work_order_id"],
        },
        {
            "table": "periodic_inspection_record",
            "columns": ["photos"],
            "label": "巡检记录照片",
            "extra_cols": ["periodic_inspection_id"],
        },
        {
            "table": "maintenance_log",
            "columns": ["images"],
            "label": "维保日志照片",
            "extra_cols": ["work_plan_id"],
        },
        {
            "table": "weekly_report",
            "columns": ["images"],
            "label": "周报照片",
            "extra_cols": ["work_plan_id"],
        },
    ]

    for config in scan_configs:
        table = config["table"]
        columns = config["columns"]
        label = config["label"]
        extra_cols = config.get("extra_cols", [])

        try:
            cols_sql = ", ".join(["id"] + extra_cols + columns)
            sql = text(f"SELECT {cols_sql} FROM {table}")
            result = db.execute(sql)

            for row in result:
                row_dict = dict(row._mapping)
                row_id = row_dict["id"]

                for col in columns:
                    value = row_dict.get(col)
                    paths = extract_upload_paths(value)

                    for file_path in paths:
                        if file_path not in references:
                            references[file_path] = []
                        references[file_path].append({
                            "table": table,
                            "label": label,
                            "column": col,
                            "row_id": row_id,
                            "extra": {k: row_dict.get(k) for k in extra_cols},
                        })

            logger.info(f"  {label}({table}): 扫描完成")
        except Exception as e:
            logger.warning(f"  {label}({table}): 扫描失败 - {e}")

    logger.info(f"共发现 {len(references)} 个唯一的文件引用路径")
    return references


def check_file_in_uploaded_file(db, file_path: str) -> UploadedFile | None:
    return db.query(UploadedFile).filter(
        UploadedFile.file_path == file_path
    ).first()


def check_file_in_oss(oss: OSSService, file_path: str) -> tuple[bool, str | None]:
    parts = file_path.strip("/").split("/")
    if len(parts) < 3:
        return False, None

    upload_date = parts[1]
    filename = parts[2]
    oss_key = OSSService.generate_oss_key(upload_date, filename)

    if oss.file_exists(oss_key):
        oss_url = oss.get_file_url(oss_key)
        return True, oss_url

    return False, None


def recover_file_record(db, file_path: str, oss_url: str) -> UploadedFile:
    parts = file_path.strip("/").split("/")
    upload_date = parts[1] if len(parts) >= 3 else "unknown"
    filename = parts[2] if len(parts) >= 3 else "unknown"

    content_type = "image/jpeg"
    if filename.lower().endswith(".png"):
        content_type = "image/png"
    elif filename.lower().endswith(".gif"):
        content_type = "image/gif"
    elif filename.lower().endswith(".webp"):
        content_type = "image/webp"

    recovered = UploadedFile(
        file_id=str(uuid.uuid4()),
        original_filename=filename,
        stored_filename=filename,
        content_type=content_type,
        file_data=None,
        file_size=0,
        file_path=file_path,
        upload_date=upload_date,
        storage_type="oss",
        oss_url=oss_url,
    )

    db.add(recovered)
    db.commit()
    db.refresh(recovered)

    return recovered


def main():
    parser = argparse.ArgumentParser(description="文件恢复脚本")
    parser.add_argument("--dry-run", action="store_true", help="只检查不恢复")
    parser.add_argument("--check-only", action="store_true", help="只检查文件状态")
    args = parser.parse_args()

    logger.info("=" * 60)
    logger.info("文件恢复脚本启动")
    logger.info(f"模式: {'仅检查' if args.check_only else '干运行' if args.dry_run else '恢复'}")
    logger.info("=" * 60)

    db = get_db_session()

    try:
        oss = get_oss_service()
        oss_available = oss.is_available
        logger.info(f"OSS服务: {'可用' if oss_available else '不可用'}")
    except Exception as e:
        logger.error(f"OSS服务初始化失败: {e}")
        oss_available = False

    references = scan_all_file_references(db)

    stats = {
        "total_paths": len(references),
        "in_database": 0,
        "missing_from_database": 0,
        "in_oss": 0,
        "not_in_oss": 0,
        "recovered": 0,
        "unrecoverable": 0,
    }

    missing_files = []
    unrecoverable_files = []

    for file_path, refs in references.items():
        existing = check_file_in_uploaded_file(db, file_path)

        if existing:
            stats["in_database"] += 1
            continue

        stats["missing_from_database"] += 1

        ref_info = refs[0]
        logger.info(f"缺失: {file_path} (来源: {ref_info['label']}-{ref_info['column']}, ID={ref_info['row_id']})")

        if not oss_available:
            stats["not_in_oss"] += 1
            unrecoverable_files.append({
                "file_path": file_path,
                "reason": "OSS不可用",
                "references": refs,
            })
            continue

        in_oss, oss_url = check_file_in_oss(oss, file_path)

        if in_oss:
            stats["in_oss"] += 1
            logger.info(f"  -> OSS中存在: {oss_url}")

            if args.check_only or args.dry_run:
                logger.info(f"  -> [干运行] 将恢复数据库记录")
                missing_files.append({
                    "file_path": file_path,
                    "oss_url": oss_url,
                    "status": "can_recover",
                    "references": refs,
                })
            else:
                try:
                    recovered = recover_file_record(db, file_path, oss_url)
                    stats["recovered"] += 1
                    logger.info(f"  -> 已恢复: file_id={recovered.file_id}")
                    missing_files.append({
                        "file_path": file_path,
                        "oss_url": oss_url,
                        "status": "recovered",
                        "file_id": recovered.file_id,
                        "references": refs,
                    })
                except Exception as e:
                    logger.error(f"  -> 恢复失败: {e}")
                    db.rollback()
                    unrecoverable_files.append({
                        "file_path": file_path,
                        "reason": f"恢复失败: {e}",
                        "references": refs,
                    })
        else:
            stats["not_in_oss"] += 1
            stats["unrecoverable"] += 1
            logger.warning(f"  -> OSS中也不存在，文件已永久丢失")
            unrecoverable_files.append({
                "file_path": file_path,
                "reason": "OSS中不存在",
                "references": refs,
            })

    logger.info("=" * 60)
    logger.info("扫描结果汇总:")
    logger.info(f"  总文件引用数: {stats['total_paths']}")
    logger.info(f"  数据库中存在: {stats['in_database']}")
    logger.info(f"  数据库中缺失: {stats['missing_from_database']}")
    logger.info(f"  OSS中可恢复: {stats['in_oss']}")
    logger.info(f"  OSS中不存在: {stats['not_in_oss']}")
    logger.info(f"  已恢复: {stats['recovered']}")
    logger.info(f"  不可恢复: {stats['unrecoverable']}")
    logger.info("=" * 60)

    if unrecoverable_files:
        logger.warning("以下文件已永久丢失，需要用户重新上传:")
        for f in unrecoverable_files:
            ref = f["references"][0]
            logger.warning(f"  {f['file_path']}")
            logger.warning(f"    原因: {f['reason']}")
            logger.warning(f"    来源: {ref['label']}-{ref['column']}, 表={ref['table']}, ID={ref['row_id']}")

    db.close()

    return 0 if stats["unrecoverable"] == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
