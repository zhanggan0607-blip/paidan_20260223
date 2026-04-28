"""
SSTCP维保系统 - FastAPI后端主入口

功能模块：
- 工单管理（临时维修/定期巡检/零星用工）
- 维保计划管理
- 人员管理
- 备品备件/维修工具管理
- 周报/维保日志
- PDF导出
- 阿里云OCR身份证识别
- 钉钉免登

TODO: 统一API错误响应格式（当前混用HTTPException和ApiResponse）
TODO: 统一错误信息语言（当前中英混用）
FIXME: 全局异常处理器将detail映射为message后，前端读取方式不统一
"""
import os
import time
import uuid
from contextlib import asynccontextmanager
from datetime import datetime

from io import BytesIO

from fastapi import Depends, FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from prometheus_fastapi_instrumentator import Instrumentator
from sqlalchemy import text
from starlette.exceptions import HTTPException as StarletteHTTPException
from starlette.responses import StreamingResponse

from app.api.v1 import (
    admin_edit,
    auth,
    customer,
    dictionary,
    dingtalk_auth,
    expiring_soon,
    export_pdf,
    files,
    inspection_item,
    maintenance_log,
    maintenance_plan,
    migration,
    ocr,
    online_user,
    operation_type,
    overdue_alert,
    periodic_inspection,
    periodic_inspection_record,
    personnel,
    project_info,
    repair_tools,
    spare_parts,
    spare_parts_stock,
    spot_work,
    statistics,
    temporary_repair,
    upload,
    weekly_report,
    websocket as websocket_api,
    work_order,
    work_order_operation_log,
    work_plan,
)
from app.config import get_settings
from app.database import Base, engine, async_engine
from app.dependencies import UserInfo, get_admin_user
from app.exceptions import BusinessException
from app.middleware.rate_limit import RateLimitMiddleware
from app.middleware.csp import CSPMiddleware
from app.utils.logging_config import get_logger, setup_logging



setup_logging(debug=get_settings().debug)

logger = get_logger(__name__)
settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理（替代废弃的on_event）"""
    logger.info("正在创建数据库表...")
    try:
        Base.metadata.create_all(bind=engine, checkfirst=True)
        logger.info("数据库表创建成功")
    except Exception as e:
        if "already exists" not in str(e).lower() and "duplicate" not in str(e).lower():
            logger.error(f"创建数据库表失败: {str(e)}", exc_info=True)
        else:
            logger.info("数据库表或索引已存在，跳过创建")

    logger.info("正在创建工单编号序列...")
    try:
        with engine.connect() as conn:
            conn.execute(text("CREATE SEQUENCE IF NOT EXISTS work_order_seq START 1"))
            conn.commit()
        logger.info("工单编号序列创建成功")
    except Exception as e:
        logger.warning(f"创建工单编号序列失败（可能已存在）: {str(e)}")

    yield

    logger.info("正在关闭数据库连接...")
    if async_engine:
        await async_engine.dispose()
    engine.dispose()
    logger.info("数据库连接已关闭")


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    docs_url=settings.docs_url if settings.debug else None,
    redoc_url=settings.redoc_url if settings.debug else None,
    openapi_url=settings.openapi_url if settings.debug else None,
    lifespan=lifespan,
)

Instrumentator().instrument(app).expose(app)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],
    allow_headers=["*"],
)

app.add_middleware(GZipMiddleware, minimum_size=1000)

app.add_middleware(CSPMiddleware)

if not settings.debug:
    app.add_middleware(
        RateLimitMiddleware,
        requests_per_minute=300,
        requests_per_hour=5000,
    )



@app.middleware("http")
async def log_requests(request: Request, call_next):
    """记录请求日志中间件 + 安全响应头"""
    start_time = time.time()
    request_id = str(uuid.uuid4())

    request.state.request_id = request_id
    request.state.start_time = start_time

    logger.info(f"[{request_id}] {request.method} {request.url.path} - 开始")

    try:
        response = await call_next(request)

        process_time = (time.time() - start_time) * 1000
        status_code = response.status_code

        if request.url.path.startswith('/uploads/'):
            response.headers['Cache-Control'] = 'public, max-age=31536000'
        elif request.url.path.startswith('/api/'):
            response.headers['Cache-Control'] = 'public, max-age=60'

        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-XSS-Protection'] = '1; mode=block'
        if request.url.scheme == 'https':
            response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'

        logger.info(
            f"[{request_id}] {request.method} {request.url.path} - "
            f"状态码: {status_code}, "
            f"处理时间: {process_time:.2f}ms"
        )

        return response
    except Exception as e:
        process_time = (time.time() - start_time) * 1000
        logger.error(
            f"[{request_id}] {request.method} {request.url.path} - "
            f"异常: {str(e)}, "
            f"处理时间: {process_time:.2f}ms"
        )
        raise

app.include_router(auth.router, prefix=settings.api_prefix)
app.include_router(project_info.router, prefix=settings.api_prefix)
app.include_router(maintenance_plan.router, prefix=settings.api_prefix)
app.include_router(personnel.router, prefix=settings.api_prefix)
app.include_router(periodic_inspection.router, prefix=settings.api_prefix)
app.include_router(periodic_inspection_record.router, prefix=settings.api_prefix)
app.include_router(inspection_item.router, prefix=settings.api_prefix)
app.include_router(overdue_alert.router, prefix=settings.api_prefix)
app.include_router(expiring_soon.router, prefix=settings.api_prefix)
app.include_router(temporary_repair.router, prefix=settings.api_prefix)
app.include_router(spot_work.router, prefix=settings.api_prefix)
app.include_router(spare_parts.router, prefix=settings.api_prefix)
app.include_router(spare_parts_stock.router, prefix=settings.api_prefix)
app.include_router(statistics.router, prefix=settings.api_prefix)
app.include_router(dictionary.router, prefix=settings.api_prefix)
app.include_router(work_plan.router, prefix=settings.api_prefix)
app.include_router(customer.router, prefix=settings.api_prefix)
app.include_router(repair_tools.router, prefix=settings.api_prefix)
app.include_router(upload.router, prefix=settings.api_prefix)
app.include_router(files.router, prefix=settings.api_prefix)
app.include_router(work_order.router, prefix=settings.api_prefix)
app.include_router(maintenance_log.router, prefix=settings.api_prefix)
app.include_router(weekly_report.router, prefix=settings.api_prefix)
app.include_router(work_order_operation_log.router, prefix=settings.api_prefix)
app.include_router(operation_type.router, prefix=settings.api_prefix)
app.include_router(ocr.router, prefix=settings.api_prefix)
app.include_router(migration.router, prefix=settings.api_prefix)
app.include_router(dingtalk_auth.router, prefix=settings.api_prefix)
app.include_router(online_user.router, prefix=settings.api_prefix)
app.include_router(websocket_api.router, prefix=settings.api_prefix)
app.include_router(export_pdf.router, prefix=settings.api_prefix)
app.include_router(admin_edit.router, prefix=settings.api_prefix)



from app.models.uploaded_file import UploadedFile
from app.utils import get_inline_content_disposition

UPLOAD_DIR = "/app/uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)


@app.get("/uploads/{upload_date}/{filename}")
async def get_uploaded_file(upload_date: str, filename: str):
    """
    从OSS或数据库获取上传的文件

    读取优先级：
    1. OSS存储的文件（storage_type=oss）→ 重定向到OSS URL
    2. 数据库存储的文件（storage_type=database）→ 从数据库读取
    3. 文件系统（兼容旧数据）→ 从本地文件读取
    """
    file_path = f"/uploads/{upload_date}/{filename}"

    from app.database import SessionLocal
    db = SessionLocal()
    try:
        uploaded_file = db.query(UploadedFile).filter(
            UploadedFile.file_path == file_path
        ).first()

        if uploaded_file:
            if uploaded_file.storage_type == "oss" and uploaded_file.oss_url:
                from fastapi.responses import RedirectResponse
                logger.info(f"重定向到OSS: {file_path}")
                return RedirectResponse(url=uploaded_file.oss_url)

            if uploaded_file.file_data:
                logger.info(f"从数据库读取文件: {file_path}")
                media_type = uploaded_file.content_type or "application/octet-stream"
                return StreamingResponse(
                    BytesIO(uploaded_file.file_data),
                    media_type=media_type,
                    headers={
                        "Cache-Control": "public, max-age=31536000",
                        "Content-Disposition": get_inline_content_disposition(uploaded_file.original_filename or filename)
                    }
                )

        file_system_path = os.path.join(UPLOAD_DIR, upload_date, filename)
        if os.path.exists(file_system_path):
            logger.info(f"从文件系统读取文件(兼容旧数据): {file_path}")

            content_type = "image/jpeg"
            if filename.lower().endswith(".png"):
                content_type = "image/png"
            elif filename.lower().endswith(".gif"):
                content_type = "image/gif"
            elif filename.lower().endswith(".webp"):
                content_type = "image/webp"

            def file_iterator():
                with open(file_system_path, "rb") as f:
                    while chunk := f.read(65536):
                        yield chunk

            return StreamingResponse(
                file_iterator(),
                media_type=content_type,
                headers={
                    "Cache-Control": "public, max-age=31536000",
                    "Content-Disposition": get_inline_content_disposition(filename)
                }
            )

        logger.warning(f"文件不存在: {file_path}")
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="文件不存在")
    finally:
        db.close()





@app.get("/")
def read_root():
    return {
        "message": "SSTCP Maintenance System API",
        "version": settings.app_version,
        "docs": settings.docs_url,
        "supported_versions": ["/api/v1"],
    }


@app.get("/api/v1/health")
async def health_check():
    """
    健康检查端点（异步）
    用于监控服务状态和数据库连接
    路径: /api/v1/health
    """
    db_status = "healthy"
    try:
        if async_engine:
            async with async_engine.connect() as conn:
                await conn.execute(text("SELECT 1"))
        else:
            with engine.connect() as conn:
                conn.execute(text("SELECT 1"))
    except Exception as e:
        db_status = f"unhealthy: {str(e)}"
        logger.error(f"健康检查数据库连接失败: {e}")

    return {
        "status": "healthy" if db_status == "healthy" else "degraded",
        "timestamp": datetime.now().isoformat(),
        "version": settings.app_version,
        "database": db_status,
        "async_db": async_engine is not None,
    }


VALID_TABLE_NAMES = {
    'periodic_inspection', 'temporary_repair', 'spot_work',
    'maintenance_plan', 'work_plan', 'maintenance_log',
    'weekly_report', 'project_info', 'personnel',
    'spot_work_worker', 'dictionary', 'uploaded_file',
    'spare_parts_stock', 'spare_parts_usage', 'spare_parts_inbound',
    'repair_tools_stock', 'repair_tools_issue', 'repair_tools_inbound',
    'customer', 'customer_contact', 'inspection_item',
    'work_order_operation_log', 'operation_type', 'online_user',
    'periodic_inspection_record',
}

VALID_COLUMN_NAMES = {
    'total_count', 'plan_id', 'signature',
    'maintenance_personnel', 'responsible_department', 'contact_info',
    'maintenance_requirements', 'maintenance_standard', 'plan_status',
    'status', 'completion_rate', 'filled_count', 'inspection_items',
    'project_manager', 'id_card_number', 'name', 'is_deleted',
}

VALID_INDEX_NAMES = {
    'idx_project_info_project_manager', 'idx_spot_work_worker_id_card',
    'idx_spot_work_worker_name', 'idx_weekly_report_is_deleted',
    'idx_maintenance_log_is_deleted',
    'idx_periodic_inspection_plan_id', 'idx_temporary_repair_plan_id',
    'idx_spot_work_plan_id',
}


def _validate_table_name(name: str) -> str:
    if name not in VALID_TABLE_NAMES:
        raise ValueError(f"Invalid table name: {name}")
    return name


def _validate_column_name(name: str) -> str:
    if name not in VALID_COLUMN_NAMES:
        raise ValueError(f"Invalid column name: {name}")
    return name


def _validate_identifier(name: str, allowed: set[str]) -> str:
    if name not in allowed:
        raise ValueError(f"Invalid identifier: {name}")
    return name


@app.post("/migrate/add-total-count")
def migrate_add_total_count(admin_user: UserInfo = Depends(get_admin_user)):
    """
    数据库迁移：添加total_count字段
    需要超级管理员权限
    """
    logger.info(f"迁移操作由管理员 {admin_user.name} 执行")
    try:
        with engine.connect() as conn:
            result = conn.execute(
                text("SELECT column_name FROM information_schema.columns WHERE table_name = :table AND column_name = :col"),
                {"table": "periodic_inspection", "col": "total_count"}
            )

            if result.fetchone() is None:
                conn.execute(text("ALTER TABLE periodic_inspection ADD COLUMN total_count INTEGER DEFAULT 5"))
                conn.commit()
                return {"success": True, "message": "Successfully added total_count column"}
            else:
                return {"success": True, "message": "Column total_count already exists"}
    except Exception as e:
        error_id = str(uuid.uuid4())[:8]
        logger.error(f"[{error_id}] 迁移失败: {str(e)}")
        return {"success": False, "message": f"迁移失败，错误ID: {error_id}，请联系管理员"}


@app.post("/migrate/add-plan-id-to-work-orders")
def migrate_add_plan_id(admin_user: UserInfo = Depends(get_admin_user)):
    """
    为工单表添加plan_id字段，关联维保计划
    需要超级管理员权限
    """
    logger.info(f"迁移操作由管理员 {admin_user.name} 执行")
    results = {}

    tables = [
        ('periodic_inspection', 'inspection_id'),
        ('temporary_repair', 'repair_id'),
        ('spot_work', 'work_id')
    ]

    try:
        with engine.connect() as conn:
            for table_name, _id_field in tables:
                _validate_table_name(table_name)
                result = conn.execute(
                    text("SELECT column_name FROM information_schema.columns WHERE table_name = :table AND column_name = :col"),
                    {"table": table_name, "col": "plan_id"}
                )

                if result.fetchone() is None:
                    idx_name = f"idx_{table_name}_plan_id"
                    _validate_identifier(idx_name, VALID_INDEX_NAMES | {f"idx_{t}_plan_id" for t, _ in tables})
                    conn.execute(text(f"ALTER TABLE {_validate_table_name(table_name)} ADD COLUMN plan_id VARCHAR(50) NULL"))
                    conn.execute(text(f"CREATE INDEX IF NOT EXISTS {_validate_identifier(idx_name, VALID_INDEX_NAMES | {f'idx_{t}_plan_id' for t, _ in tables})} ON {_validate_table_name(table_name)}(plan_id)"))
                    conn.commit()
                    results[table_name] = "Added plan_id column"
                else:
                    results[table_name] = "Column plan_id already exists"

            return {"success": True, "message": "Migration completed", "details": results}
    except Exception as e:
        error_id = str(uuid.uuid4())[:8]
        logger.error(f"[{error_id}] 迁移失败: {str(e)}")
        return {"success": False, "message": f"迁移失败，错误ID: {error_id}，请联系管理员", "details": results}


@app.post("/migrate/add-signature-field")
def migrate_add_signature_field(admin_user: UserInfo = Depends(get_admin_user)):
    """
    为工单表添加signature字段
    需要超级管理员权限
    """
    logger.info(f"迁移操作由管理员 {admin_user.name} 执行")
    results = {}

    tables = ['periodic_inspection', 'temporary_repair', 'spot_work']

    try:
        with engine.connect() as conn:
            for table_name in tables:
                _validate_table_name(table_name)
                result = conn.execute(
                    text("SELECT column_name FROM information_schema.columns WHERE table_name = :table AND column_name = :col"),
                    {"table": table_name, "col": "signature"}
                )

                if result.fetchone() is None:
                    conn.execute(text(f"ALTER TABLE {_validate_table_name(table_name)} ADD COLUMN signature TEXT NULL"))
                    conn.commit()
                    results[table_name] = "Added signature column"
                else:
                    results[table_name] = "Column signature already exists"

            return {"success": True, "message": "Migration completed", "details": results}
    except Exception as e:
        error_id = str(uuid.uuid4())[:8]
        logger.error(f"[{error_id}] 迁移失败: {str(e)}")
        return {"success": False, "message": f"迁移失败，错误ID: {error_id}，请联系管理员", "details": results}


@app.post("/migrate/fix-maintenance-plan-columns")
def migrate_fix_maintenance_plan_columns(admin_user: UserInfo = Depends(get_admin_user)):
    """
    修复maintenance_plan表缺失的字段
    需要超级管理员权限
    """
    logger.info(f"迁移操作由管理员 {admin_user.name} 执行")
    results = {}

    columns_to_add = [
        ('maintenance_personnel', 'VARCHAR(100)'),
        ('responsible_department', 'VARCHAR(100)'),
        ('contact_info', 'VARCHAR(50)'),
        ('maintenance_requirements', 'TEXT'),
        ('maintenance_standard', 'TEXT'),
        ('plan_status', 'VARCHAR(20)'),
        ('status', "VARCHAR(20) DEFAULT '执行中'"),
        ('completion_rate', 'INTEGER DEFAULT 0'),
        ('filled_count', 'INTEGER DEFAULT 0'),
        ('total_count', 'INTEGER DEFAULT 5'),
        ('inspection_items', 'TEXT'),
    ]

    try:
        with engine.connect() as conn:
            for col_name, col_type in columns_to_add:
                _validate_column_name(col_name)
                result = conn.execute(
                    text("SELECT column_name FROM information_schema.columns WHERE table_name = :table AND column_name = :col"),
                    {"table": "maintenance_plan", "col": col_name}
                )

                if result.fetchone() is None:
                    conn.execute(text(f"ALTER TABLE maintenance_plan ADD COLUMN {_validate_column_name(col_name)} {col_type} NULL"))
                    conn.commit()
                    results[col_name] = f"Added column {col_name}"
                else:
                    results[col_name] = f"Column {col_name} already exists"

            return {"success": True, "message": "Migration completed", "details": results}
    except Exception as e:
        error_id = str(uuid.uuid4())[:8]
        logger.error(f"[{error_id}] 迁移失败: {str(e)}")
        return {"success": False, "message": f"迁移失败，错误ID: {error_id}，请联系管理员", "details": results}


@app.post("/migrate/unify-status")
def migrate_unify_status(admin_user: UserInfo = Depends(get_admin_user)):
    """
    统一工单状态为4种：执行中、待确认、已完成、已退回
    需要超级管理员权限
    """
    logger.info(f"迁移操作由管理员 {admin_user.name} 执行")
    results = {}

    try:
        with engine.connect() as conn:
            tables = ['periodic_inspection', 'temporary_repair', 'spot_work', 'maintenance_plan', 'work_plan']
            old_statuses = ['未下发', '待执行', '未进行']

            for table in tables:
                _validate_table_name(table)
                try:
                    for old_status in old_statuses:
                        result = conn.execute(
                            text(f"UPDATE {_validate_table_name(table)} SET status = :new_status WHERE status = :old_status"),
                            {"new_status": "执行中", "old_status": old_status}
                        )
                        if result.rowcount > 0:
                            results[f"{table}_{old_status}"] = f"Updated {result.rowcount} rows"
                    conn.commit()
                except Exception as e:
                    results[table] = f"Error: {str(e)}"

            try:
                conn.execute(text("""
                    UPDATE dictionary
                    SET dict_value = '执行中'
                    WHERE dict_value IN ('未下发', '待执行', '未进行')
                    AND dict_type LIKE '%status%'
                """))
                conn.commit()
                results['dictionary'] = "Updated dictionary entries"
            except Exception as e:
                results['dictionary'] = f"Error: {str(e)}"

            return {"success": True, "message": "状态统一迁移完成", "details": results}
    except Exception as e:
        error_id = str(uuid.uuid4())[:8]
        logger.error(f"[{error_id}] 迁移失败: {str(e)}")
        return {"success": False, "message": f"迁移失败，错误ID: {error_id}，请联系管理员", "details": results}


@app.post("/migrate/add-indexes")
def migrate_add_indexes(admin_user: UserInfo = Depends(get_admin_user)):
    """
    添加缺失索引
    需要超级管理员权限
    """
    logger.info(f"迁移操作由管理员 {admin_user.name} 执行")
    results = {}

    indexes = [
        ('idx_project_info_project_manager', 'project_info', 'project_manager'),
        ('idx_spot_work_worker_id_card', 'spot_work_worker', 'id_card_number'),
        ('idx_spot_work_worker_name', 'spot_work_worker', 'name'),
        ('idx_weekly_report_is_deleted', 'weekly_report', 'is_deleted'),
        ('idx_maintenance_log_is_deleted', 'maintenance_log', 'is_deleted'),
    ]

    try:
        with engine.connect() as conn:
            for idx_name, table, column in indexes:
                try:
                    _validate_identifier(idx_name, VALID_INDEX_NAMES)
                    _validate_table_name(table)
                    _validate_column_name(column)
                    conn.execute(text(f"CREATE INDEX IF NOT EXISTS {_validate_identifier(idx_name, VALID_INDEX_NAMES)} ON {_validate_table_name(table)}({_validate_column_name(column)})"))
                    conn.commit()
                    results[idx_name] = f"Created index on {table}.{column}"
                except Exception as e:
                    results[idx_name] = f"Error: {str(e)}"

            return {"success": True, "message": "索引添加完成", "details": results}
    except Exception as e:
        error_id = str(uuid.uuid4())[:8]
        logger.error(f"[{error_id}] 迁移失败: {str(e)}")
        return {"success": False, "message": f"迁移失败，错误ID: {error_id}，请联系管理员", "details": results}


@app.exception_handler(BusinessException)
async def business_exception_handler(request: Request, exc: BusinessException):
    """
    处理业务异常
    业务异常是预期的错误，可以安全地返回给客户端
    """
    logger.warning(f"业务异常 [{request.method} {request.url.path}]: {exc.code} - {exc.message}")
    return JSONResponse(
        status_code=exc.code,
        content={"code": exc.code, "message": exc.message, "data": None},
    )


@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    """
    处理HTTP异常
    """
    logger.warning(f"HTTP异常 [{request.method} {request.url.path}]: {exc.status_code} - {exc.detail}")
    return JSONResponse(
        status_code=exc.status_code,
        content={"code": exc.status_code, "message": exc.detail, "data": None},
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """
    处理请求参数验证异常
    """
    errors = []
    for error in exc.errors():
        errors.append({
            "field": ".".join(str(x) for x in error["loc"]),
            "message": error["msg"],
            "type": error["type"],
        })
    logger.warning(f"参数验证失败 [{request.method} {request.url.path}]: {errors}")
    return JSONResponse(
        status_code=422,
        content={"code": 422, "message": "参数验证失败", "data": {"errors": errors}},
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """
    处理未捕获异常
    不暴露内部错误信息，只返回错误ID用于追踪
    """
    import traceback
    error_id = str(uuid.uuid4())[:8]
    error_trace = traceback.format_exc()
    logger.error(f"[{error_id}] 未处理异常 [{request.method} {request.url.path}]: {str(exc)}\n{error_trace}")

    return JSONResponse(
        status_code=500,
        content={
            "code": 500,
            "message": f"服务器内部错误，错误ID: {error_id}，请联系管理员",
            "data": None
        },
    )
